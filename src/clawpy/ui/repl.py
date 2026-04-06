"""Interactive REPL with prompt_toolkit input and rich streaming output.

Slash commands mimic Claude Code's UI where practical.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from clawpy.engine.engine import Engine
from clawpy.engine.token_budget import get_context_window
from clawpy.provider.base import EventType, StreamEvent, Usage

# ---- Model catalog ----

_MODEL_CATALOG: list[dict[str, str]] = [
    {"alias": "opus", "id": "claude-opus-4-6", "name": "Opus 4.6", "desc": "Most capable for complex work"},
    {"alias": "opus[1m]", "id": "claude-opus-4-6[1m]", "name": "Opus 4.6 (1M context)", "desc": "Most capable, extended context"},
    {"alias": "sonnet", "id": "claude-sonnet-4-6", "name": "Sonnet 4.6", "desc": "Best for everyday tasks"},
    {"alias": "sonnet[1m]", "id": "claude-sonnet-4-6[1m]", "name": "Sonnet 4.6 (1M context)", "desc": "Extended context"},
    {"alias": "haiku", "id": "claude-haiku-4-5-20251001", "name": "Haiku 4.5", "desc": "Fastest for quick answers"},
    {"alias": "gpt-4o", "id": "gpt-4o", "name": "GPT-4o", "desc": "OpenAI flagship"},
    {"alias": "gpt-4o-mini", "id": "gpt-4o-mini", "name": "GPT-4o Mini", "desc": "OpenAI fast & cheap"},
    {"alias": "gemini-2.5-pro", "id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "desc": "Google flagship, 1M context"},
    {"alias": "gemini-2.5-flash", "id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "desc": "Google fast"},
    {"alias": "deepseek-chat", "id": "deepseek-chat", "name": "DeepSeek Chat", "desc": "DeepSeek V3"},
    {"alias": "deepseek-reasoner", "id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "desc": "DeepSeek R1 with reasoning"},
]

_EFFORT_SYMBOLS = {"low": "○", "medium": "◐", "high": "●", "max": "◉"}


def _resolve_model(name: str) -> str:
    """Resolve alias to full model ID."""
    lower = name.lower().strip()
    for m in _MODEL_CATALOG:
        if lower in (m["alias"].lower(), m["id"].lower(), m["name"].lower()):
            return m["id"]
    return name  # Return as-is if not a known alias


def _get_model_info(model_id: str) -> dict[str, str] | None:
    """Get catalog entry for a model ID."""
    for m in _MODEL_CATALOG:
        if model_id == m["id"] or model_id == m["alias"]:
            return m
    return None


class REPL:
    """Interactive REPL with streaming output."""

    def __init__(self, engine: Engine, console: Console | None = None) -> None:
        self.engine = engine
        self.console = console or Console()
        self.session: PromptSession[str] = PromptSession(
            history=InMemoryHistory(),
        )
        self._session_id = uuid.uuid4().hex[:12]
        self._start_time = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._turn_count = 0

    async def run(self) -> None:
        """Main REPL loop."""
        cfg = self.engine.config
        model_info = _get_model_info(cfg.model)
        model_display = model_info["name"] if model_info else cfg.model

        self.console.print(f"[bold]ClawPy v0.1.0[/bold] — {model_display}")
        self.console.print(f"Working directory: {cfg.work_dir}")
        self.console.print("Type [bold]/help[/bold] for commands, [bold]/quit[/bold] to exit.\n")

        while True:
            try:
                user_input = await self.session.prompt_async("❯ ")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\nBye!")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                should_quit = self._handle_slash(user_input)
                if should_quit:
                    break
                continue

            await self._run_turn(user_input)

    async def _run_turn(self, user_input: str) -> None:
        """Execute a turn with streaming output."""
        text_buf = ""

        def on_stream(event: StreamEvent) -> None:
            nonlocal text_buf
            match event.type:
                case EventType.DELTA:
                    if event.delta and event.delta.text:
                        text_buf += event.delta.text
                        print(event.delta.text, end="", flush=True)
                case EventType.TOOL_START:
                    if event.tool_call:
                        if text_buf and not text_buf.endswith("\n"):
                            print()
                        self.console.print(
                            f"\n[blue]⚡ {event.tool_call.name}[/blue]", highlight=False
                        )
                case EventType.TOOL_END:
                    pass
                case EventType.ERROR:
                    if event.error:
                        self.console.print(f"[red]Error: {event.error}[/red]")

        try:
            result = await self.engine.run_turn(user_input, on_stream=on_stream)
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            return

        if text_buf and not text_buf.endswith("\n"):
            print()

        self._total_input_tokens += result.usage.input_tokens
        self._total_output_tokens += result.usage.output_tokens
        self._turn_count += 1

        if result.usage.input_tokens > 0 or result.usage.output_tokens > 0:
            self.console.print(
                f"[dim]tokens: {result.usage.input_tokens}↓ {result.usage.output_tokens}↑[/dim]"
            )

        print()

        if result.error:
            self.console.print(f"[yellow]Warning: {result.error}[/yellow]")

    def _handle_slash(self, raw: str) -> bool:
        """Handle slash commands. Returns True if REPL should exit."""
        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        match cmd:
            case "/quit" | "/exit" | "/q":
                self.console.print("Bye!")
                return True
            case "/clear":
                self.engine.clear()
                self._total_input_tokens = 0
                self._total_output_tokens = 0
                self._turn_count = 0
                self.console.print("[green]Conversation cleared.[/green]")
            case "/model":
                self._cmd_model(args)
            case "/context":
                self._cmd_context()
            case "/status":
                self._cmd_status()
            case "/compact":
                self.console.print("[yellow]Manual compact not yet implemented.[/yellow]")
            case "/plan":
                self._cmd_plan()
            case "/login":
                self._cmd_login()
            case "/logout":
                from clawpy.auth.oauth import clear_tokens
                clear_tokens()
                self.console.print("[green]Logged out.[/green]")
            case "/help":
                self._cmd_help()
            case _:
                self.console.print(f"Unknown command: {cmd}. Type /help for available commands.")

        return False

    # ---- /model ----

    def _cmd_model(self, args: str) -> None:
        if args:
            resolved = _resolve_model(args)
            self.engine.config.model = resolved
            info = _get_model_info(resolved)
            display = info["name"] if info else resolved
            desc = f" · {info['desc']}" if info else ""
            self.console.print(f"Model set to: [bold]{display}[/bold]{desc}")
            return

        # Show model selector
        self.console.print(Rule("Select model"))
        self.console.print(
            "[dim]Switch between models. Use /model <name> to set directly.[/dim]\n"
        )

        current = self.engine.config.model
        provider = self.engine.config.provider

        # Filter models by provider
        models_to_show = []
        for m in _MODEL_CATALOG:
            mid = m["id"].lower()
            if provider == "anthropic" and ("claude" in mid or "haiku" in mid):
                models_to_show.append(m)
            elif provider == "openai" and "gpt" in mid:
                models_to_show.append(m)
            elif provider == "gemini" and "gemini" in mid:
                models_to_show.append(m)
            elif provider == "deepseek" and "deepseek" in mid:
                models_to_show.append(m)
            elif provider == "ollama":
                pass  # Ollama models are custom

        # If no match (e.g. ollama), show all
        if not models_to_show:
            models_to_show = _MODEL_CATALOG

        for i, m in enumerate(models_to_show, 1):
            is_current = m["id"] == current or m["alias"] == current
            marker = "[bold green]→[/bold green]" if is_current else " "
            name_style = "bold" if is_current else ""
            ctx = get_context_window(m["id"])
            ctx_str = f"{ctx // 1000}K" if ctx < 1_000_000 else f"{ctx // 1_000_000}M"
            self.console.print(
                f"  {marker} {i}. [{name_style}]{m['name']:<28}[/{name_style}] "
                f"{m['desc']} · {ctx_str} context"
            )

        self.console.print(
            f"\n[dim]Current: [bold]{current}[/bold] · "
            f"Use /model <name or number> to switch[/dim]"
        )

        # Handle number input
        if models_to_show:
            self.console.print(
                "[dim]Aliases: " + ", ".join(m["alias"] for m in models_to_show) + "[/dim]"
            )

    # ---- /status ----

    def _cmd_status(self) -> None:
        self.console.print(Rule("Status"))

        cfg = self.engine.config
        model_info = _get_model_info(cfg.model)
        model_display = f"{model_info['name']} · {model_info['desc']}" if model_info else cfg.model

        # Auth info
        auth_method = "API Key"
        email = ""
        org = ""
        try:
            from clawpy.auth.oauth import load_tokens
            tokens = load_tokens()
            if tokens and tokens.access_token:
                auth_method = "Claude Subscription (OAuth)"
                email = tokens.email or tokens.account_uuid or ""
                org = tokens.organization_uuid or ""
        except Exception:
            pass
        if not email and cfg.api_key:
            auth_method = f"API Key ({cfg.provider})"

        elapsed = time.time() - self._start_time
        mins = int(elapsed) // 60

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="dim", width=20)
        table.add_column()

        table.add_row("Version", "ClawPy 0.1.0")
        table.add_row("Session ID", self._session_id)
        table.add_row("Working dir", cfg.work_dir)
        table.add_row("Login method", auth_method)
        if email:
            table.add_row("Email", email)
        if org:
            table.add_row("Organization", org)
        table.add_row("", "")
        table.add_row("Model", model_display)
        table.add_row("Provider", cfg.provider)
        table.add_row("Permission mode", cfg.permission_mode)
        table.add_row("Tools", str(len(self.engine.tools)))
        table.add_row("", "")
        table.add_row("Session duration", f"{mins}m {int(elapsed) % 60}s")
        table.add_row("Turns", str(self._turn_count))
        table.add_row("Total tokens", f"{self._total_input_tokens + self._total_output_tokens:,}")
        table.add_row("  Input", f"{self._total_input_tokens:,}")
        table.add_row("  Output", f"{self._total_output_tokens:,}")

        self.console.print(table)
        self.console.print()

    # ---- /context ----

    def _cmd_context(self) -> None:
        self.console.print(Rule("Context Usage"))

        model = self.engine.config.model
        ctx_window = get_context_window(model)
        msg_count = len(self.engine.messages)

        # Estimate tokens
        sys_tokens = len(self.engine.system_prompt) // 4
        msg_tokens = sum(
            sum(len(b.text) + len(b.thinking) + (50 if b.tool_call else 0) + len(b.tool_result.content if b.tool_result else "") for b in m.content)
            for m in self.engine.messages
        ) // 4
        tool_schema_tokens = len(self.engine.tools) * 100  # ~100 tokens per tool schema
        total_est = sys_tokens + msg_tokens + tool_schema_tokens

        pct = min(100, (total_est / ctx_window) * 100) if ctx_window > 0 else 0

        # Progress bar
        bar_width = 50
        filled = int(bar_width * pct / 100)
        bar_color = "green" if pct < 70 else ("yellow" if pct < 90 else "red")
        bar = f"[{bar_color}]{'█' * filled}[/{bar_color}][dim]{'░' * (bar_width - filled)}[/dim]"

        model_info = _get_model_info(model)
        model_name = model_info["name"] if model_info else model
        ctx_str = f"{ctx_window // 1000}K" if ctx_window < 1_000_000 else f"{ctx_window // 1_000_000}M"

        self.console.print(f"  {bar} {pct:.0f}%")
        self.console.print(f"  [dim]{model_name} · ~{total_est:,}/{ctx_window:,} tokens ({ctx_str} window)[/dim]\n")

        # Breakdown
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(width=3)
        table.add_column(width=25)
        table.add_column(justify="right")
        table.add_column(justify="right", style="dim")

        table.add_row("⛁", "System prompt", f"~{sys_tokens:,}", f"{sys_tokens * 100 // max(total_est, 1)}%")
        table.add_row("⛁", "Tool schemas", f"~{tool_schema_tokens:,}", f"{tool_schema_tokens * 100 // max(total_est, 1)}%")
        table.add_row("⛁", f"Messages ({msg_count})", f"~{msg_tokens:,}", f"{msg_tokens * 100 // max(total_est, 1)}%")

        self.console.print(table)
        self.console.print()

    # ---- /plan ----

    def _cmd_plan(self) -> None:
        from clawpy.tool.permission import PermissionMode
        current = self.engine.enforcer.mode
        if current == PermissionMode.PLAN:
            self.engine.enforcer.mode = PermissionMode.DEFAULT
            self.console.print("[green]Exited plan mode.[/green]")
        else:
            self.engine.enforcer.mode = PermissionMode.PLAN
            self.console.print("[yellow]Entered plan mode (read-only, no edits allowed).[/yellow]")

    # ---- /login ----

    def _cmd_login(self) -> None:
        import asyncio
        from clawpy.auth.oauth import OAuthFlow
        try:
            flow = OAuthFlow()
            tokens = asyncio.get_event_loop().run_until_complete(flow.login(manual=True))
            email = tokens.email or tokens.account_uuid or "unknown"
            self.console.print(f"[green]Logged in as: {email}[/green]")
        except Exception as e:
            self.console.print(f"[red]Login failed: {e}[/red]")

    # ---- /help ----

    def _cmd_help(self) -> None:
        commands = [
            ("/help", "Show this help"),
            ("/quit", "Exit the REPL"),
            ("/clear", "Clear conversation history"),
            ("/model [name]", "Select model or list available models"),
            ("/context", "Show context window usage with breakdown"),
            ("/status", "Show session info, auth, and usage stats"),
            ("/compact", "Compact conversation history"),
            ("/plan", "Toggle plan mode (read-only)"),
            ("/login", "Login with Claude subscription"),
            ("/logout", "Remove stored credentials"),
        ]
        self.console.print("[bold]Available commands:[/bold]\n")
        for cmd, desc in commands:
            self.console.print(f"  [cyan]{cmd:<20}[/cyan] {desc}")
        self.console.print()
