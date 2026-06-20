from __future__ import annotations

from pathlib import Path

from guardpilot.core.replay_engine import ReplayEngine


def test_replay_generates_auditable_outputs():
    root = Path(__file__).resolve().parents[4]
    summary = ReplayEngine(root).run("samples/scenarios/btc_momentum_crash.json")
    assert summary["total_intents"] >= 1
    assert summary["allowed"] >= 1
    assert summary["blocked"] >= 1
    assert (root / summary["report_path"]).exists()
    assert (root / "samples" / "outputs" / "sample_api_calls.jsonl").exists()
