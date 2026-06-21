from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from guardpilot.config import ROOT_DIR
from guardpilot.core.replay_engine import ReplayEngine

router = APIRouter(prefix="/api/v1", tags=["replay"])

SCENARIOS = {
    "btc_momentum_crash": "samples/scenarios/btc_momentum_crash.json",
    "eth_overtrade": "samples/scenarios/eth_overtrade.json",
}


def _scenario_path(scenario: str) -> str:
    if scenario in SCENARIOS:
        return SCENARIOS[scenario]
    candidate = Path(scenario)
    if candidate.suffix == ".json" and candidate.parent.as_posix() == "samples/scenarios" and candidate.stem in SCENARIOS:
        return SCENARIOS[candidate.stem]
    raise HTTPException(
        status_code=400,
        detail=f"Unknown replay scenario '{scenario}'. Allowed values: {', '.join(sorted(SCENARIOS))}",
    )


@router.post("/replay")
def replay(scenario: str = "btc_momentum_crash") -> dict:
    try:
        return ReplayEngine(ROOT_DIR).run(_scenario_path(scenario))
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/{report_id}")
def report(report_id: str) -> dict:
    path = ROOT_DIR / "reports" / "demo_report.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run replay first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("report_id") != report_id and report_id != "latest":
        raise HTTPException(status_code=404, detail="Report not found")
    return data
