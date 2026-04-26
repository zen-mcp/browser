import asyncio
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

browser_use = types.ModuleType("browser_use")
browser_use.BrowserSession = object
sys.modules.setdefault("browser_use", browser_use)

playwright = types.ModuleType("playwright")
async_api = types.ModuleType("playwright.async_api")
async_api.Browser = object
async_api.BrowserContext = object
async_api.Page = object
async_api.async_playwright = lambda: None
sys.modules.setdefault("playwright", playwright)
sys.modules.setdefault("playwright.async_api", async_api)

import browser  # noqa: E402
from browser import BrowserRuntime  # noqa: E402
from config import Settings  # noqa: E402


class BrowserRuntimeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = TemporaryDirectory()
        self.data_dir = Path(self._temp_dir.name)
        self.previous_data_dir = browser.DATA_DIR
        browser.DATA_DIR = self.data_dir
        self.runtime = BrowserRuntime(
            Settings(
                openai_api_key="test-key",
                openai_base_url="https://example.test/v1",
                model_name="test-model",
            )
        )

    def tearDown(self) -> None:
        browser.DATA_DIR = self.previous_data_dir
        self._temp_dir.cleanup()

    def test_build_artifact_path_sanitizes_prefix_inside_data_dir(self) -> None:
        path = self.runtime.build_artifact_path("../../bad prefix!*", ".png")

        self.assertEqual(path.parent, self.data_dir)
        self.assertTrue(path.name.startswith("bad_prefix_"))
        self.assertTrue(path.name.endswith(".png"))

    def test_build_artifact_path_uses_defaults_for_empty_parts(self) -> None:
        path = self.runtime.build_artifact_path("...", "")

        self.assertEqual(path.parent, self.data_dir)
        self.assertTrue(path.name.startswith("artifact_"))
        self.assertTrue(path.name.endswith(".dat"))

    def test_resolve_file_path_allows_files_inside_data_dir(self) -> None:
        file_path = self.data_dir / "safe.txt"
        file_path.write_text("ok", encoding="utf-8")

        self.assertEqual(
            self.runtime.resolve_file_path("safe.txt"),
            file_path.resolve(),
        )
        self.assertEqual(
            self.runtime.resolve_file_path("nested/file.txt", "downloads"),
            (self.data_dir / "nested" / "file.txt").resolve(),
        )

    def test_resolve_file_path_blocks_traversal_and_absolute_paths(self) -> None:
        invalid_names = [
            "../outside.txt",
            "nested/../../outside.txt",
            "/tmp/outside.txt",
            ".",
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.runtime.resolve_file_path(name)

    def test_resolve_file_path_rejects_unknown_category(self) -> None:
        with self.assertRaises(ValueError):
            self.runtime.resolve_file_path("safe.txt", "other")

    def test_list_artifacts_returns_top_level_files_from_data_dir(self) -> None:
        file_path = self.data_dir / "a.txt"
        file_path.write_text("ok", encoding="utf-8")
        (self.data_dir / "nested").mkdir()
        (self.data_dir / "nested" / "ignored.txt").write_text("skip", encoding="utf-8")

        result = asyncio.run(self.runtime.list_artifacts())

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "a.txt")
        self.assertEqual(result[0]["category"], "artifacts")

    def test_concurrent_get_page_launches_browser_once(self) -> None:
        class FakePage:
            pass

        class FakeContext:
            def __init__(self) -> None:
                self.pages = []
                self.new_page_calls = 0

            async def new_page(self):
                self.new_page_calls += 1
                page = FakePage()
                self.pages.append(page)
                return page

        class FakeBrowser:
            def __init__(self, context: FakeContext) -> None:
                self.context = context
                self.new_context_calls = 0

            async def new_context(self, **kwargs):
                self.new_context_calls += 1
                return self.context

        class FakeChromium:
            def __init__(self, fake_browser: FakeBrowser) -> None:
                self.fake_browser = fake_browser
                self.launch_calls = 0

            async def launch(self, **kwargs):
                self.launch_calls += 1
                return self.fake_browser

        class FakePlaywright:
            def __init__(self, chromium: FakeChromium) -> None:
                self.chromium = chromium

        class FakeStarter:
            def __init__(self, fake_playwright: FakePlaywright) -> None:
                self.fake_playwright = fake_playwright
                self.start_calls = 0

            async def start(self):
                self.start_calls += 1
                return self.fake_playwright

        fake_context = FakeContext()
        fake_browser = FakeBrowser(fake_context)
        fake_chromium = FakeChromium(fake_browser)
        fake_playwright = FakePlaywright(fake_chromium)
        fake_starter = FakeStarter(fake_playwright)
        previous_async_playwright = browser.async_playwright
        browser.async_playwright = lambda: fake_starter

        try:
            async def run_concurrent_get_page():
                return await asyncio.gather(
                    self.runtime.get_page(),
                    self.runtime.get_page(),
                    self.runtime.get_page(),
                )

            pages = asyncio.run(run_concurrent_get_page())
        finally:
            browser.async_playwright = previous_async_playwright

        self.assertIs(pages[0], pages[1])
        self.assertIs(pages[1], pages[2])
        self.assertEqual(fake_starter.start_calls, 1)
        self.assertEqual(fake_chromium.launch_calls, 1)
        self.assertEqual(fake_browser.new_context_calls, 1)
        self.assertEqual(fake_context.new_page_calls, 1)

    def test_prewarm_initializes_page(self) -> None:
        class FakeContext:
            pages = ["existing-page"]

        self.runtime._playwright = object()
        self.runtime._browser = object()
        self.runtime._context = FakeContext()

        asyncio.run(self.runtime.prewarm())

        self.assertEqual(self.runtime._page, "existing-page")


if __name__ == "__main__":
    unittest.main()
