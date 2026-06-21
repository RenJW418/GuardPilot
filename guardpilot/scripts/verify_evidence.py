from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "samples" / "outputs" / "sample_risk_report.json"
SUMMARY_PATH = ROOT / "samples" / "outputs" / "sample_replay_summary.json"
MANIFEST_PATH = ROOT / "samples" / "outputs" / "evidence_manifest.json"


def pct(value: float) -> str:
    return f"{value:.2%}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    missing = [path for path in [REPORT_PATH, SUMMARY_PATH, MANIFEST_PATH] if not path.exists()]
    if missing:
        raise SystemExit(
            "Evidence files are missing. Run `python3 scripts/replay.py --scenario samples/scenarios/btc_momentum_crash.json` first. "
            f"Missing: {', '.join(str(path.relative_to(ROOT)) for path in missing)}"
        )

    report = load_json(REPORT_PATH)
    summary = load_json(SUMMARY_PATH)
    manifest = load_json(MANIFEST_PATH)
    impact = report["impact_metrics"]

    file_hashes_match = True
    row_counts_match_manifest = True
    for meta in manifest["files"].values():
        path = ROOT / meta["path"]
        file_hashes_match = file_hashes_match and path.exists() and sha256(path) == meta["sha256"]
        if path.suffix == ".jsonl" and "rows" in meta:
            row_counts_match_manifest = row_counts_match_manifest and count_jsonl(path) == meta["rows"]

    trade_rows = manifest["files"]["trade_log"].get("rows", 0)
    api_rows = manifest["files"]["api_calls"].get("rows", 0)
    risk_event_rows = manifest["files"]["risk_events"].get("rows", 0)

    checks = [
        ("total intents", report["total_intents"] == 42),
        ("blocked high-risk intents", report["blocked"] == 22),
        ("warned elevated-risk intents", report["warned"] == 4),
        ("final equity improved", report["final_equity_with_guard"] > report["final_equity_without_guard"]),
        ("max drawdown reduced", report["max_drawdown_with_guard"] < report["max_drawdown_without_guard"]),
        ("audit records generated", impact["audit_records_generated"] >= 100),
        ("summary/report scenario match", summary["scenario_id"] == report["scenario_id"]),
        ("manifest/report scenario match", manifest["scenario_id"] == report["scenario_id"]),
        ("manifest hashes match files", file_hashes_match),
        ("manifest JSONL row counts match files", row_counts_match_manifest),
        ("trade log rows match total intents", trade_rows == report["total_intents"]),
        ("API log rows match total intents", api_rows == report["total_intents"]),
        ("risk event rows match warned + blocked", risk_event_rows == report["warned"] + report["blocked"]),
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
    print(f"Evidence manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print()
    print("Evidence file checks:")
    print(f"- trade log rows: {trade_rows}")
    print(f"- API log rows: {api_rows}")
    print(f"- risk event rows: {risk_event_rows}")
    print(f"- files hashed: {len(manifest['files'])}")
    print()
    print("Validation checks:")
    failed = False
    for name, ok in checks:
        marker = "PASS" if ok else "FAIL"
        print(f"- {marker}: {name}")
        failed = failed or not ok

    if failed:
        raise SystemExit(1)

    print()
    print("Result: PASS — GuardPilot reduced simulated drawdown, improved final equity, blocked high-risk intents, and generated hash-verifiable audit evidence for the deterministic replay.")


if __name__ == "__main__":
    main()
