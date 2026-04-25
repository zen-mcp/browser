from browser import BrowserRuntime
from .contracts import mcp_tool_guard


def register_interaction_tools(mcp, runtime: BrowserRuntime) -> None:
    @mcp.tool(
        description=(
            "Click the first element matching a CSS selector on the direct "
            "Playwright page and return the resulting URL."
        )
    )
    @mcp_tool_guard
    async def click(selector: str) -> dict:
        """Click an element by CSS selector."""
        page = await runtime.get_page()
        await page.locator(selector).first.click()
        return {"ok": True, "selector": selector, "url": page.url}

    @mcp.tool(
        description=(
            "Type text into the first input-like element matching a CSS "
            "selector. Returns character count, never the typed value."
        )
    )
    @mcp_tool_guard
    async def type_text(selector: str, text: str, clear_first: bool = True) -> dict:
        """Type text into an element without echoing the text back."""
        page = await runtime.get_page()
        locator = page.locator(selector).first
        if clear_first:
            await locator.fill("")
        await locator.type(text)
        return {"ok": True, "selector": selector, "chars": len(text)}

    @mcp.tool(
        description=(
            "Press a keyboard key such as Enter, Tab, or Escape on the current "
            "page and return the resulting URL."
        )
    )
    @mcp_tool_guard
    async def press_key(key: str) -> dict:
        """Press a keyboard key on the active page."""
        page = await runtime.get_page()
        await page.keyboard.press(key)
        return {"ok": True, "key": key, "url": page.url}
