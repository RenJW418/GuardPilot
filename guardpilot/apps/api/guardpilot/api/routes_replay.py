from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from guardpilot.config import ROOT_DIR
from guardpilot.core.replay_engine import ReplayEngine

router = APIRouter(prefix="/api/v1", tags=["replay"])


@router.post("/replay")
def replay(scenario: str = "samples/scenarios/btc_momentum_crash.json") -> dict:
    return ReplayEngine(ROOT_DIR).run(scenario)


@router.get("/reports/{report_id}")
def report(report_id: str) -> dict:
    path = ROOT_DIR / "reports" / "demo_report.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run replay first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("report_id") != report_id and report_id != "latest":
        raise HTTPException(status_code=404, detail="Report not found")
    return data
