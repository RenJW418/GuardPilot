from __future__ import annotations


class AgentHubAdapter:
    """Maps Bitget Agent Hub / Playbook style outputs into GuardPilot intents.

    The hackathon requirements describe Bitget Agent Hub-style capabilities: Tools,
    Skill Hub context, and MCP Server boundaries. Playbook can also emit a strategy
    signal. GuardPilot accepts that combined signal shape and keeps source metadata
    for audit while normalizing only the fields needed by the risk engine.
    """

    def to_guardpilot_intent(self, payload: dict) -> dict:
        source = payload.get("source", "Bitget Agent Hub / Playbook style signal")
        skill_context = payload.get("skill_context") or payload.get("skill") or payload.get("signal_source")
        reason = payload.get("reason", "Agent Hub signal")
        if skill_context:
            reason = f"{reason} | Bitget context: {skill_context}"
        return {
            "timestamp": payload.get("timestamp"),
            "agent_id": payload.get("agent_id", "bitget_agent"),
            "symbol": payload.get("symbol", "BTCUSDT"),
            "side": payload.get("side", "BUY").upper(),
            "order_type": payload.get("order_type", "MARKET"),
            "quantity": payload.get("quantity", 0.01),
            "leverage": payload.get("leverage", 1),
            "confidence": payload.get("confidence", 0.5),
            "reason": f"{source} | {reason}",
        }
