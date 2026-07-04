from fastapi import FastAPI

from app.api.briefs import router as briefs_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="brief-decoder")
app.include_router(briefs_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
