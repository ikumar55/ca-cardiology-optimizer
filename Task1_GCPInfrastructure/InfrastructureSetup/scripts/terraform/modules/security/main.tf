# Security Module for LA County Cardiology Access Optimizer
# Healthcare compliance with HIPAA requirements and PHI protection

# VPC Network for Private Connectivity and PHI Protection
resource "google_compute_network" "la_cardio_vpc" {
  name                    = "la-cardio-healthcare-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  description             = "Private VPC for LA County cardiology healthcare data with PHI protection"
  
  # Enable global routing for cross-region connectivity
  routing_mode = "GLOBAL"
}

# Private Subnet for Healthcare Data Processing
resource "google_compute_subnetwork" "la_cardio_private_subnet" {
  name          = "la-cardio-private-subnet"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.la_cardio_vpc.id
  ip_cidr_range = var.private_subnet_cidr
  
  # Enable private Google access for BigQuery/Cloud Storage
  private_ip_google_access = true
  
  description = "Private subnet for healthcare data processing with PHI protection"
  
  # Secondary IP ranges for services
  secondary_ip_range {
    range_name    = "la-cardio-services"
    ip_cidr_range = var.services_subnet_cidr
  }
  
  secondary_ip_range {
    range_name    = "la-cardio-pods"
    ip_cidr_range = var.pods_subnet_cidr
  }
  
  # Log configuration for security monitoring
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling       = 0.5
    metadata            = "INCLUDE_ALL_METADATA"
  }
}

# Cloud NAT for Secure Outbound Internet Access
resource "google_compute_router" "la_cardio_router" {
  name    = "la-cardio-healthcare-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.la_cardio_vpc.id
  
  description = "Router for secure outbound internet access with healthcare compliance"
}

resource "google_compute_router_nat" "la_cardio_nat" {
  name                               = "la-cardio-healthcare-nat"
  project                           = var.project_id
  region                            = var.region
  router                            = google_compute_router.la_cardio_router.name
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  # Security logging for NAT
  log_config {
    enable = true
    filter = "ALL"
  }
  
  # Minimum ports allocation for security
  min_ports_per_vm = 64
  
  # Enable endpoint independent mapping for security
  enable_endpoint_independent_mapping = false
}

# Healthcare Data Processing Firewall Rules
resource "google_compute_firewall" "allow_healthcare_internal" {
  name    = "la-cardio-allow-healthcare-internal"
  project = var.project_id
  network = google_compute_network.la_cardio_vpc.name
  
  description = "Allow internal communication for healthcare data processing"
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080", "8443"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = [var.private_subnet_cidr]
  target_tags   = ["la-cardio-healthcare"]
  
  priority = 1000
}

resource "google_compute_firewall" "allow_bigquery_access" {
  name    = "la-cardio-allow-bigquery-access"
  project = var.project_id
  network = google_compute_network.la_cardio_vpc.name
  
  description = "Allow secure access to BigQuery for healthcare analytics"
  
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  
  source_ranges = [var.private_subnet_cidr]
  target_tags   = ["la-cardio-bigquery"]
  
  priority = 1100
}

resource "google_compute_firewall" "allow_cloud_functions" {
  name    = "la-cardio-allow-cloud-functions"
  project = var.project_id
  network = google_compute_network.la_cardio_vpc.name
  
  description = "Allow secure access to Cloud Functions for ETL processing"
  
  allow {
    protocol = "tcp"
    ports    = ["443", "8080"]
  }
  
  source_ranges = [var.private_subnet_cidr]
  target_tags   = ["la-cardio-functions"]
  
  priority = 1200
}

# Deny All External Access (Healthcare Security)
resource "google_compute_firewall" "deny_all_external" {
  name    = "la-cardio-deny-all-external"
  project = var.project_id
  network = google_compute_network.la_cardio_vpc.name
  
  description = "Deny all external access for healthcare data protection"
  
  deny {
    protocol = "all"
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["la-cardio-healthcare"]
  
  priority = 65534
}

# Allow Health Checks from Google Load Balancers
resource "google_compute_firewall" "allow_health_checks" {
  name    = "la-cardio-allow-health-checks"
  project = var.project_id
  network = google_compute_network.la_cardio_vpc.name
  
  description = "Allow health checks from Google load balancers"
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }
  
  # Google health check source ranges
  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]
  
  target_tags = ["la-cardio-healthcare"]
  
  priority = 1300
}

