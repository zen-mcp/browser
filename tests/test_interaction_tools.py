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

browser_use = sys.modules.get("browser_use") or types.ModuleType("browser_use")
browser_use.BrowserSession = object
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

from tools.interaction import register_interaction_tools  # noqa: E402


class ToolRegistry:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self, *args, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeLocator:
    def __init__(self) -> None:
        self.first = self
        self.calls = []

    async def fill(self, text):
        self.calls.append(("fill", text))

    async def type(self, text):
        self.calls.append(("type", text))


class FakePage:
    url = "https://example.test"

    def __init__(self, locator: FakeLocator) -> None:
        self.fake_locator = locator

    def locator(self, selector: str):
        return self.fake_locator


class FakeRuntime:
    def __init__(self, page: FakePage) -> None:
        self.page = page

    async def get_page(self):
        return self.page


class InteractionToolsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_type_text_uses_fill_by_default(self) -> None:
        locator = FakeLocator()
        registry = ToolRegistry()
        register_interaction_tools(registry, FakeRuntime(FakePage(locator)))

        result = await registry.tools["type_text"]("#email", "secret")

        self.assertEqual(locator.calls, [("fill", "secret")])
        self.assertEqual(
            result,
            {
                "ok": True,
                "selector": "#email",
                "chars": 6,
                "mode": "fill",
                "slow": False,
            },
        )

    async def test_type_text_uses_type_when_slow(self) -> None:
        locator = FakeLocator()
        registry = ToolRegistry()
        register_interaction_tools(registry, FakeRuntime(FakePage(locator)))

        result = await registry.tools["type_text"]("#email", "secret", slow=True)

        self.assertEqual(locator.calls, [("fill", ""), ("type", "secret")])
        self.assertEqual(result["mode"], "type")
        self.assertTrue(result["slow"])

    async def test_type_text_preserves_append_behavior_without_clear_first(self) -> None:
        locator = FakeLocator()
        registry = ToolRegistry()
        register_interaction_tools(registry, FakeRuntime(FakePage(locator)))

        result = await registry.tools["type_text"](
            "#email",
            "suffix",
            clear_first=False,
        )

        self.assertEqual(locator.calls, [("type", "suffix")])
        self.assertEqual(result["mode"], "type")


if __name__ == "__main__":
    unittest.main()
