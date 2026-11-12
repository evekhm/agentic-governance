variable "org_id" {
  description = "Google Cloud Organization ID (numeric)."
  type        = string
}

variable "folder_id" {
  description = "Google Cloud Folder ID (numeric) containing the Episode 01 lab projects."
  type        = string
}

variable "billing_account" {
  description = "Billing account ID (XXXXXX-XXXXXX-XXXXXX) attached to all five projects."
  type        = string
}

variable "region" {
  description = "Primary Google Cloud region."
  type        = string
  default     = "us-central1"
}

variable "project_prefix" {
  description = "Prefix used for project IDs (suffix is randomized for global uniqueness)."
  type        = string
  default     = "ep01"
}

variable "corp_idp_issuer_uri" {
  description = "Keycloak OIDC issuer URI for Workforce Identity Federation (set after Keycloak deploy or placeholder initially)."
  type        = string
  default     = "https://keycloak.internal.corp/realms/ep01"
}

variable "corp_idp_client_id" {
  description = "OIDC client ID registered in Keycloak for Workforce Identity Federation."
  type        = string
  default     = "ep01-workforce-client"
}
