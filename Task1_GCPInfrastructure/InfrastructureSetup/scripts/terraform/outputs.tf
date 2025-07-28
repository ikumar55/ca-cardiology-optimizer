# Output values for CA Cardiology Optimizer infrastructure

# Storage Module Outputs
output "raw_data_bucket_name" {
  description = "Name of the raw data storage bucket"
  value       = module.storage.raw_data_bucket_name
}

output "processed_data_bucket_name" {
  description = "Name of the processed data storage bucket"
  value       = module.storage.processed_data_bucket_name
}

output "functions_bucket_name" {
  description = "Name of the Cloud Functions storage bucket"
  value       = module.storage.functions_bucket_name
}

output "terraform_state_bucket_name" {
  description = "Name of the Terraform state storage bucket"
  value       = module.storage.terraform_state_bucket_name
}

output "all_bucket_names" {
  description = "List of all created storage bucket names"
  value       = module.storage.all_bucket_names
}

# BigQuery Module Outputs
output "raw_data_dataset_id" {
  description = "ID of the raw data BigQuery dataset"
  value       = module.bigquery.raw_data_dataset_id
}

output "processed_data_dataset_id" {
  description = "ID of the processed data BigQuery dataset"
  value       = module.bigquery.processed_data_dataset_id
}

output "analytics_dataset_id" {
  description = "ID of the analytics BigQuery dataset"
  value       = module.bigquery.analytics_dataset_id
}

output "providers_table_id" {
  description = "Full ID of the providers BigQuery table"
  value       = module.bigquery.providers_table_id
}

output "travel_matrix_table_id" {
  description = "Full ID of the travel matrix BigQuery table"
  value       = module.bigquery.travel_matrix_table_id
}

output "health_equity_metrics_table_id" {
  description = "Full ID of the health equity metrics BigQuery table"
  value       = module.bigquery.health_equity_metrics_table_id
}

output "all_dataset_ids" {
  description = "List of all created BigQuery dataset IDs"
  value       = module.bigquery.all_dataset_ids
}

output "bigquery_cost_optimization_features" {
  description = "Summary of BigQuery cost optimization features"
  value       = module.bigquery.cost_optimization_features
}

# Cloud Functions Module Outputs
output "data_ingestion_function_uri" {
  description = "URI of the data ingestion Cloud Function"
  value       = module.cloud_functions.data_ingestion_function_uri
}

output "travel_matrix_function_uri" {
  description = "URI of the travel matrix calculator Cloud Function"
  value       = module.cloud_functions.travel_matrix_function_uri
}

output "health_equity_function_uri" {
  description = "URI of the health equity calculator Cloud Function"
  value       = module.cloud_functions.health_equity_function_uri
}

output "manual_processor_function_uri" {
  description = "URI of the manual processor Cloud Function (HTTP trigger)"
  value       = module.cloud_functions.manual_processor_function_uri
}

output "all_cloud_function_names" {
  description = "List of all Cloud Function names"
  value       = module.cloud_functions.all_function_names
}

output "cloud_functions_cost_optimization" {
  description = "Summary of Cloud Functions cost optimization features"
  value       = module.cloud_functions.cost_optimization_features
}

output "healthcare_compliance_features" {
  description = "Summary of healthcare compliance features implemented"
  value       = module.cloud_functions.healthcare_compliance_features
}

output "etl_pipeline_integration_points" {
  description = "Integration points for the lightweight ETL pipeline"
  value       = module.cloud_functions.etl_integration_points
}

output "batch_processing_schedule" {
  description = "Cron schedule for cost-optimized batch processing"
  value       = module.cloud_functions.batch_processor_schedule
}

output "function_memory_allocations" {
  description = "Memory allocations for cost tracking and optimization"
  value       = module.cloud_functions.function_memory_allocations
}

# Cloud Scheduler Module Outputs
output "all_scheduler_job_names" {
  description = "List of all Cloud Scheduler job names for ETL pipeline orchestration"
  value       = module.cloud_scheduler.all_scheduler_job_names
}

