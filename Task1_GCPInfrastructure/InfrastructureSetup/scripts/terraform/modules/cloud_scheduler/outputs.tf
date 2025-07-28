# Outputs for Cloud Scheduler Module

# Core Scheduler Jobs
output "daily_provider_ingestion_job_name" {
  description = "Name of the daily provider data ingestion scheduler job"
  value       = google_cloud_scheduler_job.daily_provider_ingestion.name
}

output "weekly_travel_matrix_job_name" {
  description = "Name of the weekly travel matrix calculation scheduler job"
  value       = google_cloud_scheduler_job.weekly_travel_matrix.name
}

output "daily_health_equity_job_name" {
  description = "Name of the daily health equity metrics scheduler job"
  value       = google_cloud_scheduler_job.daily_health_equity.name
}

output "monthly_data_refresh_job_name" {
  description = "Name of the monthly data refresh scheduler job"
  value       = google_cloud_scheduler_job.monthly_data_refresh.name
}

output "health_check_job_name" {
  description = "Name of the health check scheduler job"
  value       = google_cloud_scheduler_job.health_check.name
}

output "resource_cleanup_job_name" {
  description = "Name of the resource cleanup scheduler job"
  value       = google_cloud_scheduler_job.resource_cleanup.name
}

# Optional Jobs (with conditional outputs)
output "hourly_validation_job_name" {
  description = "Name of the hourly data validation scheduler job"
  value       = var.enable_continuous_validation ? google_cloud_scheduler_job.hourly_data_validation[0].name : null
}

output "cost_monitoring_job_name" {
  description = "Name of the cost monitoring scheduler job"
  value       = var.enable_cost_monitoring ? google_cloud_scheduler_job.cost_monitoring[0].name : null
}

output "emergency_processing_job_name" {
  description = "Name of the emergency processing scheduler job"
  value       = var.enable_emergency_processing ? google_cloud_scheduler_job.emergency_processing[0].name : null
}

# Job Schedules Summary
output "scheduler_job_schedules" {
  description = "Summary of all scheduler job schedules and frequencies"
  value = {
    provider_ingestion   = var.provider_ingestion_schedule
    travel_matrix       = var.travel_matrix_schedule
    health_equity       = var.health_equity_schedule
    monthly_refresh     = var.monthly_refresh_schedule
    health_check        = var.health_check_schedule
    resource_cleanup    = var.cleanup_schedule
    validation          = var.enable_continuous_validation ? var.validation_schedule : null
    cost_monitoring     = var.enable_cost_monitoring ? var.cost_monitoring_schedule : null
  }
}

# All Job Names (for easier iteration)
output "all_scheduler_job_names" {
  description = "List of all created Cloud Scheduler job names"
  value = concat(
    [
      google_cloud_scheduler_job.daily_provider_ingestion.name,
      google_cloud_scheduler_job.weekly_travel_matrix.name,
      google_cloud_scheduler_job.daily_health_equity.name,
      google_cloud_scheduler_job.monthly_data_refresh.name,
      google_cloud_scheduler_job.health_check.name,
      google_cloud_scheduler_job.resource_cleanup.name
    ],
    var.enable_continuous_validation ? [google_cloud_scheduler_job.hourly_data_validation[0].name] : [],
    var.enable_cost_monitoring ? [google_cloud_scheduler_job.cost_monitoring[0].name] : [],
    var.enable_emergency_processing ? [google_cloud_scheduler_job.emergency_processing[0].name] : []
  )
}

# Notification System Outputs
output "scheduler_notifications_topic_name" {
  description = "Name of the Pub/Sub topic for scheduler notifications"
  value       = google_pubsub_topic.scheduler_notifications.name
}

output "scheduler_alerts_subscription_name" {
  description = "Name of the Pub/Sub subscription for scheduler alerts"
  value       = google_pubsub_subscription.scheduler_alerts.name
}

output "notification_system_enabled" {
  description = "Whether the notification system is enabled"
  value       = var.enable_notification_system
}

# Cost Optimization Features
output "cost_optimization_features" {
  description = "Summary of cost optimization features in scheduler configuration"
  value = {
    off_peak_scheduling       = var.off_peak_hours_only
    batch_size_limits        = var.batch_size_limit
    resource_cleanup_enabled = var.enable_resource_cleanup
    cost_monitoring_enabled  = var.enable_cost_monitoring
    emergency_cost_controls  = !var.emergency_bypass_cost_controls
    retention_optimization   = var.data_retention_days
  }
}