# VPC Connector for Cloud Functions Private Access
resource "google_vpc_access_connector" "la_cardio_connector" {
  name    = "la-cardio-vpc-connector"
  project = var.project_id
  region  = var.region
  
  min_throughput = var.vpc_connector_min_throughput
  max_throughput = var.vpc_connector_max_throughput
  
  # Security subnet for VPC connector
  subnet {
    name       = google_compute_subnetwork.la_cardio_private_subnet.name
    project_id = var.project_id
  }
}

# Security Service Accounts for Healthcare Data Access
resource "google_service_account" "la_cardio_security_sa" {
  account_id   = "la-cardio-security-sa"
  project      = var.project_id
  display_name = "LA Cardiology Security Service Account"
  description  = "Service account for security operations and healthcare compliance monitoring"
}

resource "google_service_account" "la_cardio_audit_sa" {
  account_id   = "la-cardio-audit-sa"
  project      = var.project_id
  display_name = "LA Cardiology Audit Service Account"
  description  = "Service account for audit logging and healthcare compliance reporting"
}

# IAM Security Policies for Healthcare Data
resource "google_project_iam_binding" "security_viewer" {
  project = var.project_id
  role    = "roles/security.admin"
  
  members = [
    "serviceAccount:${google_service_account.la_cardio_security_sa.email}"
  ]
}

resource "google_project_iam_binding" "audit_log_viewer" {
  project = var.project_id
  role    = "roles/logging.viewer"
  
  members = [
    "serviceAccount:${google_service_account.la_cardio_audit_sa.email}"
  ]
}

resource "google_project_iam_binding" "healthcare_compliance_admin" {
  project = var.project_id
  role    = "roles/healthcare.consentAdmin"
  
  members = [
    "serviceAccount:${google_service_account.la_cardio_security_sa.email}"
  ]
  
  # Only create if healthcare API is enabled
  count = var.enable_healthcare_api ? 1 : 0
}

# Cloud KMS for Healthcare Data Encryption
resource "google_kms_key_ring" "la_cardio_keyring" {
  name     = "la-cardio-healthcare-keyring"
  project  = var.project_id
  location = var.region
}

resource "google_kms_crypto_key" "la_cardio_healthcare_key" {
  name     = "la-cardio-healthcare-encryption-key"
  key_ring = google_kms_key_ring.la_cardio_keyring.id
  
  purpose = "ENCRYPT_DECRYPT"
  
  # Key rotation for security
  rotation_period = "7776000s"  # 90 days
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
  
  lifecycle {
    prevent_destroy = true
  }
  
  labels = {
    environment = var.environment
    purpose     = "healthcare-data-encryption"
    compliance  = "hipaa"
  }
}

resource "google_kms_crypto_key" "la_cardio_backup_key" {
  name     = "la-cardio-backup-encryption-key"
  key_ring = google_kms_key_ring.la_cardio_keyring.id
  
  purpose = "ENCRYPT_DECRYPT"
  
  # Longer rotation for backup data
  rotation_period = "15552000s"  # 180 days
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
  
  lifecycle {
    prevent_destroy = true
  }
  
  labels = {
    environment = var.environment
    purpose     = "backup-data-encryption"
    compliance  = "hipaa"
  }
}

# KMS IAM for Service Accounts
resource "google_kms_crypto_key_iam_binding" "healthcare_key_users" {
  crypto_key_id = google_kms_crypto_key.la_cardio_healthcare_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  
  members = [
    "serviceAccount:${var.data_processing_sa_email}",
    "serviceAccount:${var.functions_sa_email}",
    "serviceAccount:${google_service_account.la_cardio_security_sa.email}"
  ]
}

# Private DNS Zone for Internal Services
resource "google_dns_managed_zone" "la_cardio_private_zone" {
  name        = "la-cardio-private-zone"
  project     = var.project_id
  dns_name    = "la-cardio.internal."
  description = "Private DNS zone for LA County cardiology internal services"
  
  visibility = "private"
  
  private_visibility_config {
    networks {
      network_url = google_compute_network.la_cardio_vpc.id
    }
  }
  
  dnssec_config {
    state = "on"
  }
}

