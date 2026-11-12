# Phase 2 Terraform: `01_gcp_foundation`

Provisions the five-project hierarchy, Shared VPC, `/26` PSC-I subnet & Network Attachment, Cloud NAT (`ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG`), Private Cloud SQL PostgreSQL 15 (`pgaudit` enabled), BigQuery datasets (including 400-day telemetry), and Workforce Identity Pool skeleton.

See [03 · Phase 2 GCP Foundation Guide](../../../docs/03_PHASE2_GCP_FOUNDATION.md) for the step-by-step walkthrough.

```bash
cp terraform.tfvars.example terraform.tfvars   # edit with your real IDs (git-ignored)
terraform init
terraform plan
terraform apply
```
