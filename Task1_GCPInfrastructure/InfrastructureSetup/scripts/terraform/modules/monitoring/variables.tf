# Variables for Monitoring Module

# Basic Project Configuration
variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for monitoring resources (us-west1 for LA County proximity)"
  type        = string
  default     = "us-west1"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

# Budget Management Configuration
variable "billing_account_id" {
  description = "GCP Billing Account ID for budget management and cost tracking"
  type        = string
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD for LA County cardiology healthcare project"
  type        = number
  default     = 100
  
  validation {
    condition     = var.monthly_budget_limit >= 10 && var.monthly_budget_limit <= 1000
    error_message = "Monthly budget limit must be between $10 and $1000."
  }
}

variable "bigquery_daily_cost_limit" {
  description = "Daily cost limit for BigQuery operations in USD"
  type        = number
  default     = 20
  
  validation {
    condition     = var.bigquery_daily_cost_limit >= 5 && var.bigquery_daily_cost_limit <= 100
    error_message = "BigQuery daily cost limit must be between $5 and $100."
  }
}

# Notification Configuration
variable "budget_alert_email" {
  description = "Email address for budget alerts and cost management notifications"
  type        = string
  default     = ""
}

variable "infrastructure_alert_email" {
  description = "Email address for infrastructure alerts and performance notifications"
  type        = string
  default     = ""
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for budget and infrastructure alerts"
  type        = string
  default     = ""
  sensitive   = true
}

variable "slack_channel" {
  description = "Slack channel name for notifications (e.g., #la-cardio-alerts)"
  type        = string
  default     = "#alerts"
}

# Monitoring Feature Toggles
variable "enable_uptime_checks" {
  description = "Enable uptime checks for critical services"
  type        = bool
  default     = true
}

