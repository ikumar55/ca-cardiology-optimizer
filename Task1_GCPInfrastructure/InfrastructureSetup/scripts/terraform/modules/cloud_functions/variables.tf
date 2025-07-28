# Variables for Cloud Functions Module

# Basic Project Configuration
variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Functions deployment (us-west1 for LA County proximity)"
  type        = string
  default     = "us-west1"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

# BigQuery Dataset IDs (from bigquery module outputs)
variable "raw_data_dataset_id" {
  description = "BigQuery dataset ID for raw healthcare data"
  type        = string
}

variable "processed_data_dataset_id" {
  description = "BigQuery dataset ID for processed analytics data"
  type        = string
}

variable "analytics_dataset_id" {
  description = "BigQuery dataset ID for final analytics results"
  type        = string
}

# Cloud Storage Bucket Names (from storage module outputs)
variable "functions_bucket_name" {
  description = "Cloud Storage bucket name for Cloud Functions source code"
  type        = string
}

variable "raw_data_bucket_name" {
  description = "Cloud Storage bucket name for raw healthcare data"
  type        = string
}

variable "processed_data_bucket_name" {
  description = "Cloud Storage bucket name for processed data"
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

# API Keys and External Services
variable "openrouteservice_api_key" {
  description = "API key for OpenRouteService travel time calculations"
  type        = string
  default     = ""
  sensitive   = true
}

variable "alert_email" {
  description = "Email address for data validation alerts and notifications"
  type        = string
  default     = ""
}

# Cost Optimization Settings
variable "function_cost_threshold_usd" {
  description = "Cost threshold in USD for Cloud Functions billing alerts"
  type        = number
  default     = 10.00
}

variable "enable_cost_monitoring" {
  description = "Enable cost monitoring and alerts for Cloud Functions"
  type        = bool
  default     = true
}

variable "notification_channels" {
  description = "List of notification channel IDs for cost alerts"
  type        = list(string)
  default     = []
}

# Optional Features
variable "enable_batch_processing" {
  description = "Enable scheduled batch processing for cost optimization"
  type        = bool
  default     = true
}

variable "log_level" {
  description = "Logging level for Cloud Functions (DEBUG, INFO, WARNING, ERROR)"
  type        = string
  default     = "INFO"
  
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

# Function Configuration
variable "max_function_instances" {
  description = "Maximum number of function instances for cost control"
  type        = map(number)
  default = {
    data_ingestion         = 10
    travel_matrix         = 20
    health_equity         = 5
    data_validator        = 5
    manual_processor      = 3
  }
}

variable "function_memory_limits" {
  description = "Memory limits for different function types (cost optimization)"
  type        = map(string)
  default = {
    data_ingestion         = "512Mi"
    travel_matrix         = "1Gi"
    health_equity         = "1Gi"
    data_validator        = "512Mi"
    manual_processor      = "512Mi"
  }
}

variable "function_timeout_seconds" {
  description = "Timeout settings for different function types"
  type        = map(number)
  default = {
    data_ingestion         = 300    # 5 minutes
    travel_matrix         = 540    # 9 minutes
    health_equity         = 300    # 5 minutes
    data_validator        = 180    # 3 minutes
    manual_processor      = 300    # 5 minutes
  }
}

# Healthcare Compliance Settings
variable "hipaa_compliance_enabled" {
  description = "Enable HIPAA compliance features for healthcare data"
  type        = bool
  default     = true
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

variable "confidence_level" {
  description = "Statistical confidence level for health equity calculations"
  type        = number
  default     = 0.95
  
  validation {
    condition     = var.confidence_level > 0 && var.confidence_level < 1
    error_message = "Confidence level must be between 0 and 1."
  }
}

# Travel Time Calculation Settings
variable "max_travel_time_minutes" {
  description = "Maximum travel time to consider for accessibility calculations"
  type        = number
  default     = 120
}

variable "transport_modes" {
  description = "List of transportation modes for travel time calculations"
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
  description = "List of LA County supervisorial districts (1-5)"
  type        = list(number)
  default     = [1, 2, 3, 4, 5]
  
  validation {
    condition = alltrue([
      for district in var.supervisorial_districts : district >= 1 && district <= 5
    ])
    error_message = "Supervisorial districts must be between 1 and 5."
  }
} 