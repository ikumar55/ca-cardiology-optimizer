# Outputs for Security Module

# VPC and Network Outputs
output "vpc_network_name" {
  description = "Name of the healthcare VPC network"
  value       = google_compute_network.la_cardio_vpc.name
}

output "vpc_network_id" {
  description = "ID of the healthcare VPC network"
  value       = google_compute_network.la_cardio_vpc.id
}

output "vpc_network_self_link" {
  description = "Self link of the healthcare VPC network"
  value       = google_compute_network.la_cardio_vpc.self_link
}

output "private_subnet_name" {
  description = "Name of the private subnet for healthcare data processing"
  value       = google_compute_subnetwork.la_cardio_private_subnet.name
}

output "private_subnet_id" {
  description = "ID of the private subnet for healthcare data processing"
  value       = google_compute_subnetwork.la_cardio_private_subnet.id
}

output "private_subnet_self_link" {
  description = "Self link of the private subnet"
  value       = google_compute_subnetwork.la_cardio_private_subnet.self_link
}

output "private_subnet_cidr" {
  description = "CIDR range of the private subnet"
  value       = google_compute_subnetwork.la_cardio_private_subnet.ip_cidr_range
}

# VPC Connector Outputs
output "vpc_connector_name" {
  description = "Name of the VPC connector for Cloud Functions"
  value       = google_vpc_access_connector.la_cardio_connector.name
}

output "vpc_connector_id" {
  description = "ID of the VPC connector"
  value       = google_vpc_access_connector.la_cardio_connector.id
}

output "vpc_connector_self_link" {
  description = "Self link of the VPC connector"
  value       = google_vpc_access_connector.la_cardio_connector.self_link
}

# Service Account Outputs
output "security_sa_email" {
  description = "Email of the security service account"
  value       = google_service_account.la_cardio_security_sa.email
}

output "security_sa_id" {
  description = "ID of the security service account"
  value       = google_service_account.la_cardio_security_sa.id
}

output "audit_sa_email" {
  description = "Email of the audit service account"
  value       = google_service_account.la_cardio_audit_sa.email
}

output "audit_sa_id" {
  description = "ID of the audit service account"
  value       = google_service_account.la_cardio_audit_sa.id
}

# All Security Service Accounts
output "all_security_service_accounts" {
  description = "List of all security-related service account emails"
  value = [
    google_service_account.la_cardio_security_sa.email,
    google_service_account.la_cardio_audit_sa.email
  ]
}

# KMS and Encryption Outputs
output "kms_keyring_name" {
  description = "Name of the KMS keyring for healthcare data encryption"
  value       = google_kms_key_ring.la_cardio_keyring.name
}

output "kms_keyring_id" {
  description = "ID of the KMS keyring"
  value       = google_kms_key_ring.la_cardio_keyring.id
}

output "healthcare_encryption_key_name" {
  description = "Name of the healthcare data encryption key"
  value       = google_kms_crypto_key.la_cardio_healthcare_key.name
}

output "healthcare_encryption_key_id" {
  description = "ID of the healthcare data encryption key"
  value       = google_kms_crypto_key.la_cardio_healthcare_key.id
}

output "backup_encryption_key_name" {
  description = "Name of the backup data encryption key"
  value       = google_kms_crypto_key.la_cardio_backup_key.name
}

output "backup_encryption_key_id" {
  description = "ID of the backup data encryption key"
  value       = google_kms_crypto_key.la_cardio_backup_key.id
}

# DNS Outputs
output "private_dns_zone_name" {
  description = "Name of the private DNS zone"
  value       = google_dns_managed_zone.la_cardio_private_zone.name
}

output "private_dns_zone_id" {
  description = "ID of the private DNS zone"
  value       = google_dns_managed_zone.la_cardio_private_zone.id
}

output "private_dns_zone_dns_name" {
  description = "DNS name of the private zone"
  value       = google_dns_managed_zone.la_cardio_private_zone.dns_name
}

