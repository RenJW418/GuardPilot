from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_market_csv(path: Path, symbol: str = "BTCUSDT", start_price: float = 65000.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)
    rows = ["timestamp,symbol,open,high,low,close,volume"]
    price = start_price
    moves = [
        80, 150, -70, 120, 180, -90, -160, -260, 140, -220,
        90, 130, 170, -80, 110, -120, -180, -220, -320, 260,
        180, -140, 90, 120, -70, 160, -110, 80, 95, -130,
        170, -210, -260, 340, 220, -180, 130, 90, -75, 115,
        160, -140, 95, -85, 120, 140, -105, 90, -70, 110,
    ]
    for i, move in enumerate(moves):
        timestamp = start + timedelta(minutes=i)
        open_price = price
        close_price = max(100, price + move)
        high = max(open_price, close_price) + abs(move) * 0.35 + 35
        low = min(open_price, close_price) - abs(move) * 0.35 - 35
        volume = 120 + abs(move) * 0.22 + (i % 7) * 8
        rows.append(
            f"{timestamp.isoformat().replace('+00:00','Z')},{symbol},{open_price:.2f},{high:.2f},{low:.2f},{close_price:.2f},{volume:.2f}"
        )
        price = close_price
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def generate_signal_jsonl(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)
    signals = []
    sides = ["BUY", "BUY", "SELL", "BUY", "SELL", "SELL", "BUY", "BUY", "SELL", "BUY"]
    for i in range(42):
        timestamp = start + timedelta(minutes=i + 1)
        side = sides[i % len(sides)]
        quantity = 0.012 + (i % 4) * 0.004
        leverage = 2 + (i % 3)
        confidence = 0.58 + (i % 5) * 0.07
        reason = "Momentum signal with controlled position sizing"
        if i in {8, 9, 10, 11, 12, 13, 14, 15}:
            quantity = 0.018
            leverage = 4
            confidence = 0.52
            reason = "High frequency signal during unstable market window"
        if i in {18, 19, 20, 21}:
            quantity = 0.055 + (i - 18) * 0.01
            leverage = 7 + (i - 18)
            confidence = 0.43
            reason = "Trying to recover previous losses after breakout failure"
        if i in {31, 32}:
            quantity = 0.075
            leverage = 8
            confidence = 0.31
            reason = "Low-confidence oversized trade during volatile reversal"
        signals.append(
            {
                "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                "agent_id": "demo_momentum_agent",
                "symbol": "BTCUSDT",
                "side": side,
                "order_type": "MARKET",
                "quantity": round(quantity, 4),
                "leverage": leverage,
                "confidence": round(min(confidence, 0.92), 2),
                "reason": reason,
            }
        )
    import json
    path.write_text("\n".join(json.dumps(signal, separators=(",", ":")) for signal in signals) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    generate_market_csv(root / "samples" / "market" / "btcusdt_1m.csv")
    generate_market_csv(root / "samples" / "market" / "ethusdt_1m.csv", symbol="ETHUSDT", start_price=3500)
    generate_signal_jsonl(root / "samples" / "agents" / "demo_momentum_signals.jsonl")
