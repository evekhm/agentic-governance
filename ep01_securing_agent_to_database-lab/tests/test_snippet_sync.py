"""Verifies that Episode 01 HTML snippets remain aligned with tested lab code."""

from __future__ import annotations

from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parent
EPISODE_HTML = REPO_ROOT / "ep01_securing_agent_to_database.html"


def test_episode_html_snippets_match_lab_symbols() -> None:
    html = EPISODE_HTML.read_text(encoding="utf-8")

    # Stage 3: tools.read.yaml uses authServices + agent_orders_v
    assert "authServices" in html
    tools_read = (LAB_ROOT / "config" / "tools.read.yaml").read_text(encoding="utf-8")
    assert "authServices:" in tools_read and "sales.agent_orders_v" in tools_read

    # Stage 5: Postgres FORCE ROW LEVEL SECURITY + security_invoker + BigQuery SESSION_USER()
    pg_rls = (LAB_ROOT / "db" / "postgres" / "03_rls_and_procs.sql").read_text(encoding="utf-8")
    pg_views = (LAB_ROOT / "db" / "postgres" / "02_views_and_roles.sql").read_text(encoding="utf-8")
    bq_rls = (LAB_ROOT / "db" / "bigquery" / "02_row_access_policy.sql").read_text(encoding="utf-8")
    assert "FORCE ROW LEVEL SECURITY" in pg_rls and "FORCE" in html
    assert "security_invoker = true" in pg_views and "security_invoker" in html
    assert "SESSION_USER()" in bq_rls and "SESSION_USER()" in html

    # Stage 8/10: normalize_for_screening + Quarantine SafeNoteSummary + include_contents="none"
    callbacks = (LAB_ROOT / "services" / "agent" / "callbacks.py").read_text(encoding="utf-8")
    quarantine = (LAB_ROOT / "services" / "agent" / "quarantine.py").read_text(encoding="utf-8")
    assert "def normalize_for_screening" in callbacks and "normalize_for_screening" in html
    assert "class SafeNoteSummary" in quarantine and "SafeNoteSummary" in html
    assert 'include_contents="none"' in quarantine and "include_contents" in html

    # Stage 13: chain_of_custody.sql trace_id join
    coc = (LAB_ROOT / "db" / "bigquery" / "03_chain_of_custody.sql").read_text(encoding="utf-8")
    assert "agent_tool_turns" in coc and "db_data_access" in coc
    assert "agent_tool_turns" in html and "db_data_access" in html
