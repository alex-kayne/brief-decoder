from app.config import settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeProvider


def get_provider() -> LLMProvider:
    match settings.llm_provider:
        case "fake":
            return FakeProvider()
        case _:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
