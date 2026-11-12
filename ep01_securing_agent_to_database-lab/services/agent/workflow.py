"""Governed ADK 2.x Workflow + HITL Approval Card + Deterministic Idempotency Key (L8)."""

from __future__ import annotations

import uuid
from pydantic import BaseModel, Field
from google.adk import Workflow
from google.adk.agents import LlmAgent
from google.genai.types import ThinkingConfig
from services.agent.app import write_session_state


class RefundProposal(BaseModel):
    order_id: str = Field(pattern=r"^ORD-[0-9]{3,8}$")
    amount_usd: float = Field(gt=0, le=500.0)
    reason_code: str = Field(pattern=r"^(DAMAGED|LATE_DELIVERY|WRONG_ITEM)$")


def build_refund_planner(model: object = "gemini-3.8-flash") -> LlmAgent:
    """Single-turn model node: proposes structured parameters only; cannot execute writes directly."""
    return LlmAgent(
        name="refund_planner",
        model=model,
        include_contents="none",
        generate_content_config={"thinking_config": ThinkingConfig(thinking_level="LOW")},
        output_schema=RefundProposal,
        output_key="refund_proposal",
        instruction="Extract the requested order_id, amount_usd, and reason_code from the user request.",
    )


def build_hitl_card(state: dict, proposal: RefundProposal) -> dict:
    """Deterministic code node: builds approval payload from verified session state + proposal."""
    verified_caller = state.get("user:id") or state.get("user:verified_email")
    if not verified_caller:
        raise PermissionError("Missing verified caller identity in server-side SessionService")
    idem_key = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{verified_caller}:{proposal.order_id}:refund"))
    pending_payload = {
        "verified_caller": verified_caller,
        "order_id": proposal.order_id,
        "amount_usd": proposal.amount_usd,
        "reason_code": proposal.reason_code,
        "idempotency_key": idem_key,
    }
    write_session_state(state, "pending_write", pending_payload, writer="control_plane")
    return state["pending_write"]


def build_orders_workflow(model: object = "gemini-3.8-flash") -> Workflow:
    """Builds the governed single-turn orders workflow."""
    planner_node = build_refund_planner(model=model)
    return Workflow(
        name="governed_orders_agent",
        edges=[("start", planner_node)],
    )
