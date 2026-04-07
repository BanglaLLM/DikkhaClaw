"""ClawPy interactive REPL.

Own visual identity — amber/orange theme, claw branding, unique layout.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from clawpy.engine.engine import Engine
from clawpy.engine.token_budget import get_context_window
from clawpy.provider.base import EventType, StreamEvent, Usage

# ---- Branding ----

_BRAND = "ClawPy"
_VERSION = "0.1.0"
_ACCENT = "dark_orange3"  # Our signature color (amber/orange)
_DIM = "dim"
_CLAW = "🐾"

# ---- Model catalog ----

_MODEL_CATALOG: list[dict[str, str]] = [
    # Anthropic
    {"alias": "opus", "id": "claude-opus-4-6", "label": "Opus 4.6", "tier": "anthropic", "note": "Deep reasoning, complex tasks"},
    {"alias": "opus[1m]", "id": "claude-opus-4-6[1m]", "label": "Opus 4.6 (1M)", "tier": "anthropic", "note": "Extended context window"},
    {"alias": "sonnet", "id": "claude-sonnet-4-6", "label": "Sonnet 4.6", "tier": "anthropic", "note": "Balanced speed and quality"},
    {"alias": "sonnet[1m]", "id": "claude-sonnet-4-6[1m]", "label": "Sonnet 4.6 (1M)", "tier": "anthropic", "note": "Extended context window"},
    {"alias": "haiku", "id": "claude-haiku-4-5-20251001", "label": "Haiku 4.5", "tier": "anthropic", "note": "Fast, lightweight"},
    # OpenAI
    {"alias": "gpt-4o", "id": "gpt-4o", "label": "GPT-4o", "tier": "openai", "note": "OpenAI flagship"},
    {"alias": "gpt-4o-mini", "id": "gpt-4o-mini", "label": "GPT-4o Mini", "tier": "openai", "note": "Fast and affordable"},
    # Google
    {"alias": "gemini-2.5-pro", "id": "gemini-2.5-pro", "label": "Gemini 2.5 Pro", "tier": "gemini", "note": "1M context, multimodal"},
    {"alias": "gemini-2.5-flash", "id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash", "tier": "gemini", "note": "Speed optimized"},
    # DeepSeek
    {"alias": "deepseek-chat", "id": "deepseek-chat", "label": "DeepSeek V3", "tier": "deepseek", "note": "Open-weight flagship"},
    {"alias": "deepseek-reasoner", "id": "deepseek-reasoner", "label": "DeepSeek R1", "tier": "deepseek", "note": "Chain-of-thought reasoning"},
]

_TIER_COLORS = {
    "anthropic": "medium_purple3",
    "openai": "green3",
    "gemini": "dodger_blue1",
    "deepseek": "cyan3",
    "ollama": "bright_white",
}


def _resolve_model(name: str) -> str:
    lower = name.lower().strip()
    for m in _MODEL_CATALOG:
        if lower in (m["alias"].lower(), m["id"].lower(), m["label"].lower()):
            return m["id"]
    return name


def _get_model_info(model_id: str) -> dict[str, str] | None:
    for m in _MODEL_CATALOG:
        if model_id == m["id"] or model_id == m["alias"]:
            return m
    return None


def _format_ctx(tokens: int) -> str:
    if tokens >= 1_000_000:
        return f"{tokens // 1_000_000}M"
    return f"{tokens // 1000}K"


class REPL:
    """ClawPy interactive REPL."""

    def __init__(self, engine: Engine, console: Console | None = None) -> None:
        self.engine = engine
        self.console = console or Console()
        self.session: PromptSession[str] = PromptSession(history=InMemoryHistory())
        self._session_id = uuid.uuid4().hex[:12]
        self._start_time = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._turn_count = 0

    async def run(self) -> None:
        cfg = self.engine.config
        info = _get_model_info(cfg.model)
        model_label = info["label"] if info else cfg.model

        # Banner
        self.console.print()
        self.console.print(f"  [{_ACCENT} bold]{_CLAW} {_BRAND}[/{_ACCENT} bold]  [dim]v{_VERSION}[/dim]")
        self.console.print(f"  [{_DIM}]{cfg.work_dir}[/{_DIM}]")
        self.console.print(f"  [{_DIM}]model: {model_label} via {cfg.provider}[/{_DIM}]")
        self.console.print()

        while True:
            try:
                user_input = await self.session.prompt_async(f"🐾 ")
            except (EOFError, KeyboardInterrupt):
                self.console.print(f"\n[{_ACCENT}]See you later![/{_ACCENT}]")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                if self._handle_slash(user_input):
                    break
                continue

            await self._run_turn(user_input)

    async def _run_turn(self, user_input: str) -> None:
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
                        self.console.print(f"  [{_ACCENT}]>> {event.tool_call.name}[/{_ACCENT}]")
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
                f"  [{_DIM}]{result.usage.input_tokens}in {result.usage.output_tokens}out[/{_DIM}]"
            )
        print()

        if result.error:
            self.console.print(f"[yellow]  {result.error}[/yellow]")

    def _handle_slash(self, raw: str) -> bool:
        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        match cmd:
            case "/quit" | "/exit" | "/q":
                self.console.print(f"[{_ACCENT}]See you later![/{_ACCENT}]")
                return True
            case "/clear":
                self.engine.clear()
                self._total_input_tokens = 0
                self._total_output_tokens = 0
                self._turn_count = 0
                self.console.print(f"[{_ACCENT}]Conversation cleared.[/{_ACCENT}]")
            case "/model":
                self._cmd_model(args)
            case "/context":
                self._cmd_context()
            case "/status":
                self._cmd_status()
            case "/usage":
                import asyncio
                asyncio.get_event_loop().run_until_complete(self._cmd_usage())
            case "/compact":
                self.console.print(f"[{_DIM}]Manual compact not yet implemented.[/{_DIM}]")
            case "/plan":
                self._cmd_plan()
            case "/login":
                self._cmd_login()
            case "/logout":
                from clawpy.auth.oauth import clear_tokens
                clear_tokens()
                self.console.print(f"[{_ACCENT}]Logged out.[/{_ACCENT}]")
            case "/help":
                self._cmd_help()
            case _:
                self.console.print(f"[{_DIM}]Unknown command: {cmd}. Try /help[/{_DIM}]")
        return False

    # ---- /model ----

    def _cmd_model(self, args: str) -> None:
        if args:
            resolved = _resolve_model(args)
            self.engine.config.model = resolved
            info = _get_model_info(resolved)
            label = info["label"] if info else resolved
            note = f"  [{_DIM}]{info['note']}[/{_DIM}]" if info else ""
            self.console.print(f"  [{_ACCENT}]model[/{_ACCENT}] {label}{note}")
            return

        # Show model picker grouped by provider
        self.console.print()
        self.console.print(
            Panel(
                self._render_model_list(),
                title=f"[{_ACCENT} bold]Models[/{_ACCENT} bold]",
                subtitle=f"[{_DIM}]/model <alias> to switch[/{_DIM}]",
                border_style=_ACCENT,
                padding=(1, 2),
            )
        )

    def _render_model_list(self) -> str:
        current = self.engine.config.model
        lines: list[str] = []

        # Group by tier
        tiers: dict[str, list[dict[str, str]]] = {}
        for m in _MODEL_CATALOG:
            tiers.setdefault(m["tier"], []).append(m)

        tier_names = {"anthropic": "Anthropic", "openai": "OpenAI", "gemini": "Google Gemini", "deepseek": "DeepSeek"}

        for tier, models in tiers.items():
            color = _TIER_COLORS.get(tier, "white")
            lines.append(f"[{color} bold]{tier_names.get(tier, tier)}[/{color} bold]")
            for m in models:
                is_current = m["id"] == current or m["alias"] == current
                marker = f"[{_ACCENT}]>[/{_ACCENT}]" if is_current else " "
                ctx = _format_ctx(get_context_window(m["id"]))
                bold = " bold" if is_current else ""
                lines.append(
                    f"  {marker} [{color}{bold}]{m['label']:<24}[/{color}{bold}] "
                    f"[{_DIM}]{m['note']:<30} {ctx}[/{_DIM}]"
                )
            lines.append("")

        # Aliases
        aliases = ", ".join(f"{m['alias']}" for m in _MODEL_CATALOG)
        lines.append(f"[{_DIM}]aliases: {aliases}[/{_DIM}]")

        return "\n".join(lines)

    # ---- /status ----

    def _cmd_status(self) -> None:
        # Gather info
        cfg = self.engine.config
        info = _get_model_info(cfg.model)
        model_label = info["label"] if info else cfg.model
        model_note = info["note"] if info else ""

        auth_line = "API Key"
        email_line = ""
        try:
            from clawpy.auth.oauth import load_tokens
            tokens = load_tokens()
            if tokens and tokens.access_token:
                auth_line = "Claude Subscription"
                email_line = tokens.email or tokens.account_uuid or ""
                if tokens.is_expired:
                    auth_line += " [red](expired)[/red]"
        except Exception:
            pass
        if not email_line and cfg.api_key:
            auth_line = f"{cfg.provider.title()} API Key"

        elapsed = time.time() - self._start_time
        total_tok = self._total_input_tokens + self._total_output_tokens

        rows = [
            ("session", self._session_id),
            ("uptime", f"{int(elapsed) // 60}m {int(elapsed) % 60}s"),
            ("", ""),
            ("auth", auth_line),
        ]
        if email_line:
            rows.append(("account", email_line))
        rows += [
            ("", ""),
            ("model", f"{model_label}  [{_DIM}]{model_note}[/{_DIM}]"),
            ("provider", cfg.provider),
            ("permissions", cfg.permission_mode),
            ("tools", f"{len(self.engine.tools)} loaded"),
            ("", ""),
            ("turns", str(self._turn_count)),
            ("tokens", f"{total_tok:,} total  [{_DIM}]{self._total_input_tokens:,}in {self._total_output_tokens:,}out[/{_DIM}]"),
        ]

        table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        table.add_column(style=_ACCENT, width=14, justify="right")
        table.add_column()
        for key, val in rows:
            table.add_row(key, val)

        self.console.print()
        self.console.print(Panel(table, title=f"[{_ACCENT} bold]{_CLAW} {_BRAND}[/{_ACCENT} bold]", border_style=_ACCENT, padding=(1, 2)))

    # ---- /context ----

    def _cmd_context(self) -> None:
        model = self.engine.config.model
        ctx_window = get_context_window(model)
        msg_count = len(self.engine.messages)
        info = _get_model_info(model)
        model_label = info["label"] if info else model

        # Estimate tokens
        sys_tokens = len(self.engine.system_prompt) // 4
        msg_tokens = sum(
            sum(
                len(b.text) + len(b.thinking)
                + (50 if b.tool_call else 0)
                + len(b.tool_result.content if b.tool_result else "")
                for b in m.content
            )
            for m in self.engine.messages
        ) // 4
        tool_tokens = len(self.engine.tools) * 100
        total = sys_tokens + msg_tokens + tool_tokens

        pct = min(100.0, (total / ctx_window) * 100) if ctx_window > 0 else 0.0

        # Build bar with our accent color
        bar_w = 40
        filled = int(bar_w * pct / 100)
        if pct < 50:
            fill_color = "green"
        elif pct < 80:
            fill_color = _ACCENT
        else:
            fill_color = "red"
        bar = f"[{fill_color}]{'━' * filled}[/{fill_color}][{_DIM}]{'╌' * (bar_w - filled)}[/{_DIM}]"

        lines: list[str] = []
        lines.append(f"{bar}  {pct:.0f}%")
        lines.append(f"[{_DIM}]{model_label} — ~{total:,} / {ctx_window:,} tokens ({_format_ctx(ctx_window)} window)[/{_DIM}]")
        lines.append("")
        lines.append(f"  [{_ACCENT}]system[/{_ACCENT}]    ~{sys_tokens:,} tokens")
        lines.append(f"  [{_ACCENT}]tools[/{_ACCENT}]     ~{tool_tokens:,} tokens  [{_DIM}]({len(self.engine.tools)} schemas)[/{_DIM}]")
        lines.append(f"  [{_ACCENT}]messages[/{_ACCENT}]  ~{msg_tokens:,} tokens  [{_DIM}]({msg_count} messages)[/{_DIM}]")

        self.console.print()
        self.console.print(Panel(
            "\n".join(lines),
            title=f"[{_ACCENT} bold]Context[/{_ACCENT} bold]",
            border_style=_ACCENT,
            padding=(1, 2),
        ))

    # ---- /usage ----

    async def _cmd_usage(self) -> None:
        from clawpy.auth.usage import fetch_usage

        self.console.print(f"  [{_DIM}]Fetching usage...[/{_DIM}]")
        info = await fetch_usage()

        if info.error:
            self.console.print(f"  [red]{info.error}[/red]")
            return

        if not info.windows:
            self.console.print(f"  [{_DIM}]No usage data available.[/{_DIM}]")
            return

        lines: list[str] = []
        for w in info.windows:
            pct = w.utilization
            bar_w = 30
            filled = int(bar_w * min(pct, 100) / 100)
            if pct < 50:
                color = "green"
            elif pct < 80:
                color = _ACCENT
            else:
                color = "red"
            bar = f"[{color}]{'━' * filled}[/{color}][{_DIM}]{'╌' * (bar_w - filled)}[/{_DIM}]"
            reset_text = f"resets in {w.resets_in}" if w.resets_at else ""
            lines.append(f"  [{_ACCENT}]{w.label:<22}[/{_ACCENT}] {bar} {pct:.0f}%  [{_DIM}]{reset_text}[/{_DIM}]")

        if info.extra and info.extra.enabled:
            lines.append("")
            ex = info.extra
            if ex.monthly_limit is not None and ex.used_credits is not None:
                lines.append(
                    f"  [{_ACCENT}]{'Extra usage':<22}[/{_ACCENT}] "
                    f"${ex.used_credits:.2f} / ${ex.monthly_limit:.2f}"
                )
            elif ex.utilization is not None:
                lines.append(f"  [{_ACCENT}]{'Extra usage':<22}[/{_ACCENT}] {ex.utilization:.0f}% used")

        self.console.print()
        self.console.print(Panel(
            "\n".join(lines),
            title=f"[{_ACCENT} bold]Usage[/{_ACCENT} bold]",
            border_style=_ACCENT,
            padding=(1, 2),
        ))

    # ---- /plan ----

    def _cmd_plan(self) -> None:
        from clawpy.tool.permission import PermissionMode
        current = self.engine.enforcer.mode
        if current == PermissionMode.PLAN:
            self.engine.enforcer.mode = PermissionMode.DEFAULT
            self.console.print(f"  [{_ACCENT}]Plan mode off[/{_ACCENT}] — tools unrestricted")
        else:
            self.engine.enforcer.mode = PermissionMode.PLAN
            self.console.print(f"  [{_ACCENT}]Plan mode on[/{_ACCENT}] — read-only, no edits")

    # ---- /login ----

    def _cmd_login(self) -> None:
        import asyncio
        from clawpy.auth.oauth import OAuthFlow
        try:
            flow = OAuthFlow()
            tokens = asyncio.get_event_loop().run_until_complete(flow.login(manual=True))
            email = tokens.email or tokens.account_uuid or "unknown"
            self.console.print(f"  [{_ACCENT}]Logged in as {email}[/{_ACCENT}]")
        except Exception as e:
            self.console.print(f"[red]Login failed: {e}[/red]")

    # ---- /help ----

    def _cmd_help(self) -> None:
        commands = [
            ("/model [name]", "Pick a model or list all available"),
            ("/usage", "Claude subscription usage & rate limits"),
            ("/status", "Session info, auth, usage stats"),
            ("/context", "Context window usage breakdown"),
            ("/plan", "Toggle read-only plan mode"),
            ("/clear", "Reset conversation"),
            ("/compact", "Compress conversation history"),
            ("/login", "Authenticate with Claude subscription"),
            ("/logout", "Clear stored credentials"),
            ("/help", "This help"),
            ("/quit", "Exit"),
        ]
        self.console.print()
        for cmd, desc in commands:
            self.console.print(f"  [{_ACCENT}]{cmd:<18}[/{_ACCENT}] {desc}")
        self.console.print()
