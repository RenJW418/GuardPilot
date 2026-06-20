from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "samples" / "outputs" / "sample_risk_report.json"
SUMMARY_PATH = ROOT / "samples" / "outputs" / "sample_replay_summary.json"


def pct(value: float) -> str:
    return f"{value:.2%}"


def main() -> None:
    if not REPORT_PATH.exists() or not SUMMARY_PATH.exists():
        raise SystemExit(
            "Evidence files are missing. Run `python3 scripts/replay.py --scenario samples/scenarios/btc_momentum_crash.json` first."
        )

    report = json.loads(REPORT_PATH.read_text())
    summary = json.loads(SUMMARY_PATH.read_text())
    impact = report["impact_metrics"]

    checks = [
        ("total intents", report["total_intents"] == 42),
        ("blocked high-risk intents", report["blocked"] == 22),
        ("warned elevated-risk intents", report["warned"] == 4),
        ("final equity improved", report["final_equity_with_guard"] > report["final_equity_without_guard"]),
        ("max drawdown reduced", report["max_drawdown_with_guard"] < report["max_drawdown_without_guard"]),
        ("audit records generated", impact["audit_records_generated"] >= 100),
    ]

    print("GuardPilot Evidence Verification")
    print("================================")
    print(f"Scenario: {report['scenario_id']}")
    print(f"Total intents: {report['total_intents']}")
    print(f"Allowed / Warned / Blocked: {report['allowed']} / {report['warned']} / {report['blocked']}")
    print(f"Blocked intent rate: {pct(impact['blocked_intent_rate'])}")
    print()
    print(f"Final equity without guard: {report['final_equity_without_guard']:.2f} USDT")
    print(f"Final equity with GuardPilot: {report['final_equity_with_guard']:.2f} USDT")
    print(f"Equity improvement: +{impact['equity_improvement_usdt']:.2f} USDT")
    print()
    print(f"Max drawdown without guard: {pct(report['max_drawdown_without_guard'])}")
    print(f"Max drawdown with GuardPilot: {pct(report['max_drawdown_with_guard'])}")
    print(f"Relative drawdown reduction: {pct(impact['max_drawdown_reduction_relative'])}")
    print()
    print(f"Average raw risk score: {report['average_risk_score']:.2f}")
    print(f"Residual risk score after guardrails: {report['residual_risk_score_after_guard']:.2f}")
    print(f"Audit records generated: {impact['audit_records_generated']}")
    print()
    print("Validation checks:")
    failed = False
    for name, ok in checks:
        marker = "PASS" if ok else "FAIL"
        print(f"- {marker}: {name}")
        failed = failed or not ok

    if failed:
        raise SystemExit(1)

    if summary["scenario_id"] != report["scenario_id"]:
        raise SystemExit("Summary/report scenario mismatch")

    print()
    print("Result: PASS — GuardPilot reduced simulated drawdown, improved final equity, blocked high-risk intents, and generated audit evidence for the deterministic replay.")


if __name__ == "__main__":
    main()
