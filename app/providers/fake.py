import re
from app.providers.base import ProviderError
import json

VALID_RESPONSE = json.dumps({
    "summary": "Short normalized summary of the client request",
    "goals": ["..."],
    "deliverables": ["..."],
    "constraints": ["..."],
    "risks": [
        {
            "risk": "...",
            "severity": "low|medium|high",
            "reason": "..."
        }
    ],
    "clarifying_questions": ["..."],
    "recommended_next_action": "..."
})


class FakeProvider:
    async def decode_brief(self, text: str) -> str | ProviderError:
        if match := re.search(r"^FAIL:\s*(\w+)", text):
            mode = match.group(1)

            if mode == "malformed":
                return '{"summary": "broken", это не json'
            elif mode == "missing":
                return '{"summary": "only summary"}'
            elif mode == "severity":
                return '{"summary": "only summary", "risks": [{"risk": "...", "severity": "catastrophic", "reason": "..."}]}'
            elif mode == "provider":
                return ProviderError("fake provider failure")

        return VALID_RESPONSE
