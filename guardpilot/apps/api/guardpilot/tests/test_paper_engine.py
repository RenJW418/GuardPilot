from __future__ import annotations

from guardpilot.core.paper_engine import PaperTradingEngine
from guardpilot.models.account import Account
from guardpilot.models.intent import TradeIntent


def test_block_mark_only_does_not_change_balance():
    account = Account()
    intent = TradeIntent(timestamp="2026-06-20T10:01:00Z", agent_id="a", symbol="BTCUSDT", side="BUY", quantity=0.01, leverage=2)
    trade = PaperTradingEngine().mark_only(intent, account, 65000, 90, "BLOCK", "blocked")
    assert trade["balance_before"] == trade["balance_after"]
    assert account.balance == 10000


def test_allowed_order_records_required_fields():
    account = Account()
    intent = TradeIntent(timestamp="2026-06-20T10:01:00Z", agent_id="a", symbol="BTCUSDT", side="BUY", quantity=0.01, leverage=2)
    fill = PaperTradingEngine().execute(intent, account, 65000, 20, "ALLOW").model_dump()
    for field in ["timestamp", "symbol", "side", "price", "quantity", "balance_after"]:
        assert field in fill
