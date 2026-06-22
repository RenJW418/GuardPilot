from __future__ import annotations

import json
from pathlib import Path

import pytest

from guardpilot.core.replay_engine import ReplayEngine


ROOT = Path(__file__).resolve().parents[4]


def test_replay_generates_auditable_outputs():
    summary = ReplayEngine(ROOT).run("samples/scenarios/btc_momentum_crash.json")
    assert summary["total_intents"] >= 1
    assert summary["allowed"] >= 1
    assert summary["blocked"] >= 1
    assert summary["data_provenance"]["market_data_source"] == "Bitget public market API snapshot"
    assert summary["data_provenance"]["execution_mode"] == "paper_trading_only"
    assert summary["data_provenance"]["live_orders"] is False
    assert (ROOT / summary["report_path"]).exists()
    assert (ROOT / summary["evidence_manifest_path"]).exists()
    assert (ROOT / "samples" / "outputs" / "sample_api_calls.jsonl").exists()


def test_replay_rejects_absolute_and_escaping_paths():
    engine = ReplayEngine(ROOT)
    with pytest.raises(ValueError):
        engine.run("/etc/passwd")
    with pytest.raises(ValueError):
        engine.run("../README.md")


def test_replay_manifest_counts_match_report():
    summary = ReplayEngine(ROOT).run("samples/scenarios/btc_momentum_crash.json")
    report = json.loads((ROOT / summary["report_path"]).read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / summary["evidence_manifest_path"]).read_text(encoding="utf-8"))

    assert manifest["scenario_id"] == report["scenario_id"]
    assert manifest["totals"]["total_intents"] == report["total_intents"]
    assert manifest["files"]["trade_log"]["rows"] == report["total_intents"]
    assert manifest["files"]["api_calls"]["rows"] == report["total_intents"]
    assert manifest["files"]["risk_events"]["rows"] == report["warned"] + report["blocked"]
    assert manifest["files"]["market_data_provenance"]["path"] == "samples/market/bitget_btcusdt_1m.provenance.json"
    assert manifest["data_provenance"]["market_sha256"] == manifest["files"]["market_data"]["sha256"]


def test_replay_requires_explicit_inputs(tmp_path: Path):
    scenario = {
        "scenario_id": "missing_input",
        "initial_balance": 10000,
        "market_data": "samples/market/not-present.csv",
        "agent_signals": "samples/agents/not-present.jsonl",
        "risk_profile": "configs/risk_profiles/default.yaml",
        "outputs": {
            "trade_log": "samples/outputs/tmp_trade_log.jsonl",
            "api_calls": "samples/outputs/tmp_api_calls.jsonl",
            "risk_report": "samples/outputs/tmp_risk_report.json",
            "risk_events": "samples/outputs/tmp_risk_events.jsonl",
            "summary": "samples/outputs/tmp_summary.json",
        },
    }
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text(json.dumps(scenario), encoding="utf-8")
    with pytest.raises(ValueError):
        ReplayEngine(ROOT).run(scenario_path)


def test_replay_order_ids_are_stable_within_same_process():
    engine = ReplayEngine(ROOT)
    first = engine.run("samples/scenarios/btc_momentum_crash.json")
    first_trade_log = (ROOT / first["risk_report"]["trade_log_path"]).read_text(encoding="utf-8")

    second = engine.run("samples/scenarios/btc_momentum_crash.json")
    second_trade_log = (ROOT / second["risk_report"]["trade_log_path"]).read_text(encoding="utf-8")

    assert first_trade_log == second_trade_log
