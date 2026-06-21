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


def test_bitget_dry_run_route_risk_blocks_dangerous_payload():
    payload = {
        "timestamp": "2026-06-20T10:08:00Z",
        "agent_id": "risky_agenthub_agent",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.2,
        "leverage": 10,
        "confidence": 0.2,
        "reason": "Aggressively increasing leverage after losses",
        "price_hint": 65000,
    }
    response = client.post("/api/v1/bitget/dry-run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_decision"] == "BLOCK"
    assert data["forwarding_status"] == "BLOCKED_BY_GUARDPILOT"
    assert data["bitget_dry_run"] is None
    assert any(check["status"] == "fail" for check in data["checks"])
