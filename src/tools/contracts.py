from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec


ToolPayload = dict[str, Any]
P = ParamSpec("P")


def error_payload(error: BaseException) -> ToolPayload:
    return {
        "ok": False,
        "error": str(error),
        "error_type": type(error).__name__,
    }


def legacy_error_text(error: BaseException) -> str:
    return f"Error ({type(error).__name__}): {error}"


def ensure_ok(payload: ToolPayload) -> ToolPayload:
    if "ok" in payload:
        return payload
    return {"ok": True, **payload}


def mcp_tool_guard(
    func: Callable[P, Awaitable[ToolPayload]],
) -> Callable[P, Awaitable[ToolPayload]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> ToolPayload:
        try:
            return ensure_ok(await func(*args, **kwargs))
        except Exception as error:
            return error_payload(error)

    return wrapper
