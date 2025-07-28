# Outputs for Monitoring Module

# Budget Management Outputs
output "budget_name" {
  description = "Name of the budget for LA County cardiology healthcare project"
  value       = google_billing_budget.la_cardio_budget.display_name
}

output "budget_id" {
  description = "ID of the budget"
  value       = google_billing_budget.la_cardio_budget.name
}

output "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  value       = var.monthly_budget_limit
}

output "budget_alert_thresholds" {
  description = "Budget alert thresholds configured"
  value       = var.budget_alert_thresholds
}

# Pub/Sub Outputs
output "budget_alerts_topic_name" {
  description = "Name of the Pub/Sub topic for budget alerts"
  value       = google_pubsub_topic.budget_alerts.name
}

output "budget_alerts_topic_id" {
  description = "ID of the Pub/Sub topic for budget alerts"
  value       = google_pubsub_topic.budget_alerts.id
}

output "budget_alerts_subscription_name" {
  description = "Name of the Pub/Sub subscription for budget alerts"
  value       = google_pubsub_subscription.budget_alerts_subscription.name
}

# Notification Channels Outputs
output "budget_email_notification_channel" {
  description = "Budget email notification channel name"
  value       = google_monitoring_notification_channel.budget_email.name
}

output "budget_slack_notification_channel" {
  description = "Budget Slack notification channel name"
  value       = google_monitoring_notification_channel.budget_slack.name
}

output "infrastructure_email_notification_channel" {
  description = "Infrastructure email notification channel name"
  value       = google_monitoring_notification_channel.infrastructure_email.name
}

output "all_notification_channels" {
  description = "List of all notification channel names"
  value = [
    google_monitoring_notification_channel.budget_email.name,
    google_monitoring_notification_channel.budget_slack.name,
    google_monitoring_notification_channel.infrastructure_email.name
  ]
}

# Dashboard Outputs
output "infrastructure_dashboard_url" {
  description = "URL to access the infrastructure overview dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_infrastructure.id}?project=${var.project_id}"
}

output "cost_management_dashboard_url" {
  description = "URL to access the cost management dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_cost_management.id}?project=${var.project_id}"
}

output "healthcare_compliance_dashboard_url" {
  description = "URL to access the healthcare compliance dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_healthcare_compliance.id}?project=${var.project_id}"
}

output "all_dashboard_urls" {
  description = "Map of all dashboard URLs for easy access"
  value = {
    infrastructure_overview = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_infrastructure.id}?project=${var.project_id}"
    cost_management        = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_cost_management.id}?project=${var.project_id}"
    healthcare_compliance  = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.la_cardio_healthcare_compliance.id}?project=${var.project_id}"
  }
}

# Alert Policy Outputs
output "budget_alert_policy_name" {
  description = "Name of the budget alert policy"
  value       = google_monitoring_alert_policy.budget_alert_75_percent.display_name
}

output "high_error_rate_alert_policy_name" {
  description = "Name of the high error rate alert policy"
  value       = google_monitoring_alert_policy.high_error_rate.display_name
}

output "bigquery_cost_spike_alert_policy_name" {
  description = "Name of the BigQuery cost spike alert policy"
  value       = google_monitoring_alert_policy.bigquery_cost_spike.display_name
}

output "resource_utilization_alert_policy_name" {
  description = "Name of the resource utilization alert policy"
  value       = google_monitoring_alert_policy.resource_utilization.display_name
}

output "data_processing_performance_alert_policy_name" {
  description = "Name of the data processing performance alert policy"
  value       = google_monitoring_alert_policy.data_processing_performance.display_name
}

output "all_alert_policy_names" {
  description = "List of all alert policy names"
  value = [
    google_monitoring_alert_policy.budget_alert_75_percent.display_name,
    google_monitoring_alert_policy.high_error_rate.display_name,
    google_monitoring_alert_policy.bigquery_cost_spike.display_name,
    google_monitoring_alert_policy.resource_utilization.display_name,
    google_monitoring_alert_policy.data_processing_performance.display_name
  ]
}

