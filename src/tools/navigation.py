from browser import BrowserRuntime
from .contracts import mcp_tool_guard


def register_navigation_tools(mcp, runtime: BrowserRuntime) -> None:
    @mcp.tool(
        description=(
            "Navigate the direct Playwright page to a URL and return the final "
            "URL and title after DOMContentLoaded."
        )
    )
    @mcp_tool_guard
    async def navigate(url: str) -> dict:
        """Navigate the active browser page to a URL."""
        page = await runtime.get_page()
        await page.goto(url, wait_until="domcontentloaded")
        return {"ok": True, "url": page.url, "title": await page.title()}

    @mcp.tool(
        description=(
            "Scroll the current page up or down by a pixel amount. Use after "
            "navigation or snapshot when content is below the fold."
        )
    )
    @mcp_tool_guard
    async def scroll(direction: str = "down", pixels: int = 800) -> dict:
        """Scroll the active page by mouse wheel."""
        page = await runtime.get_page()
        delta = abs(pixels)
        if direction.lower() == "up":
            delta = -delta
        await page.mouse.wheel(0, delta)
        return {"ok": True, "direction": direction.lower(), "pixels": abs(pixels)}

    @mcp.tool(
        description=(
            "Wait for a CSS selector, visible text, or fixed timeout. Use this "
            "between browser actions to stabilize page state."
        )
    )
    @mcp_tool_guard
    async def wait_for(
        seconds: float | None = None,
        selector: str | None = None,
        text: str | None = None,
        timeout_ms: int = 10000,
    ) -> dict:
        """Wait for page state by selector, text, or timeout."""
        page = await runtime.get_page()

        if selector:
            await page.wait_for_selector(selector, timeout=timeout_ms)
            return {"ok": True, "mode": "selector", "selector": selector}

        if text:
            await page.get_by_text(text).first.wait_for(timeout=timeout_ms)
            return {"ok": True, "mode": "text", "text": text}

        delay = seconds if seconds is not None else timeout_ms / 1000.0
        await page.wait_for_timeout(delay * 1000)
        return {"ok": True, "mode": "timeout", "seconds": delay}
