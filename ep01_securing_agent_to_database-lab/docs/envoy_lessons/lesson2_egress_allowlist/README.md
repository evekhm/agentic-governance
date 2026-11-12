# Lesson 2: Egress Domain Allowlist & Default-Deny (`L6`)

**Estimated time:** 10 minutes  
**Episode 01 context:** [Stage 9 (Network Egress & PSC)](../../../ep01_securing_agent_to_database.html#part-09) · Track A [envoy-egress.yaml](../../../services/envoy_sidecar/envoy-egress.yaml)

---

## Concept: Why Default-Deny Matters (`T6` Exfiltration)

If an agent is tricked by a poisoned database row (`T2`) into calling `POST https://attacker.example/exfil`, application-level prompt instructions will not stop it. **Defense Layer `L6`** places an egress proxy in front of the agent that **denies every destination by default** and only forwards traffic to explicitly allowlisted MCP servers.

In Envoy, you implement this with **ordered `virtual_hosts`** inside `route_config`:
1. **First `virtual_host` (`allowed_mcp`):** Matches `domains: ["orders-read-mcp.internal", ...]` and forwards to `cluster: echo_service`.
2. **Fallback `virtual_host` (`deny_all_unregistered`):** Matches `domains: ["*"]` and returns `direct_response: { status: 403 }` immediately inside Envoy—no connection is ever opened to the upstream internet.

In **Track B**, Google-managed `AgentGateway` does the exact same thing using **Agent Registry + `AuthzPolicy`** (`default_denied` in Cloud Logging).

---

## Run

```bash
cd docs/envoy_lessons/lesson2_egress_allowlist
docker compose up -d

# 1. Allowed registered MCP destination -> 200 OK
curl -i -H "Host: orders-read-mcp.internal" http://localhost:10001/mcp

# 2. Unregistered destination (T6 exfiltration attempt) -> 403 Forbidden
curl -i -H "Host: attacker.example" http://localhost:10001/exfil
```

## What to Observe & Self-Check

- Request 1 reaches `echo-upstream` (`HTTP/1.1 200 OK`).
- Request 2 returns `HTTP/1.1 403 Forbidden` with body `Blocked by L6 default-deny egress allowlist` directly from Envoy (`server: envoy`).
- **Check:** Why must `deny_all_unregistered` (`domains: ["*"]`) come *after* `allowed_mcp`?  
  *(Answer: Envoy evaluates `domains` most-specifically, and keeping the wildcard fallback last makes the default-deny policy explicit and easy to audit.)*

## Clean Up

```bash
docker compose down -t 1
```
