# All About Agents

Architecture notes, system-design mental models, and governance blueprints for production AI agents.

## Topic: Agentic Governance

### [Episode 01 — Securing the Agent-to-Database Connection](https://evekhm.github.io/all-about-agents/ep01_securing_agent_to_database.html) ([PDF](ep01_securing_agent_to_database.pdf))

Follows a customer request from the top-level picture (user, agent, and database) down to the low-level details of each hop: which token travels on each call, which SQL runs, and whose identity the database sees. Maps where threats strike on the wire and layers defense-in-depth guardrails aligned to the OWASP Agentic Top 10 (2026) and OWASP LLM Top 10 (2025).

- **Hands-on lab:** [ep01_securing_agent_to_database-lab/](ep01_securing_agent_to_database-lab/README.md) · [Start Here Guide](ep01_securing_agent_to_database-lab/docs/START_HERE.md) · [Progress](ep01_securing_agent_to_database-lab/PROGRESS.md)

## Topic: System Design

### [Episode 02 — A Mental Model for Designing Agentic Systems](https://evekhm.github.io/all-about-agents/ep02_designing_agentic_systems.html) ([PDF](ep02_designing_agentic_systems.pdf))

Starts from an abstract sequence of agents and follows it down to what that sketch actually means as an architecture: where language models belong versus deterministic code, how the surrounding harness coordinates control flow and state, and how structured context moves from one step to the next. Uses a self-healing code repository system as a reference example to lay out a systematic, reusable approach to agentic system design.

## Up Next

- **Governance:** *Dual LLM and CaMeL, in depth.*