# Security Logging and Monitoring
resource "google_logging_project_sink" "healthcare_security_sink" {
  name        = "la-cardio-healthcare-security-sink"
  project     = var.project_id
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${var.security_logs_dataset_id}"
  
  description = "Security logs sink for healthcare compliance monitoring"
  
  # Filter for security-relevant events
  filter = <<EOF
    (protoPayload.serviceName="bigquery.googleapis.com" OR
     protoPayload.serviceName="storage.googleapis.com" OR
     protoPayload.serviceName="cloudfunctions.googleapis.com" OR
     protoPayload.serviceName="cloudscheduler.googleapis.com") AND
    (protoPayload.methodName=~".*get.*" OR
     protoPayload.methodName=~".*list.*" OR
     protoPayload.methodName=~".*create.*" OR
     protoPayload.methodName=~".*update.*" OR
     protoPayload.methodName=~".*delete.*")
  EOF
  
  # Unique writer identity for security
  unique_writer_identity = true
  
  bigquery_options {
    use_partitioned_tables = true
  }
}

# Network Security Policy
resource "google_compute_security_policy" "la_cardio_security_policy" {
  name    = "la-cardio-healthcare-security-policy"
  project = var.project_id
  
  description = "Security policy for LA County cardiology healthcare services"
  
  # Default rule - deny all
  rule {
    action   = "deny(403)"
    priority = "2147483647"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    
    description = "Default deny rule for healthcare security"
  }
  
  # Allow internal traffic
  rule {
    action   = "allow"
    priority = "1000"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = [var.private_subnet_cidr]
      }
    }
    
    description = "Allow internal healthcare network traffic"
  }
  
  # Rate limiting for API protection
  rule {
    action   = "rate_based_ban"
    priority = "2000"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      
      rate_limit_threshold {
        count        = var.rate_limit_requests_per_minute
        interval_sec = 60
      }
    }
    
    description = "Rate limiting for healthcare API protection"
  }
}

# Organization Policy Constraints for Healthcare Compliance
resource "google_organization_policy" "disable_serial_port_access" {
  count      = var.enable_organization_policies ? 1 : 0
  org_id     = var.organization_id
  constraint = "compute.disableSerialPortAccess"
  
  boolean_policy {
    enforced = true
  }
}

resource "google_organization_policy" "require_ssl_certificates" {
  count      = var.enable_organization_policies ? 1 : 0
  org_id     = var.organization_id
  constraint = "compute.requireSslCertificates"
  
  boolean_policy {
    enforced = true
  }
}

resource "google_organization_policy" "restrict_public_ip" {
  count      = var.enable_organization_policies ? 1 : 0
  org_id     = var.organization_id
  constraint = "compute.vmExternalIpAccess"
  
  list_policy {
    deny {
      all = true
    }
  }
}

# Binary Authorization for Container Security
resource "google_binary_authorization_policy" "la_cardio_policy" {
  count = var.enable_binary_authorization ? 1 : 0
  
  project = var.project_id
  
  admission_whitelist_patterns {
    name_pattern = "gcr.io/${var.project_id}/*"
  }
  
  default_admission_rule {
    evaluation_mode  = "REQUIRE_ATTESTATION"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    
    require_attestations_by = [
      google_binary_authorization_attestor.la_cardio_attestor[0].name
    ]
  }
  
  cluster_admission_rules {
    cluster                = "projects/${var.project_id}/locations/*/clusters/*"
    evaluation_mode        = "REQUIRE_ATTESTATION"
    enforcement_mode       = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    
    require_attestations_by = [
      google_binary_authorization_attestor.la_cardio_attestor[0].name
    ]
  }
}

resource "google_binary_authorization_attestor" "la_cardio_attestor" {
  count = var.enable_binary_authorization ? 1 : 0
  
  name    = "la-cardio-healthcare-attestor"
  project = var.project_id
  
  description = "Attestor for LA County cardiology healthcare containers"
  
  attestation_authority_note {
    note_reference = google_container_analysis_note.la_cardio_note[0].name
  }
}

resource "google_container_analysis_note" "la_cardio_note" {
  count = var.enable_binary_authorization ? 1 : 0
  
  name    = "la-cardio-healthcare-note"
  project = var.project_id
  
  attestation_authority {
    hint {
      human_readable_name = "LA County Cardiology Healthcare Attestor"
    }
  }
} 