output "scheduler_job_schedules" {
  description = "Summary of all scheduler job schedules and frequencies"
  value       = module.cloud_scheduler.scheduler_job_schedules
}

output "schedule_frequencies" {
  description = "Human-readable schedule frequencies for all orchestration jobs"
  value       = module.cloud_scheduler.schedule_frequencies
}

output "scheduler_cost_optimization_features" {
  description = "Summary of cost optimization features in scheduler configuration"
  value       = module.cloud_scheduler.cost_optimization_features
}

output "etl_orchestration_summary" {
  description = "Summary of complete ETL pipeline orchestration configuration"
  value       = module.cloud_scheduler.etl_orchestration_summary
}

output "scheduler_notification_system" {
  description = "Notification system configuration for scheduler alerts"
  value = {
    topic_name        = module.cloud_scheduler.scheduler_notifications_topic_name
    subscription_name = module.cloud_scheduler.scheduler_alerts_subscription_name
    system_enabled    = module.cloud_scheduler.notification_system_enabled
  }
}

output "orchestration_integration_points" {
  description = "Integration points for complete ETL pipeline orchestration"
  value       = module.cloud_scheduler.orchestration_integration_points
}

output "budget_configuration" {
  description = "Budget and cost control configuration for the complete infrastructure"
  value       = module.cloud_scheduler.budget_configuration
}

# Security Module Outputs
output "vpc_network_name" {
  description = "Name of the healthcare VPC network for secure data processing"
  value       = module.security.vpc_network_name
}

output "vpc_network_id" {
  description = "ID of the healthcare VPC network"
  value       = module.security.vpc_network_id
}

output "private_subnet_name" {
  description = "Name of the private subnet for healthcare data processing"
  value       = module.security.private_subnet_name
}

output "vpc_connector_name" {
  description = "Name of the VPC connector for Cloud Functions private access"
  value       = module.security.vpc_connector_name
}

output "security_service_accounts" {
  description = "List of all security-related service account emails"
  value       = module.security.all_security_service_accounts
}

output "healthcare_encryption_key_id" {
  description = "ID of the healthcare data encryption key"
  value       = module.security.healthcare_encryption_key_id
}

output "backup_encryption_key_id" {
  description = "ID of the backup data encryption key"
  value       = module.security.backup_encryption_key_id
}

output "security_policy_name" {
  description = "Name of the network security policy"
  value       = module.security.security_policy_name
}

output "private_dns_zone_name" {
  description = "Name of the private DNS zone"
  value       = module.security.private_dns_zone_name
}

output "firewall_rules" {
  description = "List of created firewall rule names"
  value       = module.security.firewall_rules
}

output "security_healthcare_compliance_features" {
  description = "Summary of security healthcare compliance features implemented"
  value       = module.security.healthcare_compliance_features
}

output "security_configuration_summary" {
  description = "Summary of security configuration and features"
  value       = module.security.security_configuration_summary
}

output "cloud_functions_network_config" {
  description = "Network configuration for Cloud Functions integration"
  value       = module.security.cloud_functions_network_config
}

output "healthcare_data_protection" {
  description = "Summary of healthcare data protection measures"
  value       = module.security.healthcare_data_protection
}

output "security_monitoring_configuration" {
  description = "Security monitoring and alerting configuration"
  value       = module.security.security_monitoring_configuration
}

output "advanced_security_features" {
  description = "Status of advanced security features"
  value       = module.security.advanced_security_features
}

output "security_cost_optimization_features" {
  description = "Summary of security cost optimization features"
  value       = module.security.security_cost_optimization_features
}

output "regional_security_configuration" {
  description = "Regional security configuration details"
  value       = module.security.regional_configuration
}

# Monitoring Module Outputs
output "budget_name" {
  description = "Name of the budget for cost management"
  value       = module.monitoring.budget_name
}

output "monthly_budget_limit" {
  description = "Monthly budget limit configured for the project"
  value       = module.monitoring.monthly_budget_limit
}

output "infrastructure_dashboard_url" {
  description = "URL to access the infrastructure overview dashboard"
  value       = module.monitoring.infrastructure_dashboard_url
}

