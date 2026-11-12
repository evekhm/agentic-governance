output "project_ids" {
  description = "Created five-project hierarchy IDs."
  value       = { for k, p in google_project.tier : k => p.project_id }
}

output "shared_vpc_id" {
  value = google_compute_network.shared_vpc.id
}

output "psc_network_attachment_id" {
  value = google_compute_network_attachment.psc_agw.id
}

output "cloudsql_private_ip" {
  value = google_sql_database_instance.orders_pg.private_ip_address
}

output "workforce_pool_name" {
  value = google_iam_workforce_pool.ep01_pool.name
}
