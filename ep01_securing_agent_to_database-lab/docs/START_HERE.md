# Start Here: Step-by-Step Lab & Episode 01 Guide

Use this document as your single linear path through **Episode 01** and the **Reference Lab**. Every step tells you **what to read in Episode 01**, **what to run in the lab**, and **what to verify** before moving on.

---

## Step 1 · Understand the Problem & Naive Baseline (15 min)

1. **Read in Episode 01:**
   - [Scenario & Naive Prototype (`#part-01`)](../../ep01_securing_agent_to_database.html#part-01)
   - [Threats `T1`–`T8` & Nine Defense Layers `L1`–`L9` (`#part-02`)](../../ep01_securing_agent_to_database.html#part-02)
   - [Reference Architecture Hero (`#part-02b`)](../../ep01_securing_agent_to_database.html#part-02b)
2. **Inspect in the lab:**
   - Open [services/agent/naive_agent.py](../services/agent/naive_agent.py) to see why `execute_sql(sql, user_id)` fails all eight threats.
   - Open [attacks/payloads.py](../attacks/payloads.py) to see the exact `T1`–`T8` attack prompts.

---

## Step 2 · Learn the Proxy Mechanics Locally with Docker (35 min, Optional)

If you are new to Envoy Proxy, complete these three local Docker Compose exercises before touching Google Cloud:

1. **Read context:** [02 · Envoy Proxy & Agent Gateway Mechanics](02_ENVOY_AND_AGENT_GATEWAY_MECHANICS.md)
2. **Run in order:**
   - [Lesson 1: Basic Proxy (`Listener → Cluster`)](envoy_lessons/lesson1_basic_proxy/README.md) — `10 min`
   - [Lesson 2: Egress Allowlist (`L6` Default-Deny `403`)](envoy_lessons/lesson2_egress_allowlist/README.md) — `10 min`
   - [Lesson 3: `ext_proc` Header Mutation (`L2` / `L5`)](envoy_lessons/lesson3_ext_proc/README.md) — `15 min`
3. **Read the matching Episode 01 stages:**
   - [Stage 6 · mTLS, DPoP & Token Exchange (`#part-06`)](../../ep01_securing_agent_to_database.html#part-06)
   - [Stage 7–8 · Envoy Ingress, Egress & Screening (`#part-07`)](../../ep01_securing_agent_to_database.html#part-07)

---

## Step 3 · Verify the Shared Python Core Locally (5 min, No Cloud Required)

1. **Create the virtual environment and run unit + snippet-sync tests:**
   ```bash
   cd ep01_securing_agent_to_database-lab
   python3 -m venv .venv
   .venv/bin/pip install -e ".[dev]"
   .venv/bin/pytest -v tests/unit tests/test_snippet_sync.py
   ```
   Expected result: **11 passed**.
2. **Preview the Governance Workbench UI locally:**
   ```bash
   .venv/bin/uvicorn services.demo_ui.server:app --port 8090
   ```
   Open `http://localhost:8090` to inspect the Figure 4 architecture flow, layer toggles, and `T1`–`T8` preset buttons.
3. **Walk through each defense layer in Episode 01 alongside the tested code:**
   - `L4` Tool boundary → [Episode Stage 3](../../ep01_securing_agent_to_database.html#part-03) · [tools.read.yaml](../config/tools.read.yaml) · [mcp_client.py](../services/agent/mcp_client.py)
   - `L7` Database RLS/CLS → [Episode Stage 5](../../ep01_securing_agent_to_database.html#part-05) · [03_rls_and_procs.sql](../db/postgres/03_rls_and_procs.sql) · [02_row_access_policy.sql](../db/bigquery/02_row_access_policy.sql)
   - `L2` Screening & normalization → [Episode Stage 9](../../ep01_securing_agent_to_database.html#part-09) · [callbacks.py](../services/agent/callbacks.py)
   - `L3` Quarantine & `L8` HITL → [Episode Stage 12](../../ep01_securing_agent_to_database.html#part-12) · [quarantine.py](../services/agent/quarantine.py) · [workflow.py](../services/agent/workflow.py)
   - `L9` Audit & Kill Switch → [Episode Stage 13](../../ep01_securing_agent_to_database.html#part-13) · [03_chain_of_custody.sql](../db/bigquery/03_chain_of_custody.sql)

---

## Step 4 · Set Up Google Cloud & Provision Phase 2 Foundation

1. **Organization, Folder & Local `.env`:** Follow [00 · GCP Organization, Folder & Project Setup](00_GCP_ORG_AND_PROJECT_SETUP.md) to create your folder, review org-policy constraints (`requireInvokerIam`, `requireShieldedVm`, `allowedPolicyMemberDomains`), and store IDs in git-ignored `.env`.
2. **Provision the 5-Project Hierarchy & Network/Data Foundation:** Follow [03 · Phase 2 GCP Foundation](03_PHASE2_GCP_FOUNDATION.md) (`terraform init && terraform plan && terraform apply` in [infra/terraform/01_gcp_foundation/](../infra/terraform/01_gcp_foundation/README.md)) and apply the Phase 1 PostgreSQL and BigQuery schemas.
3. *(Optional Deep Dive)* **Gateway-Side Token Injection Spike:** Review [01 · Gateway-Side Token Injection Spike](01_GATEWAY_INJECTION_SPIKE.md) to see how `AgentGateway` + `REQUEST_AUTHZ` `AuthzExtension` + TLS `ext_proc` rewrites `Authorization` outside `AgentRuntime`.

---

## Step 5 · Track Progress & Upcoming Phases

Check [PROGRESS.md](../PROGRESS.md) at any time for what is built vs. verified:
- **Phase 3 (Next):** Track A (`02_track_a_cloudrun_envoy`) — Cloud Run 3-container pod (`agent` + `envoy` + `tokenx`), Read/Write MCP Toolbox, and live `T1`–`T8` layer-toggle tests.
- **Phase 4:** Track B (`03_track_b_enterprise`) — Managed `AgentRuntime` + `AgentGateway` + UAP V2 + VPC-SC + 400-day audit sink & IAM PAB kill switch.
