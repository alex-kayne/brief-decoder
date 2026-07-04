from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Risk(BaseModel):
    risk: str
    severity: Severity
    reason: str


class BriefDecodeResult(BaseModel):
    summary: str
    goals: list[str]
    deliverables: list[str]
    constraints: list[str]
    risks: list[Risk]
    clarifying_questions: list[str]
    recommended_next_action: str