# Security Policy Outputs
output "security_policy_name" {
  description = "Name of the network security policy"
  value       = google_compute_security_policy.la_cardio_security_policy.name
}

output "security_policy_id" {
  description = "ID of the network security policy"
  value       = google_compute_security_policy.la_cardio_security_policy.id
}

output "security_policy_self_link" {
  description = "Self link of the network security policy"
  value       = google_compute_security_policy.la_cardio_security_policy.self_link
}

# Logging and Monitoring Outputs
output "security_logs_sink_name" {
  description = "Name of the security logs sink"
  value       = google_logging_project_sink.healthcare_security_sink.name
}

output "security_logs_sink_writer_identity" {
  description = "Writer identity of the security logs sink"
  value       = google_logging_project_sink.healthcare_security_sink.writer_identity
}

# Firewall Rules Summary
output "firewall_rules" {
  description = "List of created firewall rule names"
  value = [
    google_compute_firewall.allow_healthcare_internal.name,
    google_compute_firewall.allow_bigquery_access.name,
    google_compute_firewall.allow_cloud_functions.name,
    google_compute_firewall.deny_all_external.name,
    google_compute_firewall.allow_health_checks.name
  ]
}

# Healthcare Compliance Summary
output "healthcare_compliance_features" {
  description = "Summary of healthcare compliance features implemented"
  value = {
    hipaa_compliance_enabled       = var.hipaa_compliance_enabled
    customer_managed_encryption    = var.enable_customer_managed_encryption
    vpc_flow_logs_enabled         = var.enable_vpc_flow_logs
    security_monitoring_enabled   = var.enable_security_monitoring
    compliance_monitoring_enabled = var.enable_compliance_monitoring
    audit_log_retention_days      = var.audit_log_retention_days
    kms_key_rotation_days         = var.kms_key_rotation_period_days
    private_google_access_enabled = var.enable_private_google_access
    dns_security_enabled          = var.enable_dns_security
  }
}

# Security Configuration Summary
output "security_configuration_summary" {
  description = "Summary of security configuration and features"
  value = {
    vpc_network_name              = google_compute_network.la_cardio_vpc.name
    private_subnet_cidr          = google_compute_subnetwork.la_cardio_private_subnet.ip_cidr_range
    vpc_connector_enabled        = true
    kms_encryption_enabled       = var.enable_customer_managed_encryption
    security_policy_enabled      = true
    firewall_rules_count         = length(local.firewall_rules)
    service_accounts_count       = 2
    dns_zone_name               = google_dns_managed_zone.la_cardio_private_zone.dns_name
    security_logging_enabled    = true
    rate_limiting_enabled       = true
    ddos_protection_enabled     = var.enable_ddos_protection
    waf_enabled                 = var.enable_waf
  }
}

# Integration Points for Other Modules
output "integration_configuration" {
  description = "Configuration details for integration with other modules"
  value = {
    vpc_network_self_link        = google_compute_network.la_cardio_vpc.self_link
    private_subnet_self_link     = google_compute_subnetwork.la_cardio_private_subnet.self_link
    vpc_connector_self_link      = google_vpc_access_connector.la_cardio_connector.self_link
    healthcare_encryption_key_id = google_kms_crypto_key.la_cardio_healthcare_key.id
    backup_encryption_key_id     = google_kms_crypto_key.la_cardio_backup_key.id
    security_policy_self_link    = google_compute_security_policy.la_cardio_security_policy.self_link
    security_sa_email           = google_service_account.la_cardio_security_sa.email
    audit_sa_email              = google_service_account.la_cardio_audit_sa.email
  }
}

# Network Configuration for Cloud Functions
output "cloud_functions_network_config" {
  description = "Network configuration for Cloud Functions integration"
  value = {
    vpc_connector = google_vpc_access_connector.la_cardio_connector.id
    network       = google_compute_network.la_cardio_vpc.name
    subnet        = google_compute_subnetwork.la_cardio_private_subnet.name
  }
}

