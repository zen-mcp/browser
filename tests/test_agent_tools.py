import sys
import types
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class FakeAgentResult:
    def final_result(self):
        return "done"


class FakeAgent:
    raise_error = False
    last_task = None

    def __init__(self, task, llm, browser, controller):
        FakeAgent.last_task = task

    async def run(self):
        if FakeAgent.raise_error:
            raise RuntimeError("agent failed")
        return FakeAgentResult()


class FakeController:
    def action(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


browser_use = sys.modules.get("browser_use") or types.ModuleType("browser_use")
browser_use.Agent = FakeAgent
browser_use.BrowserSession = object
browser_use.Controller = FakeController
sys.modules["browser_use"] = browser_use

dotenv = types.ModuleType("dotenv")
dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv)

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

from tools.agent import register_agent_tools  # noqa: E402


class ToolRegistry:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self, *args, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeRuntime:
    def get_agent_browser(self):
        return object()

    def build_artifact_path(self, prefix: str, extension: str) -> Path:
        return Path(f"/tmp/{prefix}.{extension}")


class AgentToolsTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        FakeAgent.raise_error = False
        FakeAgent.last_task = None

    async def test_browse_and_act_is_structured_tool(self) -> None:
        registry = ToolRegistry()
        register_agent_tools(registry, FakeRuntime(), object())

        self.assertEqual(set(registry.tools), {"browse_and_act"})

        result = await registry.tools["browse_and_act"](
            "collect the title",
            url="https://example.test",
        )

        self.assertEqual(
            result,
            {
                "ok": True,
                "result": "done",
                "instruction": "collect the title",
                "start_url": "https://example.test",
            },
        )
        self.assertEqual(
            FakeAgent.last_task,
            "Start from https://example.test. Then: collect the title",
        )

    async def test_browse_and_act_returns_structured_errors(self) -> None:
        registry = ToolRegistry()
        register_agent_tools(registry, FakeRuntime(), object())
        FakeAgent.raise_error = True

        result = await registry.tools["browse_and_act"]("fail")

        self.assertEqual(
            result,
            {
                "ok": False,
                "error": "agent failed",
                "error_type": "RuntimeError",
            },
        )


if __name__ == "__main__":
    unittest.main()
