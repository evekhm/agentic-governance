# Lesson 3: `ext_proc` Header Mutation (`L2` / `L5`)

**Estimated time:** 15 minutes  
**Episode 01 context:** [Stage 6 (Token Exchange)](../../../ep01_securing_agent_to_database.html#part-06) · [Stage 8 (Screening)](../../../ep01_securing_agent_to_database.html#part-08) · [01 · Gateway Spike](../../01_GATEWAY_INJECTION_SPIKE.md)

---

## Concept: Out-of-Process Inspection & Token Translation

In **Track A** and **Track B**, we want **credentials (`Token_obo`) and safety screening (`Model Armor` / `Cloud SDP`) to stay outside the agent container**. Envoy's `envoy.filters.http.ext_proc` filter makes this possible:

1. Envoy places `ext_proc` **before** `envoy.filters.http.router` in `http_filters`.
2. When a request arrives, Envoy opens a **bidirectional HTTP/2 gRPC stream** to `ext-proc-upstream:8080` (running our real [ext_proc_server.py](../../../services/envoy_sidecar/ext_proc_server.py)).
3. Because `processing_mode` sets `request_header_mode: SEND` and `request_body_mode: NONE`, Envoy sends `request_headers` only (matching the `REQUEST_AUTHZ` profile we verified on `AgentGateway`).
4. `ext_proc_server.py` reads `x-user-token`, computes a new `Authorization` header, and returns a `HeaderMutation` (`OVERWRITE_IF_EXISTS_OR_ADD`). Envoy applies the mutation and forwards the request to `echo-upstream`.

> **Fail-Closed (`failure_mode_allow: false`):** If `ext-proc-upstream` is down or times out, Envoy rejects the request with `500` rather than letting unauthenticated or unscreened traffic pass.

---

## Run

```bash
cd docs/envoy_lessons/lesson3_ext_proc
docker compose up -d --build

curl -s -H "Host: orders-read-mcp.internal" \
  -H "x-user-token: alice-jwt" \
  -H "Authorization: Bearer ORIGINAL_AGENT_TOKEN" \
  http://localhost:10002/mcp
```

Expected `headers_received` at `echo-upstream`:
- `"authorization": "Bearer OBO_<hash>"` (the client's `ORIGINAL_AGENT_TOKEN` was replaced outside the client)
- `"x-ext-proc-user-token-seen": "yes"`

Now test **fail-closed** behavior:

```bash
docker compose stop ext-proc-upstream
curl -i -H "Host: orders-read-mcp.internal" http://localhost:10002/mcp
# Expect HTTP/1.1 500 Internal Server Error
```

## Clean Up

```bash
docker compose down -t 1
```
