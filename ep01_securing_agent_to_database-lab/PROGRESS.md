# Episode 01 lab: progress

What is built and what is verified, per item of the [implementation plan](IMPLEMENTATION_PLAN.md).

**How to read this file**
- **Built** means the code or infrastructure exists in the repository or the cloud projects.
- **Verified** means it was run and the result was observed. The evidence column says how: a test name, a command, or a trace ID.
- An item is never marked verified from reading code or documentation alone. Documentation checks are labelled as such.
- Status values: `no`, `in progress`, `yes`.

Project IDs, organization IDs and hostnames are kept out of this repository (local `.env`, git-ignored).

## Environment

| Item | Status | Notes |
| :--- | :--- | :--- |
| Folder and five projects (`net-host`, `gov-hub`, `agent-runtime`, `data-mcp`, `naive`) | no | IDs to be provided |
| Organization-level permissions (service perimeter, principal access boundary, workforce identity pool) | no | |
| Billing linked, APIs enabled | no | |

## Checks before building

| Check | Result | Evidence | Still open |
| :--- | :--- | :--- | :--- |
| Keycloak accepts the agent's platform token as `actor_token` | No. The actor token must be a Keycloak access token of the actor. The documented client-delegation flow is used instead (plan decision 11). | Documentation check, 2026-11-12: Keycloak 26.8 token exchange guide and feature list | Run the flow hands-on: federated client authentication with the Cloud Run and Agent Runtime identity tokens, user consent to the delegation scope, `act` in the exchanged token |
| Agent Gateway injects or translates tokens outside the agent (`ExtensionBinding` Early Preview / `AuthzExtension` `ext_proc` / `AuthProviderBinding`) | **Yes (`AuthzExtension` `REQUEST_AUTHZ` works)**; `ExtensionBinding` does not target `googleManaged` `AgentGateway` | Live sandbox test in spike project (`us-central1`, 2026-11-12): (1) `ProducerExtension --phase=traffic` rejected (`only AUTHZ phase`); `ExtensionBinding` rejected (`Only AgentGateways with deployment_mode=self_managed can be targeted`). (2) `AuthzExtension` (`extproc.spike.internal` -> Internal ALB `--protocol=HTTP2` -> TLS `ext_proc`) + `AuthzPolicy` (`CONTENT_AUTHZ`) rewrote `authorization` but failed `REQUEST_BODY` (`FAILED_PRECONDITION`, `body_len: 0`). (3) `AuthzPolicy` (`REQUEST_AUTHZ`) returned `HTTP 200`, rewrote `authorization` to `Bearer SPIKE_GATEWAY_OBO_<hash>`, added `x-spike-injected-by: agent-gateway-ext-proc` and `x-original-user-token-seen: yes`, and preserved the full JSON-RPC `tools/call` body (`content-length: 122`). See [01_GATEWAY_INJECTION_SPIKE.md](docs/01_GATEWAY_INJECTION_SPIKE.md) | Integrate real RFC 8693 Keycloak/STS exchange into `tokenx` / `ext_proc` in Phase 4 |
| Launch stage and availability of Agent Gateway, Agent Registry and V2 access policies in the sandbox organization | **Yes — available** | Live `gcloud` + API provisioning in spike project (`2026-11-12`): `AgentGateway`, `AgentConnectivityTemplate`, `AgentRegistry`, `CertificateManager TrustConfig`, `AuthzExtension`, and `AuthzPolicy` all provisioned and active. Org policies observed: `run.managed.requireInvokerIam`, `compute.requireShieldedVm`, `iam.allowedPolicyMemberDomains` (documented in [00_GCP_ORG_AND_PROJECT_SETUP.md](docs/00_GCP_ORG_AND_PROJECT_SETUP.md)) | Verify V2 `AccessPolicy` + `PolicyBinding` during Phase 4 |
| Cloud NAT endpoint-type setting for the gateway subnet | **Verified (`ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG`)** | Created `spike-router` + `spike-nat` with `--endpoint-types=ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG` on `spike-vpc` (`2026-11-12`) | None |

## Phase 1: shared application core (no cloud resources)

