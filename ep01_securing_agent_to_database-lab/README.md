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
4. **Step 3 (Gateway-Side Token Injection Spike · Optional Deep Dive):**
   - Review or reproduce [01 · Gateway-Side Token Injection Spike](docs/01_GATEWAY_INJECTION_SPIKE.md) (`AgentGateway` + `REQUEST_AUTHZ` `AuthzExtension` + TLS `ext_proc`).
5. **Step 4 (Cloud Foundation, Track A & Track B · Next in [PROGRESS.md](PROGRESS.md)):**
   - Phase 2 Terraform (`infra/terraform/01_gcp_foundation/`), Track A (`02_track_a_cloudrun_envoy/`), and Track B (`03_track_b_enterprise/`).
