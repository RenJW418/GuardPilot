from __future__ import annotations


class BitgetAdapter:
    """Build Bitget-compatible dry-run execution previews.

    GuardPilot's hackathon submission deliberately keeps real order forwarding off by
    default. This adapter is not an official Bitget order API client and never submits
    live orders; it documents the payload boundary that a production deployment could
    review before connecting to order-capable tooling.
    """

    def normalize_symbol(self, symbol: str) -> str:
        return symbol.upper().replace("-", "")

    def build_execution_payload(self, intent: dict) -> dict:
        return {
            "symbol": self.normalize_symbol(intent["symbol"]),
            "side": intent["side"],
            "orderType": intent.get("order_type", "MARKET"),
            "quantity": intent["quantity"],
            "size": intent["quantity"],
            "leverage": intent.get("leverage", 1),
            "clientTag": f"guardpilot:{intent.get('agent_id', 'agent')}",
            "auditReason": intent.get("reason", "GuardPilot approved intent"),
            "bitgetAgentSurface": {
                "tools": "Agent Hub trading APIs / order tools",
                "skills": "Skill Hub market context can be embedded in the Agent reason",
                "mcp": "MCP Server order calls should sit behind this risk decision",
                "playbook": "Playbook strategy output can be mapped to the same guarded intent",
            },
            "guardpilotPolicy": "ALLOW_OR_WARN_ONLY_DRY_RUN_NO_LIVE_ORDER",
        }

    def dry_run_forward_allowed_intent(self, intent: dict) -> dict:
        return {
            "status": "DRY_RUN_READY",
            "message": "GuardPilot generated a Bitget-compatible dry-run preview; live forwarding is intentionally disabled for safety.",
            "execution_payload": self.build_execution_payload(intent),
        }
