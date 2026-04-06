"""Agent tool — spawns a sub-engine for delegated tasks.

Mirrors claurst spec's Task tool:
- Spawns sub-Engine with filtered tools (no Agent to prevent recursion)
- Isolated message history
- Shares provider and permission enforcer
"""

from __future__ import annotations

from typing import Any

from clawpy.tool.base import Permission, RunContext, ToolResult


class AgentTool:
    """Spawn a sub-agent to handle a complex task."""

    def __init__(self) -> None:
        # These are set by the CLI when building the engine
        self._provider: Any = None
        self._enforcer: Any = None
        self._config: Any = None
        self._parent_tools: Any = None

    @property
    def name(self) -> str:
        return "Agent"

    @property
    def description(self) -> str:
        return (
            "Launch a sub-agent to handle a complex task autonomously. "
            "The agent gets its own conversation context and tool access."
        )

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The task for the agent to perform",
                },
                "description": {
                    "type": "string",
                    "description": "Short description of the task (3-5 words)",
                },
                "model": {
                    "type": "string",
                    "description": "Optional model override for the sub-agent",
                },
            },
            "required": ["prompt"],
        }

    def permission_for(self, input: dict[str, Any]) -> Permission:
        return Permission.SHELL_UNSAFE

    def is_read_only(self, input: dict[str, Any]) -> bool:
        return False

    async def run(self, input: dict[str, Any], ctx: RunContext) -> ToolResult:
        prompt = input.get("prompt", "")
        if not prompt:
            return ToolResult(content="Error: prompt is required", is_error=True)

        if not self._provider or not self._config:
            return ToolResult(
                content="Error: Agent tool not properly initialized",
                is_error=True,
            )

        # Lazy imports to avoid circular dependency
        from clawpy.config.config import Config
        from clawpy.engine.engine import Engine
        from clawpy.engine.system_prompt import build_system_prompt
        from clawpy.tool.registry import ToolRegistry

        # Build sub-tool registry excluding Agent (prevent recursion)
        sub_tools = ToolRegistry()
        if self._parent_tools:
            for tool in self._parent_tools.all():
                if tool.name != "Agent":
                    sub_tools.register(tool)

        # Optional model override
        sub_config = Config(
            provider=self._config.provider,
            model=input.get("model") or self._config.model,
            api_key=self._config.api_key,
            base_url=self._config.base_url,
            max_tokens=self._config.max_tokens,
            permission_mode=self._config.permission_mode,
            work_dir=ctx.work_dir,
        )

        sub_engine = Engine(
            provider=self._provider,
            tools=sub_tools,
            enforcer=self._enforcer,
            config=sub_config,
        )
        sub_engine.set_system_prompt(build_system_prompt(ctx.work_dir, sub_config.model))

        try:
            result = await sub_engine.run_turn(prompt)
        except Exception as e:
            return ToolResult(content=f"Agent error: {e}", is_error=True)

        # Return the final assistant text
        if result.messages:
            for msg in reversed(result.messages):
                text = msg.text_content()
                if text and msg.role.value == "assistant":
                    return ToolResult(content=text)

        return ToolResult(content="Agent completed but produced no text output.")
