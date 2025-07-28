# Variables for Storage Module

variable "project_id" {
  description = "GCP Project ID for the LA County Cardiology Optimizer"
  type        = string
}

variable "region" {
  description = "GCP region for storage buckets (us-west1 for LA County proximity)"
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