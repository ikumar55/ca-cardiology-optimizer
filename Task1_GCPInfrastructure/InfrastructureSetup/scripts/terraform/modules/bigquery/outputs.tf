# Outputs for BigQuery Module

# Dataset outputs
output "raw_data_dataset_id" {
  description = "ID of the raw data dataset"
  value       = google_bigquery_dataset.raw_data.dataset_id
}

output "processed_data_dataset_id" {
  description = "ID of the processed data dataset"
  value       = google_bigquery_dataset.processed_data.dataset_id
}

output "analytics_dataset_id" {
  description = "ID of the analytics dataset"
  value       = google_bigquery_dataset.analytics.dataset_id
}

# Dataset URLs for reference
output "raw_data_dataset_url" {
  description = "URL of the raw data dataset"
  value       = "https://console.cloud.google.com/bigquery?project=${var.project_id}&ws=!1m4!1m3!3m2!1s${var.project_id}!2s${google_bigquery_dataset.raw_data.dataset_id}"
}

output "processed_data_dataset_url" {
  description = "URL of the processed data dataset"
  value       = "https://console.cloud.google.com/bigquery?project=${var.project_id}&ws=!1m4!1m3!3m2!1s${var.project_id}!2s${google_bigquery_dataset.processed_data.dataset_id}"
}

output "analytics_dataset_url" {
  description = "URL of the analytics dataset"
  value       = "https://console.cloud.google.com/bigquery?project=${var.project_id}&ws=!1m4!1m3!3m2!1s${var.project_id}!2s${google_bigquery_dataset.analytics.dataset_id}"
}

# Table outputs
output "providers_table_id" {
  description = "Full ID of the providers table"
  value       = "${google_bigquery_table.providers_raw.project}.${google_bigquery_table.providers_raw.dataset_id}.${google_bigquery_table.providers_raw.table_id}"
}

output "travel_matrix_table_id" {
  description = "Full ID of the travel matrix table"
  value       = "${google_bigquery_table.travel_matrix.project}.${google_bigquery_table.travel_matrix.dataset_id}.${google_bigquery_table.travel_matrix.table_id}"
}

output "health_equity_metrics_table_id" {
  description = "Full ID of the health equity metrics table"
  value       = "${google_bigquery_table.health_equity_metrics.project}.${google_bigquery_table.health_equity_metrics.dataset_id}.${google_bigquery_table.health_equity_metrics.table_id}"
}

# All dataset IDs for reference
output "all_dataset_ids" {
  description = "List of all created BigQuery dataset IDs"
  value = [
    google_bigquery_dataset.raw_data.dataset_id,
    google_bigquery_dataset.processed_data.dataset_id,
    google_bigquery_dataset.analytics.dataset_id
  ]
}

# All table IDs for reference
output "all_table_ids" {
  description = "List of all created BigQuery table IDs"
  value = [
    google_bigquery_table.providers_raw.table_id,
    google_bigquery_table.travel_matrix.table_id,
    google_bigquery_table.health_equity_metrics.table_id
  ]
}

# Cost optimization summary
output "cost_optimization_features" {
  description = "Summary of cost optimization features implemented"
  value = {
    partitioning_enabled = true
    clustering_enabled   = true
    expiration_policies  = true
    time_travel_minimal  = true
    query_cost_controls  = var.enable_cost_controls
  }
} 