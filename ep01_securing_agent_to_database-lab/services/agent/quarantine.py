"""Quarantine LLM pattern (L3): zero tools, strict enum/bool output_schema, severed history."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel
from google.adk.agents import LlmAgent
from google.genai.types import ThinkingConfig


class DropoffLocation(str, Enum):
    FRONT_DOOR = "FRONT_DOOR"
    SIDE_GATE = "SIDE_GATE"
    MAILROOM = "MAILROOM"
    LOCKER = "LOCKER"


class SafeNoteSummary(BaseModel):
    dropoff: DropoffLocation
    requires_signature: bool


def build_quarantine_note_parser(model: object = "gemini-3.8-flash") -> LlmAgent:
    """Quarantine LLM: zero tools, strict enum/boolean schema, and include_contents='none'."""
    return LlmAgent(
        name="quarantine_note_parser",
        model=model,
        include_contents="none",
        generate_content_config={"thinking_config": ThinkingConfig(thinking_level="LOW")},
        tools=[],
        output_schema=SafeNoteSummary,
        output_key="clean_note",
        instruction="Classify the delivery note into the schema: {raw_delivery_note}",
    )


def build_privileged_order_responder(model: object = "gemini-3.8-flash") -> LlmAgent:
    """Privileged orchestrator consuming only the validated Quarantine struct with severed history."""
    return LlmAgent(
        name="privileged_order_responder",
        model=model,
        include_contents="none",
        generate_content_config={"thinking_config": ThinkingConfig(thinking_level="LOW")},
        instruction="Answer the user's question for order {order_id} using verified note summary: {clean_note}",
    )
