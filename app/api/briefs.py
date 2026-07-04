from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import BriefService, get_brief_service
from app.schemas import RunRead, DecodeRequest

router = APIRouter(prefix="/v1/briefs", tags=["briefs"])


@router.post("/decode", response_model=RunRead)
async def decode_brief(
        data: DecodeRequest,
        service: BriefService = Depends(get_brief_service),
):
    return await service.decode(data.text)


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(
        run_id: int,
        service: BriefService = Depends(get_brief_service),
):
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run
