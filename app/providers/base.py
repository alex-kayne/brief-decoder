from typing import Protocol


class LLMProvider(Protocol):
    async def decode_brief(self, text: str) -> str: ...


class ProviderError(Exception):
    """Сбой LLM-провайдера (сеть, лимиты, недоступность)."""