variable "enable_resource_monitoring" {
  description = "Enable resource utilization monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_performance_monitoring" {
  description = "Enable performance monitoring for BigQuery and Cloud Functions"
  type        = bool
  default     = true
}

variable "enable_security_monitoring" {
  description = "Enable security event monitoring and compliance tracking"
  type        = bool
  default     = true
}

variable "enable_cost_optimization_alerts" {
  description = "Enable cost optimization alerts and recommendations"
  type        = bool
  default     = true
}

# Performance Thresholds
variable "function_memory_threshold_mb" {
  description = "Memory threshold in MB for Cloud Functions alerting"
  type        = number
  default     = 450  # Alert when approaching 512MB limit
  
  validation {
    condition     = var.function_memory_threshold_mb >= 100 && var.function_memory_threshold_mb <= 8192
    error_message = "Function memory threshold must be between 100MB and 8192MB."
  }
}

variable "bigquery_job_duration_threshold_seconds" {
  description = "Duration threshold in seconds for BigQuery job alerting"
  type        = number
  default     = 300  # 5 minutes
  
  validation {
    condition     = var.bigquery_job_duration_threshold_seconds >= 60 && var.bigquery_job_duration_threshold_seconds <= 3600
    error_message = "BigQuery job duration threshold must be between 60 seconds and 1 hour."
  }
}

variable "function_error_rate_threshold" {
  description = "Error rate threshold (0.0-1.0) for Cloud Functions alerting"
  type        = number
  default     = 0.05  # 5%
  
  validation {
    condition     = var.function_error_rate_threshold >= 0.01 && var.function_error_rate_threshold <= 0.5
    error_message = "Function error rate threshold must be between 1% and 50%."
  }
}

# Healthcare Compliance Monitoring
variable "enable_hipaa_compliance_monitoring" {
  description = "Enable HIPAA compliance monitoring and audit logging"
  type        = bool
  default     = true
}

variable "enable_phi_access_monitoring" {
  description = "Enable PHI access monitoring for healthcare data protection"
  type        = bool
  default     = true
}

variable "compliance_alert_email" {
  description = "Email address for healthcare compliance alerts"
  type        = string
  default     = ""
}

variable "audit_log_retention_days" {
  description = "Retention period for audit logs in days (healthcare compliance)"
  type        = number
  default     = 2555  # 7 years for healthcare compliance
  
  validation {
    condition     = var.audit_log_retention_days >= 365
    error_message = "Audit log retention must be at least 365 days for healthcare compliance."
  }
}

# Dashboard Configuration
variable "enable_infrastructure_dashboard" {
  description = "Enable infrastructure overview dashboard"
  type        = bool
  default     = true
}

variable "enable_cost_management_dashboard" {
  description = "Enable cost management and budget tracking dashboard"
  type        = bool
  default     = true
}

variable "enable_healthcare_compliance_dashboard" {
  description = "Enable healthcare compliance and security dashboard"
  type        = bool
  default     = true
}

variable "dashboard_refresh_interval" {
  description = "Dashboard refresh interval in minutes"
  type        = number
  default     = 5
  
  validation {
    condition     = var.dashboard_refresh_interval >= 1 && var.dashboard_refresh_interval <= 60
    error_message = "Dashboard refresh interval must be between 1 and 60 minutes."
  }
}

# Alert Timing Configuration
variable "budget_alert_thresholds" {
  description = "List of budget alert thresholds as percentages (0.0-1.0)"
  type        = list(number)
  default     = [0.5, 0.75, 0.9, 1.0]  # 50%, 75%, 90%, 100%
  
  validation {
    condition = alltrue([
      for threshold in var.budget_alert_thresholds : threshold >= 0.1 && threshold <= 1.0
    ])
    error_message = "Budget alert thresholds must be between 10% and 100%."
  }
}

variable "alert_evaluation_period_seconds" {
  description = "Alert evaluation period in seconds"
  type        = number
  default     = 300  # 5 minutes
  
  validation {
    condition     = var.alert_evaluation_period_seconds >= 60 && var.alert_evaluation_period_seconds <= 3600
    error_message = "Alert evaluation period must be between 60 seconds and 1 hour."
  }
}

variable "alert_auto_close_duration_seconds" {
  description = "Duration in seconds before alerts automatically close"
  type        = number
  default     = 86400  # 24 hours
  
  validation {
    condition     = var.alert_auto_close_duration_seconds >= 3600 && var.alert_auto_close_duration_seconds <= 604800
    error_message = "Alert auto-close duration must be between 1 hour and 7 days."
  }
}

# Log-based Metrics Configuration
variable "enable_custom_metrics" {
  description = "Enable custom log-based metrics for healthcare specific monitoring"
  type        = bool
  default     = true
}

variable "log_sampling_rate" {
  description = "Sampling rate for log-based metrics (0.0-1.0)"
  type        = number
  default     = 1.0  # 100% for healthcare compliance
  
  validation {
    condition     = var.log_sampling_rate >= 0.1 && var.log_sampling_rate <= 1.0
    error_message = "Log sampling rate must be between 10% and 100%."
  }
}

# Cost Optimization Configuration
variable "enable_cost_anomaly_detection" {
  description = "Enable cost anomaly detection and alerting"
  type        = bool
  default     = true
}

variable "cost_anomaly_threshold_percentage" {
  description = "Cost anomaly threshold as percentage increase over baseline"
  type        = number
  default     = 50  # 50% increase over baseline
  
  validation {
    condition     = var.cost_anomaly_threshold_percentage >= 10 && var.cost_anomaly_threshold_percentage <= 200
    error_message = "Cost anomaly threshold must be between 10% and 200%."
  }
}

variable "enable_resource_waste_detection" {
  description = "Enable detection of unused or underutilized resources"
  type        = bool
  default     = true
}

# Uptime Check Configuration
variable "uptime_check_timeout_seconds" {
  description = "Timeout for uptime checks in seconds"
  type        = number
  default     = 10
  
  validation {
    condition     = var.uptime_check_timeout_seconds >= 1 && var.uptime_check_timeout_seconds <= 60
    error_message = "Uptime check timeout must be between 1 and 60 seconds."
  }
}

variable "uptime_check_period_seconds" {
  description = "Period between uptime checks in seconds"
  type        = number
  default     = 300  # 5 minutes
  
  validation {
    condition     = var.uptime_check_period_seconds >= 60 && var.uptime_check_period_seconds <= 3600
    error_message = "Uptime check period must be between 60 seconds and 1 hour."
  }
}

# Integration with Other Modules
variable "bigquery_dataset_ids" {
  description = "List of BigQuery dataset IDs to monitor (from BigQuery module)"
  type        = list(string)
  default     = []
}

variable "cloud_function_names" {
  description = "List of Cloud Function names to monitor (from Cloud Functions module)"
  type        = list(string)
  default     = []
}

variable "storage_bucket_names" {
  description = "List of Cloud Storage bucket names to monitor (from Storage module)"
  type        = list(string)
  default     = []
}

variable "vpc_network_name" {
  description = "VPC network name to monitor (from Security module)"
  type        = string
  default     = ""
}

variable "subnet_names" {
  description = "List of subnet names to monitor (from Security module)"
  type        = list(string)
  default     = []
}

# Advanced Monitoring Configuration
variable "enable_sla_monitoring" {
  description = "Enable SLA monitoring for healthcare service availability"
  type        = bool
  default     = true
}

variable "sla_availability_target" {
  description = "Target availability percentage for SLA monitoring"
  type        = number
  default     = 99.9
  
  validation {
    condition     = var.sla_availability_target >= 95.0 && var.sla_availability_target <= 100.0
    error_message = "SLA availability target must be between 95% and 100%."
  }
}

variable "enable_predictive_analytics" {
  description = "Enable predictive analytics for cost and performance forecasting"
  type        = bool
  default     = false  # Advanced feature, disabled by default
}

# Regional Configuration
variable "multi_region_monitoring" {
  description = "Enable multi-region monitoring for disaster recovery"
  type        = bool
  default     = false
}

variable "monitoring_regions" {
  description = "List of regions for multi-region monitoring"
  type        = list(string)
  default     = ["us-west1"]  # LA County primary region
}

# Labels and Tags
variable "monitoring_labels" {
  description = "Additional labels for monitoring resources"
  type        = map(string)
  default = {
    purpose     = "healthcare-monitoring"
    compliance  = "hipaa"
    project     = "la-cardiology-optimizer"
  }
}

# Export Configuration
variable "enable_metrics_export" {
  description = "Enable export of monitoring metrics to external systems"
  type        = bool
  default     = false
}

variable "metrics_export_destination" {
  description = "Destination for metrics export (bigquery, pubsub, cloud_storage)"
  type        = string
  default     = "bigquery"
  
  validation {
    condition = contains(["bigquery", "pubsub", "cloud_storage"], var.metrics_export_destination)
    error_message = "Metrics export destination must be one of: bigquery, pubsub, cloud_storage."
  }
}

# Emergency Procedures Configuration
variable "enable_emergency_alerts" {
  description = "Enable emergency alert procedures for critical healthcare issues"
  type        = bool
  default     = true
}

variable "emergency_contact_email" {
  description = "Emergency contact email for critical healthcare system issues"
  type        = string
  default     = ""
}

variable "emergency_escalation_minutes" {
  description = "Minutes before emergency escalation for unresolved critical alerts"
  type        = number
  default     = 15
  
  validation {
    condition     = var.emergency_escalation_minutes >= 5 && var.emergency_escalation_minutes <= 60
    error_message = "Emergency escalation time must be between 5 and 60 minutes."
  }
} 