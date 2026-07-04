from datetime import datetime, UTC
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class RunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ErrorCode(StrEnum):
    PROVIDER_ERROR = "provider_error"
    VALIDATION_ERROR = "validation_error"


class Base(DeclarativeBase):
    ...


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status", values_callable=lambda e: [m.value for m in e]))
    input_text: Mapped[str] = mapped_column(Text)
    result: Mapped[dict] = mapped_column(JSONB, nullable=True)
    raw_output: Mapped[str] = mapped_column(Text, nullable=True)
    error_code: Mapped[ErrorCode] = mapped_column(
        Enum(ErrorCode, name="error_code", values_callable=lambda e: [m.value for m in e]), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
