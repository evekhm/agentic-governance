# Agentic Governance on Google Cloud

Architecture blueprints, threat models, and step-by-step zero-trust engineering guides for production AI agents.

## Introduction

I decided to start a series dedicated to **Agentic Governance** to help engineers and architects fit all the scattered pieces of this puzzle into a single, structured picture. My goal is to make it clear at the top level what kinds of **threats** are possible when we connect AI agents to real systems, which **guardrails** prevent them, and how all of those controls fit together end-to-end.

This series is not meant to promise a silver-bullet, 100% foolproof security guarantee—no architecture can. Instead, it is meant to serve as a practical foundation: walking through the known failure modes of agentic systems and bringing the architectural defenses together into one coherent mental model.

When I began researching Agentic Governance, I struggled to find material that explained the end-to-end mechanics in a clear, approachable way. So I started compiling my own architectural notes and diagrams, and I will be sharing them across this series as I work through each topic.

## Episode 01 — Securing the Agent-to-Database Connection

- **Main Episode 01 Post:** [`ep01_securing_agent_to_database.html`](ep01_securing_agent_to_database.html) ([PDF](ep01_securing_agent_to_database.pdf))

### Companion Reference Deep Dives (`ref/`)

1. **Platform-Agnostic Zero-Trust Reference Architecture:** [`ref/agnostic-architecture.html`](ref/agnostic-architecture.html) ([PDF](ref/agnostic-architecture.pdf))
2. **MCP Tool Server Options (`FastMCP` vs. `MCP Toolbox` vs. Managed MCP):** [`ref/mcp-tool-server-options.html`](ref/mcp-tool-server-options.html) ([PDF](ref/mcp-tool-server-options.pdf))
3. **Row- & Column-Level Security (BigQuery Stateless HTTP vs. Cloud SQL Pooled TCP):** [`ref/rls-cls.html`](ref/rls-cls.html) ([PDF](ref/rls-cls.pdf))
4. **mTLS, SPIFFE SVIDs, DPoP & OAuth 2.1 RFC 8693 OBO Token Exchange:** [`ref/mtls-and-tokens.html`](ref/mtls-and-tokens.html) ([PDF](ref/mtls-and-tokens.pdf))
5. **Envoy Proxy at Ingress & Egress (`ext_authz` + `ext_proc`):** [`ref/envoy-proxy.html`](ref/envoy-proxy.html) ([PDF](ref/envoy-proxy.pdf))
6. **Model Armor Inline Screening & Cloud SDP Deterministic Tokenization:** [`ref/model-armor.html`](ref/model-armor.html) ([PDF](ref/model-armor.pdf))
7. **Private Service Connect (3 PSC Doors) & VPC Service Controls:** [`ref/psc-and-vpc-sc.html`](ref/psc-and-vpc-sc.html) ([PDF](ref/psc-and-vpc-sc.pdf))
8. **Immutable Audit Logging, Distributed Trace (`W3C traceparent`) & Kill Switch:** [`ref/audit-and-containment.html`](ref/audit-and-containment.html) ([PDF](ref/audit-and-containment.pdf))
9. **Complete 22-Row OWASP Top 10 Mapping (`ASI01–ASI10`, `LLM01–LLM10`, `API1:2023`, `A03:2021`):** [`ref/owasp-mapping.html`](ref/owasp-mapping.html) ([PDF](ref/owasp-mapping.pdf))
