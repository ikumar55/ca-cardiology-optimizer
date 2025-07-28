# Main Terraform configuration for CA Cardiology Optimizer
# This file orchestrates all GCP resources and modules

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file("service-account-key.json")
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "cloudfunctions.googleapis.com",
    "compute.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# Storage Module - Cost-optimized Cloud Storage buckets
module "storage" {
  source = "./modules/storage"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  cost_center = var.cost_center
}

# BigQuery Module - Cost-optimized datasets for healthcare analytics
module "bigquery" {
  source = "./modules/bigquery"
  
  project_id             = var.project_id
  region                 = var.region
  environment            = var.environment
  cost_center            = var.cost_center
  enable_cost_controls   = var.enable_bigquery_cost_controls
  max_query_cost_usd     = var.max_query_cost_usd
}

# Cloud Functions Module - Lightweight ETL replacing Dataflow for 60% cost reduction
module "cloud_functions" {
  source = "./modules/cloud_functions"
  
  # Dependencies from other modules
  depends_on = [module.storage, module.bigquery]
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  
  # BigQuery dataset IDs from bigquery module
  raw_data_dataset_id       = module.bigquery.raw_data_dataset_id
  processed_data_dataset_id = module.bigquery.processed_data_dataset_id
  analytics_dataset_id      = module.bigquery.analytics_dataset_id
  
  # Storage bucket names from storage module
  functions_bucket_name       = module.storage.functions_bucket_name
  raw_data_bucket_name       = module.storage.raw_data_bucket_name
  processed_data_bucket_name = module.storage.processed_data_bucket_name
  
  # Service account emails from storage module
  data_processing_sa_email = module.storage.data_processing_sa_email
  functions_sa_email       = module.storage.functions_sa_email
  
  # Cost optimization settings
  function_cost_threshold_usd = var.function_cost_threshold_usd
  enable_cost_monitoring      = var.enable_cloud_functions_monitoring
  enable_batch_processing     = var.enable_batch_processing
  
  # Healthcare compliance settings
  hipaa_compliance_enabled = var.hipaa_compliance_enabled
  min_cell_size           = var.min_cell_size
  confidence_level        = var.confidence_level
  
  # External API configuration
  openrouteservice_api_key = var.openrouteservice_api_key
  alert_email             = var.alert_email
  
  # Travel calculation settings
  max_travel_time_minutes = var.max_travel_time_minutes
  transport_modes         = var.transport_modes
  supervisorial_districts = var.supervisorial_districts
}

# Cloud Scheduler Module - Cost-efficient orchestration replacing Prefect
module "cloud_scheduler" {
  source = "./modules/cloud_scheduler"
  
  # Dependencies from other modules
  depends_on = [module.cloud_functions]
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  
  # Cloud Functions integration
  manual_processor_function_uri = module.cloud_functions.manual_processor_function_uri
  
  # Service account emails from storage module
  data_processing_sa_email = module.storage.data_processing_sa_email
  functions_sa_email       = module.storage.functions_sa_email
  
  # Notification configuration
  alert_email = var.alert_email
  
  # Scheduling control features
  enable_continuous_validation = var.enable_continuous_validation
  enable_cost_monitoring      = var.enable_scheduler_cost_monitoring
  enable_emergency_processing = var.enable_emergency_processing
  enable_health_checks       = var.enable_health_checks
  enable_resource_cleanup    = var.enable_resource_cleanup
  
  # Cost optimization settings
  budget_thresholds        = var.budget_thresholds
  off_peak_hours_only     = var.off_peak_hours_only
  batch_size_limit        = var.batch_size_limit
  
  # Healthcare compliance settings
  hipaa_compliance_enabled = var.hipaa_compliance_enabled
  min_cell_size           = var.min_cell_size
  confidence_level        = var.confidence_level
  
  # Schedule customization
  time_zone                    = var.time_zone
  provider_ingestion_schedule  = var.provider_ingestion_schedule
  travel_matrix_schedule      = var.travel_matrix_schedule
  health_equity_schedule      = var.health_equity_schedule
  
