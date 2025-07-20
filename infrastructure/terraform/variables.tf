# Variables for Cardiology Care Optimization System AWS Infrastructure

variable "aws_region" {
  description = "AWS region for the infrastructure"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Owner of the infrastructure resources"
  type        = string
  default     = "cardiology-optimizer-team"
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD for cost monitoring"
  type        = string
  default     = "50"
}

variable "budget_alert_email" {
  description = "Email address for budget alerts"
  type        = string
  # No default - should be provided by user
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT gateway for private subnets"
  type        = bool
  default     = false  # Cost optimization for dev environment
}

variable "instance_type" {
  description = "EC2 instance type for model training"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the AWS key pair for EC2 access"
  type        = string
  default     = null
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the infrastructure"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict this in production
}

variable "enable_cloudtrail" {
  description = "Whether to enable CloudTrail for audit logging"
  type        = bool
  default     = false  # Cost optimization for dev environment
}

variable "enable_vpc_flow_logs" {
  description = "Whether to enable VPC flow logs"
  type        = bool
  default     = false  # Cost optimization for dev environment
}

variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket names (must be globally unique)"
  type        = string
  default     = ""

  validation {
    condition     = can(regex("^[a-z0-9-]*$", var.s3_bucket_prefix))
    error_message = "S3 bucket prefix must contain only lowercase letters, numbers, and hyphens."
  }
}