# Log-based Metrics Outputs
output "hipaa_compliance_metric_name" {
  description = "Name of the HIPAA compliance log-based metric"
  value       = google_logging_metric.hipaa_compliance_events.name
}

output "security_events_metric_name" {
  description = "Name of the security events log-based metric"
  value       = google_logging_metric.security_events.name
}

output "custom_metrics" {
  description = "List of custom log-based metric names"
  value = [
    google_logging_metric.hipaa_compliance_events.name,
    google_logging_metric.security_events.name
  ]
}

# Uptime Check Outputs
output "bigquery_uptime_check_name" {
  description = "Name of the BigQuery uptime check (if enabled)"
  value       = var.enable_uptime_checks ? google_monitoring_uptime_check_config.bigquery_health[0].display_name : null
}

output "uptime_checks_enabled" {
  description = "Whether uptime checks are enabled"
  value       = var.enable_uptime_checks
}

# Monitoring Configuration Summary
output "monitoring_configuration_summary" {
  description = "Summary of monitoring configuration and features"
  value = {
    budget_management = {
      monthly_limit            = var.monthly_budget_limit
      alert_thresholds        = var.budget_alert_thresholds
      bigquery_daily_limit    = var.bigquery_daily_cost_limit
    }
    dashboards = {
      infrastructure_enabled  = var.enable_infrastructure_dashboard
      cost_management_enabled = var.enable_cost_management_dashboard
      compliance_enabled      = var.enable_healthcare_compliance_dashboard
    }
    alerts = {
      uptime_checks_enabled        = var.enable_uptime_checks
      resource_monitoring_enabled  = var.enable_resource_monitoring
      performance_monitoring_enabled = var.enable_performance_monitoring
      security_monitoring_enabled   = var.enable_security_monitoring
    }
    compliance = {
      hipaa_monitoring_enabled = var.enable_hipaa_compliance_monitoring
      phi_access_monitoring    = var.enable_phi_access_monitoring
      audit_retention_days     = var.audit_log_retention_days
    }
  }
}

# Healthcare Compliance Features
output "healthcare_compliance_monitoring" {
  description = "Summary of healthcare compliance monitoring features"
  value = {
    hipaa_compliance_enabled  = var.enable_hipaa_compliance_monitoring
    phi_access_monitoring     = var.enable_phi_access_monitoring
    audit_log_retention_days  = var.audit_log_retention_days
    compliance_metric_name    = google_logging_metric.hipaa_compliance_events.name
    security_metric_name      = google_logging_metric.security_events.name
    log_sampling_rate         = var.log_sampling_rate
  }
}

# Cost Optimization Features
output "cost_optimization_features" {
  description = "Summary of cost optimization monitoring features"
  value = {
    budget_alerts_enabled        = true
    cost_anomaly_detection       = var.enable_cost_anomaly_detection
    resource_waste_detection     = var.enable_resource_waste_detection
    cost_optimization_alerts     = var.enable_cost_optimization_alerts
    anomaly_threshold_percentage = var.cost_anomaly_threshold_percentage
    budget_management_enabled    = true
  }
}

# Performance Monitoring Features
output "performance_monitoring_features" {
  description = "Summary of performance monitoring configuration"
  value = {
    bigquery_job_threshold_seconds   = var.bigquery_job_duration_threshold_seconds
    function_memory_threshold_mb     = var.function_memory_threshold_mb
    function_error_rate_threshold    = var.function_error_rate_threshold
    sla_availability_target         = var.sla_availability_target
    alert_evaluation_period_seconds = var.alert_evaluation_period_seconds
  }
}

# Alert Configuration
output "alert_configuration" {
  description = "Alert configuration details"
  value = {
    evaluation_period_seconds = var.alert_evaluation_period_seconds
    auto_close_duration_seconds = var.alert_auto_close_duration_seconds
    emergency_escalation_minutes = var.emergency_escalation_minutes
    emergency_alerts_enabled = var.enable_emergency_alerts
  }
}

