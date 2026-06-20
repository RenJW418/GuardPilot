from __future__ import annotations

from fastapi import APIRouter

from guardpilot.storage.repositories import list_risk_events

router = APIRouter(prefix="/api/v1", tags=["risk"])


@router.get("/risk-events")
def risk_events(limit: int = 200) -> list[dict]:
    return list_risk_events(limit=limit)
