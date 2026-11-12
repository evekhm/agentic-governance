# Agentic Governance on Google Cloud

Architecture blueprints, threat models, and step-by-step zero-trust engineering guides for production AI agents.

## Introduction

I started this series to bring the different pieces of agentic governance into one structured picture. I want to understand, at the top level, what kinds of threats are possible when an AI agent is connected to real systems, which guardrails prevent them, and how it all fits together.

The series does not give a bulletproof, guaranteed-safe solution. It is meant as a foundation: the known problems, the controls that address them, and a way to see the whole picture at once.

I could not find much material on this topic that was easy to follow, so I began compiling my own notes. I am sharing them here as I go through each topic.

## Episodes

### [Episode 01 — Securing the Agent-to-Database Connection](https://evekhm.github.io/agentic-governance/ep01_securing_agent_to_database.html) ([PDF](ep01_securing_agent_to_database.pdf))

Follows a single request from the top-level picture (user chat UI, LLM agent, and internal customer database) down to the low-level details of each hop, and builds up a production Zero-Trust architecture. Maps eight threat vectors (`T1`–`T8`) across the wire and layers nine defense-in-depth controls (`L1`–`L9`)—including parameterized MCP tool boundaries, SPIFFE workload identity and RFC 8693 OBO token exchange, database Row/Column-Level Security, Envoy ingress/egress gateways, inline Model Armor and Cloud SDP tokenization, Private Service Connect and VPC Service Controls, tool-less Quarantine LLMs with HITL write gates, and end-to-end W3C trace auditing with kill-switch containment—aligned to the OWASP Agentic Top 10 (2026) and OWASP LLM Top 10 (2025).

**Hands-on lab (in preparation):** a companion lab will run the same architecture in two tracks (Cloud Run with self-managed Envoy sidecars, and the managed Agent Runtime) and replay the `T1`–`T8` attacks against the prototype and the governed build. See the [implementation plan](ep01_securing_agent_to_database-lab/IMPLEMENTATION_PLAN.md); the lab code is not yet available.
