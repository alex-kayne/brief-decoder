from app.providers import get_provider
from app.repository import RunRepository
from app.service import BriefService


def get_brief_service() -> BriefService:
    return BriefService(get_provider(), RunRepository())
