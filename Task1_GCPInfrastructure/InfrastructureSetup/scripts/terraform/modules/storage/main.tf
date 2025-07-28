# Storage Module for LA County Cardiology Access Optimizer
# Creates cost-optimized Cloud Storage buckets with lifecycle policies

# Raw data bucket for initial data ingestion
resource "google_storage_bucket" "la_cardio_raw_data" {
  name     = "${var.project_id}-cardio-raw-data"
  location = var.region
  
  # Cost optimization: Standard storage class for frequent access
  storage_class = "STANDARD"
  
  # Enable versioning for data protection (critical raw data)
  versioning {
    enabled = true
  }
  
  # Lifecycle policy for cost optimization
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  # Delete old versions after 90 days to control costs
  lifecycle_rule {
    condition {
      age                = 90
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }
  
  # Uniform bucket-level access for simplified IAM
  uniform_bucket_level_access = true
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
  
  labels = {
    environment = "production"
    project     = "la-cardiology-optimizer"
    data_type   = "raw-healthcare"
    cost_center = "research"
  }
}

# Processed data bucket for transformed datasets
resource "google_storage_bucket" "la_cardio_processed" {
  name     = "${var.project_id}-cardio-processed"
  location = var.region
  
  # Standard storage for frequent access by analytics
  storage_class = "STANDARD"
  
  # Limited versioning for processed data
  versioning {
    enabled = false
  }
  
  # Aggressive lifecycle for cost control (processed data can be regenerated)
  lifecycle_rule {
    condition {
      age = 60
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type = "Delete"
    }
  }
  
  uniform_bucket_level_access = true
  
  labels = {
    environment = "production"
    project     = "la-cardiology-optimizer"
    data_type   = "processed-analytics"
    cost_center = "research"
  }
}

# Cloud Functions source code bucket
resource "google_storage_bucket" "la_cardio_functions" {
  name     = "${var.project_id}-cardio-functions"
  location = var.region
  
  # Standard storage for function deployments
  storage_class = "STANDARD"
  
  # Enable versioning for function code rollbacks
  versioning {
    enabled = true
  }
  
  # Keep function versions for limited time
  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
  
  uniform_bucket_level_access = true
  
  labels = {
    environment = "production"
    project     = "la-cardiology-optimizer"
    data_type   = "function-code"
    cost_center = "infrastructure"
  }
}

# Terraform state bucket (if not already created)
resource "google_storage_bucket" "la_cardio_terraform_state" {
  name     = "${var.project_id}-terraform-state"
  location = var.region
  
  # Standard storage for state files
  storage_class = "STANDARD"
  
  # Enable versioning for state file protection
  versioning {
    enabled = true
  }
  
  # Keep state versions for recovery
  lifecycle_rule {
    condition {
      num_newer_versions = 10
    }
    action {
      type = "Delete"
    }
  }
  
  uniform_bucket_level_access = true
  
  # Prevent accidental deletion of state
  lifecycle {
    prevent_destroy = true
  }
  
  labels = {
    environment = "production"
    project     = "la-cardiology-optimizer"
    data_type   = "terraform-state"
    cost_center = "infrastructure"
  }
} 