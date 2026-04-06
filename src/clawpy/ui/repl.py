"""Interactive REPL with prompt_toolkit input and rich streaming output.

Replaces the basic input() REPL with:
- prompt_toolkit async prompt with history
- rich Live display for streaming responses
- Slash command dispatch
- Permission prompts for non-read-only tools
"""

from __future__ import annotations

import asyncio
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from clawpy.engine.engine import Engine
from clawpy.provider.base import EventType, StreamEvent, Usage


class REPL:
    """Interactive REPL with streaming output."""

    def __init__(self, engine: Engine, console: Console | None = None) -> None:
        self.engine = engine
        self.console = console or Console()
        self.session: PromptSession[str] = PromptSession(
            history=InMemoryHistory(),
        )

    async def run(self) -> None:
        """Main REPL loop."""
        cfg = self.engine.config
        self.console.print(
            f"[bold]ClawPy v0.1.0[/bold] — {cfg.provider}:{cfg.model}"
        )
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
        tool_active = False

        def on_stream(event: StreamEvent) -> None:
            nonlocal text_buf, tool_active
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
                        tool_active = True
                case EventType.TOOL_END:
                    tool_active = False
                case EventType.ERROR:
                    if event.error:
                        self.console.print(f"[red]Error: {event.error}[/red]")

        try:
            result = await self.engine.run_turn(user_input, on_stream=on_stream)
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            return

        # Ensure newline after streaming output
        if text_buf and not text_buf.endswith("\n"):
            print()

        # Show usage
        if result.usage.input_tokens > 0 or result.usage.output_tokens > 0:
            self.console.print(
                f"[dim]tokens: {result.usage.input_tokens}↓ {result.usage.output_tokens}↑[/dim]"
            )

        print()  # Blank line after response

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
                self.console.print("[green]Conversation cleared.[/green]")

            case "/model":
                if args:
                    self.engine.config.model = args.strip()
                    self.console.print(f"Model set to: [bold]{args.strip()}[/bold]")
                else:
                    self.console.print(f"Current model: [bold]{self.engine.config.model}[/bold]")

            case "/context":
                self._show_context()

            case "/compact":
                self.console.print("[yellow]Manual compact not yet implemented.[/yellow]")

            case "/plan":
                from clawpy.tool.permission import PermissionMode

                current = self.engine.enforcer.mode
                if current == PermissionMode.PLAN:
                    self.engine.enforcer.mode = PermissionMode.DEFAULT
                    self.console.print("[green]Exited plan mode.[/green]")
                else:
                    self.engine.enforcer.mode = PermissionMode.PLAN
                    self.console.print(
                        "[yellow]Entered plan mode (read-only, no edits allowed).[/yellow]"
                    )

            case "/help":
                self._show_help()

            case _:
                self.console.print(f"Unknown command: {cmd}. Type /help for available commands.")

        return False

    def _show_context(self) -> None:
        """Show context window usage."""
        msg_count = len(self.engine.messages)
        # Rough estimate: ~4 chars per token
        total_chars = sum(
            sum(len(b.text) + len(b.thinking) for b in m.content)
            for m in self.engine.messages
        )
        est_tokens = total_chars // 4
        self.console.print(f"Messages: {msg_count}")
        self.console.print(f"Estimated context: ~{est_tokens:,} tokens")
        self.console.print(f"System prompt: ~{len(self.engine.system_prompt) // 4:,} tokens")

    def _show_help(self) -> None:
        """Show available slash commands."""
        commands = [
            ("/help", "Show this help"),
            ("/quit", "Exit the REPL"),
            ("/clear", "Clear conversation history"),
            ("/model [name]", "Show or set the model"),
            ("/context", "Show context window usage"),
            ("/compact", "Compact conversation history"),
            ("/plan", "Toggle plan mode (read-only)"),
        ]
        self.console.print("[bold]Available commands:[/bold]")
        for cmd, desc in commands:
            self.console.print(f"  [cyan]{cmd:<20}[/cyan] {desc}")
