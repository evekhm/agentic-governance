# Lesson 2: Egress Domain Allowlist & Default-Deny (`L6`)

## Goal
See how Envoy's `virtual_hosts` implement Episode 01's `L6` egress boundary: allow registered MCP domains and reject any other destination (`attacker.example`) with `HTTP 403` before any packet leaves the pod.

## Run

```bash
docker compose up -d

# 1. Allowed destination -> 200 OK
curl -i -H "Host: orders-read-mcp.internal" http://localhost:10001/mcp

# 2. Unregistered destination (T6 exfiltration attempt) -> 403 Forbidden
curl -i -H "Host: attacker.example" http://localhost:10001/exfil
```

## What to Observe
- `orders-read-mcp.internal` matches `virtual_hosts[0]` and reaches `echo`.
- `attacker.example` falls through to `domains: ["*"]` and triggers `direct_response: 403`.
- Compare [envoy.yaml](envoy.yaml) with Track A's [envoy-egress.yaml](../../../services/envoy_sidecar/envoy-egress.yaml) and Track B's `AgentGateway` `default_denied`.

## Clean Up

```bash
docker compose down
```
