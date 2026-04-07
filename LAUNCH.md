# Launch Posts — Copy-Paste Ready

## X (Twitter) Thread

### Tweet 1 (Hook)
```
I built the first Python-native AI coding agent.

It works with Claude, GPT-4o, Gemini, Ollama, and DeepSeek.

3 dependencies. No SDK bloat. mypy --strict.

One tool, any brain.

Thread
```

### Tweet 2 (Demo)
```
Here's what it looks like:

> "Find the bug in auth.py and fix it"

The agent reads the file, greps for the issue, edits the code, and shows you the diff. All streaming in real-time.

[ATTACH: demo GIF or 30s screen recording]
```

### Tweet 3 (Multi-model)
```
Switch your AI's brain with one flag:

clawpy -p openai -m gpt-4o
clawpy -p gemini -m gemini-2.5-pro
clawpy -p ollama -m llama3.1
clawpy -p deepseek -m deepseek-chat

Or switch mid-conversation: /model gemini-2.5-pro

No config files. No restart. Just go.
```

### Tweet 4 (Claude subscription)
```
Got a Claude Pro or Max subscription?

clawpy login

That's it. OAuth PKCE flow, same as Claude Code. Uses your existing plan.

No API key needed. No extra billing.
```

### Tweet 5 (Memory)
```
It remembers things across sessions.

/memory add "Always use pytest, never unittest"
/dream  ← LLM consolidates everything it learned

Auto-dream kicks in after long sessions. Your agent gets smarter over time.
```

### Tweet 6 (Background agents)
```
Spawn parallel agents that work while you think:

"Explore the codebase AND fix the tests"

[bg a0001] started: "Explore structure"
[bg a0002] started: "Fix tests"

/tasks to check progress
/kill a0002 if it goes rogue

Real async, not fake.
```

### Tweet 7 (CTA)
```
Pure Python. 3 deps. 50+ files. 57 tests. mypy --strict.

Works with Claude, GPT-4o, Gemini, Ollama, DeepSeek.

Plugins, MCP, memory, background agents, cost tracking.

https://github.com/AIScienceStudio/clawpy

If it's useful, a star helps.
```

---

## Hacker News

### Title
```
Show HN: ClawPy – Python AI coding agent that works with any LLM
```

### Body
```
Hi HN,

I built ClawPy — an AI coding agent in typed Python that works with Claude, GPT-4o, Gemini, Ollama, and DeepSeek. Switch providers with one flag. No vendor lock-in.

It has 3 runtime dependencies (httpx, prompt-toolkit, rich), passes mypy --strict, and supports Claude subscription login (OAuth PKCE — use your existing Pro/Max plan without an API key).

Features: 9 tools (Bash, Read, Write, Edit, Grep, Glob, ListFiles, WebFetch, Agent), background agents, plugin system, MCP support, memory with LLM-powered consolidation ("dream"), smart context management (microcompact at 70%, auto-compact at 90%), cost tracking, and 22 slash commands.

The architecture is simple: a Provider Protocol (AsyncIterator streaming), a Tool Protocol (with permission levels), and an agentic loop that streams → executes tools → feeds results back → loops. Adding a new provider is ~30 lines (Gemini/Ollama/DeepSeek all inherit from the OpenAI provider).

GitHub: https://github.com/AIScienceStudio/clawpy
```

---

## Reddit

### r/Python
**Title:** `I built an AI coding agent in pure typed Python (mypy --strict, 3 deps, 5 LLM providers)`

**Body:**
```
Built ClawPy — an interactive terminal agent that reads your codebase, searches files, edits code, and runs commands, driven by the LLM of your choice.

What makes it different:
- Pure Python 3.12+, fully typed (mypy --strict passes on all 50+ files)
- Only 3 runtime deps: httpx, prompt-toolkit, rich
- Works with Claude, GPT-4o, Gemini, Ollama (local!), DeepSeek
- Switch models with one flag or mid-conversation
- Plugin system, MCP support, background agents, memory with "dream" consolidation

The Provider Protocol uses AsyncIterator[StreamEvent] for streaming — no SDK dependencies, just httpx talking to APIs directly.

Adding a new provider is ~30 lines (inherit from OpenAIProvider, change the base URL).

Would love feedback from the Python community.

https://github.com/AIScienceStudio/clawpy
```

### r/LocalLLaMA
**Title:** `ClawPy: Run AI coding agents locally with Ollama — switch to cloud models with one flag`

**Body:**
```
Built an open-source coding agent in Python that works with local models out of the box:

clawpy -p ollama -m llama3.1

It reads files, searches code, edits, runs commands — full agentic loop. And when you need more power:

clawpy -p openai -m gpt-4o
clawpy -p gemini -m gemini-2.5-pro

Same interface, same tools, just a different brain.

All conversation history, memory, and plugins carry over between providers. No config files to change.

3 Python deps. No Electron. No cloud-only lock-in.

https://github.com/AIScienceStudio/clawpy
```

### r/MachineLearning
**Title:** `[P] Open-source multi-model AI coding agent framework in Python`

**Body:**
```
Sharing ClawPy — a Python framework for building AI coding agents that work with any LLM provider.

Architecture:
- Provider Protocol with AsyncIterator streaming (Anthropic, OpenAI, Gemini, Ollama, DeepSeek)
- Tool Protocol with permission levels and concurrent execution (read-only tools run in parallel)
- Agentic loop: stream → extract tool calls → execute → feed results → loop
- Token budget management (90% threshold + diminishing returns detection)
- Three-layer context compression: microcompact (70%), auto-compact (90%), session memory

Also includes: background agents (asyncio.Task), MCP client (JSON-RPC 2.0), plugin system, memory consolidation ("dream" — LLM-powered periodic memory organization).

Fully typed (mypy --strict), 57 tests, 3 runtime deps.

https://github.com/AIScienceStudio/clawpy
```

---

## Tips for maximum impact

1. **Record a 30-second terminal demo** before posting anywhere. Use `asciinema` or screen recording. Show: prompt → agent reads file → edits → shows diff. This is the single highest-impact thing.

2. **Post the X thread first** (morning US time, Tue-Thu). Reply to AI/dev accounts who discuss coding agents.

3. **Submit to HN 30 minutes after the X thread** goes live. If it hits the front page, that's 5K-20K stars.

4. **Reddit posts 1 hour after HN.** Different angles for each subreddit.

5. **Don't post all subreddits the same day.** Space them out: r/Python day 1, r/LocalLLaMA day 2, r/MachineLearning day 3.

6. **Reply to every early comment.** Engagement in the first hour determines visibility on all platforms.