  # Advanced configuration
  transport_modes         = var.transport_modes
  supervisorial_districts = var.supervisorial_districts
  default_retry_count     = var.default_retry_count
  data_retention_days     = var.data_retention_days
}

# Security Module - Healthcare compliance with HIPAA and PHI protection
module "security" {
  source = "./modules/security"
  
  # Dependencies from other modules
  depends_on = [module.storage, module.bigquery]
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  
  # Network configuration
  private_subnet_cidr     = var.private_subnet_cidr
  services_subnet_cidr    = var.services_subnet_cidr
  pods_subnet_cidr        = var.pods_subnet_cidr
  vpc_connector_cidr      = var.vpc_connector_cidr
  
  # VPC connector throughput
  vpc_connector_min_throughput = var.vpc_connector_min_throughput
  vpc_connector_max_throughput = var.vpc_connector_max_throughput
  
  # Service account emails from storage module
  data_processing_sa_email = module.storage.data_processing_sa_email
  functions_sa_email       = module.storage.functions_sa_email
  
  # Security logging (BigQuery dataset for security logs)
  security_logs_dataset_id = module.bigquery.analytics_dataset_id
  
  # Healthcare compliance settings
  enable_healthcare_api       = var.enable_healthcare_api
  hipaa_compliance_enabled    = var.hipaa_compliance_enabled
  audit_log_retention_days    = var.audit_log_retention_days
  
  # Organization policy configuration
  organization_id               = var.organization_id
  enable_organization_policies  = var.enable_organization_policies
  
  # Container security
  enable_binary_authorization = var.enable_binary_authorization
  
  # Network security
  rate_limit_requests_per_minute = var.rate_limit_requests_per_minute
  enable_ddos_protection        = var.enable_ddos_protection
  enable_waf                    = var.enable_waf
  
  # Encryption configuration
  kms_key_rotation_period_days    = var.kms_key_rotation_period_days
  backup_key_rotation_period_days = var.backup_key_rotation_period_days
  enable_customer_managed_encryption = var.enable_customer_managed_encryption
  
  # Access control
  allowed_ip_ranges             = var.allowed_ip_ranges
  enable_private_google_access  = var.enable_private_google_access
  enable_vpc_flow_logs         = var.enable_vpc_flow_logs
  
  # DNS security
  enable_dns_security      = var.enable_dns_security
  private_dns_zone_name    = var.private_dns_zone_name
  
  # Monitoring and alerting
  enable_security_monitoring  = var.enable_security_monitoring
  security_alert_email       = var.security_alert_email
  enable_intrusion_detection = var.enable_intrusion_detection
  
  # Compliance monitoring
  enable_compliance_monitoring = var.enable_compliance_monitoring
  compliance_report_frequency  = var.compliance_report_frequency
  
  # Security scanning
  enable_vulnerability_scanning = var.enable_vulnerability_scanning
  enable_web_security_scanner   = var.enable_web_security_scanner
  
  # Backup and disaster recovery
  enable_cross_region_backup = var.enable_cross_region_backup
  backup_retention_years     = var.backup_retention_years
  
  # Advanced security features
  enable_private_service_connect = var.enable_private_service_connect
  enable_confidential_computing  = var.enable_confidential_computing
  enable_shielded_instances      = var.enable_shielded_instances
  enable_workload_identity       = var.enable_workload_identity
  enable_service_mesh            = var.enable_service_mesh
  
  # Data loss prevention
  enable_dlp               = var.enable_dlp
  dlp_inspection_templates = var.dlp_inspection_templates
  
  # Cost control
  security_budget_alert_threshold = var.security_budget_alert_threshold
  enable_security_cost_optimization = var.enable_security_cost_optimization
  
  # Regional configuration
  multi_region_deployment = var.multi_region_deployment
  secondary_region        = var.secondary_region
}

# Monitoring Module - Comprehensive cost management and healthcare compliance monitoring
module "monitoring" {
  source = "./modules/monitoring"
  
  # Dependencies from other modules
  depends_on = [module.storage, module.bigquery, module.cloud_functions, module.cloud_scheduler, module.security]
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  
  # Budget management configuration
  billing_account_id     = var.billing_account_id
  monthly_budget_limit   = var.monthly_budget_limit
  bigquery_daily_cost_limit = var.bigquery_daily_cost_limit
  
