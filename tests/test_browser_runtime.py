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


if __name__ == "__main__":
    unittest.main()
