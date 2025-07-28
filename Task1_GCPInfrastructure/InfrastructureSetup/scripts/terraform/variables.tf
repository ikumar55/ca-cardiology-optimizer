# Input variables for CA Cardiology Optimizer infrastructure

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Default GCP region for resources"
  type        = string
  default     = "us-west1"
}

variable "zone" {
  description = "Default GCP zone for resources"
  type        = string
  default     = "us-west1-a"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

variable "cost_center" {
  description = "Cost center for billing and resource tracking"
  type        = string
  default     = "research"
}

variable "enable_bigquery_cost_controls" {
  description = "Enable BigQuery cost controls and quotas"
  type        = bool
  default     = true
}

variable "max_query_cost_usd" {
  description = "Maximum cost per query in USD (for cost controls)"
  type        = number
  default     = 5.00
}

# Cloud Functions Variables
variable "function_cost_threshold_usd" {
  description = "Cost threshold in USD for Cloud Functions billing alerts"
  type        = number
  default     = 10.00
}

variable "enable_cloud_functions_monitoring" {
  description = "Enable cost monitoring and alerts for Cloud Functions"
  type        = bool
  default     = true
}

variable "enable_batch_processing" {
  description = "Enable scheduled batch processing for cost optimization"
  type        = bool
  default     = true
}

# Healthcare Compliance Variables
variable "hipaa_compliance_enabled" {
  description = "Enable HIPAA compliance features for healthcare data"
  type        = bool
  default     = true
}

variable "min_cell_size" {
  description = "Minimum cell size for HIPAA small cell suppression"
  type        = number
  default     = 11
}

variable "confidence_level" {
  description = "Statistical confidence level for health equity calculations"
  type        = number
  default     = 0.95
}

# External API Configuration
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

# Travel Calculation Settings
variable "max_travel_time_minutes" {
  description = "Maximum travel time to consider for accessibility calculations"
  type        = number
  default     = 120
}

variable "transport_modes" {
  description = "List of transportation modes for travel time calculations"
  type        = list(string)
  default     = ["driving", "transit", "walking"]
}

variable "supervisorial_districts" {
  description = "List of LA County supervisorial districts (1-5)"
  type        = list(number)
  default     = [1, 2, 3, 4, 5]
}

# Cloud Scheduler Variables
variable "enable_continuous_validation" {
  description = "Enable continuous data validation every 2 hours"
  type        = bool
  default     = true
}

variable "enable_scheduler_cost_monitoring" {
  description = "Enable daily cost monitoring and budget tracking via scheduler"
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

variable "time_zone" {
  description = "Time zone for all scheduled jobs"
  type        = string
  default     = "America/Los_Angeles"
}

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

variable "default_retry_count" {
  description = "Default retry count for scheduler jobs"
  type        = number
  default     = 3
}

variable "data_retention_days" {
  description = "Data retention period for notifications and logs"
  type        = number
  default     = 7
}

# Security Module Variables
variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet for healthcare data processing"
  type        = string
  default     = "10.0.1.0/24"
}

variable "services_subnet_cidr" {
  description = "CIDR block for secondary IP range for services"
  type        = string
  default     = "10.0.2.0/24"
}

variable "pods_subnet_cidr" {
  description = "CIDR block for secondary IP range for pods"
  type        = string
  default     = "10.0.3.0/24"
}

variable "vpc_connector_cidr" {
  description = "CIDR block for VPC connector for Cloud Functions private access"
  type        = string
  default     = "10.0.4.0/28"
}

variable "vpc_connector_min_throughput" {
  description = "Minimum throughput for VPC connector (200-1000)"
  type        = number
  default     = 200
}

variable "vpc_connector_max_throughput" {
  description = "Maximum throughput for VPC connector (200-1000)"
  type        = number
  default     = 300
}

# Healthcare Compliance Settings
variable "enable_healthcare_api" {
  description = "Enable Google Healthcare API for advanced healthcare compliance"
  type        = bool
  default     = false
}

variable "audit_log_retention_days" {
  description = "Retention period for audit logs in days"
  type        = number
  default     = 2555  # 7 years for healthcare compliance
}

# Organization Policy Configuration
variable "organization_id" {
  description = "GCP Organization ID for organization policies (optional)"
  type        = string
  default     = ""
}

variable "enable_organization_policies" {
  description = "Enable organization-level security policies"
  type        = bool
  default     = false
}

# Container Security Configuration
variable "enable_binary_authorization" {
  description = "Enable Binary Authorization for container security"
  type        = bool
  default     = false
}

# Network Security Configuration
variable "rate_limit_requests_per_minute" {
  description = "Rate limit for API requests per minute for healthcare protection"
  type        = number
  default     = 1000
}

variable "enable_ddos_protection" {
  description = "Enable DDoS protection for healthcare services"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Enable Web Application Firewall protection"
  type        = bool
  default     = true
}

# Encryption Configuration
variable "kms_key_rotation_period_days" {
  description = "KMS key rotation period in days for healthcare data encryption"
  type        = number
  default     = 90
}

variable "backup_key_rotation_period_days" {
  description = "KMS backup key rotation period in days"
  type        = number
  default     = 180
}

variable "enable_customer_managed_encryption" {
  description = "Use customer-managed encryption keys (CMEK) for healthcare data"
  type        = bool
  default     = true
}

# Access Control Configuration
variable "allowed_ip_ranges" {
  description = "List of IP ranges allowed to access healthcare services"
  type        = list(string)
  default     = []
}

variable "enable_private_google_access" {
  description = "Enable private Google API access for healthcare data processing"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs for security monitoring"
  type        = bool
  default     = true
}

# DNS Security Configuration
variable "enable_dns_security" {
  description = "Enable DNS security features including DNSSEC"
  type        = bool
  default     = true
}

variable "private_dns_zone_name" {
  description = "Name for the private DNS zone"
  type        = string
  default     = "la-cardio.internal."
}

# Monitoring and Alerting Configuration
variable "enable_security_monitoring" {
  description = "Enable comprehensive security monitoring and alerting"
  type        = bool
  default     = true
}

variable "security_alert_email" {
  description = "Email address for security alerts and notifications"
  type        = string
  default     = ""
}

variable "enable_intrusion_detection" {
  description = "Enable intrusion detection and prevention"
  type        = bool
  default     = true
}

# Compliance Monitoring Configuration
variable "enable_compliance_monitoring" {
  description = "Enable healthcare compliance monitoring and reporting"
  type        = bool
  default     = true
}

variable "compliance_report_frequency" {
  description = "Frequency for compliance reporting (daily, weekly, monthly)"
  type        = string
  default     = "weekly"
}

# Security Scanning Configuration
variable "enable_vulnerability_scanning" {
  description = "Enable vulnerability scanning for container images"
  type        = bool
  default     = true
}

variable "enable_web_security_scanner" {
  description = "Enable Web Security Scanner for application security"
  type        = bool
  default     = true
}

# Backup and Disaster Recovery Security
variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for disaster recovery"
  type        = bool
  default     = true
}

