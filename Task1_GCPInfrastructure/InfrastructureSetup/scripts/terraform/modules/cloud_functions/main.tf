# Cloud Functions Module for LA County Cardiology Access Optimizer
# Cost-optimized ETL functions replacing Dataflow for 60% cost reduction

# Data Ingestion Function - Process raw provider data from CA Medical Board
resource "google_cloudfunctions2_function" "data_ingestion" {
  name     = "la-cardio-data-ingestion"
  location = var.region
  project  = var.project_id

  description = "Ingests and validates raw cardiologist provider data from CA Medical Board"

  build_config {
    runtime     = "python311"
    entry_point = "process_provider_data"
    
    source {
      storage_source {
        bucket = var.functions_bucket_name
        object = "data-ingestion-function.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 10
    min_instance_count             = 0
    available_memory               = "512Mi"
    timeout_seconds                = 300
    max_instance_request_concurrency = 1
    available_cpu                  = "0.5"
    
    environment_variables = {
      RAW_DATA_DATASET    = var.raw_data_dataset_id
      PROCESSED_DATASET   = var.processed_data_dataset_id
      PROJECT_ID          = var.project_id
      LOG_LEVEL          = var.log_level
      ENABLE_HIPAA_LOGGING = "true"
    }
    
    service_account_email = var.data_processing_sa_email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    
    event_filters {
      attribute = "bucket"
      value     = var.raw_data_bucket_name
    }
    
    event_filters {
      attribute = "objectNamePrefix"
      value     = "providers/"
    }
    
    retry_policy = "RETRY_POLICY_RETRY"
  }

  labels = {
    function_type    = "data-ingestion"
    cost_optimization = "memory-optimized"
    environment      = var.environment
    compliance       = "hipaa-applicable"
  }
}

# Travel Matrix Calculator Function - Process travel time calculations
resource "google_cloudfunctions2_function" "travel_matrix_calculator" {
  name     = "la-cardio-travel-matrix"
  location = var.region
  project  = var.project_id

  description = "Calculates multi-modal travel times between ZIP codes and providers (900k+ calculations)"

  build_config {
    runtime     = "python311"
    entry_point = "calculate_travel_matrix"
    
    source {
      storage_source {
        bucket = var.functions_bucket_name
        object = "travel-matrix-function.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 20
    min_instance_count             = 0
    available_memory               = "1Gi"
    timeout_seconds                = 540  # 9 minutes for complex calculations
    max_instance_request_concurrency = 1
    available_cpu                  = "1"
    
    environment_variables = {
      PROCESSED_DATASET   = var.processed_data_dataset_id
      ANALYTICS_DATASET   = var.analytics_dataset_id
      PROJECT_ID          = var.project_id
      OPENROUTESERVICE_API_KEY = var.openrouteservice_api_key
      GTFS_BUCKET         = var.processed_data_bucket_name
      MAX_TRAVEL_TIME_MINUTES = "120"
      TRANSPORT_MODES     = "driving,transit,walking"
    }
    
    service_account_email = var.data_processing_sa_email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    
    event_filters {
      attribute = "bucket"
      value     = var.processed_data_bucket_name
    }
    
    event_filters {
      attribute = "objectNamePrefix"
      value     = "geocoded-providers/"
    }
    
    retry_policy = "RETRY_POLICY_RETRY"
  }

  labels = {
    function_type     = "travel-calculation"
    cost_optimization = "memory-optimized"
    performance_target = "900k-calculations"
    environment       = var.environment
  }
}

# Health Equity Metrics Calculator - Generate disparity analysis
resource "google_cloudfunctions2_function" "health_equity_calculator" {
  name     = "la-cardio-health-equity"
  location = var.region
  project  = var.project_id

  description = "Calculates health equity metrics and access disparities by supervisorial district"

  build_config {
    runtime     = "python311"
    entry_point = "calculate_health_equity"
    
    source {
      storage_source {
        bucket = var.functions_bucket_name
        object = "health-equity-function.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 5
    min_instance_count             = 0
    available_memory               = "1Gi"
    timeout_seconds                = 300
    max_instance_request_concurrency = 1
    available_cpu                  = "1"
    
    environment_variables = {
      PROCESSED_DATASET   = var.processed_data_dataset_id
      ANALYTICS_DATASET   = var.analytics_dataset_id
      PROJECT_ID          = var.project_id
      MIN_CELL_SIZE       = "11"  # HIPAA small cell suppression
      CONFIDENCE_LEVEL    = "0.95"
      SUPERVISORIAL_DISTRICTS = "1,2,3,4,5"
    }
    
    service_account_email = var.data_processing_sa_email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    
    event_filters {
      attribute = "bucket"
      value     = var.processed_data_bucket_name
    }
    
    event_filters {
      attribute = "objectNamePrefix"
      value     = "travel-matrix/"
    }
    
    retry_policy = "RETRY_POLICY_RETRY"
  }

  labels = {
    function_type     = "health-equity"
    cost_optimization = "memory-optimized"
    compliance        = "hipaa-small-cell-suppression"
    environment       = var.environment
  }
}

# Data Validation Function - Quality checks and HIPAA compliance
resource "google_cloudfunctions2_function" "data_validator" {
  name     = "la-cardio-data-validator"
  location = var.region
  project  = var.project_id

  description = "Validates data quality and ensures HIPAA compliance with small cell suppression"

  build_config {
    runtime     = "python311"
    entry_point = "validate_data_quality"
    
    source {
      storage_source {
        bucket = var.functions_bucket_name
        object = "data-validator-function.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 5
    min_instance_count             = 0
    available_memory               = "512Mi"
    timeout_seconds                = 180
    max_instance_request_concurrency = 1
    available_cpu                  = "0.5"
    
    environment_variables = {
      RAW_DATA_DATASET    = var.raw_data_dataset_id
      PROCESSED_DATASET   = var.processed_data_dataset_id
      PROJECT_ID          = var.project_id
      MIN_CELL_SIZE       = "11"
      VALIDATION_RULES    = "provider_address,zip_code,specialty"
      ALERT_EMAIL         = var.alert_email
    }
    
    service_account_email = var.data_processing_sa_email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    
    event_filters {
      attribute = "bucket"
      value     = var.raw_data_bucket_name
    }
    
    event_filters {
      attribute = "objectNamePrefix"
      value     = "validation/"
    }
    
    retry_policy = "RETRY_POLICY_RETRY"
  }

  labels = {
    function_type     = "data-validation"
    cost_optimization = "memory-optimized"
    compliance        = "hipaa-validation"
    environment       = var.environment
  }
}

# HTTP Trigger Function for Manual Data Processing
resource "google_cloudfunctions2_function" "manual_processor" {
  name     = "la-cardio-manual-processor"
  location = var.region
  project  = var.project_id

  description = "HTTP-triggered function for manual data processing and testing"

  build_config {
    runtime     = "python311"
    entry_point = "process_manual_request"
    
    source {
      storage_source {
        bucket = var.functions_bucket_name
        object = "manual-processor-function.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 3
    min_instance_count             = 0
    available_memory               = "512Mi"
    timeout_seconds                = 300
    max_instance_request_concurrency = 1
    available_cpu                  = "0.5"
    
    environment_variables = {
      RAW_DATA_DATASET    = var.raw_data_dataset_id
      PROCESSED_DATASET   = var.processed_data_dataset_id
      ANALYTICS_DATASET   = var.analytics_dataset_id
      PROJECT_ID          = var.project_id
      ENABLE_MANUAL_PROCESSING = "true"
    }
    
    service_account_email = var.data_processing_sa_email
  }

  labels = {
    function_type     = "manual-processing"
    cost_optimization = "memory-optimized"
    trigger_type      = "http"
    environment       = var.environment
  }
}

# Cost Optimization: Function Scheduling for Batch Processing
resource "google_cloud_scheduler_job" "batch_processor" {
  count    = var.enable_batch_processing ? 1 : 0
  name     = "la-cardio-batch-processor"
  region   = var.region
  project  = var.project_id

  description = "Scheduled batch processing for cost-optimized ETL during off-peak hours"
  schedule    = "0 2 * * *"  # Daily at 2 AM PT for cost efficiency
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = google_cloudfunctions2_function.manual_processor.service_config[0].uri
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      operation = "batch_process"
      mode      = "cost_optimized"
      priority  = "low"
    }))
    
    oidc_token {
      service_account_email = var.data_processing_sa_email
      audience              = google_cloudfunctions2_function.manual_processor.service_config[0].uri
    }
  }

  retry_config {
    retry_count          = 3
    max_retry_duration   = "300s"
    max_backoff_duration = "60s"
    min_backoff_duration = "5s"
  }
}

# Cost Monitoring: Function Billing Alerts
resource "google_monitoring_alert_policy" "function_cost_alert" {
  count = var.enable_cost_monitoring ? 1 : 0
  
  display_name = "LA Cardio Cloud Functions Cost Alert"
  project      = var.project_id
  combiner     = "OR"
  
  documentation {
    content = "Alert when Cloud Functions costs exceed budget thresholds for LA Cardiology Optimizer"
  }
  
  conditions {
    display_name = "Function Cost Threshold"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND resource.labels.function_name=~\"la-cardio-.*\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.function_cost_threshold_usd
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  alert_strategy {
    auto_close = "1800s"  # 30 minutes
  }
  
  notification_channels = var.notification_channels
}

# IAM Binding for Cloud Functions Invoker Role
resource "google_cloud_run_service_iam_binding" "functions_invoker" {
  for_each = toset([
    google_cloudfunctions2_function.data_ingestion.name,
    google_cloudfunctions2_function.travel_matrix_calculator.name,
    google_cloudfunctions2_function.health_equity_calculator.name,
    google_cloudfunctions2_function.data_validator.name,
    google_cloudfunctions2_function.manual_processor.name
  ])
  
  location = var.region
  project  = var.project_id
  service  = each.value
  role     = "roles/run.invoker"
  
  members = [
    "serviceAccount:${var.data_processing_sa_email}",
    "serviceAccount:${var.functions_sa_email}"
  ]
} 