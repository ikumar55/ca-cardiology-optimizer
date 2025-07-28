# Cloud Scheduler Module for LA County Cardiology Access Optimizer
# Cost-efficient orchestration replacing Prefect for licensing cost elimination

# Daily Provider Data Ingestion Schedule - Early Morning (Cost Optimization)
resource "google_cloud_scheduler_job" "daily_provider_ingestion" {
  name     = "la-cardio-daily-provider-ingestion"
  region   = var.region
  project  = var.project_id

  description = "Daily ingestion of CA Medical Board provider data during off-peak hours"
  schedule    = "0 1 * * *"  # Daily at 1 AM PT for cost efficiency
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "provider_ingestion"
      mode      = "scheduled"
      priority  = "high"
      source    = "ca_medical_board"
      validate  = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 3
    max_retry_duration   = "600s"
    max_backoff_duration = "120s"
    min_backoff_duration = "10s"
  }
}

# Weekly Travel Matrix Calculation - Off-Peak Hours for Cost Efficiency
resource "google_cloud_scheduler_job" "weekly_travel_matrix" {
  name     = "la-cardio-weekly-travel-matrix"
  region   = var.region
  project  = var.project_id

  description = "Weekly travel matrix calculation for 900k+ calculations during off-peak hours"
  schedule    = "0 2 * * 0"  # Weekly on Sunday at 2 AM PT for cost efficiency
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "travel_matrix_calculation"
      mode      = "scheduled_batch"
      priority  = "medium"
      transport_modes = ["driving", "transit", "walking"]
      batch_size = 1000
      cost_optimized = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 2
    max_retry_duration   = "1800s"  # 30 minutes for large batch
    max_backoff_duration = "300s"
    min_backoff_duration = "30s"
  }
}

# Daily Health Equity Metrics Calculation
resource "google_cloud_scheduler_job" "daily_health_equity" {
  name     = "la-cardio-daily-health-equity"
  region   = var.region
  project  = var.project_id

  description = "Daily health equity metrics calculation by supervisorial district"
  schedule    = "0 3 * * *"  # Daily at 3 AM PT (after travel matrix if needed)
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "health_equity_calculation"
      mode      = "scheduled"
      priority  = "high"
      supervisorial_districts = [1, 2, 3, 4, 5]
      confidence_level = 0.95
      min_cell_size = 11
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 3
    max_retry_duration   = "900s"
    max_backoff_duration = "180s"
    min_backoff_duration = "15s"
  }
}

# Hourly Data Validation and Quality Checks
resource "google_cloud_scheduler_job" "hourly_data_validation" {
  count = var.enable_continuous_validation ? 1 : 0
  
  name     = "la-cardio-hourly-validation"
  region   = var.region
  project  = var.project_id

  description = "Hourly data validation and HIPAA compliance checks"
  schedule    = "0 */2 6-22 * * *"  # Every 2 hours from 6 AM to 10 PM PT
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "data_validation"
      mode      = "continuous"
      priority  = "medium"
      validation_rules = ["provider_address", "zip_code", "specialty", "hipaa_compliance"]
      alert_on_failure = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 1
    max_retry_duration   = "300s"
    max_backoff_duration = "60s"
    min_backoff_duration = "5s"
  }
}

# Monthly Data Refresh and Archive Schedule
resource "google_cloud_scheduler_job" "monthly_data_refresh" {
  name     = "la-cardio-monthly-refresh"
  region   = var.region
  project  = var.project_id

  description = "Monthly data refresh and archival for cost optimization"
  schedule    = "0 0 1 * *"  # Monthly on the 1st at midnight PT
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "monthly_refresh"
      mode      = "maintenance"
      priority  = "low"
      archive_old_data = true
      refresh_all_datasets = true
      cost_optimization = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 2
    max_retry_duration   = "3600s"  # 1 hour for monthly maintenance
    max_backoff_duration = "600s"
    min_backoff_duration = "60s"
  }
}

