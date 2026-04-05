"""Anthropic Messages API provider.

Talks directly to the Anthropic API via httpx — no SDK dependency.
Converts between neutral types and Anthropic's native API format.
"""

from __future__ import annotations

import json
import os
from typing import Any, AsyncIterator

import httpx

from clawpy.config.config import ProviderConfig
from clawpy.provider.base import (
    Delta,
    EventType,
    Request,
    Response,
    StopReason,
    StreamEvent,
    ToolSpec,
    Usage,
)
from clawpy.provider.registry import register
from clawpy.provider.sse import parse_sse_with_event
from clawpy.types import ContentBlock, ContentType, ToolCall

_API_VERSION = "2023-06-01"
_DEFAULT_BASE_URL = "https://api.anthropic.com"

_STOP_MAP: dict[str | None, StopReason] = {
    "end_turn": StopReason.END_TURN,
    "tool_use": StopReason.TOOL_USE,
    "max_tokens": StopReason.MAX_TOKENS,
    "stop_sequence": StopReason.STOP_SEQUENCE,
}

_DEFAULT_MODELS = [
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-haiku-4-20250506",
]


class AnthropicProvider:
    """Direct Anthropic Messages API provider with SSE streaming."""

    def __init__(self, cfg: ProviderConfig) -> None:
        self._api_key = cfg.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._base_url = (cfg.base_url or _DEFAULT_BASE_URL).rstrip("/")
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))

    @property
    def name(self) -> str:
        return "anthropic"

    def models(self) -> list[str]:
        return _DEFAULT_MODELS

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        }

    def _build_body(self, request: Request) -> dict[str, Any]:
        """Convert neutral Request to Anthropic API request body."""
        body: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": self._convert_messages(request),
        }
        if request.system:
            body["system"] = request.system
        if request.tools:
            body["tools"] = self._convert_tools(request.tools)
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.stop_sequences:
            body["stop_sequences"] = request.stop_sequences
        return body

    def _convert_messages(self, request: Request) -> list[dict[str, Any]]:
        """Convert neutral Messages to Anthropic format."""
        from clawpy.types import Message

        result: list[dict[str, Any]] = []
        for msg in request.messages:
            assert isinstance(msg, Message)
            content_blocks: list[dict[str, Any]] = []
            for block in msg.content:
                match block.type:
                    case ContentType.TEXT:
                        content_blocks.append({"type": "text", "text": block.text})
                    case ContentType.TOOL_CALL:
                        assert block.tool_call is not None
                        content_blocks.append({
                            "type": "tool_use",
                            "id": block.tool_call.id,
                            "name": block.tool_call.name,
                            "input": block.tool_call.input,
                        })
                    case ContentType.TOOL_RESULT:
                        assert block.tool_result is not None
                        content_blocks.append({
                            "type": "tool_result",
                            "tool_use_id": block.tool_result.tool_call_id,
                            "content": block.tool_result.content,
                            **({"is_error": True} if block.tool_result.is_error else {}),
                        })
                    case ContentType.THINKING:
                        content_blocks.append({
                            "type": "thinking",
                            "thinking": block.thinking,
                        })
            result.append({"role": msg.role.value, "content": content_blocks})
        return result

    def _convert_tools(self, tools: list[ToolSpec]) -> list[dict[str, Any]]:
        """Convert ToolSpecs to Anthropic tool format."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in tools
        ]

    async def stream(self, request: Request) -> AsyncIterator[StreamEvent]:
        """Stream a request to the Anthropic API, yielding neutral StreamEvents."""
        body = self._build_body(request)
        body["stream"] = True

        # State for assembling tool calls
        active_tool_calls: dict[int, ToolCall] = {}
        tool_json_bufs: dict[int, str] = {}
        block_index = -1

        async with self._client.stream(
            "POST",
            f"{self._base_url}/v1/messages",
            json=body,
            headers=self._headers(),
        ) as resp:
            if resp.status_code != 200:
                error_body = await resp.aread()
                yield StreamEvent(
                    type=EventType.ERROR,
                    error=RuntimeError(
                        f"Anthropic API error {resp.status_code}: {error_body.decode()}"
                    ),
                )
                return

            async for event_type, data in parse_sse_with_event(resp):
                ev = self._map_event(
                    data, active_tool_calls, tool_json_bufs, block_index
                )
                if ev is not None:
                    # Track block index for tool calls
                    if data.get("type") == "content_block_start":
                        block_index = data.get("index", block_index + 1)
                    yield ev

    def _map_event(
        self,
        data: dict[str, Any],
        active_tool_calls: dict[int, ToolCall],
        tool_json_bufs: dict[int, str],
        block_index: int,
    ) -> StreamEvent | None:
        """Map a single Anthropic SSE event to a neutral StreamEvent."""
        event_type = data.get("type", "")

        match event_type:
            case "message_start":
                # Extract usage from initial message
                msg = data.get("message", {})
                usage_data = msg.get("usage", {})
                return StreamEvent(
                    type=EventType.DELTA,
                    delta=Delta(),
                    usage=Usage(
                        input_tokens=usage_data.get("input_tokens", 0),
                        output_tokens=0,
                    ),
                )

            case "content_block_start":
                index = data.get("index", 0)
                block = data.get("content_block", {})
                block_type = block.get("type", "")

                if block_type == "tool_use":
                    tc = ToolCall(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        input={},
                    )
                    active_tool_calls[index] = tc
                    tool_json_bufs[index] = ""
                    return StreamEvent(type=EventType.TOOL_START, tool_call=tc)
                elif block_type == "thinking":
                    return StreamEvent(type=EventType.DELTA, delta=Delta())
                else:
                    return StreamEvent(type=EventType.DELTA, delta=Delta())

            case "content_block_delta":
                index = data.get("index", 0)
                delta = data.get("delta", {})
                delta_type = delta.get("type", "")

                if delta_type == "text_delta":
                    return StreamEvent(
                        type=EventType.DELTA,
                        delta=Delta(text=delta.get("text", "")),
                    )
                elif delta_type == "input_json_delta":
                    partial = delta.get("partial_json", "")
                    if index in tool_json_bufs:
                        tool_json_bufs[index] += partial
                    return StreamEvent(
                        type=EventType.TOOL_DELTA,
                        delta=Delta(text=partial),
                    )
                elif delta_type == "thinking_delta":
                    return StreamEvent(
                        type=EventType.DELTA,
                        delta=Delta(thinking=delta.get("thinking", "")),
                    )

            case "content_block_stop":
                index = data.get("index", 0)
                if index in active_tool_calls:
                    # Finalize tool call with parsed JSON input
                    tc = active_tool_calls.pop(index)
                    raw_json = tool_json_bufs.pop(index, "")
                    parsed_input: dict[str, Any] = {}
                    if raw_json:
                        try:
                            parsed_input = json.loads(raw_json)
                        except json.JSONDecodeError:
                            parsed_input = {"_raw": raw_json}
                    finalized = ToolCall(id=tc.id, name=tc.name, input=parsed_input)
                    return StreamEvent(type=EventType.TOOL_END, tool_call=finalized)
                return None

            case "message_delta":
                delta = data.get("delta", {})
                usage_data = data.get("usage", {})
                stop = delta.get("stop_reason")
                return StreamEvent(
                    type=EventType.MESSAGE_STOP,
                    stop_reason=_STOP_MAP.get(stop, StopReason.END_TURN),
                    usage=Usage(
                        input_tokens=0,
                        output_tokens=usage_data.get("output_tokens", 0),
                    ),
                )

            case "message_stop":
                return None  # Already handled by message_delta

            case "ping":
                return None

        return None

    async def send(self, request: Request) -> Response:
        """Non-streaming request."""
        body = self._build_body(request)

        resp = await self._client.post(
            f"{self._base_url}/v1/messages",
            json=body,
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()

        content: list[ContentBlock] = []
        for block in data.get("content", []):
            if block["type"] == "text":
                content.append(ContentBlock(type=ContentType.TEXT, text=block["text"]))
            elif block["type"] == "tool_use":
                content.append(
                    ContentBlock(
                        type=ContentType.TOOL_CALL,
                        tool_call=ToolCall(
                            id=block["id"],
                            name=block["name"],
                            input=block.get("input", {}),
                        ),
                    )
                )

        usage_data = data.get("usage", {})
        return Response(
            id=data.get("id", ""),
            content=content,
            stop_reason=_STOP_MAP.get(data.get("stop_reason"), StopReason.END_TURN),
            usage=Usage(
                input_tokens=usage_data.get("input_tokens", 0),
                output_tokens=usage_data.get("output_tokens", 0),
            ),
        )


def _factory(cfg: ProviderConfig) -> AnthropicProvider:
    return AnthropicProvider(cfg)


register("anthropic", _factory)
