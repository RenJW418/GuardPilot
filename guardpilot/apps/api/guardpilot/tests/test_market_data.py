from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

import pytest

from guardpilot.core.market_context import MarketContextProvider
from guardpilot.integrations.bitget_market_data import parse_bitget_candles


ROOT = Path(__file__).resolve().parents[4]


def test_parse_bitget_public_candles_list_shape():
    rows = [["1782133140000", "100", "110", "95", "105", "12.5", "1312.5", "1312.5"]]
    candles = parse_bitget_candles(rows, "BTCUSDT")
    assert len(candles) == 1
    assert candles[0].symbol == "BTCUSDT"
    assert candles[0].open == 100
    assert candles[0].high == 110
    assert candles[0].low == 95
    assert candles[0].close == 105
    assert candles[0].volume == 12.5
    assert candles[0].timestamp.endswith("Z")


def test_market_context_uses_committed_bitget_snapshot():
    provider = MarketContextProvider(root_dir=ROOT)
    context = provider.for_intent("BTCUSDT", price_hint=None)
    assert context.source == "Bitget public market API snapshot"
    assert context.price > 0
    assert context.recent_volatility >= 0
    assert context.snapshot_path == "samples/market/bitget_btcusdt_1m.csv"
    assert context.price_source == "bitget_public_snapshot_close"


def test_market_context_labels_agent_price_hint():
    provider = MarketContextProvider(root_dir=ROOT)
    context = provider.for_intent("BTCUSDT", price_hint=12345.67)
    assert context.price == 12345.67
    assert context.price_source == "agent_price_hint_with_bitget_snapshot_volatility"
    assert context.source == "Bitget public market API snapshot"


def test_market_context_rejects_timestamp_outside_snapshot_range():
    provider = MarketContextProvider(root_dir=ROOT)
    early = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="outside the Bitget public market snapshot range"):
        provider.for_intent("BTCUSDT", timestamp=early)
