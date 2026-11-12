resource "google_compute_network" "shared_vpc" {
  project                 = google_project.tier["net_host"].project_id
  name                    = "ep01-shared-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.common]
}

resource "google_compute_shared_vpc_host_project" "host" {
  project    = google_project.tier["net_host"].project_id
  depends_on = [google_compute_network.shared_vpc]
}

resource "google_compute_shared_vpc_service_project" "spokes" {
  for_each = toset(["gov_hub", "agent_runtime", "data_mcp"])

  host_project    = google_compute_shared_vpc_host_project.host.project
  service_project = google_project.tier[each.value].project_id
}

# /26 PSC-I subnet (recommended size when several gateways share the subnet; documented min is /28)
resource "google_compute_subnetwork" "psc_attach" {
  project                  = google_project.tier["net_host"].project_id
  name                     = "ep01-psc-attach-subnet"
  region                   = var.region
  network                  = google_compute_network.shared_vpc.id
  ip_cidr_range            = "10.10.1.0/26"
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "services" {
  project                  = google_project.tier["net_host"].project_id
  name                     = "ep01-services-subnet"
  region                   = var.region
  network                  = google_compute_network.shared_vpc.id
  ip_cidr_range            = "10.10.2.0/24"
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "proxy_only" {
  project       = google_project.tier["net_host"].project_id
  name          = "ep01-proxy-only-subnet"
  region        = var.region
  network       = google_compute_network.shared_vpc.id
  ip_cidr_range = "10.10.3.0/26"
  purpose       = "REGIONAL_MANAGED_PROXY"
  role          = "ACTIVE"
}

resource "google_compute_router" "nat_router" {
  project = google_project.tier["net_host"].project_id
  name    = "ep01-nat-router"
  region  = var.region
  network = google_compute_network.shared_vpc.id
}

resource "google_compute_router_nat" "nat" {
  project                            = google_project.tier["net_host"].project_id
  name                               = "ep01-cloud-nat"
  router                             = google_compute_router.nat_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  endpoint_types                     = ["ENDPOINT_TYPE_VM", "ENDPOINT_TYPE_SWG"]
}

resource "google_compute_network_attachment" "psc_agw" {
  provider              = google-beta
  project               = google_project.tier["net_host"].project_id
  name                  = "ep01-psc-agw"
  region                = var.region
  connection_preference = "ACCEPT_AUTOMATIC"
  subnetworks           = [google_compute_subnetwork.psc_attach.id]
}

resource "google_dns_managed_zone" "internal_corp" {
  project     = google_project.tier["net_host"].project_id
  name        = "ep01-internal-corp"
  dns_name    = "internal.corp."
  description = "Private DNS zone for internal MCP and ext_proc endpoints"
  visibility  = "private"

  private_visibility_config {
    networks {
      network_url = google_compute_network.shared_vpc.id
    }
  }

  depends_on = [google_project_service.net_host_dns]
}

resource "google_compute_firewall" "allow_internal_and_hc" {
  project = google_project.tier["net_host"].project_id
  name    = "ep01-allow-internal-hc"
  network = google_compute_network.shared_vpc.id

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "5432", "8080", "8081"]
  }

  source_ranges = ["10.10.0.0/16", "35.191.0.0/16", "130.211.0.0/22"]
}
