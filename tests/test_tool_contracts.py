import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tools.contracts import (  # noqa: E402
    ensure_ok,
    error_payload,
    legacy_error_text,
    mcp_tool_guard,
)


class ToolContractsTestCase(unittest.IsolatedAsyncioTestCase):
    def test_error_payload_has_stable_shape(self) -> None:
        payload = error_payload(ValueError("bad path"))

        self.assertEqual(
            payload,
            {
                "ok": False,
                "error": "bad path",
                "error_type": "ValueError",
            },
        )

    def test_ensure_ok_adds_default_success_flag(self) -> None:
        self.assertEqual(ensure_ok({"value": 1}), {"ok": True, "value": 1})
        self.assertEqual(ensure_ok({"ok": False}), {"ok": False})

    def test_legacy_error_text_keeps_string_contract(self) -> None:
        self.assertEqual(
            legacy_error_text(RuntimeError("boom")),
            "Error (RuntimeError): boom",
        )

    async def test_mcp_tool_guard_returns_success_payload(self) -> None:
        @mcp_tool_guard
        async def tool() -> dict:
            return {"value": 1}

        self.assertEqual(await tool(), {"ok": True, "value": 1})

    async def test_mcp_tool_guard_returns_error_payload_for_selector_timeout(
        self,
    ) -> None:
        @mcp_tool_guard
        async def tool() -> dict:
            raise TimeoutError("selector timed out")

        self.assertEqual(
            await tool(),
            {
                "ok": False,
                "error": "selector timed out",
                "error_type": "TimeoutError",
            },
        )


if __name__ == "__main__":
    unittest.main()
