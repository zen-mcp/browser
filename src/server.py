from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from browser import BrowserRuntime
from config import Settings, load_settings
from llm import create_llm
from tools import register_tools

def create_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or load_settings()
    runtime = BrowserRuntime(settings)
    llm = create_llm(settings)

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> AsyncIterator[dict]:
        if settings.browser_prewarm:
            await runtime.prewarm()

        try:
            yield {"runtime": runtime}
        finally:
            await runtime.close()

    mcp = FastMCP(
        "browser-use-node",
        host=settings.browser_mcp_host,
        port=settings.browser_mcp_port,
        json_response=True,
        stateless_http=False,
        lifespan=lifespan,
    )
    register_tools(mcp, runtime, llm)
    return mcp


def run_server() -> None:
    settings = load_settings()
    mcp = create_server(settings)
    mcp.run(transport="streamable-http", path="/mcp")
