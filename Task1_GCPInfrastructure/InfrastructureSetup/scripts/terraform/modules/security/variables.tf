# Variables for Security Module

# Basic Project Configuration
variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for security resources (us-west1 for LA County proximity)"
  type        = string
  default     = "us-west1"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

# Network Configuration
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

# VPC Connector Throughput Configuration
variable "vpc_connector_min_throughput" {
  description = "Minimum throughput for VPC connector (200-1000)"
  type        = number
  default     = 200
  
  validation {
    condition     = var.vpc_connector_min_throughput >= 200 && var.vpc_connector_min_throughput <= 1000
    error_message = "VPC connector minimum throughput must be between 200 and 1000."
  }
}

variable "vpc_connector_max_throughput" {
  description = "Maximum throughput for VPC connector (200-1000)"
  type        = number
  default     = 300
  
  validation {
    condition     = var.vpc_connector_max_throughput >= 200 && var.vpc_connector_max_throughput <= 1000
    error_message = "VPC connector maximum throughput must be between 200 and 1000."
  }
}

# Service Account Integration (from other modules)
variable "data_processing_sa_email" {
  description = "Email of the data processing service account from storage module"
  type        = string
}

variable "functions_sa_email" {
  description = "Email of the Cloud Functions service account from storage module"
  type        = string
}

# Security Logging Configuration
variable "security_logs_dataset_id" {
  description = "BigQuery dataset ID for security logs (from BigQuery module)"
  type        = string
}

# Healthcare Compliance Settings
variable "enable_healthcare_api" {
  description = "Enable Google Healthcare API for advanced healthcare compliance"
  type        = bool
  default     = false
}

variable "hipaa_compliance_enabled" {
  description = "Enable HIPAA compliance features and controls"
  type        = bool
  default     = true
}

variable "audit_log_retention_days" {
  description = "Retention period for audit logs in days"
  type        = number
  default     = 2555  # 7 years for healthcare compliance
  
  validation {
    condition     = var.audit_log_retention_days >= 365
    error_message = "Audit log retention must be at least 365 days for healthcare compliance."
  }
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
  
  validation {
    condition     = var.rate_limit_requests_per_minute >= 100 && var.rate_limit_requests_per_minute <= 10000
    error_message = "Rate limit must be between 100 and 10000 requests per minute."
  }
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
  
  validation {
    condition     = var.kms_key_rotation_period_days >= 30 && var.kms_key_rotation_period_days <= 365
    error_message = "KMS key rotation period must be between 30 and 365 days."
  }
}

variable "backup_key_rotation_period_days" {
  description = "KMS backup key rotation period in days"
  type        = number
  default     = 180
  
  validation {
    condition     = var.backup_key_rotation_period_days >= 90 && var.backup_key_rotation_period_days <= 730
    error_message = "Backup key rotation period must be between 90 and 730 days."
  }
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
  
  validation {
    condition     = can(regex("\\.$", var.private_dns_zone_name))
    error_message = "Private DNS zone name must end with a dot."
  }
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
  
  validation {
    condition = contains(["daily", "weekly", "monthly"], var.compliance_report_frequency)
    error_message = "Compliance report frequency must be daily, weekly, or monthly."
  }
}

# Network Access Control
variable "enable_bastion_host" {
  description = "Enable bastion host for secure administrative access"
  type        = bool
  default     = false
}

variable "bastion_allowed_ip_ranges" {
  description = "IP ranges allowed to access bastion host"
  type        = list(string)
  default     = []
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
  
  validation {
    condition     = var.backup_retention_years >= 3 && var.backup_retention_years <= 30
    error_message = "Backup retention must be between 3 and 30 years."
  }
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

# Network Segmentation
variable "enable_network_segmentation" {
  description = "Enable network segmentation for healthcare data isolation"
  type        = bool
  default     = true
}

variable "healthcare_data_subnet_cidr" {
  description = "Dedicated CIDR for healthcare data processing (if network segmentation enabled)"
  type        = string
  default     = "10.0.10.0/24"
}

variable "analytics_subnet_cidr" {
  description = "Dedicated CIDR for analytics workloads (if network segmentation enabled)"
  type        = string
  default     = "10.0.11.0/24"
}

# Certificate Management
variable "enable_managed_ssl_certificates" {
  description = "Enable Google-managed SSL certificates for secure communications"
  type        = bool
  default     = true
}

variable "ssl_certificate_domains" {
  description = "List of domains for SSL certificates"
  type        = list(string)
  default     = []
}

# Identity and Access Management
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

# Labels and Tags
variable "security_labels" {
  description = "Additional labels for security resources"
  type        = map(string)
  default = {
    compliance = "hipaa"
    data_class = "healthcare"
    purpose    = "security"
  }
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