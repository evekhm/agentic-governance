# Lesson 1: Listener → HttpConnectionManager → Router → Cluster

## Goal
See how a minimal static `envoy.yaml` accepts HTTP traffic on port `10000`, parses it in `HttpConnectionManager`, matches a route, and forwards it to an upstream cluster (`echo:8080`).

## Run

```bash
docker compose up -d
curl -s http://localhost:10000/hello
```

## What to Observe
- `headers_received` includes `x-envoy-expected-rq-timeout-ms` and `x-forwarded-proto` added by Envoy before forwarding to `echo`.
- Look at [envoy.yaml](envoy.yaml): `listeners[0]` binds `0.0.0.0:10000`, `http_filters` ends with `envoy.filters.http.router`, and `clusters[0]` resolves `echo:8080` via `STRICT_DNS`.

## Clean Up

```bash
docker compose down
```
