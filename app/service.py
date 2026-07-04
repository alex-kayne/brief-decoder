from pydantic import ValidationError

from app.database import async_session_maker
from app.models import Run
from app.models import RunStatus, ErrorCode
from app.providers import LLMProvider
from app.providers.base import ProviderError
from app.repository import RunRepository
from app.schemas import BriefDecodeResult


class BriefService:
    def __init__(self, provider: LLMProvider, repo: RunRepository):
        self.provider = provider
        self.repo = repo

    async def decode(self, text: str) -> Run:
        raw: str | None = None

        try:
            raw = await self.provider.decode_brief(text)
            result = BriefDecodeResult.model_validate_json(raw)
            run = Run(status=RunStatus.SUCCEEDED, input_text=text,
                      result=result.model_dump(), raw_output=raw)
        except ProviderError:
            run = Run(status=RunStatus.FAILED, input_text=text,
                      error_code=ErrorCode.PROVIDER_ERROR,
                      error_message="LLM provider failed")
        except ValidationError:
            run = Run(status=RunStatus.FAILED, input_text=text,
                      raw_output=raw,
                      error_code=ErrorCode.VALIDATION_ERROR,
                      error_message="Provider returned invalid structured output")
        async with async_session_maker.begin() as session:
            await self.repo.add(session, run)
        return run

    async def get_run(self, run_id: int) -> Run | None:
        async with async_session_maker() as session:
            return await self.repo.get_by_id(session, run_id)
