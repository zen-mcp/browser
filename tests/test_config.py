import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

dotenv = types.ModuleType("dotenv")
dotenv.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv)

from config import load_settings, parse_bool, parse_port  # noqa: E402


class ConfigTestCase(unittest.TestCase):
    def test_load_settings_uses_browser_mcp_defaults(self) -> None:
        env = {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://example.test/v1",
            "MODEL_NAME": "test-model",
        }

        with patch.dict(os.environ, env, clear=True):
            settings = load_settings()

        self.assertEqual(settings.browser_mcp_host, "127.0.0.1")
        self.assertEqual(settings.browser_mcp_port, 8000)
        self.assertTrue(settings.browser_prewarm)

    def test_load_settings_parses_browser_mcp_overrides(self) -> None:
        env = {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://example.test/v1",
            "MODEL_NAME": "test-model",
            "BROWSER_MCP_HOST": "0.0.0.0",
            "BROWSER_MCP_PORT": "9000",
            "BROWSER_PREWARM": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            settings = load_settings()

        self.assertEqual(settings.browser_mcp_host, "0.0.0.0")
        self.assertEqual(settings.browser_mcp_port, 9000)
        self.assertFalse(settings.browser_prewarm)

    def test_bool_and_port_validation(self) -> None:
        self.assertTrue(parse_bool("on", False))
        self.assertFalse(parse_bool("0", True))
        self.assertEqual(parse_port("1234"), 1234)

        with self.assertRaises(RuntimeError):
            parse_bool("maybe", True)
        with self.assertRaises(RuntimeError):
            parse_port("70000")

    def test_empty_host_is_rejected(self) -> None:
        env = {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://example.test/v1",
            "MODEL_NAME": "test-model",
            "BROWSER_MCP_HOST": " ",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                load_settings()


if __name__ == "__main__":
    unittest.main()
