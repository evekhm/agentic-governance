# All About Agents

Architecture notes, system-design mental models, and governance blueprints for production AI agents.

## Topic: Agentic Governance

### [Episode 01 — Securing the Agent-to-Database Connection](https://evekhm.github.io/agentic-governance/ep01_securing_agent_to_database.html) ([PDF](ep01_securing_agent_to_database.pdf))

Follows a single request from the top-level picture (user chat UI, LLM agent, and internal customer database) down to the low-level details of each hop, and builds up a production Zero-Trust architecture. Maps eight threat vectors (`T1`–`T8`) across the wire and layers nine defense-in-depth controls (`L1`–`L9`) aligned to the OWASP Agentic Top 10 (2026) and OWASP LLM Top 10 (2025).

- **Hands-on lab:** [ep01_securing_agent_to_database-lab/](ep01_securing_agent_to_database-lab/README.md) · [Start Here Guide](ep01_securing_agent_to_database-lab/docs/START_HERE.md) · [Progress](ep01_securing_agent_to_database-lab/PROGRESS.md)

## Up Next

- **System Design:** *The Mental Model for Designing Agentic Systems* — problem-first architecture, deterministic vs. LLM boundaries, async queues, circuit breakers, and staged autonomy (worked through on a self-healing code repository).
- **Governance:** *Dual LLM and CaMeL, in depth.*
