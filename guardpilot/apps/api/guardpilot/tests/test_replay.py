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