  # Notification configuration
  budget_alert_email         = var.budget_alert_email
  infrastructure_alert_email = var.infrastructure_alert_email
  slack_webhook_url          = var.slack_webhook_url
  slack_channel              = var.slack_channel
  
  # Monitoring feature toggles
  enable_uptime_checks           = var.enable_uptime_checks
  enable_resource_monitoring     = var.enable_resource_monitoring
  enable_performance_monitoring  = var.enable_performance_monitoring
  enable_security_monitoring     = var.enable_security_monitoring
  enable_cost_optimization_alerts = var.enable_cost_optimization_alerts
  
  # Performance thresholds
  function_memory_threshold_mb            = var.function_memory_threshold_mb
  bigquery_job_duration_threshold_seconds = var.bigquery_job_duration_threshold_seconds
  function_error_rate_threshold           = var.function_error_rate_threshold
  
  # Healthcare compliance monitoring
  enable_hipaa_compliance_monitoring = var.enable_hipaa_compliance_monitoring
  enable_phi_access_monitoring      = var.enable_phi_access_monitoring
  compliance_alert_email            = var.compliance_alert_email
  audit_log_retention_days          = var.audit_log_retention_days
  
  # Dashboard configuration
  enable_infrastructure_dashboard         = var.enable_infrastructure_dashboard
  enable_cost_management_dashboard        = var.enable_cost_management_dashboard
  enable_healthcare_compliance_dashboard  = var.enable_healthcare_compliance_dashboard
  dashboard_refresh_interval              = var.dashboard_refresh_interval
  
  # Alert timing configuration
  budget_alert_thresholds             = var.budget_alert_thresholds
  alert_evaluation_period_seconds     = var.alert_evaluation_period_seconds
  alert_auto_close_duration_seconds   = var.alert_auto_close_duration_seconds
  
  # Log-based metrics configuration
  enable_custom_metrics    = var.enable_custom_metrics
  log_sampling_rate       = var.log_sampling_rate
  
  # Cost optimization configuration
  enable_cost_anomaly_detection       = var.enable_cost_anomaly_detection
  cost_anomaly_threshold_percentage   = var.cost_anomaly_threshold_percentage
  enable_resource_waste_detection     = var.enable_resource_waste_detection
  
  # Uptime check configuration
  uptime_check_timeout_seconds = var.uptime_check_timeout_seconds
  uptime_check_period_seconds  = var.uptime_check_period_seconds
  
  # Integration with other modules
  bigquery_dataset_ids = [
    module.bigquery.raw_data_dataset_id,
    module.bigquery.processed_data_dataset_id,
    module.bigquery.analytics_dataset_id
  ]
  
  cloud_function_names = [
    "data_ingestion",
    "travel_matrix_calculator", 
    "health_equity_calculator",
    "data_validator",
    "manual_processor"
  ]
  
  storage_bucket_names = [
    module.storage.raw_data_bucket_name,
    module.storage.processed_data_bucket_name,
    module.storage.functions_bucket_name,
    module.storage.terraform_state_bucket_name
  ]
  
  vpc_network_name = module.security.vpc_network_name
  subnet_names     = [module.security.private_subnet_name]
  
  # Advanced monitoring configuration
  enable_sla_monitoring      = var.enable_sla_monitoring
  sla_availability_target    = var.sla_availability_target
  enable_predictive_analytics = var.enable_predictive_analytics
  
  # Regional configuration
  multi_region_monitoring = var.multi_region_monitoring
  monitoring_regions      = var.monitoring_regions
  
  # Labels and metadata
  monitoring_labels = var.monitoring_labels
  
  # Export configuration
  enable_metrics_export        = var.enable_metrics_export
  metrics_export_destination   = var.metrics_export_destination
  
  # Emergency procedures configuration
  enable_emergency_alerts      = var.enable_emergency_alerts
  emergency_contact_email      = var.emergency_contact_email
  emergency_escalation_minutes = var.emergency_escalation_minutes
} 