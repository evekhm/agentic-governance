# Lesson 1: Listener → HttpConnectionManager → Router → Cluster

**Estimated time:** 10 minutes  
**Episode 01 context:** [Stage 6](../../../ep01_securing_agent_to_database.html#part-06) · [Envoy & Agent Gateway Mechanics](../../02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md)

---

## Concept: How Envoy Handles a Request

Every Envoy configuration follows a four-stage pipeline from left to right:

1. **Listener (`listeners[0]`):** Binds a TCP socket (`0.0.0.0:10000`) and waits for connections.
2. **Network Filter (`HttpConnectionManager`):** Parses raw TCP bytes into HTTP/1.1 or HTTP/2 requests (`:method`, `:path`, `Host`, headers).
3. **HTTP Filter Chain (`http_filters`):** Runs ordered filters on each HTTP request. In this baseline lesson there is only the terminal `envoy.filters.http.router` filter, which evaluates `route_config` (`virtual_hosts` → `routes`) to pick an upstream cluster.
4. **Cluster (`clusters[0]`):** Defines the upstream service (`echo-upstream:8080`), DNS discovery (`STRICT_DNS` with `dns_lookup_family: V4_ONLY`), and load-balancing policy (`ROUND_ROBIN`).

> **Why `dns_lookup_family: V4_ONLY`?** On networks with a corporate DNS search suffix, short hostnames like `echo` can resolve via search domains to external IPv6 addresses. Using `echo-upstream` + `V4_ONLY` forces Envoy to resolve only the Docker Compose IPv4 container address.

---

## Run

```bash
cd docs/envoy_lessons/lesson1_basic_proxy
docker compose up -d
curl -s http://localhost:10000/hello
```

Expected JSON from `echo-upstream`:

```json
{
  "method": "GET",
  "path": "/hello",
  "headers_received": {
    "host": "localhost:10000",
    "user-agent": "curl/...",
    "accept": "*/*",
    "x-forwarded-proto": "http",
    "x-request-id": "...",
    "x-envoy-expected-rq-timeout-ms": "15000"
  },
  "body": ""
}
```

## What to Observe & Self-Check

- Notice `x-request-id` and `x-envoy-expected-rq-timeout-ms`: Envoy automatically injects request correlation and timeout headers before forwarding upstream.
- **Check:** Inspect [envoy.yaml](envoy.yaml). Which field connects the `route` to `clusters[0]`?  
  *(Answer: `route: { cluster: echo_service }` matches `clusters[0].name: echo_service`.)*

## Clean Up

```bash
docker compose down -t 1
```
