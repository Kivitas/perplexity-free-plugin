# Perplexity MCP Server — Free Search (No API Credits)

An MCP server that lets you search Perplexity AI **without using API credits**. It works by automating your browser — so you search through Perplexity's web UI instead of their paid API.

## Why this exists

Perplexity's API costs money per query. Their Pro subscription gives you unlimited searches on the website, but the API is billed separately.

This is a workaround: it automates a hidden Chrome window to search perplexity.ai, so you get the same results for free — using the subscription you already pay for.

**TL;DR:** If you have Perplexity Pro, you're already paying for unlimited searches. This lets any MCP client (Claude Code, Cursor, etc.) use those searches instead of burning API credits.

## How it works

```
Claude Code  →  MCP Server (this repo)  →  Playwright  →  Chrome  →  perplexity.ai
```

1. Chrome runs in the background with remote debugging enabled (port 9222)
2. You log into perplexity.ai once in that Chrome window
3. The MCP server connects to Chrome via CDP (Chrome DevTools Protocol)
4. When a search is requested, it types the query into perplexity.ai and reads the response
5. The result is returned to Claude Code — no API key needed

## Search modes

| Mode | Description | Use case |
|------|-------------|----------|
| `standard` | Default Perplexity search | Quick factual lookups |
| `pro` | Sonar Pro model | Better context, richer answers |
| `reasoning` | Chain-of-thought | Complex problems, step-by-step analysis |
| `deep` | Deep Research | Long-form research, multi-source synthesis |

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/elliotbakke/perplexity-mcp-free.git
cd perplexity-mcp-free

# macOS/Linux
./setup.sh

# Windows
setup.bat
```

### 2. Start Chrome with remote debugging

**macOS/Linux:**
```bash
./scripts/chrome-debug.sh
```

**Windows (PowerShell):**
```powershell
powershell -File scripts\chrome-debug.ps1
```

This opens a separate Chrome window with its own profile (won't affect your normal Chrome). **Log into perplexity.ai** in this window — this is the session the MCP server will use.

### 3. Add to Claude Code

```bash
# macOS/Linux
claude mcp add perplexity -- /path/to/perplexity-mcp-free/venv/bin/python /path/to/perplexity-mcp-free/mcp_server.py

# Windows
claude mcp add perplexity -- C:\path\to\perplexity-mcp-free\venv\Scripts\python.exe C:\path\to\perplexity-mcp-free\mcp_server.py
```

Replace the paths with wherever you cloned the repo.

### 4. (Optional) Install the /pplx slash command

The [`/pplx` skill](https://github.com/elliotbakke/claude-pplx-skill) gives you a convenient slash command with automatic mode selection:

```bash
mkdir -p ~/.claude/commands ~/.claude/agents && \
curl -sL https://raw.githubusercontent.com/elliotbakke/claude-pplx-skill/main/commands/pplx.md -o ~/.claude/commands/pplx.md && \
curl -sL https://raw.githubusercontent.com/elliotbakke/claude-pplx-skill/main/agents/pplx.md -o ~/.claude/agents/pplx.md
```

Then type `/pplx what is the weather in Oslo?` in Claude Code.

### 5. Restart Claude Code

The `perplexity_search` tool is now available.

## Keeping Chrome alive (optional)

Chrome can crash or close accidentally. The watchdog script checks every 5 minutes and restarts it if needed:

**Windows (PowerShell):**
```powershell
powershell -File scripts\chrome-debug-watchdog.ps1
```

**macOS/Linux:**
```bash
# Simple cron job alternative — add to crontab:
*/5 * * * * curl -s http://localhost:9222/json/version || ~/perplexity-mcp-free/scripts/chrome-debug.sh
```

## Files

| File | Purpose |
|------|---------|
| `mcp_server.py` | The MCP server — connects to Chrome and queries Perplexity |
| `requirements.txt` | Python dependencies (mcp, playwright) |
| `setup.sh` / `setup.bat` | One-command setup (venv + deps + Playwright) |
| `scripts/chrome-debug.sh` | Start Chrome with remote debugging (macOS/Linux) |
| `scripts/chrome-debug.ps1` | Start Chrome with remote debugging (Windows) |
| `scripts/chrome-debug-watchdog.ps1` | Auto-restart Chrome if it crashes (Windows) |

## Requirements

- Python 3.10+
- Google Chrome
- [Claude Code](https://claude.com/claude-code) (or any MCP client)
- Perplexity Pro subscription (for unlimited web searches)

**No Perplexity API key needed.**

## Troubleshooting

**"Cannot connect to Chrome"**
- Make sure Chrome is running with `--remote-debugging-port=9222`
- Check: open `http://localhost:9222/json/version` in your browser — you should see JSON

**"No results / empty response"**
- Log into perplexity.ai in the debug Chrome window
- Perplexity may have changed their UI — open an issue if selectors are broken

**"Mode selection failed"**
- Mode switching depends on Perplexity's UI elements which can change
- Falls back to standard mode automatically

## License

MIT
