from __future__ import annotations

from pydantic import BaseModel


class OrderFill(BaseModel):
    order_id: str
    timestamp: str
    agent_id: str
    symbol: str
    side: str
    price: float
    quantity: float
    notional: float
    fee: float
    realized_pnl: float
    balance_before: float
    balance_after: float
    equity_after: float
    risk_score: int
    decision: str
    reason: str = ""
