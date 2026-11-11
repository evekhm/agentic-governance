# Agentic Governance on Google Cloud

Architecture blueprints, threat models, and step-by-step zero-trust engineering guides for production AI agents.

## Introduction

I decided to start a series dedicated to **Agentic Governance** to help engineers and architects fit all the scattered pieces of this puzzle into a single, structured picture. My goal is to make it clear at the top level what kinds of **threats** are possible when we connect AI agents to real systems, which **guardrails** prevent them, and how all of those controls fit together end-to-end.

This series is not meant to promise a silver-bullet, 100% foolproof security guarantee—no architecture can. Instead, it is meant to serve as a practical foundation: walking through the known failure modes of agentic systems and bringing the architectural defenses together into one coherent mental model.

When I began researching Agentic Governance, I struggled to find material that explained the end-to-end mechanics in a clear, approachable way. So I started compiling my own architectural notes and diagrams, and I will be sharing them across this series as I work through each topic.

## Episodes

### [Episode 01 — Securing the Agent-to-Database Connection](https://evekhm.github.io/agentic-governance/ep01_securing_agent_to_database.html) ([PDF](ep01_securing_agent_to_database.pdf))

Walks bottom-up from a naive three-box prototype (user chat UI, LLM agent, and internal customer database) to a production Zero-Trust architecture. Maps eight threat vectors (`T1`–`T8`) across the wire and layers nine defense-in-depth controls (`L1`–`L9`)—including parameterized MCP tool boundaries, SPIFFE workload identity and RFC 8693 OBO token exchange, database Row/Column-Level Security, Envoy ingress/egress gateways, inline Model Armor and Cloud SDP tokenization, Private Service Connect and VPC Service Controls, tool-less Quarantine LLMs with HITL write gates, and end-to-end W3C trace auditing with kill-switch containment—aligned to the OWASP Agentic Top 10 (2026) and OWASP LLM Top 10 (2025).
