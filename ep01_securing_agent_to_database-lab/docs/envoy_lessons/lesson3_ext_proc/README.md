# Lesson 3: `ext_proc` Header Mutation (`L2` / `L5`)

## Goal
See how `envoy.filters.http.ext_proc` pauses an outgoing request, calls our real [ext_proc_server.py](../../../services/envoy_sidecar/ext_proc_server.py) over HTTP/2 gRPC, and rewrites `Authorization` **outside** the client process (the exact same `REQUEST_HEADERS` pattern used by Track A's sidecar and Track B's `AgentGateway` `AuthzExtension`).

## Run

```bash
docker compose up -d --build

curl -s -H "Host: orders-read-mcp.internal" \
  -H "x-user-token: alice-jwt" \
  -H "Authorization: Bearer ORIGINAL_AGENT_TOKEN" \
  http://localhost:10002/mcp
```

## What to Observe
- Even though the client sent `Authorization: Bearer ORIGINAL_AGENT_TOKEN`, `echo` receives:
  - `"authorization": "Bearer OBO_..."`
  - `"x-ext-proc-user-token-seen": "yes"`
- Notice `processing_mode` in [envoy.yaml](envoy.yaml): `request_header_mode: SEND` and `request_body_mode: NONE`, matching the `REQUEST_AUTHZ` profile that worked on `AgentGateway`.
- Notice `failure_mode_allow: false` (fail-closed): if you run `docker compose stop ext-proc-upstream`, Envoy returns `500` rather than letting unscreened/unexchanged traffic pass.

## Clean Up

```bash
docker compose down
```
