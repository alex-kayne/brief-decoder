from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict

from app.models import RunStatus, ErrorCode


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

class DecodeRequest(BaseModel):
    text: str = Field(min_length=1)

class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    run_id: int = Field(validation_alias="id")
    status: RunStatus
    result: BriefDecodeResult | None
    error_code: ErrorCode | None
    error_message: str | None
    created_at: datetime