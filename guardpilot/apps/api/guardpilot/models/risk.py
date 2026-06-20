from __future__ import annotations

from pydantic import BaseModel


class RiskCheck(BaseModel):
    name: str
    status: str
    score: int
    message: str


class RiskDecision(BaseModel):
    decision: str
    risk_score: int
    risk_level: str
    checks: list[RiskCheck]