# Integration Points
output "monitoring_integration_points" {
  description = "Integration points for monitoring with other modules"
  value = {
    bigquery_datasets_monitored = var.bigquery_dataset_ids
    cloud_functions_monitored  = var.cloud_function_names
    storage_buckets_monitored  = var.storage_bucket_names
    vpc_network_monitored      = var.vpc_network_name
    subnets_monitored         = var.subnet_names
  }
}

# Regional Configuration
output "monitoring_regions" {
  description = "Regions configured for monitoring"
  value = {
    primary_region           = var.region
    multi_region_enabled     = var.multi_region_monitoring
    monitoring_regions       = var.monitoring_regions
  }
}

# Emergency Procedures
output "emergency_procedures" {
  description = "Emergency procedures configuration"
  value = {
    emergency_alerts_enabled     = var.enable_emergency_alerts
    emergency_contact_configured = var.emergency_contact_email != ""
    escalation_time_minutes     = var.emergency_escalation_minutes
  }
}

# SLA and Service Level Monitoring
output "sla_monitoring" {
  description = "SLA monitoring configuration"
  value = {
    sla_monitoring_enabled  = var.enable_sla_monitoring
    availability_target     = var.sla_availability_target
    uptime_check_timeout    = var.uptime_check_timeout_seconds
    uptime_check_period     = var.uptime_check_period_seconds
  }
}

# Metrics Export Configuration
output "metrics_export_configuration" {
  description = "Metrics export configuration details"
  value = {
    export_enabled  = var.enable_metrics_export
    destination     = var.metrics_export_destination
    custom_metrics_enabled = var.enable_custom_metrics
  }
}

# Labels and Metadata
output "monitoring_labels" {
  description = "Labels applied to monitoring resources"
  value       = var.monitoring_labels
}

# Cost Summary
output "monitoring_cost_summary" {
  description = "Summary of monitoring costs and optimization"
  value = {
    estimated_monthly_cost = "Approximately $5-10 for comprehensive monitoring"
    cost_optimization_features = [
      "Budget alerts at multiple thresholds",
      "Resource utilization monitoring",
      "Cost anomaly detection",
      "Automated resource waste detection"
    ]
    free_tier_usage = [
      "Cloud Monitoring metrics (first 150 metrics free)",
      "Basic alerting policies",
      "Standard dashboards"
    ]
  }
}

# Quick Access URLs
output "quick_access_monitoring" {
  description = "Quick access URLs for monitoring console"
  value = {
    monitoring_overview = "https://console.cloud.google.com/monitoring/dashboards?project=${var.project_id}"
    alerting_policies  = "https://console.cloud.google.com/monitoring/alerting/policies?project=${var.project_id}"
    budget_management  = "https://console.cloud.google.com/billing/budgets?project=${var.project_id}"
    logs_explorer      = "https://console.cloud.google.com/logs/query?project=${var.project_id}"
    metrics_explorer   = "https://console.cloud.google.com/monitoring/metrics-explorer?project=${var.project_id}"
  }
}

# Healthcare Specific Monitoring URLs
output "healthcare_monitoring_quick_access" {
  description = "Quick access URLs for healthcare compliance monitoring"
  value = {
    hipaa_compliance_logs = "https://console.cloud.google.com/logs/query;query=metric.type%3D%22logging.googleapis.com%2Fuser%2Fhipaa_compliance_events%22?project=${var.project_id}"
    security_events_logs  = "https://console.cloud.google.com/logs/query;query=metric.type%3D%22logging.googleapis.com%2Fuser%2Fsecurity_events%22?project=${var.project_id}"
    audit_logs           = "https://console.cloud.google.com/logs/query;query=protoPayload.serviceName%3D%22bigquery.googleapis.com%22%20OR%20protoPayload.serviceName%3D%22storage.googleapis.com%22?project=${var.project_id}"
  }
} 