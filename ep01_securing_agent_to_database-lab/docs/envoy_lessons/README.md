# Envoy Prerequisites for Episode 01 (Hands-On Docker Lessons)

Before deploying Track A (Cloud Run + self-managed Envoy sidecars) or Track B (Google-managed `AgentGateway`), these three short Docker Compose lessons (~35 minutes total) teach the exact Envoy mechanics used in Episode 01.

For broader interactive Envoy fundamentals (listeners, filter chains, clusters, and load balancing), see [envoy-guide.vercel.app/learn](https://envoy-guide.vercel.app/learn).

## Lessons

| Lesson | Time | Envoy Concept | Episode 01 Mapping |
| :--- | :--- | :--- | :--- |
| [Lesson 1: Basic Proxy](lesson1_basic_proxy/README.md) | 10 min | `Listener` → `HttpConnectionManager` → `router` → `Cluster` | Baseline reverse/forward proxy mechanics |
| [Lesson 2: Egress Allowlist (`L6`)](lesson2_egress_allowlist/README.md) | 10 min | `virtual_hosts` + `direct_response: 403` | Track A [envoy-egress.yaml](../../services/envoy_sidecar/envoy-egress.yaml) & Track B `AgentGateway` default-deny |
| [Lesson 3: `ext_proc` Header Mutation (`L2` / `L5`)](lesson3_ext_proc/README.md) | 15 min | `envoy.filters.http.ext_proc` bidirectional gRPC stream | [ext_proc_server.py](../../services/envoy_sidecar/ext_proc_server.py) & `AgentGateway` `AuthzExtension` |

## What You Can Skip for Episode 01

Track A uses static YAML configs and Track B (`AgentGateway`) configures Envoy for you, so you do **not** need dynamic xDS control planes, ADS/EDS, Wasm filters, or service mesh (`Istio`) for this lab.

See [02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md](../02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md) for how each Envoy concept maps onto Google Cloud's `AgentGateway`.
