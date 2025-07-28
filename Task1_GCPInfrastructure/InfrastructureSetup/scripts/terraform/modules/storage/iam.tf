# IAM Configuration for Storage Buckets
# Implements least privilege access model for healthcare data

# Service Account for data ingestion
resource "google_service_account" "data_ingestion_sa" {
  account_id   = "la-data-ingestion-sa"
  display_name = "LA County Data Ingestion Service Account"
  description  = "Service account for ingesting raw healthcare data"
}

# Service Account for data processing
resource "google_service_account" "data_processing_sa" {
  account_id   = "la-data-processing-sa"
  display_name = "LA County Data Processing Service Account"
  description  = "Service account for processing and transforming healthcare data"
}

# Service Account for Cloud Functions
resource "google_service_account" "functions_sa" {
  account_id   = "la-functions-sa"
  display_name = "LA County Cloud Functions Service Account"
  description  = "Service account for Cloud Functions execution"
}

# IAM binding for raw data bucket - data ingestion SA has write access
resource "google_storage_bucket_iam_binding" "raw_data_writer" {
  bucket = google_storage_bucket.la_cardio_raw_data.name
  role   = "roles/storage.objectCreator"

  members = [
    "serviceAccount:${google_service_account.data_ingestion_sa.email}",
  ]
}

# IAM binding for raw data bucket - processing SA has read access
resource "google_storage_bucket_iam_binding" "raw_data_reader" {
  bucket = google_storage_bucket.la_cardio_raw_data.name
  role   = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.data_processing_sa.email}",
    "serviceAccount:${google_service_account.functions_sa.email}",
  ]
}

# IAM binding for processed data bucket - processing SA has full access
resource "google_storage_bucket_iam_binding" "processed_data_admin" {
  bucket = google_storage_bucket.la_cardio_processed.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${google_service_account.data_processing_sa.email}",
    "serviceAccount:${google_service_account.functions_sa.email}",
  ]
}

# IAM binding for functions bucket - functions SA has full access
resource "google_storage_bucket_iam_binding" "functions_admin" {
  bucket = google_storage_bucket.la_cardio_functions.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${google_service_account.functions_sa.email}",
  ]
}

# IAM binding for terraform state bucket - only Terraform SA has access
resource "google_storage_bucket_iam_binding" "terraform_state_admin" {
  bucket = google_storage_bucket.la_cardio_terraform_state.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:terraform-automation@${var.project_id}.iam.gserviceaccount.com",
  ]
}

# Cross-bucket access for analytics - functions SA can read from all buckets
resource "google_storage_bucket_iam_binding" "analytics_cross_access" {
  for_each = toset([
    google_storage_bucket.la_cardio_raw_data.name,
    google_storage_bucket.la_cardio_processed.name
  ])
  
  bucket = each.value
  role   = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.functions_sa.email}",
  ]
} 