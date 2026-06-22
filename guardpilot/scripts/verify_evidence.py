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


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


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
    data_provenance = manifest.get("data_provenance", {})

    file_hashes_match = True
    row_counts_match_manifest = True
    for key, meta in manifest["files"].items():
        path = ROOT / meta["path"]
        file_hashes_match = file_hashes_match and path.exists() and sha256(path) == meta["sha256"]
        if path.suffix == ".jsonl" and "rows" in meta:
            row_counts_match_manifest = row_counts_match_manifest and count_jsonl(path) == meta["rows"]
        if path.suffix == ".csv" and "rows" in meta:
            row_counts_match_manifest = row_counts_match_manifest and count_csv_rows(path) == meta["rows"]

    trade_rows = manifest["files"]["trade_log"].get("rows", 0)
    api_rows = manifest["files"]["api_calls"].get("rows", 0)
    risk_event_rows = manifest["files"]["risk_events"].get("rows", 0)
    market_file_meta = manifest["files"].get("market_data", {})
    market_provenance_meta = manifest["files"].get("market_data_provenance")
    market_provenance = {}
    if market_provenance_meta:
        market_provenance = load_json(ROOT / market_provenance_meta["path"])

    checks = [
        ("total intents present", report["total_intents"] >= 1),
        ("at least one blocked high-risk intent", report["blocked"] >= 1),
        ("final equity improved", report["final_equity_with_guard"] > report["final_equity_without_guard"]),
        ("max drawdown reduced", report["max_drawdown_with_guard"] < report["max_drawdown_without_guard"]),
        ("audit records generated", impact["audit_records_generated"] >= report["total_intents"] * 2),
        ("summary/report scenario match", summary["scenario_id"] == report["scenario_id"]),
        ("manifest/report scenario match", manifest["scenario_id"] == report["scenario_id"]),
        ("manifest hashes match files", file_hashes_match),
        ("manifest row counts match files", row_counts_match_manifest),
        ("trade log rows match total intents", trade_rows == report["total_intents"]),
        ("API log rows match total intents", api_rows == report["total_intents"]),
        ("risk event rows match warned + blocked", risk_event_rows == report["warned"] + report["blocked"]),
        ("Bitget public market provenance present", data_provenance.get("market_data_source") == "Bitget public market API snapshot"),
        ("paper trading only", data_provenance.get("execution_mode") == "paper_trading_only" and data_provenance.get("live_orders") is False),
        ("market provenance file included", market_provenance_meta is not None),
        ("market CSV hash matches provenance", bool(market_provenance) and market_provenance.get("sha256") == market_file_meta.get("sha256")),
        ("market provenance source is Bitget public API", market_provenance.get("source") == "Bitget public market API"),
    ]

    print("GuardPilot Evidence Verification")
    print("================================")
    print(f"Scenario: {report['scenario_id']}")
    print(f"Data source: {data_provenance.get('market_data_source', 'unknown')}")
    print(f"Market file: {data_provenance.get('market_data_file', 'unknown')}")
    print(f"Market range: {data_provenance.get('market_time_start', 'unknown')} -> {data_provenance.get('market_time_end', 'unknown')}")
    print(f"Execution mode: {data_provenance.get('execution_mode', 'unknown')} · live_orders={data_provenance.get('live_orders')}")
    print()
    print(f"Total intents: {report['total_intents']}")
    print(f"Allowed / Warned / Blocked: {report['allowed']} / {report['warned']} / {report['blocked']}")
    print(f"Blocked intent rate: {pct(impact['blocked_intent_rate'])}")
    print()
    print(f"Final equity without guard: {report['final_equity_without_guard']:.2f} USDT")
    print(f"Final equity with GuardPilot: {report['final_equity_with_guard']:.2f} USDT")
    print(f"Equity improvement: {impact['equity_improvement_usdt']:+.2f} USDT")
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
    print(f"- market sha256: {market_file_meta.get('sha256', 'unknown')}")
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
    print(
        "Result: PASS — GuardPilot replay uses a hash-verifiable Bitget public market snapshot, "
        "keeps execution paper-only, blocks high-risk intents, and regenerates auditable evidence."
    )


if __name__ == "__main__":
    main()
