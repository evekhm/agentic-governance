"""Shared ADK App entrypoint, W3C traceparent helper, and trace_schema.json event builder."""

from __future__ import annotations

from datetime import datetime, timezone
import secrets
from typing import Any


def new_traceparent() -> tuple[str, str]:
    """Generates a W3C traceparent header (`00-<trace_id>-<span_id>-01`) and returns (trace_id, header)."""
    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return trace_id, f"00-{trace_id}-{span_id}-01"


def build_trace_event(
    *,
    trace_id: str,
    component: str,
    layer: str,
    threat: str,
    track: str,
    model_mode: str,
    verdict: str,
    payload: dict[str, Any],
    span_id: str | None = None,
) -> dict[str, Any]:
    """Builds a versioned trace event conforming to `attacks/trace_schema.json`."""
    return {
        "schema_version": "1.0.0",
        "trace_id": trace_id,
        "span_id": span_id or secrets.token_hex(8),
        "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "component": component,
        "layer": layer,
        "threat": threat,
        "track": track,
        "model_mode": model_mode,
        "verdict": verdict,
        "payload": payload,
    }
