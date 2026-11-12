"""Exports redacted replay bundles and fails if any sensitive pattern remains."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LEFTOVER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("jwt_signature", re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("private_ipv4", re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
    ("ssn_pattern", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("internal_domain", re.compile(r"\b[a-z0-9-]+\.(internal|run\.app)\b")),
)


def redact_trace_event(
    event: dict[str, Any],
    extra_literals: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Deep-copies and redacts project IDs, domains, IPs, and JWT signatures from an event."""
    raw = json.dumps(event)
    for lit in extra_literals:
        if lit:
            raw = raw.replace(lit, "<REDACTED>")
    raw = re.sub(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "10.0.0.x", raw)
    raw = re.sub(
        r"(eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.)[A-Za-z0-9_-]{8,}",
        r"\1<REDACTED_SIG>",
        raw,
    )
    raw = re.sub(r"\b[a-z0-9-]+\.(internal|run\.app)\b", "<REDACTED_HOST>", raw)
    return json.loads(raw)


def assert_no_leftover_secrets(bundle: list[dict[str, Any]], extra_literals: tuple[str, ...] = ()) -> None:
    """Raises ValueError if any secret, raw IP, internal host, or JWT signature remains."""
    serialized = json.dumps(bundle)
    for label, pattern in LEFTOVER_PATTERNS:
        match = pattern.search(serialized)
        if match:
            raise ValueError(f"Leftover pattern detected ({label}): {match.group(0)}")
    for lit in extra_literals:
        if lit and lit in serialized:
            raise ValueError(f"Leftover literal detected: {lit}")


def export_trace_bundle(
    events: list[dict[str, Any]],
    output_path: Path,
    extra_literals: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    redacted = [redact_trace_event(ev, extra_literals=extra_literals) for ev in events]
    assert_no_leftover_secrets(redacted, extra_literals=extra_literals)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(redacted, indent=2), encoding="utf-8")
    return redacted
