"""Vulnerable baseline agent (prototype project only) demonstrating T1-T8 failure modes."""

from __future__ import annotations

from typing import Callable
from google.adk.agents import LlmAgent


def make_naive_execute_sql_tool(sql_runner: Callable[[str], list[dict]]) -> Callable[[str, str], list[dict]]:
    """Intentionally vulnerable tool: accepts raw SQL and in-band user_id from the LLM."""

    def execute_sql(sql: str, user_id: str = "alice") -> list[dict]:
        _ = user_id
        return sql_runner(sql)

    return execute_sql


def build_naive_agent(
    sql_runner: Callable[[str], list[dict]],
    model: object = "gemini-3.8-flash",
) -> LlmAgent:
    """Prototype agent with raw execute_sql, no quarantine, and no screening."""
    return LlmAgent(
        name="naive_orders_agent",
        model=model,
        tools=[make_naive_execute_sql_tool(sql_runner)],
        instruction=(
            "You are an orders assistant. Call execute_sql(sql, user_id) to answer questions "
            "or issue refunds directly."
        ),
    )
