from __future__ import annotations


def risk_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


def decision_for(score: int) -> str:
    if score <= 60:
        return "ALLOW"
    if score <= 80:
        return "WARN"
    return "BLOCK"


def grade_for(score: float) -> str:
    if score <= 25:
        return "A"
    if score <= 45:
        return "B"
    if score <= 65:
        return "C"
    if score <= 80:
        return "D"
    return "F"


def clamp_score(value: float) -> int:
    return int(max(0, min(100, round(value))))
