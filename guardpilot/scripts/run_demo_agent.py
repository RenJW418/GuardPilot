from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from guardpilot.core.replay_engine import ReplayEngine


if __name__ == "__main__":
    summary = ReplayEngine(ROOT).run("samples/scenarios/btc_momentum_crash.json")
    print(f"Demo agent replay complete: {summary['blocked']} blocked, grade {summary['risk_grade']}")
