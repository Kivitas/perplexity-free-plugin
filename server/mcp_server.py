#!/usr/bin/env python3
"""
Perplexity MCP Server (stdio) — Free search via browser automation.
Connects to Chrome via CDP and queries perplexity.ai directly.
No API key needed — uses your existing Perplexity Pro subscription.
"""
import asyncio
import os
import subprocess
import urllib.request
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

mcp = FastMCP("perplexity")


def _cdp_alive() -> bool:
    try:
        urllib.request.urlopen(CDP_URL + "/json/version", timeout=2).close()
        return True
    except Exception:
        return False


async def ensure_chrome() -> None:
    """Start the hidden debug Chrome if nothing is listening on the CDP port."""
    if _cdp_alive():
        return
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(SCRIPTS / "chrome-debug.ps1")]
    else:
        cmd = ["bash", str(SCRIPTS / "chrome-debug.sh")]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        await asyncio.sleep(1)
        if _cdp_alive():
            return


async def query_perplexity(prompt: str, mode: str = "standard", timeout: int = 120) -> str:
    """Query Perplexity via Chrome CDP with mode selection."""
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto("https://www.perplexity.ai/", timeout=60000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Select mode if not standard
        if mode != "standard":
            try:
                mode_selector = await page.query_selector(
                    '[data-testid="model-selector"], [aria-label*="model"], '
                    'button:has-text("Pro"), button:has-text("Sonar")'
                )
                if mode_selector:
                    await mode_selector.click()
                    await asyncio.sleep(0.5)

                    mode_map = {
                        "pro": ["Pro", "Sonar Pro"],
                        "reasoning": ["Reasoning", "Sonar Reasoning", "Reasoning Pro"],
                        "deep": ["Deep Research", "Research"],
                    }

                    for text in mode_map.get(mode, []):
                        option = await page.query_selector(
                            f'button:has-text("{text}"), '
                            f'[role="option"]:has-text("{text}"), '
                            f'li:has-text("{text}")'
                        )
                        if option:
                            await option.click()
                            await asyncio.sleep(0.5)
                            break
            except Exception as e:
                print(f"Mode selection failed: {e}, continuing with default")

        # Find input and type query
        input_box = await page.wait_for_selector(
            "[role='textbox'][contenteditable='true']", timeout=10000
        )
        await input_box.click()
        await page.keyboard.type(prompt)
        await page.keyboard.press("Enter")

        # Wait for response — longer timeout for deep research
        actual_timeout = timeout * 2 if mode == "deep" else timeout
        await page.wait_for_selector('[class*="prose"]', timeout=actual_timeout * 1000)

        # Wait for streaming to complete (text stabilizes)
        last_text = ""
        stable_count = 0
        required_stable = 5 if mode == "deep" else 3

        for _ in range(actual_timeout * 2):
            await asyncio.sleep(0.5)
            elements = await page.query_selector_all('[class*="prose"]')
            if elements:
                longest = ""
                for el in elements:
                    t = await el.inner_text()
                    if len(t) > len(longest):
                        longest = t
                current_text = longest
                if current_text == last_text and current_text:
                    stable_count += 1
                    if stable_count >= required_stable:
                        break
                else:
                    stable_count = 0
                    last_text = current_text

        # Navigate away to reset for next query
        await page.goto("about:blank")
        return last_text
    finally:
        await playwright.stop()


@mcp.tool()
async def perplexity_search(query: str, mode: str = "standard") -> str:
    """Search the web using Perplexity AI. Returns up-to-date information with sources.

    Args:
        query: The search query or question to ask Perplexity
        mode: Search mode — standard (fast), pro (better), reasoning (step-by-step), deep (thorough research)
    """
    if mode not in ("standard", "pro", "reasoning", "deep"):
        mode = "standard"
    try:
        await ensure_chrome()
        return await query_perplexity(query, mode)
    except Exception as e:
        return f"Error: {e}. Make sure Chrome is running with --remote-debugging-port=9222"


if __name__ == "__main__":
    mcp.run(transport="stdio")
