from browser_use import Agent, BrowserSession, Controller

from browser import BrowserRuntime
from .contracts import error_payload


def register_agent_tools(mcp, runtime: BrowserRuntime, llm) -> None:
    controller = Controller()

    def controller_error_text(error: BaseException) -> str:
        return f"Error ({type(error).__name__}): {error}"

    @controller.action(
        "Capture a PNG screenshot artifact of the current page. "
        "Use this when the user asks for a screenshot file or screenshot artifact."
    )
    async def take_screenshot(
        browser_session: BrowserSession,
        file_name_prefix: str = "screenshot",
        full_page: bool = False,
    ) -> str:
        try:
            file_path = runtime.build_artifact_path(file_name_prefix, "png")
            await browser_session.take_screenshot(
                path=str(file_path), full_page=full_page
            )
            return f"Screenshot saved as {file_path.name} at {file_path}"
        except Exception as error:
            return controller_error_text(error)

    async def run_browser_agent(instruction: str, url: str) -> str:
        composed_task = f"Start from {url}. Then: {instruction}"
        agent = Agent(
            task=composed_task,
            llm=llm,
            browser=runtime.get_agent_browser(),
            controller=controller,
        )
        result = await agent.run()
        return str(result.final_result())

    @mcp.tool(
        description=(
            "Structured browser-use agent tool for complex browser tasks. "
            "Returns ok, result, instruction, and start_url fields."
        )
    )
    async def browse_and_act(
        instruction: str, url: str = "https://google.com"
    ) -> dict:
        """Run a browser-use agent task with structured MCP output."""
        try:
            result = await run_browser_agent(instruction, url)
            return {
                "ok": True,
                "result": result,
                "instruction": instruction,
                "start_url": url,
            }
        except Exception as error:
            return error_payload(error)
