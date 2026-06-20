from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from guardpilot.core.replay_engine import ReplayEngine  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a GuardPilot replay scenario")
    parser.add_argument("--scenario", default="samples/scenarios/btc_momentum_crash.json")
    args = parser.parse_args()

    summary = ReplayEngine(ROOT).run(args.scenario)
    print("Replay completed")
    print(f"Scenario: {summary['scenario_id']}")
    print(f"Total intents: {summary['total_intents']}")
    print(f"Allowed: {summary['allowed']}")
    print(f"Warned: {summary['warned']}")
    print(f"Blocked: {summary['blocked']}")
    print(f"Final equity with GuardPilot: {summary['final_equity_with_guard']:.2f} USDT")
    print(f"Final equity without GuardPilot: {summary['final_equity_without_guard']:.2f} USDT")
    print(f"Max drawdown with GuardPilot: {summary['max_drawdown_with_guard']:.2%}")
    print(f"Max drawdown without GuardPilot: {summary['max_drawdown_without_guard']:.2%}")
    print(f"Risk grade: {summary['risk_grade']}")
    print(f"Report: {summary['report_path']}")


if __name__ == "__main__":
    main()
