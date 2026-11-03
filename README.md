# perplexity-free (Claude Code plugin)

Free Perplexity search through your logged-in Perplexity web session. Packaged as a Claude Code plugin by Kivitas. The server is based on [perplexity-mcp-free](https://github.com/elliotbakke/perplexity-mcp-free) by Elliot Bakke (MIT, see `server/LICENSE`, original docs in `UPSTREAM-README.md`).

Provides:
- MCP tool `perplexity_search` (modes: standard, pro, reasoning, deep)
- Skill `/perplexity-free:pplx [mode] <question>`

## Install
```bash
claude plugin marketplace add /path/to/perplexity-free
claude plugin install perplexity-free@perplexity-free-local
```
Restart Claude Code. Needs `python` (3.10+) on PATH and Google Chrome. First start installs dependencies into the plugin data dir (about a minute).

## One-time login
```powershell
powershell -File scripts\chrome-debug.ps1 -Show     # Windows
./scripts/chrome-debug.sh                           # macOS/Linux
```
Log into perplexity.ai in that window, then close it. After that the server starts a hidden debug Chrome on demand.

## License
MIT, see `LICENSE`. The Claude Code plugin packaging is by Kivitas; the bundled server is derived from perplexity-mcp-free by Elliot Bakke (MIT, `server/LICENSE`).
