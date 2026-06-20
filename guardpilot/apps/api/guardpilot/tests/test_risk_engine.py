from __future__ import annotations

from guardpilot.core.risk_engine import RiskContext, RiskEngine
from guardpilot.models.account import Account
from guardpilot.models.intent import TradeIntent


def test_low_risk_intent_is_allowed():
    intent = TradeIntent(timestamp="2026-06-20T10:01:00Z", agent_id="a", symbol="BTCUSDT", side="BUY", quantity=0.01, leverage=2, confidence=0.8)
    risk = RiskEngine().evaluate(intent, RiskContext(account=Account(), current_price=65000, recent_volatility=0.01))
    assert risk.decision == "ALLOW"


def test_high_leverage_oversized_intent_is_blocked():
    intent = TradeIntent(timestamp="2026-06-20T10:01:00Z", agent_id="a", symbol="BTCUSDT", side="BUY", quantity=0.2, leverage=10, confidence=0.2)
    risk = RiskEngine().evaluate(intent, RiskContext(account=Account(), current_price=65000, recent_volatility=0.04))
    assert risk.decision == "BLOCK"
    assert risk.risk_score > 80
