import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_base_url: str
    model_name: str


def load_settings() -> Settings:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()

    if not openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")
    if not openai_base_url:
        raise RuntimeError("Missing OPENAI_BASE_URL in environment.")
    if not model_name:
        raise RuntimeError("Missing MODEL_NAME in environment.")

    return Settings(
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        model_name=model_name,
    )
