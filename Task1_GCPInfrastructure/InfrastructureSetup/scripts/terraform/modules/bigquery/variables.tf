# Variables for BigQuery Module

variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for BigQuery datasets (us-west1 for LA County proximity)"
  type        = string
  default     = "us-west1"
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

variable "enable_cost_controls" {
  description = "Enable BigQuery cost controls and quotas"
  type        = bool
  default     = true
}

variable "max_query_cost_usd" {
  description = "Maximum cost per query in USD (for cost controls)"
  type        = number
  default     = 5.00
}

variable "dataset_expiration_days" {
  description = "Default table expiration in days for cost optimization"
  type        = map(number)
  default = {
    raw_data       = 90
    processed_data = 60
    analytics      = 180
  }
} 