from __future__ import annotations

from pydantic import BaseModel


class ReplaySummary(BaseModel):
    scenario_id: str
    total_intents: int
    allowed: int
    warned: int
    blocked: int
    final_equity_with_guard: float
    final_equity_without_guard: float
    max_drawdown_with_guard: float
    max_drawdown_without_guard: float
    risk_grade: str
    report_path: str
