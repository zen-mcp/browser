from mcp.server.fastmcp import FastMCP

from browser import BrowserRuntime
from config import load_settings
from llm import create_llm
from tools import register_tools

def create_server() -> FastMCP:
    settings = load_settings()
    runtime = BrowserRuntime(settings)
    llm = create_llm(settings)

    mcp = FastMCP("browser-use-node", host="0.0.0.0")
    register_tools(mcp, runtime, llm)
    return mcp


def run_server() -> None:
    mcp = create_server()
    mcp.run(transport="sse")

