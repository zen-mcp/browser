import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

dotenv = types.ModuleType("dotenv")
dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv)

starlette = sys.modules.get("starlette") or types.ModuleType("starlette")
responses = sys.modules.get("starlette.responses") or types.ModuleType(
    "starlette.responses"
)
responses.FileResponse = object
responses.PlainTextResponse = object
sys.modules["starlette"] = starlette
sys.modules["starlette.responses"] = responses

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

from tools.artifacts import register_artifact_tools  # noqa: E402


class ToolRegistry:
    def __init__(self) -> None:
        self.tools = {}
        self.routes = {}

    def tool(self, *args, **kwargs):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def custom_route(self, path, methods):
        def decorator(func):
            self.routes[path] = (methods, func)
            return func

        return decorator


class FakeLocator:
    def __init__(self) -> None:
        self.first = self
        self.screenshot_kwargs = None

    async def screenshot(self, **kwargs):
        self.screenshot_kwargs = kwargs
        Path(kwargs["path"]).write_bytes(b"image")


class FakePage:
    url = "https://example.test"

    def __init__(self) -> None:
        self.screenshot_kwargs = None
        self.fake_locator = FakeLocator()

    def locator(self, selector):
        return self.fake_locator

    async def screenshot(self, **kwargs):
        self.screenshot_kwargs = kwargs
        Path(kwargs["path"]).write_bytes(b"image")

    async def title(self):
        return "Example"


class FakeRuntime:
    def __init__(self, page: FakePage, data_dir: Path) -> None:
        self.page = page
        self.data_dir = data_dir

    async def get_page(self):
        return self.page

    def build_artifact_path(self, prefix: str, extension: str) -> Path:
        return self.data_dir / f"{prefix}.{extension}"

    async def list_artifacts(self):
        return []

    def resolve_file_path(self, requested_name: str, category: str = "artifacts"):
        return self.data_dir / requested_name


class ArtifactToolsTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_take_screenshot_supports_jpeg_quality(self) -> None:
        with TemporaryDirectory() as temp_dir:
            page = FakePage()
            registry = ToolRegistry()
            register_artifact_tools(registry, FakeRuntime(page, Path(temp_dir)))

            result = await registry.tools["take_screenshot"](
                file_name_prefix="shot",
                image_type="jpeg",
                quality=70,
            )

            self.assertEqual(page.screenshot_kwargs["type"], "jpeg")
            self.assertEqual(page.screenshot_kwargs["quality"], 70)
            self.assertEqual(result["file_name"], "shot.jpeg")
            self.assertEqual(result["image_type"], "jpeg")
            self.assertEqual(result["quality"], 70)
            self.assertEqual(result["size_bytes"], 5)

    async def test_take_screenshot_rejects_invalid_image_type(self) -> None:
        with TemporaryDirectory() as temp_dir:
            page = FakePage()
            registry = ToolRegistry()
            register_artifact_tools(registry, FakeRuntime(page, Path(temp_dir)))

            result = await registry.tools["take_screenshot"](image_type="gif")

            self.assertFalse(result["ok"])
            self.assertEqual(result["error_type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