output "cost_management_dashboard_url" {
  description = "URL to access the cost management dashboard"
  value       = module.monitoring.cost_management_dashboard_url
}

output "healthcare_compliance_dashboard_url" {
  description = "URL to access the healthcare compliance dashboard"
  value       = module.monitoring.healthcare_compliance_dashboard_url
}

output "all_dashboard_urls" {
  description = "Map of all monitoring dashboard URLs for easy access"
  value       = module.monitoring.all_dashboard_urls
}

output "all_alert_policy_names" {
  description = "List of all alert policy names"
  value       = module.monitoring.all_alert_policy_names
}

output "all_notification_channels" {
  description = "List of all notification channel names"
  value       = module.monitoring.all_notification_channels
}

output "budget_alerts_topic_name" {
  description = "Name of the Pub/Sub topic for budget alerts"
  value       = module.monitoring.budget_alerts_topic_name
}

output "custom_metrics" {
  description = "List of custom log-based metric names for healthcare compliance"
  value       = module.monitoring.custom_metrics
}

output "monitoring_configuration_summary" {
  description = "Summary of monitoring configuration and features"
  value       = module.monitoring.monitoring_configuration_summary
}

output "healthcare_compliance_monitoring" {
  description = "Summary of healthcare compliance monitoring features"
  value       = module.monitoring.healthcare_compliance_monitoring
}

output "cost_optimization_features" {
  description = "Summary of cost optimization monitoring features"
  value       = module.monitoring.cost_optimization_features
}

output "performance_monitoring_features" {
  description = "Summary of performance monitoring configuration"
  value       = module.monitoring.performance_monitoring_features
}

output "quick_access_monitoring" {
  description = "Quick access URLs for monitoring console"
  value       = module.monitoring.quick_access_monitoring
}

output "healthcare_monitoring_quick_access" {
  description = "Quick access URLs for healthcare compliance monitoring"
  value       = module.monitoring.healthcare_monitoring_quick_access
}

output "monitoring_cost_summary" {
  description = "Summary of monitoring costs and optimization"
  value       = module.monitoring.monitoring_cost_summary
}

output "sla_monitoring" {
  description = "SLA monitoring configuration"
  value       = module.monitoring.sla_monitoring
}

output "emergency_procedures" {
  description = "Emergency procedures configuration"
  value       = module.monitoring.emergency_procedures
}

# Complete Infrastructure Summary
output "complete_infrastructure_summary" {
  description = "Complete summary of all infrastructure components and their integration"
  value = {
    total_resources = "Approximately 90-100 resources across all modules"
    modules = {
      storage           = "4 cost-optimized buckets with lifecycle policies"
      bigquery          = "3 datasets + 3 tables optimized for 900k+ records"
      cloud_functions   = "5 functions for lightweight ETL processing"
      cloud_scheduler   = "9 orchestration jobs replacing Prefect"
      security          = "21 resources including VPC, encryption, compliance"
      monitoring        = "15+ resources for comprehensive cost and performance tracking"
    }
    cost_optimization = {
      estimated_monthly_cost = "$60-80 (45-50% reduction from original design)"
      key_savings = [
        "Cloud Functions vs Dataflow (60% cost reduction)",
        "Cloud Scheduler vs Prefect (100% licensing cost elimination)",
        "Pre-computed travel matrices vs real-time routing",
        "BigQuery partitioning and clustering for query efficiency",
        "Storage lifecycle policies for automatic cost optimization"
      ]
    }
    healthcare_compliance = {
      hipaa_enabled     = true
      phi_protection    = true
      audit_retention   = "7 years"
      encryption        = "Customer-managed keys (CMEK)"
      monitoring        = "Comprehensive compliance tracking"
    }
    monitoring_features = {
      dashboards        = "3 specialized dashboards (infrastructure, cost, compliance)"
      alerts            = "5 alert policies with multiple thresholds"
      budget_tracking   = "Multi-threshold budget alerts ($50, $75, $100)"
      uptime_monitoring = "Critical service availability tracking"
      log_analytics     = "Custom metrics for healthcare compliance"
    }
  }
}

# Additional outputs will be added as modules are implemented 