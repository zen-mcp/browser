from browser_use import ChatOpenAI

from config import Settings

def create_llm(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
