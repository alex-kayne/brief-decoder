from app.providers.fake import FakeProvider
from app.repository import RunRepository
from app.service import BriefService


def get_brief_service() -> BriefService:
    return BriefService(FakeProvider(), RunRepository())
