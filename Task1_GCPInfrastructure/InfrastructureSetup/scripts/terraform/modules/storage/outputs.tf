# Outputs for Storage Module

# Raw data bucket outputs
output "raw_data_bucket_name" {
  description = "Name of the raw data bucket"
  value       = google_storage_bucket.la_cardio_raw_data.name
}

output "raw_data_bucket_url" {
  description = "URL of the raw data bucket"
  value       = google_storage_bucket.la_cardio_raw_data.url
}

# Processed data bucket outputs
output "processed_data_bucket_name" {
  description = "Name of the processed data bucket"
  value       = google_storage_bucket.la_cardio_processed.name
}

output "processed_data_bucket_url" {
  description = "URL of the processed data bucket"
  value       = google_storage_bucket.la_cardio_processed.url
}

# Functions bucket outputs
output "functions_bucket_name" {
  description = "Name of the Cloud Functions bucket"
  value       = google_storage_bucket.la_cardio_functions.name
}

output "functions_bucket_url" {
  description = "URL of the Cloud Functions bucket"
  value       = google_storage_bucket.la_cardio_functions.url
}

# Terraform state bucket outputs
output "terraform_state_bucket_name" {
  description = "Name of the Terraform state bucket"
  value       = google_storage_bucket.la_cardio_terraform_state.name
}

output "terraform_state_bucket_url" {
  description = "URL of the Terraform state bucket"
  value       = google_storage_bucket.la_cardio_terraform_state.url
}

# All bucket names for reference
output "all_bucket_names" {
  description = "List of all created bucket names"
  value = [
    google_storage_bucket.la_cardio_raw_data.name,
    google_storage_bucket.la_cardio_processed.name,
    google_storage_bucket.la_cardio_functions.name,
    google_storage_bucket.la_cardio_terraform_state.name
  ]
}

# Service Account Outputs for Cloud Functions Module
output "data_ingestion_sa_email" {
  description = "Email of the data ingestion service account"
  value       = google_service_account.data_ingestion_sa.email
}

output "data_processing_sa_email" {
  description = "Email of the data processing service account"
  value       = google_service_account.data_processing_sa.email
}

output "functions_sa_email" {
  description = "Email of the Cloud Functions service account"
  value       = google_service_account.functions_sa.email
}

# All service account emails for reference
output "all_service_account_emails" {
  description = "List of all created service account emails"
  value = [
    google_service_account.data_ingestion_sa.email,
    google_service_account.data_processing_sa.email,
    google_service_account.functions_sa.email
  ]
} 