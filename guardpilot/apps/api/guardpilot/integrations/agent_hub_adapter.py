from __future__ import annotations


class AgentHubAdapter:
    """Maps Agent Hub / Playbook style outputs into GuardPilot trade intents."""

    def to_guardpilot_intent(self, payload: dict) -> dict:
        return {
            "timestamp": payload.get("timestamp"),
            "agent_id": payload.get("agent_id", "bitget_agent"),
            "symbol": payload.get("symbol", "BTCUSDT"),
            "side": payload.get("side", "BUY").upper(),
            "order_type": payload.get("order_type", "MARKET"),
            "quantity": payload.get("quantity", 0.01),
            "leverage": payload.get("leverage", 1),
            "confidence": payload.get("confidence", 0.5),
            "reason": payload.get("reason", "Agent Hub signal"),
        }
