#!/usr/bin/env python3
"""Bootstrap launcher for the Perplexity MCP server.

On first run it creates a virtualenv in the plugin data dir, installs
requirements and Playwright's Chromium, then runs mcp_server.py with the
venv's interpreter. Stdout is reserved for the MCP stdio protocol, so all
installer output goes to stderr.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("PPLX_PLUGIN_DATA") or HERE.parent / ".data")
VENV = DATA / "venv"
STAMP = VENV / ".deps-installed"
REQS = HERE / "requirements.txt"


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=sys.stderr, stderr=sys.stderr)


def ensure_env():
    if STAMP.exists() and STAMP.stat().st_mtime >= REQS.stat().st_mtime:
        return
    DATA.mkdir(parents=True, exist_ok=True)
    if not venv_python().exists():
        print("[perplexity] creating virtualenv...", file=sys.stderr)
        run([sys.executable, "-m", "venv", str(VENV)])
    py = str(venv_python())
    print("[perplexity] installing dependencies...", file=sys.stderr)
    run([py, "-m", "pip", "install", "-q", "-r", str(REQS)])
    # Server attaches to the user's Chrome over CDP, so Playwright's own
    # browser download is not required.
    STAMP.write_text("ok")


def main():
    ensure_env()
    py = str(venv_python())
    server = str(HERE / "mcp_server.py")
    if os.name == "nt":
        sys.exit(subprocess.call([py, server]))
    os.execv(py, [py, server])


if __name__ == "__main__":
    main()
