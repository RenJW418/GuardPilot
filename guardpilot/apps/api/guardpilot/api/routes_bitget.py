from __future__ import annotations

from fastapi import APIRouter

from guardpilot.integrations.agent_hub_adapter import AgentHubAdapter
from guardpilot.integrations.bitget_adapter import BitgetAdapter
from guardpilot.models.intent import TradeIntent

router = APIRouter(prefix="/api/v1/bitget", tags=["bitget"])
_agent_hub_adapter = AgentHubAdapter()
_bitget_adapter = BitgetAdapter()


@router.post("/dry-run")
def bitget_dry_run(payload: dict) -> dict:
    """Convert an Agent Hub / Playbook style signal into a Bitget-ready dry-run payload.

    This endpoint does not place live orders. It makes the GuardPilot -> Bitget
    execution boundary explicit for hackathon review and safety testing.
    """
    intent_payload = _agent_hub_adapter.to_guardpilot_intent(payload)
    intent = TradeIntent(**intent_payload)
    return {
        "guardpilot_intent": intent.model_dump(mode="json"),
        "bitget_dry_run": _bitget_adapter.dry_run_forward_allowed_intent(intent.model_dump(mode="json")),
        "live_forwarding": "opt_in_disabled_for_hackathon_submission",
    }