# Cost Monitoring and Alerting Schedule
resource "google_cloud_scheduler_job" "cost_monitoring" {
  count = var.enable_cost_monitoring ? 1 : 0
  
  name     = "la-cardio-cost-monitoring"
  region   = var.region
  project  = var.project_id

  description = "Daily cost monitoring and budget tracking for GCP resources"
  schedule    = "0 8 * * *"  # Daily at 8 AM PT for business hours reporting
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "cost_monitoring"
      mode      = "daily_report"
      priority  = "medium"
      budget_thresholds = [50, 75, 100]
      alert_email = var.alert_email
      generate_report = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 2
    max_retry_duration   = "300s"
    max_backoff_duration = "60s"
    min_backoff_duration = "10s"
  }
}

# Emergency Data Processing Schedule (On-Demand Trigger)
resource "google_cloud_scheduler_job" "emergency_processing" {
  count = var.enable_emergency_processing ? 1 : 0
  
  name     = "la-cardio-emergency-processing"
  region   = var.region
  project  = var.project_id

  description = "Emergency data processing for urgent health equity analysis (paused by default)"
  schedule    = "0 */6 * * *"  # Every 6 hours (can be triggered manually)
  time_zone   = "America/Los_Angeles"
  paused      = true  # Paused by default, can be enabled manually

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "emergency_processing"
      mode      = "urgent"
      priority  = "critical"
      bypass_cost_controls = false
      alert_on_completion = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 1
    max_retry_duration   = "1800s"
    max_backoff_duration = "300s"
    min_backoff_duration = "30s"
  }
}

# Job Failure Notification Setup via Pub/Sub
resource "google_pubsub_topic" "scheduler_notifications" {
  name    = "la-cardio-scheduler-notifications"
  project = var.project_id

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }

  labels = {
    environment = var.environment
    purpose     = "scheduler-notifications"
    compliance  = "hipaa-applicable"
  }
}

resource "google_pubsub_subscription" "scheduler_alerts" {
  name    = "la-cardio-scheduler-alerts"
  project = var.project_id
  topic   = google_pubsub_topic.scheduler_notifications.name

  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  ack_deadline_seconds       = 20

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  labels = {
    environment = var.environment
    purpose     = "alert-processing"
  }
}

# Job Health Check Schedule
resource "google_cloud_scheduler_job" "health_check" {
  name     = "la-cardio-health-check"
  region   = var.region
  project  = var.project_id

  description = "Health check for all ETL pipeline components and dependencies"
  schedule    = "*/15 6-22 * * *"  # Every 15 minutes from 6 AM to 10 PM PT
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "health_check"
      mode      = "system_status"
      priority  = "low"
      check_components = [
        "bigquery_datasets",
        "storage_buckets", 
        "cloud_functions",
        "api_endpoints"
      ]
      alert_on_failure = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 1
    max_retry_duration   = "120s"
    max_backoff_duration = "30s"
    min_backoff_duration = "5s"
  }
}

# Resource Cleanup Schedule for Cost Optimization
resource "google_cloud_scheduler_job" "resource_cleanup" {
  name     = "la-cardio-resource-cleanup"
  region   = var.region
  project  = var.project_id

  description = "Automated resource cleanup for cost optimization and maintenance"
  schedule    = "0 4 * * 1"  # Weekly on Monday at 4 AM PT
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = var.manual_processor_function_uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "resource_cleanup"
      mode      = "maintenance"
      priority  = "low"
      cleanup_actions = [
        "delete_old_logs",
        "archive_processed_data",
        "optimize_storage_classes",
        "cleanup_temp_tables"
      ]
      cost_optimization = true
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = var.manual_processor_function_uri
    }
  }

  retry_config {
    retry_count          = 2
    max_retry_duration   = "1800s"
    max_backoff_duration = "300s"
    min_backoff_duration = "30s"
  }
}

# IAM for Pub/Sub Topic Access
resource "google_pubsub_topic_iam_binding" "scheduler_publisher" {
  topic   = google_pubsub_topic.scheduler_notifications.name
  role    = "roles/pubsub.publisher"
  project = var.project_id

  members = [
    "serviceAccount:${var.data_processing_sa_email}",
    "serviceAccount:${var.functions_sa_email}"
  ]
}

resource "google_pubsub_subscription_iam_binding" "scheduler_subscriber" {
  subscription = google_pubsub_subscription.scheduler_alerts.name
  role         = "roles/pubsub.subscriber"
  project      = var.project_id

  members = [
    "serviceAccount:${var.data_processing_sa_email}"
  ]
} 