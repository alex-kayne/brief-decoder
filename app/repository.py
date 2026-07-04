from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run


class RunRepository:

    async def add(self, async_session: AsyncSession, run: Run) -> None:
        async_session.add(run)
        await async_session.flush()

    async def get_by_id(self, async_session: AsyncSession, run_id: int) -> Run | None:
        stmt = select(Run).where(Run.id == run_id)
        result = await async_session.execute(stmt)
        return result.scalar_one_or_none()
