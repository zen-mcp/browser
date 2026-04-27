import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_base_url: str
    model_name: str
    browser_mcp_host: str = "127.0.0.1"
    browser_mcp_port: int = 8000
    browser_prewarm: bool = True


def parse_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise RuntimeError(f"Invalid boolean value: {value!r}.")


def parse_port(value: str | None, default: int = 8000) -> int:
    if value is None or not value.strip():
        return default

    try:
        port = int(value)
    except ValueError as error:
        raise RuntimeError(f"Invalid BROWSER_MCP_PORT {value!r}.") from error

    if port < 1 or port > 65535:
        raise RuntimeError("BROWSER_MCP_PORT must be between 1 and 65535.")
    return port


def load_settings() -> Settings:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()
    browser_mcp_host = os.getenv("BROWSER_MCP_HOST", "127.0.0.1").strip()

    if not openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")
    if not openai_base_url:
        raise RuntimeError("Missing OPENAI_BASE_URL in environment.")
    if not model_name:
        raise RuntimeError("Missing MODEL_NAME in environment.")
    if not browser_mcp_host:
        raise RuntimeError("Missing BROWSER_MCP_HOST in environment.")

    return Settings(
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        model_name=model_name,
        browser_mcp_host=browser_mcp_host,
        browser_mcp_port=parse_port(os.getenv("BROWSER_MCP_PORT")),
        browser_prewarm=parse_bool(os.getenv("BROWSER_PREWARM"), True),
    )
