resource "random_id" "suffix" {
  byte_length = 2
}

locals {
  projects = {
    net_host      = "${var.project_prefix}-net-host-${random_id.suffix.hex}"
    gov_hub       = "${var.project_prefix}-gov-hub-${random_id.suffix.hex}"
    agent_runtime = "${var.project_prefix}-agent-rt-${random_id.suffix.hex}"
    data_mcp      = "${var.project_prefix}-data-mcp-${random_id.suffix.hex}"
    naive         = "${var.project_prefix}-naive-${random_id.suffix.hex}"
  }

  common_apis = [
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "compute.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ]

  gov_apis = [
    "networkservices.googleapis.com",
    "networksecurity.googleapis.com",
    "agentregistry.googleapis.com",
    "agentidentity.googleapis.com",
    "agentidentitycredentials.googleapis.com",
    "modelarmor.googleapis.com",
    "dlp.googleapis.com",
    "bigquery.googleapis.com",
    "certificatemanager.googleapis.com",
    "iap.googleapis.com",
  ]

  runtime_apis = [
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
  ]

  data_apis = [
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
    "bigquery.googleapis.com",
    "run.googleapis.com",
    "dns.googleapis.com",
  ]
}

resource "google_project" "tier" {
  for_each = local.projects

  name                = each.value
  project_id          = each.value
  folder_id           = var.folder_id
  billing_account     = var.billing_account
  auto_create_network = false
}

resource "google_project_service" "common" {
  for_each = {
    for pair in flatten([
      for k, p in google_project.tier : [
        for api in local.common_apis : {
          key     = "${k}/${api}"
          project = p.project_id
          api     = api
        }
      ]
    ]) : pair.key => pair
  }

  project            = each.value.project
  service            = each.value.api
  disable_on_destroy = false
}

resource "google_project_service" "gov_hub" {
  for_each           = toset(local.gov_apis)
  project            = google_project.tier["gov_hub"].project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "agent_runtime" {
  for_each           = toset(local.runtime_apis)
  project            = google_project.tier["agent_runtime"].project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "data_mcp" {
  for_each           = toset(local.data_apis)
  project            = google_project.tier["data_mcp"].project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "net_host_dns" {
  for_each           = toset(["dns.googleapis.com", "servicenetworking.googleapis.com"])
  project            = google_project.tier["net_host"].project_id
  service            = each.value
  disable_on_destroy = false
}