variable "backup_retention_years" {
  description = "Backup retention period in years for healthcare compliance"
  type        = number
  default     = 7
}

# Advanced Security Features
variable "enable_private_service_connect" {
  description = "Enable Private Service Connect for secure service access"
  type        = bool
  default     = true
}

variable "enable_confidential_computing" {
  description = "Enable Confidential Computing for sensitive healthcare workloads"
  type        = bool
  default     = false
}

variable "enable_shielded_instances" {
  description = "Enable Shielded VM instances for additional security"
  type        = bool
  default     = true
}

variable "enable_workload_identity" {
  description = "Enable Workload Identity for secure service-to-service authentication"
  type        = bool
  default     = true
}

variable "enable_service_mesh" {
  description = "Enable service mesh for micro-segmentation and secure communication"
  type        = bool
  default     = false
}

# Data Loss Prevention
variable "enable_dlp" {
  description = "Enable Data Loss Prevention for PHI protection"
  type        = bool
  default     = true
}

variable "dlp_inspection_templates" {
  description = "List of DLP inspection templates for healthcare data"
  type        = list(string)
  default     = ["PHI_DETECTION", "MEDICAL_RECORD_DETECTION"]
}

# Cost Control for Security
variable "security_budget_alert_threshold" {
  description = "Budget threshold for security-related costs in USD"
  type        = number
  default     = 200
}

variable "enable_security_cost_optimization" {
  description = "Enable cost optimization for security services"
  type        = bool
  default     = true
}

# Regional Configuration
variable "multi_region_deployment" {
  description = "Enable multi-region deployment for disaster recovery"
  type        = bool
  default     = false
}

variable "secondary_region" {
  description = "Secondary region for disaster recovery (if multi-region enabled)"
  type        = string
  default     = "us-central1"
}

# Monitoring Module Variables
variable "billing_account_id" {
  description = "GCP Billing Account ID for budget management and cost tracking"
  type        = string
  default     = ""
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD for LA County cardiology healthcare project"
  type        = number
  default     = 100
}

variable "bigquery_daily_cost_limit" {
  description = "Daily cost limit for BigQuery operations in USD"
  type        = number
  default     = 20
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

variable "enable_cost_optimization_alerts" {
  description = "Enable cost optimization alerts and recommendations"
  type        = bool
  default     = true
}

# Performance Thresholds
variable "function_memory_threshold_mb" {
  description = "Memory threshold in MB for Cloud Functions alerting"
  type        = number
  default     = 450
}

variable "bigquery_job_duration_threshold_seconds" {
  description = "Duration threshold in seconds for BigQuery job alerting"
  type        = number
  default     = 300
}

variable "function_error_rate_threshold" {
  description = "Error rate threshold (0.0-1.0) for Cloud Functions alerting"
  type        = number
  default     = 0.05
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
}

# Alert Timing Configuration
variable "budget_alert_thresholds" {
  description = "List of budget alert thresholds as percentages (0.0-1.0)"
  type        = list(number)
  default     = [0.5, 0.75, 0.9, 1.0]
}

variable "alert_evaluation_period_seconds" {
  description = "Alert evaluation period in seconds"
  type        = number
  default     = 300
}

variable "alert_auto_close_duration_seconds" {
  description = "Duration in seconds before alerts automatically close"
  type        = number
  default     = 86400
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
  default     = 1.0
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
  default     = 50
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
}

variable "uptime_check_period_seconds" {
  description = "Period between uptime checks in seconds"
  type        = number
  default     = 300
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
}

variable "enable_predictive_analytics" {
  description = "Enable predictive analytics for cost and performance forecasting"
  type        = bool
  default     = false
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
  default     = ["us-west1"]
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
}

# Additional variables will be defined for each module 