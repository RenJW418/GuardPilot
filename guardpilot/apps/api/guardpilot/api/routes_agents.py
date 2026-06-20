from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, HTTPException

from guardpilot.storage.repositories import list_risk_events, list_trades

router = APIRouter(prefix="/api/v1", tags=["agents"])


@router.get("/agents")
def agents() -> list[dict]:
    trades = list_trades(limit=1000)
    grouped: dict[str, dict] = defaultdict(lambda: {"agent_id": "", "trades": 0, "blocked": 0, "pnl": 0.0, "risk_score_sum": 0})
    for trade in trades:
        item = grouped[trade["agent_id"]]
        item["agent_id"] = trade["agent_id"]
        item["trades"] += 1
        item["blocked"] += 1 if trade["decision"] == "BLOCK" else 0
        item["pnl"] += trade.get("realized_pnl", 0) or 0
        item["risk_score_sum"] += trade.get("risk_score", 0) or 0
    result = []
    for item in grouped.values():
        avg = item["risk_score_sum"] / max(item["trades"], 1)
        result.append({**item, "pnl": round(item["pnl"], 4), "average_risk_score": round(avg, 2)})
    return result


@router.get("/agents/{agent_id}")
def agent_detail(agent_id: str) -> dict:
    trades = [trade for trade in list_trades(limit=1000) if trade["agent_id"] == agent_id]
    if not trades:
        raise HTTPException(status_code=404, detail="Agent not found")
    events = [event for event in list_risk_events(limit=1000) if event["agent_id"] == agent_id]
    return {"agent_id": agent_id, "trades": trades, "risk_events": events}
