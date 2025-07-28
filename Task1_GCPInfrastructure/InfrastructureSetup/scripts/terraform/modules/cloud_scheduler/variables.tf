# Variables for Cloud Scheduler Module

# Basic Project Configuration
variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Scheduler jobs (us-west1 for LA County proximity)"
  type        = string
  default     = "us-west1"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

# Cloud Functions Integration (from cloud_functions module outputs)
variable "manual_processor_function_uri" {
  description = "URI of the manual processor Cloud Function for orchestration"
  type        = string
}

# Service Account Emails (from storage module outputs)
variable "data_processing_sa_email" {
  description = "Email of the data processing service account"
  type        = string
}

variable "functions_sa_email" {
  description = "Email of the Cloud Functions service account"
  type        = string
}

# Notification Configuration
variable "alert_email" {
  description = "Email address for scheduling alerts and notifications"
  type        = string
  default     = ""
}

# Scheduling Control Features
variable "enable_continuous_validation" {
  description = "Enable continuous data validation every 2 hours"
  type        = bool
  default     = true
}

variable "enable_cost_monitoring" {
  description = "Enable daily cost monitoring and budget tracking"
  type        = bool
  default     = true
}

variable "enable_emergency_processing" {
  description = "Enable emergency processing scheduler job (paused by default)"
  type        = bool
  default     = true
}

variable "enable_health_checks" {
  description = "Enable regular health checks for system components"
  type        = bool
  default     = true
}

variable "enable_resource_cleanup" {
  description = "Enable automated resource cleanup for cost optimization"
  type        = bool
  default     = true
}

# Cost Optimization Settings
variable "budget_thresholds" {
  description = "Budget alert thresholds in USD for cost monitoring"
  type        = list(number)
  default     = [50, 75, 100]
}

variable "off_peak_hours_only" {
  description = "Restrict expensive operations to off-peak hours for cost efficiency"
  type        = bool
  default     = true
}

variable "batch_size_limit" {
  description = "Maximum batch size for travel matrix calculations to control costs"
  type        = number
  default     = 1000
}

# Healthcare Compliance Settings
variable "hipaa_compliance_enabled" {
  description = "Enable HIPAA compliance features in scheduled jobs"
  type        = bool
  default     = true
}

variable "data_retention_days" {
  description = "Data retention period for notifications and logs"
  type        = number
  default     = 7
}

# Schedule Customization
variable "provider_ingestion_schedule" {
  description = "Cron schedule for provider data ingestion (default: daily 1 AM PT)"
  type        = string
  default     = "0 1 * * *"
}

variable "travel_matrix_schedule" {
  description = "Cron schedule for travel matrix calculation (default: weekly Sunday 2 AM PT)"
  type        = string
  default     = "0 2 * * 0"
}

variable "health_equity_schedule" {
  description = "Cron schedule for health equity calculations (default: daily 3 AM PT)"
  type        = string
  default     = "0 3 * * *"
}

variable "validation_schedule" {
  description = "Cron schedule for data validation (default: every 2 hours, 6 AM-10 PM PT)"
  type        = string
  default     = "0 */2 6-22 * * *"
}

variable "cost_monitoring_schedule" {
  description = "Cron schedule for cost monitoring (default: daily 8 AM PT)"
  type        = string
  default     = "0 8 * * *"
}

variable "health_check_schedule" {
  description = "Cron schedule for health checks (default: every 15 minutes, 6 AM-10 PM PT)"
  type        = string
  default     = "*/15 6-22 * * *"
}

variable "cleanup_schedule" {
  description = "Cron schedule for resource cleanup (default: weekly Monday 4 AM PT)"
  type        = string
  default     = "0 4 * * 1"
}

variable "monthly_refresh_schedule" {
  description = "Cron schedule for monthly data refresh (default: 1st of month midnight PT)"
  type        = string
  default     = "0 0 1 * *"
}

# Retry Configuration
variable "default_retry_count" {
  description = "Default retry count for scheduler jobs"
  type        = number
  default     = 3
  
  validation {
    condition     = var.default_retry_count >= 1 && var.default_retry_count <= 5
    error_message = "Retry count must be between 1 and 5."
  }
}

variable "default_retry_duration" {
  description = "Default maximum retry duration in seconds"
  type        = number
  default     = 600
}

# Advanced Configuration
variable "time_zone" {
  description = "Time zone for all scheduled jobs"
  type        = string
  default     = "America/Los_Angeles"
  
  validation {
    condition = contains([
      "America/Los_Angeles",
      "America/New_York", 
      "UTC"
    ], var.time_zone)
    error_message = "Time zone must be one of: America/Los_Angeles, America/New_York, UTC."
  }
}

variable "transport_modes" {
  description = "List of transportation modes for travel matrix calculations"
  type        = list(string)
  default     = ["driving", "transit", "walking"]
  
  validation {
    condition = alltrue([
      for mode in var.transport_modes : contains(["driving", "transit", "walking"], mode)
    ])
    error_message = "Transport modes must be from: driving, transit, walking."
  }
}

variable "supervisorial_districts" {
  description = "List of LA County supervisorial districts for health equity calculations"
  type        = list(number)
  default     = [1, 2, 3, 4, 5]
  
  validation {
    condition = alltrue([
      for district in var.supervisorial_districts : district >= 1 && district <= 5
    ])
    error_message = "Supervisorial districts must be between 1 and 5."
  }
}

variable "confidence_level" {
  description = "Statistical confidence level for health equity calculations"
  type        = number
  default     = 0.95
  
  validation {
    condition     = var.confidence_level > 0 && var.confidence_level < 1
    error_message = "Confidence level must be between 0 and 1."
  }
}

variable "min_cell_size" {
  description = "Minimum cell size for HIPAA small cell suppression"
  type        = number
  default     = 11
  
  validation {
    condition     = var.min_cell_size >= 5
    error_message = "Minimum cell size must be at least 5 for healthcare data protection."
  }
}

# Pub/Sub Configuration
variable "notification_retention_days" {
  description = "Retention period for notification messages in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.notification_retention_days >= 1 && var.notification_retention_days <= 30
    error_message = "Notification retention must be between 1 and 30 days."
  }
}

variable "enable_notification_system" {
  description = "Enable Pub/Sub notification system for job failures and alerts"
  type        = bool
  default     = true
}

# Emergency Processing Configuration
variable "emergency_bypass_cost_controls" {
  description = "Allow emergency processing to bypass cost controls (use with caution)"
  type        = bool
  default     = false
}

variable "emergency_alert_on_completion" {
  description = "Send alert notifications when emergency processing completes"
  type        = bool
  default     = true
}

# Resource Management
variable "cleanup_actions" {
  description = "List of cleanup actions for cost optimization"
  type        = list(string)
  default     = [
    "delete_old_logs",
    "archive_processed_data", 
    "optimize_storage_classes",
    "cleanup_temp_tables"
  ]
}

variable "health_check_components" {
  description = "List of components to include in health checks"
  type        = list(string)
  default     = [
    "bigquery_datasets",
    "storage_buckets",
    "cloud_functions", 
    "api_endpoints"
  ]
} 