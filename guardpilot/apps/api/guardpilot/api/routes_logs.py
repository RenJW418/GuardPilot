from __future__ import annotations

from fastapi import APIRouter

from guardpilot.storage.repositories import list_api_logs

router = APIRouter(prefix="/api/v1", tags=["logs"])


@router.get("/api-logs")
def api_logs(limit: int = 200) -> list[dict]:
    return list_api_logs(limit=limit)
