import re
from app.providers.base import ProviderError
import json

VALID_RESPONSE = json.dumps({
    "summary": "Client needs a marketing landing page for a B2B SaaS analytics product "
               "with email capture, pricing teaser, copy suggestions and basic SEO, "
               "delivered within 2 weeks on a limited budget.",
    "goals": [
        "Explain the product value to B2B visitors",
        "Capture leads via email signup",
        "Tease pricing to qualify prospects",
    ],
    "deliverables": [
        "Responsive landing page",
        "Email capture form",
        "Pricing teaser section",
        "Copy suggestions",
        "Basic on-page SEO",
    ],
    "constraints": [
        "Deadline: 2 weeks",
        "Limited budget",
    ],
    "risks": [
        {
            "risk": "Scope exceeds the 2-week deadline",
            "severity": "high",
            "reason": "Copy, SEO and design iterations rarely fit a two-week window together",
        },
        {
            "risk": "Budget is not quantified",
            "severity": "medium",
            "reason": "The brief says 'limited' without a number, estimation may misalign",
        },
    ],
    "clarifying_questions": [
        "What is the actual budget range?",
        "Is there existing branding or design system to reuse?",
        "Where should captured emails be delivered (CRM, mailing tool)?",
    ],
    "recommended_next_action": "Confirm budget and branding assets, then propose "
                               "a one-page scope with a fixed 2-week plan.",
})

INVALID_SEVERITY_RESPONSE = VALID_RESPONSE.replace('"high"', '"catastrophic"')


class FakeProvider:
    async def decode_brief(self, text: str) -> str:
        if match := re.search(r"^FAIL:\s*(\w+)", text.strip()):
            mode = match.group(1)

            if mode == "malformed":
                return '{"summary": "broken", это не json'
            elif mode == "missing":
                return '{"summary": "only summary"}'
            elif mode == "severity":
                return INVALID_SEVERITY_RESPONSE
            elif mode == "provider":
                raise ProviderError("fake provider failure")

        return VALID_RESPONSE
