# Private Service Access allocation for Cloud SQL private IP
resource "google_compute_global_address" "psa_range" {
  project       = google_project.tier["net_host"].project_id
  name          = "ep01-psa-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 20
  network       = google_compute_network.shared_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.shared_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.psa_range.name]
  depends_on              = [google_project_service.net_host_dns]
}

resource "google_sql_database_instance" "orders_pg" {
  project             = google_project.tier["data_mcp"].project_id
  name                = "ep01-orders-pg"
  region              = var.region
  database_version    = "POSTGRES_15"
  deletion_protection = false

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.shared_vpc.id
      enable_private_path_for_google_cloud_services = true
    }

    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }

    database_flags {
      name  = "pgaudit.log"
      value = "read,write,function"
    }

    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_project_service.data_mcp,
  ]
}

resource "google_sql_database" "orders_db" {
  project  = google_project.tier["data_mcp"].project_id
  instance = google_sql_database_instance.orders_pg.name
  name     = "orders"
}

resource "google_bigquery_dataset" "sales" {
  project    = google_project.tier["data_mcp"].project_id
  dataset_id = "sales"
  location   = "US"
  depends_on = [google_project_service.data_mcp]
}

resource "google_bigquery_dataset" "agent_views" {
  project    = google_project.tier["data_mcp"].project_id
  dataset_id = "agent_views"
  location   = "US"
  depends_on = [google_project_service.data_mcp]
}

# Central 400-day security telemetry dataset in gov-hub (T8 chain of custody)
resource "google_bigquery_dataset" "security_telemetry" {
  project                         = google_project.tier["gov_hub"].project_id
  dataset_id                      = "security_telemetry"
  location                        = "US"
  default_table_expiration_ms     = 400 * 24 * 60 * 60 * 1000
  default_partition_expiration_ms = 400 * 24 * 60 * 60 * 1000
  depends_on                      = [google_project_service.gov_hub]
}
