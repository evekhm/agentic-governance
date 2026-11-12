"""RFC 8693 OBO token exchange and claim validation helpers for Track A & Track B."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
import jwt


@dataclass(frozen=True)
class OboTokenValidationResult:
    valid: bool
    reason: str
    claims: dict[str, Any] | None = None


def build_obo_claims(
    *,
    subject_email: str,
    actor_spiffe_id: str,
    audience: str,
    scope: str = "orders:read",
    ttl_seconds: int = 300,
    jwk_thumbprint: str | None = None,
    now: int | None = None,
) -> dict[str, Any]:
    """Constructs canonical Episode 01 Token_obo claims (aud, scp, act.sub, 5-min TTL)."""
    issued_at = now if now is not None else int(time.time())
    claims: dict[str, Any] = {
        "sub": subject_email,
        "email": subject_email,
        "aud": audience,
        "scp": scope,
        "act": {"sub": actor_spiffe_id},
        "iat": issued_at,
        "exp": issued_at + ttl_seconds,
    }
    if jwk_thumbprint:
        claims["cnf"] = {"jkt": jwk_thumbprint}
    return claims


def validate_obo_claims(
    claims: dict[str, Any],
    *,
    expected_audience: str,
    required_scope: str,
    expected_actor_prefix: str = "spiffe://",
    now: int | None = None,
) -> OboTokenValidationResult:
    """Rejects Token_in passthrough, cross-service replay, expired tokens, and missing act.sub."""
    current = now if now is not None else int(time.time())
    if claims.get("aud") != expected_audience:
        return OboTokenValidationResult(False, f"audience mismatch: {claims.get('aud')} != {expected_audience}")
    scopes = set(str(claims.get("scp", "")).split())
    if required_scope not in scopes:
        return OboTokenValidationResult(False, f"missing scope {required_scope}")
    act_sub = (claims.get("act") or {}).get("sub", "")
    if not str(act_sub).startswith(expected_actor_prefix):
        return OboTokenValidationResult(False, "missing or invalid act.sub claim")
    exp = int(claims.get("exp", 0))
    if exp <= current:
        return OboTokenValidationResult(False, "token expired")
    if exp - int(claims.get("iat", current)) > 300:
        return OboTokenValidationResult(False, "token lifetime exceeds 300s ceiling")
    return OboTokenValidationResult(True, "ok", claims=claims)


def decode_jwt_unverified_redacted(token: str) -> dict[str, Any]:
    """Returns JWT header and claims without signature for trace_schema.json export."""
    header = jwt.get_unverified_header(token)
    claims = jwt.decode(token, options={"verify_signature": False})
    return {"header": header, "claims": claims, "signature": "<REDACTED>"}