| Item | Built | Verified | Evidence |
| :--- | :--- | :--- | :--- |
| Trace event format (`trace_schema.json`) | yes | yes | `tests/unit/test_core.py::test_trace_schema_and_redaction` (11 passed, 2026-11-12) |
| PostgreSQL schema, seed data, views, roles, row security, stored procedure | yes | no | SQL files written in `db/postgres/01..04.sql`; live Cloud SQL execution pending Phase 2 |
| BigQuery schema, row access policy, chain-of-custody query | yes | no | SQL files written in `db/bigquery/01..03.sql`; live BigQuery execution pending Phase 2 |
| MCP Toolbox tool definitions (read and write) | yes | no | `config/tools.read.yaml`, `config/tools.write.yaml`; live MCP Toolbox run pending Phase 3 |
| Governed agent (workflow, quarantine, callbacks, tool client) | yes | yes | `tests/unit/test_core.py` (`normalize_for_screening`, fail-closed Model Armor mock, HITL card, `Quarantine`, `LayerPolicy`) |
| Naive agent | yes | no | `services/agent/naive_agent.py` written; live exploit run pending Phase 2/3 |
| Hostile-model stub and attack payloads | yes | yes | `tests/unit/test_core.py::test_mock_hijacked_llm_produces_hostile_calls` (`T1`–`T8` payloads + `MockHijackedLlm`) |
| Envoy configuration, `tokenx`, screening callout | yes | yes | `tests/unit/test_core.py::test_obo_claims_validation_blocks_passthrough_and_replay`, `test_gateway_ext_proc_header_mutation` (live Envoy sidecar pending Phase 3) |
| Workbench UI | yes | no | `services/demo_ui/{server.py,static/index.html}` written; browser/SSE check pending |
| Trace export with redaction and leftover-pattern check | yes | yes | `tests/unit/test_core.py::test_trace_schema_and_redaction` |
| Unit tests | yes | yes | `.venv/bin/pytest -v tests/unit` (10 passed, 2026-11-12) |
| Snippet sync test against the episode | yes | yes | `.venv/bin/pytest -v tests/test_snippet_sync.py` (1 passed, 2026-11-12) |

## Phase 2: Google Cloud foundation

| Item | Built | Verified | Evidence |
| :--- | :--- | :--- | :--- |
| Projects, shared VPC, gateway subnet and network attachment | yes | no | Terraform written in `infra/terraform/01_gcp_foundation/{projects,network}.tf`; `terraform apply` pending |
| Cloud SQL (private, row security applied) | yes | no | Terraform written in `infra/terraform/01_gcp_foundation/data.tf` + `db/postgres/01..04.sql`; apply pending |
| BigQuery dataset, row access policy, policy tags | yes | no | Terraform written in `infra/terraform/01_gcp_foundation/data.tf` + `db/bigquery/01..02.sql`; apply pending |
| Keycloak on Cloud Run, realm, demo users | no | no | |
| Workforce Identity Federation from Keycloak | yes | no | Workforce pool + OIDC provider skeleton in `infra/terraform/01_gcp_foundation/identity.tf`; apply pending |
| Prototype project: naive agent, synthetic database, attacker sink | yes | no | `naive` project provisioned in `projects.tf`; Cloud Run naive deploy pending |

## Phase 3: Track A (Cloud Run with self-managed Envoy)

| Item | Built | Verified | Evidence |
| :--- | :--- | :--- | :--- |
| Read and write tool servers | no | no | |
| Agent service with Envoy and `tokenx` sidecars | no | no | |
| Model Armor and Sensitive Data Protection | no | no | |
| Test runner job inside the VPC | no | no | |
| Integration tests | no | no | |

## Phase 4: Track B (managed Agent Runtime)

| Item | Built | Verified | Evidence |
| :--- | :--- | :--- | :--- |
| Agent Gateway, connectivity template, Agent Registry entries | no | no | |
| Access policies and Model Armor at the gateway | no | no | |
| Agent on Agent Runtime, and the stub agent next to it | no | no | |
| Internal load balancer in front of the tool servers | no | no | |
| Service perimeter | no | no | |
| Audit sink and kill-switch script (apply and revert) | no | no | |

## Attack tests

Each cell is `no`, `in progress` or `yes`, and a `yes` needs a test run as evidence. "Stub" runs assert the outcome; "live" runs record it.

| Threat | Prototype: exploit succeeds (stub) | Track A: blocked (stub) | Track A: live run recorded | Track B: blocked (stub) | Track B: live run recorded | Replay bundle published |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `T1` Direct SQL injection | no | no | no | no | no | no |
| `T2` Poisoned row and PII | no | no | no | no | no | no |
| `T3` Confused deputy | no | no | no | no | no | no |
| `T4` In-band identity spoofing | no | no | no | no | no | no |
| `T5` Token passthrough | no | no | no | no | no | no |
| `T6` Network and Markdown exfiltration | no | no | no | no | no | no |
| `T7` Unbounded or duplicate writes | no | no | no | no | no | no |
| `T8` Blind audit and kill switch | no | no | no | no | no | no |

## Per-request switches on Track A

| Layer | Switch built | Verified that the attack succeeds with it off | Evidence |
| :--- | :--- | :--- | :--- |
| `L2` screening | no | no | |
| `L3` quarantine | no | no | |
| `L4` tool boundary | no | no | |
| `L5` token exchange | no | no | |
| `L8` human approval | no | no | |
