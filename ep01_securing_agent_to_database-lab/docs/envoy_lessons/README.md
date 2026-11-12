# Envoy Prerequisites for Episode 01 (Hands-On Docker Lessons)

If you are new to Envoy Proxy, these three short Docker Compose exercises (~35 minutes total) give you the exact mental model you need before deploying **Track A** (Cloud Run + self-managed Envoy sidecars) or **Track B** (Google-managed `AgentGateway`).

- **Where this fits in Episode 01:** Read alongside [Stage 6 (mTLS, DPoP & Token Exchange)](../../ep01_securing_agent_to_database.html#part-06) and [Stage 9 (Network Egress & PSC)](../../ep01_securing_agent_to_database.html#part-09), plus [02 · Envoy Proxy & Agent Gateway Mechanics](../02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md).
- **Broader Envoy fundamentals:** For interactive diagrams on listeners, filter chains, and load balancing, see [envoy-guide.vercel.app/learn](https://envoy-guide.vercel.app/learn).

---

## Why Envoy Matters for Securing AI Agents

In a naive agent deployment, the LLM process makes direct HTTP calls to tool servers and holds credentials in its own memory. If an indirect prompt injection (`T2`) or SSRF payload (`T6`) hijacks the agent's control flow, the agent can exfiltrate data to any URL or replay high-privilege tokens.

**Sidecar and gateway proxies** solve this by moving network policy, egress allowlisting, and token/content inspection **out of the agent process**:

```text
[ Agent Container ] ──HTTP/HTTPS──▶ [ Envoy Proxy ] ──gRPC──▶ [ ext_proc Helper ]
                                          │
                                          ├── Allowed host? ──▶ [ Upstream MCP Server ]
                                          └── Unknown host? ──▶ 403 DirectResponse
```

---

## The Three Lessons

| Lesson | Time | Envoy Building Blocks | Episode 01 Mapping |
| :--- | :--- | :--- | :--- |
| [Lesson 1: Basic Proxy](lesson1_basic_proxy/README.md) | 10 min | `Listener` → `HttpConnectionManager` → `router` → `Cluster` | Baseline proxy request lifecycle |
| [Lesson 2: Egress Allowlist (`L6`)](lesson2_egress_allowlist/README.md) | 10 min | `virtual_hosts`, `domains`, `direct_response: 403` | Track A [envoy-egress.yaml](../../services/envoy_sidecar/envoy-egress.yaml) & Track B `AgentGateway` `default_denied` |
| [Lesson 3: `ext_proc` Header Mutation (`L2` / `L5`)](lesson3_ext_proc/README.md) | 15 min | `envoy.filters.http.ext_proc` bidirectional gRPC stream | [ext_proc_server.py](../../services/envoy_sidecar/ext_proc_server.py) & Track B `AgentGateway` `AuthzExtension` (`REQUEST_AUTHZ`) |

---

## What You Can Skip for Episode 01

Envoy supports dynamic xDS control planes (ADS/CDS/EDS), Wasm/Lua plugins, and full service meshes (Istio). You do **not** need any of those here:
- **Track A** uses static Envoy YAML files mounted into the sidecar container.
- **Track B** uses `AgentGateway`, where Google Cloud generates and runs the Envoy data plane from your `AgentRegistry`, `AuthzPolicy`, and `AuthzExtension` resources.
