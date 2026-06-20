from __future__ import annotations


class BitgetAdapter:
    """Dry-run contract for connecting GuardPilot to Bitget execution tools.

    GuardPilot's hackathon submission deliberately keeps real order forwarding off by
    default. This adapter documents the exact boundary: after an intent is ALLOWed by
    the risk engine, the same normalized payload can be handed to Bitget Agent Hub or
    Playbook execution tooling in a production deployment.
    """

    def normalize_symbol(self, symbol: str) -> str:
        return symbol.upper().replace("-", "")

    def build_execution_payload(self, intent: dict) -> dict:
        return {
            "symbol": self.normalize_symbol(intent["symbol"]),
            "side": intent["side"],
            "orderType": intent.get("order_type", "MARKET"),
            "quantity": intent["quantity"],
            "leverage": intent.get("leverage", 1),
            "clientTag": f"guardpilot:{intent.get('agent_id', 'agent')}",
            "auditReason": intent.get("reason", "GuardPilot approved intent"),
        }

    def dry_run_forward_allowed_intent(self, intent: dict) -> dict:
        return {
            "status": "DRY_RUN_READY",
            "message": "GuardPilot generated a Bitget-ready execution payload; live forwarding is intentionally opt-in for safety.",
            "execution_payload": self.build_execution_payload(intent),
        }
