from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from guardpilot.demo_agents.momentum_agent import generate_market_csv, generate_signal_jsonl


LEGACY_DIR = ROOT / "samples" / "legacy_deterministic"


def main() -> None:
    """Seed legacy deterministic fixtures for local experiments only.

    The default hackathon replay uses the committed Bitget public-market snapshot
    and does not depend on these generated fixtures.
    """
    generate_market_csv(LEGACY_DIR / "btcusdt_1m.csv")
    generate_market_csv(LEGACY_DIR / "ethusdt_1m.csv", symbol="ETHUSDT", start_price=3500)
    generate_signal_jsonl(LEGACY_DIR / "demo_momentum_signals.jsonl")
    generate_signal_jsonl(LEGACY_DIR / "risky_agent_signals.jsonl")
    print(f"Seeded legacy deterministic fixtures under {LEGACY_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
