# 00 · Google Cloud Organization, Folder & Project Setup

Reproducible steps to create the organization folder, link billing, enable required APIs, and store environment variables locally without committing real IDs to git.

## 1. Prerequisites

- Google Cloud SDK (`gcloud`) authenticated with permissions to create folders/projects, link billing, and configure IAM/Service Extensions/VPC-SC (`roles/resourcemanager.folderCreator`, `roles/resourcemanager.projectCreator`, `roles/billing.user`).
- Verify your active `gcloud` profile, Organization ID, and Billing Account ID:

```bash
gcloud auth list
gcloud organizations list
gcloud beta billing accounts list
```

Export those values in your shell:

```bash
export ORG_ID="<YOUR_ORG_ID>"
export BILLING_ACCOUNT="<YOUR_BILLING_ACCOUNT_ID>"
export REGION="us-central1"
```

## 2. Create the Organization Folder

Create one folder to isolate all Episode 01 projects and billing alerts:

```bash
gcloud resource-manager folders create \
  --display-name="ep01-agentic-governance" \
  --organization="${ORG_ID}"
```

Retrieve the generated numeric Folder ID:

```bash
gcloud resource-manager folders list --organization="${ORG_ID}"
export FOLDER_ID="<NUMERIC_FOLDER_ID>"
```

## 3. Option A — Create a Single Gateway Spike Project (Pre-Build Verification)

Use a single temporary project inside `${FOLDER_ID}` to verify `AgentGateway` and `ExtensionBinding` / `AuthzExtension` behavior before provisioning the full 5-project topology:

```bash
export SPIKE_PROJECT_ID="ep01-gw-spike-$(date +%m%d)"

gcloud projects create "${SPIKE_PROJECT_ID}" \
  --folder="${FOLDER_ID}" \
  --name="EP01 Gateway Spike"

gcloud billing projects link "${SPIKE_PROJECT_ID}" \
  --billing-account="${BILLING_ACCOUNT}"

export SPIKE_PROJECT_NUMBER=$(gcloud projects describe "${SPIKE_PROJECT_ID}" --format='value(projectNumber)')
```

Enable required APIs on the spike project:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  agentregistry.googleapis.com \
  agentidentity.googleapis.com \
  agentidentitycredentials.googleapis.com \
  networkservices.googleapis.com \
  networksecurity.googleapis.com \
  iap.googleapis.com \
  modelarmor.googleapis.com \
  run.googleapis.com \
  compute.googleapis.com \
  dns.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  certificatemanager.googleapis.com \
  --project="${SPIKE_PROJECT_ID}"
```

### Grant Cloud Build Permissions on Fresh Projects

On new Google Cloud projects, `gcloud builds submit` defaults to using the Compute Engine default service account (`${PROJECT_NUMBER}-compute@developer.gserviceaccount.com`) and fails with `403 storage.objects.get` on the `_cloudbuild` staging bucket unless granted build permissions:

```bash
for role in \
  roles/cloudbuild.builds.builder \
  roles/storage.objectAdmin \
  roles/artifactregistry.writer \
  roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${SPIKE_PROJECT_ID}" \
    --member="serviceAccount:${SPIKE_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="${role}" \
    --quiet
done
```

### Grant Vertex AI Service Agent Gateway Read Access

Before deploying an Agent Runtime instance attached to an `AgentGateway`, grant `roles/networkservices.viewer` (not `agentGatewayViewer`, which lacks `networkservices.agentGateways.get`) to the Vertex AI service agent:

```bash
gcloud projects add-iam-policy-binding "${SPIKE_PROJECT_ID}" \
  --member="serviceAccount:service-${SPIKE_PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/networkservices.viewer"
```

## 4. Organization Policy Notes & Service-Agent Prerequisites

No organization-policy overrides are required when running `ext_proc` or internal MCP servers behind a Regional Internal ALB with a Shielded GCE/GKE backend:

- **`constraints/run.managed.requireInvokerIam`:** When enforced, Cloud Run requires IAM invoker auth (`--no-invoker-iam-check` is denied even with a project-level override in some orgs). Rather than weakening this org policy, keep Cloud Run services IAM-authenticated (using `roles/run.invoker` for authorized agent principals within `constraints/iam.allowedPolicyMemberDomains`), or host the `ext_proc` Service Extension backend behind a Regional Internal ALB + Compute/GKE backend.
- **`constraints/compute.requireShieldedVm`:** When enforced, GCE VM creation fails unless Shielded VM flags are explicitly passed (`--shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring`).
- **`constraints/iam.allowedPolicyMemberDomains`:** Restricts `allUsers` / external members; internal org principals (`principal://...` and `service-${PROJECT_NUMBER}@...`) are permitted.

Additional service-agent IAM prerequisites verified during setup:

- `service-${PROJECT_NUMBER}@gcp-sa-agentgateway.iam.gserviceaccount.com` requires `roles/compute.networkViewer` (to read the VPC and Network Attachment) and `roles/dns.reader` (to read Cloud DNS managed zones for `dnsPeeringConfig`) before `agent-connectivity-templates import` succeeds.
- `service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com` may need to be materialized first (`gcloud beta services identity create --service=aiplatform.googleapis.com --project=${PROJECT_ID}`) before granting `roles/networkservices.viewer`.
- Allow 10–15 seconds for IAM policy propagation before importing `AgentConnectivityTemplate` resources.

## 5. Save Local Configuration (`.env`)

Store all real IDs in `ep01_securing_agent_to_database-lab/.env` (excluded from git by `.gitignore`):

```bash
cat > ep01_securing_agent_to_database-lab/.env <<EOF
ORG_ID=${ORG_ID}
FOLDER_ID=${FOLDER_ID}
BILLING_ACCOUNT=${BILLING_ACCOUNT}
REGION=${REGION}
SPIKE_PROJECT_ID=${SPIKE_PROJECT_ID}
EOF
```

Verify that `.env` is ignored before committing anything:

```bash
git status --ignored
```

## 6. Teardown (Spike Project)

When finished with the spike project:

```bash
gcloud projects delete "${SPIKE_PROJECT_ID}"
```
