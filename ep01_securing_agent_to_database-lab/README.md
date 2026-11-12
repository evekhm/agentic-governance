# Episode 01 Reference Lab — Securing the Agent-to-Database Connection

Companion runnable lab for [Episode 01](../ep01_securing_agent_to_database.html).

- **Architecture & Roadmap:** [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **Live Build & Verification Tracker:** [PROGRESS.md](PROGRESS.md)

---

## Where to Start (Recommended Order)

Follow these steps in order so you build the mental model first, verify the Python core locally, and then provision Google Cloud:

1. **Step 0 (Optional Prerequisite · ~35 min, local Docker):**
   - Complete the three hands-on [Envoy Docker Lessons](docs/envoy_lessons/README.md) (`Listener → Cluster`, `L6 Egress Default-Deny`, and `L2 / L5 ext_proc Header Mutation`).
   - Read [Envoy Proxy & Agent Gateway Mechanics](docs/02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md) to see how Track A's self-managed Envoy sidecars map onto Track B's Google-managed `AgentGateway`.
2. **Step 1 (Verify Phase 1 Core Locally · 5 min, no cloud resources):**
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -e ".[dev]"
   .venv/bin/pytest -v tests/unit tests/test_snippet_sync.py
   ```
3. **Step 2 (Google Cloud Organization, Folder & Project Setup):**
   - Follow [00 · GCP Organization, Folder & Project Setup](docs/00_GCP_ORG_AND_PROJECT_SETUP.md) to create your folder, link billing, enable APIs, review organization-policy notes, and save IDs in a local git-ignored `.env` (never commit real IDs).
4. **Step 3 (Phase 2 · Google Cloud 5-Project Foundation):**
   - Follow [03 · Phase 2 GCP Foundation](docs/03_PHASE2_GCP_FOUNDATION.md) and [infra/terraform/01_gcp_foundation/](infra/terraform/01_gcp_foundation/README.md) to provision the 5-project hierarchy, Shared VPC, `/26` PSC-I subnet, Cloud NAT, Cloud SQL, BigQuery, and Workforce Identity Federation.
5. **Step 4 (Gateway-Side Token Injection Spike · Optional Deep Dive):**
   - Review or reproduce [01 · Gateway-Side Token Injection Spike](docs/01_GATEWAY_INJECTION_SPIKE.md) (`AgentGateway` + `REQUEST_AUTHZ` `AuthzExtension` + TLS `ext_proc`).

---

## Reading Map: Episode 01 ↔ Lab Stages

Use this map to jump between each stage of [Episode 01](../ep01_securing_agent_to_database.html) and its runnable code or exercises in the lab:

| Episode 01 Stage | Defense Layer | Lab Files & Exercises |
| :--- | :--- | :--- |
| [Stage 3 · Tool Boundary](../ep01_securing_agent_to_database.html#part-03) | `L4` | [config/tools.read.yaml](config/tools.read.yaml), [config/tools.write.yaml](config/tools.write.yaml), [services/agent/mcp_client.py](services/agent/mcp_client.py) |
| [Stage 5 · Database RLS & CLS](../ep01_securing_agent_to_database.html#part-05) | `L7` | [db/postgres/01..03.sql](db/postgres/03_rls_and_procs.sql), [db/bigquery/01..02.sql](db/bigquery/02_row_access_policy.sql) |
| [Stage 6 · mTLS, DPoP & Token Exchange](../ep01_securing_agent_to_database.html#part-06) | `L5` | [services/envoy_sidecar/tokenx_service.py](services/envoy_sidecar/tokenx_service.py), [01 · Gateway Spike](docs/01_GATEWAY_INJECTION_SPIKE.md), [Envoy Lesson 3](docs/envoy_lessons/lesson3_ext_proc/README.md) |
| [Stage 7–8 · Envoy Ingress, Egress & Screening](../ep01_securing_agent_to_database.html#part-07) | `L1` `L2` `L6` | [Envoy Lesson 1](docs/envoy_lessons/lesson1_basic_proxy/README.md), [Envoy Lesson 2](docs/envoy_lessons/lesson2_egress_allowlist/README.md), [02 · Envoy & Agent Gateway Mechanics](docs/02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md), [services/envoy_sidecar/](services/envoy_sidecar/envoy-egress.yaml) |
| [Stage 9 · Model Armor & Normalization](../ep01_securing_agent_to_database.html#part-09) | `L2` | [services/agent/callbacks.py](services/agent/callbacks.py) |
| [Stage 10–11 · PSC & VPC-SC](../ep01_securing_agent_to_database.html#part-10) | `L6` | [03 · Phase 2 GCP Foundation](docs/03_PHASE2_GCP_FOUNDATION.md), [infra/terraform/01_gcp_foundation/](infra/terraform/01_gcp_foundation/network.tf) |
| [Stage 12 · Workflows, HITL & Quarantine](../ep01_securing_agent_to_database.html#part-12) | `L3` `L8` | [services/agent/workflow.py](services/agent/workflow.py), [services/agent/quarantine.py](services/agent/quarantine.py) |
| [Stage 13 · Audit & Kill Switch](../ep01_securing_agent_to_database.html#part-13) | `L9` | [db/bigquery/03_chain_of_custody.sql](db/bigquery/03_chain_of_custody.sql), [db/postgres/04_pgaudit.sql](db/postgres/04_pgaudit.sql) |
