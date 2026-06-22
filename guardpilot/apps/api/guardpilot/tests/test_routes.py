from __future__ import annotations

from fastapi.testclient import TestClient

from guardpilot.main import app


client = TestClient(app)


def test_core_routes_are_registered():
    assert client.get("/health").status_code == 200
    assert client.post("/api/v1/replay").status_code == 200


def test_replay_rejects_path_traversal_query():
    response = client.post("/api/v1/replay", params={"scenario": "../../README.md"})
    assert response.status_code == 400


def test_intents_route_uses_bitget_snapshot_without_price_hint():
    payload = {
        "timestamp": "2026-06-22T16:10:00Z",
        "agent_id": "snapshot_route_test_agent",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.005,
        "leverage": 1,
        "confidence": 0.82,
        "reason": "Small paper order should use committed Bitget public snapshot context",
    }
    response = client.post("/api/v1/intents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["market_context"]["source"] == "Bitget public market API snapshot"
    assert data["market_context"]["price_source"] == "bitget_public_snapshot_close"
    assert data["execution_mode"] == "paper_trading_only"


def test_intents_route_rejects_unsupported_symbol_without_fake_price():
    payload = {
        "timestamp": "2026-06-22T16:10:00Z",
        "agent_id": "unsupported_symbol_agent",
        "symbol": "DOGEUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.005,
        "leverage": 1,
        "confidence": 0.82,
        "reason": "Unsupported symbols should not fall back to fake prices",
    }
    response = client.post("/api/v1/intents", json=payload)
    assert response.status_code == 400
    assert "No Bitget public market snapshot rows" in response.json()["detail"]


def test_bitget_dry_run_route_risk_blocks_dangerous_payload():
    payload = {
        "timestamp": "2026-06-22T16:08:00Z",
        "agent_id": "risky_agenthub_agent",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.2,
        "leverage": 10,
        "confidence": 0.2,
        "reason": "Aggressively increasing leverage after losses",
    }
    response = client.post("/api/v1/bitget/dry-run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_decision"] == "BLOCK"
    assert data["forwarding_status"] == "BLOCKED_BY_GUARDPILOT"
    assert data["bitget_dry_run"] is None
    assert data["market_context"]["source"] == "Bitget public market API snapshot"
    assert data["execution_mode"] == "paper_trading_only"
    assert data["live_forwarding"]["enabled"] is False
    assert any(check["status"] == "fail" for check in data["checks"])


def test_bitget_dry_run_route_returns_payload_for_safe_agenthub_signal():
    payload = {
        "source": "Bitget Agent Hub / Playbook style signal",
        "skill_context": "technical-analysis confirmed low-volatility continuation",
        "timestamp": "2026-06-22T16:15:00Z",
        "agent_id": "safe_agenthub_agent",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.005,
        "leverage": 1,
        "confidence": 0.82,
        "reason": "Small conservative test order",
    }
    response = client.post("/api/v1/bitget/dry-run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_decision"] in {"ALLOW", "WARN"}
    assert data["forwarding_status"] == "DRY_RUN_READY_NO_LIVE_ORDER_PLACED"
    assert data["bitget_dry_run"]["status"] == "DRY_RUN_READY"
    assert data["market_context"]["source"] == "Bitget public market API snapshot"
    assert data["live_forwarding"]["enabled"] is False
    execution_payload = data["bitget_dry_run"]["execution_payload"]
    assert execution_payload["symbol"] == "BTCUSDT"
    assert execution_payload["size"] == payload["quantity"]
    assert execution_payload["guardpilotPolicy"] == "ALLOW_OR_WARN_ONLY_DRY_RUN_NO_LIVE_ORDER"
