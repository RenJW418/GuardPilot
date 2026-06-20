from __future__ import annotations

from fastapi import APIRouter

from guardpilot.storage.repositories import list_trades

router = APIRouter(prefix="/api/v1", tags=["trades"])


@router.get("/trades")
def trades(limit: int = 200) -> list[dict]:
    return list_trades(limit=limit)
