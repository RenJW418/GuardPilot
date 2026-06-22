from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"


class TradeIntent(BaseModel):
    timestamp: datetime
    agent_id: str = Field(min_length=1)
    symbol: str = Field(default="BTCUSDT", min_length=3)
    side: Side
    order_type: OrderType = OrderType.MARKET
    quantity: float = Field(gt=0)
    leverage: float = Field(default=1, ge=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    reason: str = Field(default="")
    price_hint: Optional[float] = Field(default=None, gt=0)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    def normalized_timestamp(self) -> str:
        value = self.timestamp
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class IntentResponse(BaseModel):
    intent_id: str
    decision: str
    risk_score: int
    risk_level: str
    simulated_order_id: Optional[str]
    account_equity_after: float
    checks: list[dict]
    bitget_dry_run_payload: Optional[dict] = None
    market_context: Optional[dict] = None
    execution_mode: str = "paper_trading_only"