# Healthcare Compliance Features
output "healthcare_compliance_features" {
  description = "Summary of healthcare compliance features in scheduler configuration"
  value = {
    hipaa_compliance_enabled = var.hipaa_compliance_enabled
    small_cell_suppression   = var.min_cell_size
    confidence_intervals     = var.confidence_level
    data_validation_enabled  = var.enable_continuous_validation
    audit_trail_enabled      = true
    secure_notifications     = var.enable_notification_system
  }
}

# ETL Pipeline Orchestration Summary
output "etl_orchestration_summary" {
  description = "Summary of ETL pipeline orchestration configuration"
  value = {
    total_scheduler_jobs     = length(local.all_jobs)
    off_peak_operations     = var.off_peak_hours_only
    automated_validation    = var.enable_continuous_validation
    health_monitoring       = var.enable_health_checks
    cost_tracking          = var.enable_cost_monitoring
    emergency_capabilities = var.enable_emergency_processing
    cleanup_automation     = var.enable_resource_cleanup
  }
}

# Regional Configuration
output "deployment_region" {
  description = "GCP region where Cloud Scheduler jobs are deployed"
  value       = var.region
}

output "time_zone_configuration" {
  description = "Time zone used for all scheduled jobs"
  value       = var.time_zone
}

# Integration Points
output "orchestration_integration_points" {
  description = "Integration points for ETL pipeline orchestration"
  value = {
    cloud_functions_endpoint = var.manual_processor_function_uri
    notification_topic      = google_pubsub_topic.scheduler_notifications.name
    alert_subscription     = google_pubsub_subscription.scheduler_alerts.name
    service_accounts = {
      data_processing = var.data_processing_sa_email
      functions       = var.functions_sa_email
    }
  }
}

# Job Operation Types
output "job_operation_types" {
  description = "Map of scheduler jobs to their operation types"
  value = {
    daily_provider_ingestion = "provider_ingestion"
    weekly_travel_matrix    = "travel_matrix_calculation"
    daily_health_equity     = "health_equity_calculation"
    monthly_data_refresh    = "monthly_refresh"
    health_check           = "health_check"
    resource_cleanup       = "resource_cleanup"
    hourly_validation      = var.enable_continuous_validation ? "data_validation" : null
    cost_monitoring        = var.enable_cost_monitoring ? "cost_monitoring" : null
    emergency_processing   = var.enable_emergency_processing ? "emergency_processing" : null
  }
}

# Retry Configuration Summary
output "retry_configuration" {
  description = "Summary of retry configuration for scheduler jobs"
  value = {
    default_retry_count    = var.default_retry_count
    default_retry_duration = var.default_retry_duration
    backoff_strategy      = "exponential"
    max_backoff_duration  = "600s"
  }
}

# Budget and Cost Control
output "budget_configuration" {
  description = "Budget and cost control configuration"
  value = {
    budget_thresholds     = var.budget_thresholds
    cost_monitoring_enabled = var.enable_cost_monitoring
    emergency_cost_bypass = var.emergency_bypass_cost_controls
    resource_cleanup_enabled = var.enable_resource_cleanup
  }
}

# Schedule Frequencies
output "schedule_frequencies" {
  description = "Human-readable schedule frequencies for all jobs"
  value = {
    provider_ingestion   = "Daily at 1 AM PT"
    travel_matrix       = "Weekly on Sunday at 2 AM PT"
    health_equity       = "Daily at 3 AM PT"
    monthly_refresh     = "Monthly on 1st at midnight PT"
    health_check        = "Every 15 minutes (6 AM - 10 PM PT)"
    resource_cleanup    = "Weekly on Monday at 4 AM PT"
    validation          = var.enable_continuous_validation ? "Every 2 hours (6 AM - 10 PM PT)" : "Disabled"
    cost_monitoring     = var.enable_cost_monitoring ? "Daily at 8 AM PT" : "Disabled"
    emergency_processing = var.enable_emergency_processing ? "Every 6 hours (paused by default)" : "Disabled"
  }
}

# Local values for calculations
locals {
  all_jobs = concat(
    [
      google_cloud_scheduler_job.daily_provider_ingestion,
      google_cloud_scheduler_job.weekly_travel_matrix,
      google_cloud_scheduler_job.daily_health_equity,
      google_cloud_scheduler_job.monthly_data_refresh,
      google_cloud_scheduler_job.health_check,
      google_cloud_scheduler_job.resource_cleanup
    ],
    var.enable_continuous_validation ? google_cloud_scheduler_job.hourly_data_validation : [],
    var.enable_cost_monitoring ? google_cloud_scheduler_job.cost_monitoring : [],
    var.enable_emergency_processing ? google_cloud_scheduler_job.emergency_processing : []
  )
} 