"""Out-of-band MCP client header provider and opaque handle capability pattern."""

from __future__ import annotations

import os
from typing import Callable

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext


def make_mcp_obo_header_provider(
    target_audience: str,
    scope: str,
    exchange_fn: Callable[[str, str, str], str] | None = None,
) -> Callable[[ReadonlyContext], dict[str, str]]:
    """Builds an out-of-band header_provider reading auth:subject_token from SessionService."""

    def mcp_obo_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
        subject_token = readonly_context.state.get("auth:subject_token")
        if not subject_token:
            raise PermissionError("Missing verified subject_token in server-side SessionService")
        token = (
            exchange_fn(subject_token, target_audience, scope)
            if exchange_fn is not None
            else subject_token
        )
        headers = {"Authorization": f"Bearer {token}"}
        traceparent = readonly_context.state.get("trace:traceparent")
        if traceparent:
            headers["X-Request-Trace-Id"] = traceparent
            headers["traceparent"] = traceparent
        return headers

    return mcp_obo_header_provider


def build_orders_read_toolset(
    url: str | None = None,
    exchange_fn: Callable[[str, str, str], str] | None = None,
) -> McpToolset:
    mcp_url = url or os.environ.get("MCP_READ_URL", "https://orders-read-mcp.internal/mcp")
    audience = os.environ.get("MCP_READ_AUDIENCE", "https://orders-read-mcp.internal")
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=mcp_url),
        header_provider=make_mcp_obo_header_provider(
            target_audience=audience,
            scope="orders:read",
            exchange_fn=exchange_fn,
        ),
    )


def build_orders_write_toolset(
    url: str | None = None,
    exchange_fn: Callable[[str, str, str], str] | None = None,
) -> McpToolset:
    mcp_url = url or os.environ.get("MCP_WRITE_URL", "https://orders-write-mcp.internal/mcp")
    audience = os.environ.get("MCP_WRITE_AUDIENCE", "https://orders-write-mcp.internal")
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=mcp_url),
        header_provider=make_mcp_obo_header_provider(
            target_audience=audience,
            scope="orders:write",
            exchange_fn=exchange_fn,
        ),
    )


def store_opaque_handle(
    order_id: str,
    raw_row: dict,
    tool_context: ToolContext,
) -> dict[str, str]:
    """Opaque handle pattern: stores sensitive fields in SessionService, returns handle only."""
    handle = f"tax_ref_{order_id}"
    tool_context.state[f"temp:{handle}"] = raw_row
    return {"status": "READY", "tax_handle": handle}