# Organization Policy Status (Conditional)
output "organization_policies_enabled" {
  description = "Whether organization policies are enabled"
  value       = var.enable_organization_policies
}

output "organization_policies_applied" {
  description = "List of organization policies applied (if enabled)"
  value = var.enable_organization_policies ? [
    "compute.disableSerialPortAccess",
    "compute.requireSslCertificates", 
    "compute.vmExternalIpAccess"
  ] : []
}

# Binary Authorization Status (Conditional)
output "binary_authorization_enabled" {
  description = "Whether Binary Authorization is enabled"
  value       = var.enable_binary_authorization
}

output "binary_authorization_policy_name" {
  description = "Name of the Binary Authorization policy (if enabled)"
  value       = var.enable_binary_authorization ? google_binary_authorization_policy.la_cardio_policy[0].project : null
}

output "binary_authorization_attestor_name" {
  description = "Name of the Binary Authorization attestor (if enabled)"
  value       = var.enable_binary_authorization ? google_binary_authorization_attestor.la_cardio_attestor[0].name : null
}

# Cost Optimization Features
output "security_cost_optimization_features" {
  description = "Summary of security cost optimization features"
  value = {
    cost_optimization_enabled      = var.enable_security_cost_optimization
    budget_alert_threshold        = var.security_budget_alert_threshold
    vpc_connector_min_throughput  = var.vpc_connector_min_throughput
    vpc_connector_max_throughput  = var.vpc_connector_max_throughput
    nat_minimum_ports            = 64
    flow_logs_sampling_rate      = 0.5
  }
}

# Regional and Multi-Region Configuration
output "regional_configuration" {
  description = "Regional security configuration details"
  value = {
    primary_region           = var.region
    multi_region_enabled     = var.multi_region_deployment
    secondary_region         = var.multi_region_deployment ? var.secondary_region : null
    cross_region_backup      = var.enable_cross_region_backup
  }
}

# Healthcare Data Protection Summary
output "healthcare_data_protection" {
  description = "Summary of healthcare data protection measures"
  value = {
    phi_protection_enabled       = var.hipaa_compliance_enabled
    encryption_at_rest          = var.enable_customer_managed_encryption
    encryption_in_transit       = true
    network_isolation          = true
    access_controls            = true
    audit_logging              = true
    data_loss_prevention       = var.enable_dlp
    vulnerability_scanning     = var.enable_vulnerability_scanning
    compliance_monitoring      = var.enable_compliance_monitoring
    backup_retention_years     = var.backup_retention_years
  }
}

# Security Monitoring Configuration
output "security_monitoring_configuration" {
  description = "Security monitoring and alerting configuration"
  value = {
    security_monitoring_enabled  = var.enable_security_monitoring
    intrusion_detection_enabled = var.enable_intrusion_detection
    security_alert_email        = var.security_alert_email
    compliance_report_frequency = var.compliance_report_frequency
    logs_sink_enabled          = true
    flow_logs_enabled          = var.enable_vpc_flow_logs
  }
}

# Advanced Security Features Status
output "advanced_security_features" {
  description = "Status of advanced security features"
  value = {
    private_service_connect    = var.enable_private_service_connect
    confidential_computing    = var.enable_confidential_computing
    shielded_instances        = var.enable_shielded_instances
    workload_identity         = var.enable_workload_identity
    service_mesh              = var.enable_service_mesh
    managed_ssl_certificates  = var.enable_managed_ssl_certificates
    bastion_host              = var.enable_bastion_host
    web_security_scanner      = var.enable_web_security_scanner
  }
}

# Local values for calculations
locals {
  firewall_rules = [
    google_compute_firewall.allow_healthcare_internal,
    google_compute_firewall.allow_bigquery_access,
    google_compute_firewall.allow_cloud_functions,
    google_compute_firewall.deny_all_external,
    google_compute_firewall.allow_health_checks
  ]
} 