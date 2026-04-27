import sys
import types
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

dotenv = types.ModuleType("dotenv")
dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv)


class FakeFastMCP:
    last_instance = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.run_kwargs = None
        FakeFastMCP.last_instance = self

    def run(self, **kwargs):
        self.run_kwargs = kwargs


mcp_module = types.ModuleType("mcp")
mcp_server_module = types.ModuleType("mcp.server")
mcp_fastmcp_module = types.ModuleType("mcp.server.fastmcp")
mcp_fastmcp_module.FastMCP = FakeFastMCP
sys.modules["mcp"] = mcp_module
sys.modules["mcp.server"] = mcp_server_module
sys.modules["mcp.server.fastmcp"] = mcp_fastmcp_module

browser_use = sys.modules.get("browser_use") or types.ModuleType("browser_use")
browser_use.BrowserSession = object
browser_use.ChatOpenAI = object
sys.modules["browser_use"] = browser_use

playwright = sys.modules.get("playwright") or types.ModuleType("playwright")
async_api = sys.modules.get("playwright.async_api") or types.ModuleType(
    "playwright.async_api"
)
async_api.Browser = object
async_api.BrowserContext = object
async_api.Page = object
async_api.async_playwright = lambda: None
sys.modules["playwright"] = playwright
sys.modules["playwright.async_api"] = async_api

import server  # noqa: E402
from config import Settings  # noqa: E402


class FakeRuntime:
    def __init__(self, settings):
        self.settings = settings

    async def prewarm(self):
        pass

    async def close(self):
        pass


class ServerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.original_runtime = server.BrowserRuntime
        self.original_create_llm = server.create_llm
        self.original_register_tools = server.register_tools
        self.original_load_settings = server.load_settings
        self.original_create_server = server.create_server
        server.BrowserRuntime = FakeRuntime
        server.create_llm = lambda settings: object()
        server.register_tools = lambda mcp, runtime, llm: None

    def tearDown(self) -> None:
        server.BrowserRuntime = self.original_runtime
        server.create_llm = self.original_create_llm
        server.register_tools = self.original_register_tools
        server.load_settings = self.original_load_settings
        server.create_server = self.original_create_server

    def test_create_server_hard_codes_json_response_and_stateful_http(self) -> None:
        settings = Settings(
            openai_api_key="test-key",
            openai_base_url="https://example.test/v1",
            model_name="test-model",
            browser_mcp_host="127.0.0.1",
            browser_mcp_port=9000,
            browser_prewarm=True,
        )

        server.create_server(settings)
        mcp = FakeFastMCP.last_instance

        self.assertEqual(mcp.args, ("browser-use-node",))
        self.assertEqual(mcp.kwargs["host"], "127.0.0.1")
        self.assertEqual(mcp.kwargs["port"], 9000)
        self.assertIs(mcp.kwargs["json_response"], True)
        self.assertIs(mcp.kwargs["stateless_http"], False)
        self.assertIn("lifespan", mcp.kwargs)

    def test_run_server_uses_streamable_http_path(self) -> None:
        settings = Settings(
            openai_api_key="test-key",
            openai_base_url="https://example.test/v1",
            model_name="test-model",
            browser_mcp_host="127.0.0.1",
            browser_mcp_port=8000,
            browser_prewarm=False,
        )

        fake_mcp = FakeFastMCP("browser-use-node")
        server.load_settings = lambda: settings
        server.create_server = lambda loaded_settings: fake_mcp

        server.run_server()

        self.assertEqual(
            fake_mcp.run_kwargs,
            {"transport": "streamable-http", "path": "/mcp"},
        )


if __name__ == "__main__":
    unittest.main()
