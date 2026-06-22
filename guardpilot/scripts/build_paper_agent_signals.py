from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_market(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 43:
        raise ValueError("At least 43 market rows are required to derive the default 42 paper-agent intents")
    return rows


def build_signals(rows: list[dict[str, str]], count: int = 42) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    recent_sides: list[str] = []
    for i in range(1, count + 1):
        row = rows[i]
        previous = rows[i - 1]
        timestamp = row["timestamp"]
        close = float(row["close"])
        previous_close = float(previous["close"])
        high = float(row["high"])
        low = float(row["low"])
        momentum = (close - previous_close) / previous_close if previous_close else 0.0
        volatility = (high - low) / close if close else 0.0
        side = "BUY" if momentum >= 0 else "SELL"
        quantity = 0.01 + min(abs(momentum) * 2.5, 0.018) + (i % 3) * 0.002
        leverage = 2 if volatility < 0.006 else 3
        confidence = 0.64 + min(abs(momentum) * 8, 0.18)
        reason = f"Paper momentum signal from Bitget candle: momentum={momentum:.4%}, range={volatility:.4%}"

        if 8 <= i <= 15:
            side = recent_sides[-1] if recent_sides else side
            quantity = 0.018 + (i % 2) * 0.004
            leverage = 4
            confidence = 0.52
            reason = f"Paper agent overtrading during real Bitget volatility window: momentum={momentum:.4%}, range={volatility:.4%}"
        elif 18 <= i <= 21:
            side = "BUY" if momentum < 0 else "SELL"
            quantity = 0.052 + (i - 18) * 0.012
            leverage = 7 + (i - 18)
            confidence = 0.43
            reason = f"Paper agent attempts loss recovery after real candle reversal: momentum={momentum:.4%}, range={volatility:.4%}"
        elif i in {31, 32}:
            quantity = 0.075
            leverage = 8
            confidence = 0.31
            reason = f"Low-confidence oversized paper order during Bitget snapshot reversal: momentum={momentum:.4%}, range={volatility:.4%}"

        recent_sides.append(side)
        signals.append(
            {
                "timestamp": timestamp,
                "agent_id": "paper_momentum_agent_bitget_snapshot",
                "symbol": row.get("symbol", "BTCUSDT"),
                "side": side,
                "order_type": "MARKET",
                "quantity": round(quantity, 4),
                "leverage": leverage,
                "confidence": round(min(confidence, 0.92), 2),
                "reason": reason,
            }
        )
    return signals


def write_jsonl(signals: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(signal, separators=(",", ":")) for signal in signals) + "\n", encoding="utf-8")


def write_provenance(market_path: Path, output_path: Path, signals: list[dict[str, Any]], provenance_path: Path) -> None:
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "Paper-agent signals derived from Bitget public market snapshot",
        "market_input": str(market_path.relative_to(ROOT)),
        "output": str(output_path.relative_to(ROOT)),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "rows": len(signals),
        "agent_id": signals[0]["agent_id"] if signals else "unknown",
        "method": "Deterministic momentum/reversal rules over real Bitget public candles for paper-trading risk evaluation.",
        "not_agenthub_export": True,
        "execution_mode": "paper_trading_only",
        "live_orders": False,
    }
    provenance_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic paper-agent intents from a real Bitget market snapshot.")
    parser.add_argument("--market", default="samples/market/bitget_btcusdt_1m.csv", help="Market CSV path under guardpilot/")
    parser.add_argument(
        "--output",
        default="samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl",
        help="Output JSONL path under guardpilot/",
    )
    parser.add_argument(
        "--provenance",
        default="samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json",
        help="Signal provenance JSON path under guardpilot/",
    )
    parser.add_argument("--count", type=int, default=42, help="Number of paper-agent intents to derive")
    args = parser.parse_args()

    market_path = (ROOT / args.market).resolve()
    output_path = (ROOT / args.output).resolve()
    provenance_path = (ROOT / args.provenance).resolve()
    root = ROOT.resolve()
    if root not in market_path.parents or root not in output_path.parents or root not in provenance_path.parents:
        raise SystemExit("All paths must stay inside the guardpilot project directory")

    rows = load_market(market_path)
    signals = build_signals(rows, args.count)
    write_jsonl(signals, output_path)
    write_provenance(market_path, output_path, signals, provenance_path)

    print("GuardPilot paper-agent signals")
    print("==============================")
    print(f"Market input: {market_path.relative_to(ROOT)}")
    print(f"Signals:      {output_path.relative_to(ROOT)}")
    print(f"Provenance:   {provenance_path.relative_to(ROOT)}")
    print(f"Rows:         {len(signals)}")
    print("Safety:       derived paper-agent intents only; not an official AgentHub export; no live orders")


if __name__ == "__main__":
    main()
