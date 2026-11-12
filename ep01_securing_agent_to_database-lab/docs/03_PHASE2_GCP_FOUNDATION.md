# Phase 2: Google Cloud Foundation (`01_gcp_foundation`)

This guide walks through provisioning the shared Google Cloud foundation in [infra/terraform/01_gcp_foundation/](../infra/terraform/01_gcp_foundation/README.md) so you can follow every resource as it is created.

---

## 1. What Each Terraform File Creates

| File | Purpose | Episode 01 Mapping |
| :--- | :--- | :--- |
| [projects.tf](../infra/terraform/01_gcp_foundation/projects.tf) | Creates the 5 projects (`net-host`, `gov-hub`, `agent-rt`, `data-mcp`, `naive`), links billing, and enables APIs. | Four-tier enterprise hierarchy + prototype project |
| [network.tf](../infra/terraform/01_gcp_foundation/network.tf) | Shared VPC in `net-host`, `/26` PSC-I subnet (`10.10.1.0/26`), `/24` services subnet, `/26` proxy-only subnet, Cloud NAT (`ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG`), PSC-I Network Attachment, and Private DNS `internal.corp.`. | [Stage 10 · PSC & Egress](../ep01_securing_agent_to_database.html#part-10) |
| [data.tf](../infra/terraform/01_gcp_foundation/data.tf) | Private Service Access peering, Private Cloud SQL PostgreSQL 15 (`pgaudit` + IAM auth enabled, public IP disabled), BigQuery `sales` + `agent_views` datasets, and `gov-hub` 400-day `security_telemetry` dataset. | [Stage 5 · RLS/CLS](../ep01_securing_agent_to_database.html#part-05) & [Stage 13 · Audit](../ep01_securing_agent_to_database.html#part-13) |
| [identity.tf](../infra/terraform/01_gcp_foundation/identity.tf) | Workload service accounts (`toolbox-read-sa`, `toolbox-write-sa`, `orders-agent-sa`), `AgentGateway`/`AgentRuntime` service identities, and the Workforce Identity Pool + Keycloak OIDC provider skeleton. | [Stage 4 · Agent Identity](../ep01_securing_agent_to_database.html#part-04) & BigQuery STS exchange |

---

## 2. Prepare Local Variables (Never Commit Real IDs)

Load your local `.env` from `ep01_securing_agent_to_database-lab/.env` and generate a git-ignored `terraform.tfvars`:

```bash
set -a && source .env && set +a

cat > infra/terraform/01_gcp_foundation/terraform.tfvars <<EOF
org_id          = "${ORG_ID}"
folder_id       = "${FOLDER_ID}"
billing_account = "${BILLING_ACCOUNT}"
region          = "${REGION}"
project_prefix  = "ep01"
EOF
```

---

## 3. Initialize, Plan, and Apply

```bash
cd infra/terraform/01_gcp_foundation
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Capture the generated project IDs and Cloud SQL private IP:

```bash
terraform output
```

---

## 4. Load the Phase 1 Database Schemas

Once `orders_pg` and the BigQuery datasets are created:

1. **BigQuery (`data-mcp` project):** Substitute `${DATA_PROJECT_ID}` in [db/bigquery/01_schema_and_seed.sql](../db/bigquery/01_schema_and_seed.sql) and [02_row_access_policy.sql](../db/bigquery/02_row_access_policy.sql) and run them with `bq query --use_legacy_sql=false`.
2. **Cloud SQL PostgreSQL (`data-mcp` project):** Connect via the Cloud SQL Auth Proxy (or VPC runner) and apply [db/postgres/01_schema_and_seed.sql](../db/postgres/01_schema_and_seed.sql) through `04_pgaudit.sql` in order.

---

## 5. Organization Policy Reminder

All constraints documented in [00 · GCP Org, Folder & Project Setup](00_GCP_ORG_AND_PROJECT_SETUP.md) apply here:
- Cloud SQL has `ipv4_enabled = false` (private IP only).
- Any GCE bastion/backend VM you add later must pass `--shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring`.
- Cloud Run services remain IAM-authenticated (`roles/run.invoker`) with no `allUsers` bindings.
