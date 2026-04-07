# ClawPy

Multi-model CLI coding agent written in typed Python. A ground-up rewrite inspired by [Claude Code](https://claude.ai/code), with support for Anthropic, OpenAI, Gemini, Ollama, and DeepSeek.

ClawPy gives you an interactive terminal agent that can read your codebase, search files, edit code, run commands, and fetch web content — all driven by the LLM of your choice.

## Features

- **Multi-model** — switch between Claude, GPT-4o, Gemini, Ollama, DeepSeek with a flag or env var
- **Claude subscription login** — use your Claude Pro/Max/Team subscription directly (OAuth PKCE)
- **9 built-in tools** — Bash, Read, Write, Edit, Grep, Glob, ListFiles, WebFetch, Agent
- **Agentic loop** — model calls tools autonomously, results feed back, loops until done
- **Permission system** — 4 modes (default, accept_edits, bypass, plan) with allow/deny rules
- **Read-before-write** — files must be read before editing, with mtime staleness detection
- **Token budget** — auto-stops at 90% context window, detects diminishing returns
- **Auto-compact** — summarizes old messages when context gets full
- **CLAWPY.md memory** — project-level instructions discovered from CWD to root
- **Streaming** — real-time response streaming in the terminal
- **Fully typed** — `mypy --strict` passes on all source files

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/AIScienceStudio/clawpy.git
cd clawpy
uv venv
uv pip install -e .
```

For development (tests, linting, type checking):

```bash
uv pip install -e ".[dev]"
```

## Authentication

### Option 1: Claude subscription (recommended)

Use your existing Claude Pro, Max, Team, or Enterprise subscription:

```bash
uv run clawpy login
```

This opens your browser to authenticate with your Claude account. Tokens are stored at `~/.clawpy/credentials.json`.

```bash
# Check login status
uv run clawpy status

# Logout
uv run clawpy logout
```

### Option 2: API keys

Set the API key for your provider:

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-proj-...

# Gemini
export GEMINI_API_KEY=AIza...

# DeepSeek
export DEEPSEEK_API_KEY=sk-...

# Ollama (no key needed, just have Ollama running)
```

## Usage

### Interactive REPL (default)

```bash
uv run clawpy
```

This starts an interactive session. Type prompts, get streaming responses, watch the agent use tools.

```
ClawPy v0.1.0 — anthropic:claude-sonnet-4-20250514
Working directory: /home/user/myproject
Type /help for commands, /quit to exit.

> Find all Python files that import asyncio and explain what they do
```

### Non-interactive (single prompt)

```bash
uv run clawpy run "List all TODO comments in this project"
```

Or pipe from stdin:

```bash
echo "What does the main function do?" | uv run clawpy run
```

### Switching models

```bash
# Via CLI flag
uv run clawpy -p openai -m gpt-4o
uv run clawpy -p gemini -m gemini-2.5-pro
uv run clawpy -p ollama -m llama3.1
uv run clawpy -p deepseek -m deepseek-chat

# Via environment
export CLAWPY_PROVIDER=gemini
export CLAWPY_MODEL=gemini-2.5-pro
uv run clawpy

# Switch during a session
> /model gpt-4o
```

### Permission modes

```bash
# Default — asks before non-read-only tools
uv run clawpy

# Auto-approve file edits
uv run clawpy --permission-mode accept_edits

# Approve everything (yolo mode)
uv run clawpy --permission-mode bypass

# Read-only (plan mode) — no edits allowed
uv run clawpy --permission-mode plan
```

### Slash commands

| Command | Description |
|---------|-------------|
| `/help` | List available commands |
| `/quit` | Exit the REPL |
| `/clear` | Clear conversation history |
| `/model [name]` | Show or switch model |
| `/context` | Show token usage estimate |
| `/plan` | Toggle plan mode (read-only) |
| `/compact` | Compact conversation history |

## Configuration

### Settings files

ClawPy loads settings in priority order (later overrides earlier):

1. **Defaults** — hardcoded sensible defaults
2. **Global** — `~/.clawpy/settings.json`
3. **Project** — `<project>/.clawpy/settings.json`
4. **Environment variables** — `CLAWPY_PROVIDER`, `CLAWPY_MODEL`, etc.
5. **CLI flags** — `--provider`, `--model`, `--permission-mode`

Example `settings.json`:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 16384,
  "permission_mode": "accept_edits",
  "allow_tools": ["Bash"],
  "deny_tools": ["WebFetch"]
}
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `CLAWPY_PROVIDER` | Provider name (anthropic, openai, gemini, ollama, deepseek) |
| `CLAWPY_MODEL` | Model ID |
| `CLAWPY_MAX_TOKENS` | Max output tokens |
| `CLAWPY_PERMISSION_MODE` | Permission mode |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `OLLAMA_BASE_URL` | Ollama endpoint (default: http://localhost:11434/v1) |

### Project memory (CLAWPY.md)

Create a `CLAWPY.md` file in your project root to give the agent persistent context:

```markdown
# Project: MyApp

- This is a Django project using PostgreSQL
- Always run tests with `pytest -x`
- Never modify files in `vendor/`
```

ClawPy discovers memory files by walking from the current directory to the filesystem root, plus `~/.clawpy/CLAWPY.md` for global instructions.

## Tools

| Tool | Description | Permission |
|------|-------------|------------|
| **Bash** | Execute shell commands | Dynamic (read-only for safe commands) |
| **Read** | Read files with line numbers | Read-only |
| **Write** | Write/create files | Workspace write |
| **Edit** | Search and replace in files | Workspace write |
| **Grep** | Search file contents (ripgrep) | Read-only |
| **Glob** | Find files by pattern | Read-only |
| **ListFiles** | List directory contents | Read-only |
| **WebFetch** | Fetch URL content | Shell unsafe |
| **Agent** | Spawn a sub-agent for complex tasks | Shell unsafe |

## Hooks

Run custom shell commands before/after tool execution. Add to `settings.json`:

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "tool": "Edit",
        "command": "echo 'Editing file'"
      }
    ],
    "post_tool_use": [
      {
        "tool": "Edit",
        "if": "file_path:*.py",
        "command": "ruff check --fix $CLAWPY_FILE_PATH"
      }
    ]
  }
}
```

## Architecture

```
User input → CLI → Engine.run_turn()
                      ↓
              Build Request (system prompt + messages + tools)
                      ↓
              Provider.stream() → SSE → StreamEvents
                      ↓
              Consume stream → assemble assistant Message
                      ↓
              Extract ToolCalls → permission check → execute
                      ↓
              Append results → check token budget → loop or return
```

See [spec/](spec/) for detailed architecture documentation.

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Type checking
uv run mypy --strict src/

# Lint
uv run ruff check src/

# Run benchmarks (requires API key)
GEMINI_API_KEY=... uv run python benchmarks/run_benchmark.py
```

## Providers

| Provider | Status | Models |
|----------|--------|--------|
| Anthropic | Stable | claude-opus-4, claude-sonnet-4, claude-haiku-4 |
| OpenAI | Stable | gpt-4o, gpt-4o-mini, o1, o3-mini |
| Gemini | Stable (2.5) | gemini-2.5-pro, gemini-2.5-flash |
| Ollama | Stable | Any local model |
| DeepSeek | Stable | deepseek-chat, deepseek-coder, deepseek-reasoner |

All OpenAI-compatible providers (Gemini, Ollama, DeepSeek) use the same conversion layer. Adding a new provider is ~30 lines of code.

## License

MIT
