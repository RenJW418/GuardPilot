from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from guardpilot.demo_agents.momentum_agent import generate_market_csv, generate_signal_jsonl


def main() -> None:
    generate_market_csv(ROOT / "samples" / "market" / "btcusdt_1m.csv")
    generate_market_csv(ROOT / "samples" / "market" / "ethusdt_1m.csv", symbol="ETHUSDT", start_price=3500)
    generate_signal_jsonl(ROOT / "samples" / "agents" / "demo_momentum_signals.jsonl")
    generate_signal_jsonl(ROOT / "samples" / "agents" / "risky_agent_signals.jsonl")
    print("Seeded demo market data and agent signals")


if __name__ == "__main__":
    main()
