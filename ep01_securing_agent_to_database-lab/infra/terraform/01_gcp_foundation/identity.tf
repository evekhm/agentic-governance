resource "google_service_account" "toolbox_read" {
  project      = google_project.tier["data_mcp"].project_id
  account_id   = "toolbox-read-sa"
  display_name = "MCP Toolbox Read-Only Service Account"
}

resource "google_service_account" "toolbox_write" {
  project      = google_project.tier["data_mcp"].project_id
  account_id   = "toolbox-write-sa"
  display_name = "MCP Toolbox Write Service Account"
}

resource "google_service_account" "orders_agent" {
  project      = google_project.tier["agent_runtime"].project_id
  account_id   = "orders-agent-sa"
  display_name = "Orders Agent Workload Service Account"
}

# Service identities required for AgentGateway (dnsPeeringConfig + Network Attachment) and AgentRuntime
resource "google_project_service_identity" "agentgateway_sa" {
  provider   = google-beta
  project    = google_project.tier["gov_hub"].project_id
  service    = "networkservices.googleapis.com"
  depends_on = [google_project_service.gov_hub]
}

resource "google_project_service_identity" "aiplatform_sa" {
  provider   = google-beta
  project    = google_project.tier["agent_runtime"].project_id
  service    = "aiplatform.googleapis.com"
  depends_on = [google_project_service.agent_runtime]
}

resource "google_project_iam_member" "aiplatform_gateway_viewer" {
  project = google_project.tier["gov_hub"].project_id
  role    = "roles/networkservices.viewer"
  member  = "serviceAccount:${google_project_service_identity.aiplatform_sa.email}"
}

# Workforce Identity Pool + OIDC Provider skeleton for Keycloak federation (BigQuery OBO path)
resource "google_iam_workforce_pool" "ep01_pool" {
  provider          = google-beta
  workforce_pool_id = "ep01-corp-pool-${random_id.suffix.hex}"
  parent            = "organizations/${var.org_id}"
  location          = "global"
  display_name      = "Episode 01 Corporate Workforce Pool"
}

resource "google_iam_workforce_pool_provider" "keycloak_oidc" {
  provider          = google-beta
  workforce_pool_id = google_iam_workforce_pool.ep01_pool.workforce_pool_id
  location          = "global"
  provider_id       = "keycloak-oidc"
  display_name      = "Keycloak OIDC Provider"

  attribute_mapping = {
    "google.subject" = "assertion.sub"
    "google.groups"  = "assertion.groups"
  }

  oidc {
    issuer_uri = var.corp_idp_issuer_uri
    client_id  = var.corp_idp_client_id
  }
}
