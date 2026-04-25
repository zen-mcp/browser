from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browser import BrowserRuntime
from .contracts import mcp_tool_guard


def register_observation_tools(mcp, runtime: BrowserRuntime) -> None:
    @mcp.tool(
        description=(
            "Get the current page URL, title, and visible body text. Use this "
            "before choosing selectors or summarizing browser state."
        )
    )
    @mcp_tool_guard
    async def get_page_snapshot(max_text_chars: int = 4000) -> dict:
        """Return a bounded text snapshot of the current browser page."""
        page = await runtime.get_page()
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except PlaywrightTimeoutError:
            pass

        title = await page.title()
        text = await page.inner_text("body")
        original_text_length = len(text)
        if original_text_length > max_text_chars:
            text = text[:max_text_chars]

        return {
            "ok": True,
            "url": page.url,
            "title": title,
            "text": text,
            "text_length": original_text_length,
            "text_truncated": original_text_length > max_text_chars,
        }
