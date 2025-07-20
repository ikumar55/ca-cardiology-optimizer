# Outputs for Cardiology Care Optimization System AWS Infrastructure

#################
# Account and Region Info
#################

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "AWS region"
  value       = data.aws_region.current.name
}

#################
# S3 Buckets
#################

output "s3_bucket_raw_data" {
  description = "S3 bucket for raw data storage"
  value = {
    name = aws_s3_bucket.raw_data.bucket
    arn  = aws_s3_bucket.raw_data.arn
    url  = "s3://${aws_s3_bucket.raw_data.bucket}"
  }
}

output "s3_bucket_processed_data" {
  description = "S3 bucket for processed data storage"
  value = {
    name = aws_s3_bucket.processed_data.bucket
    arn  = aws_s3_bucket.processed_data.arn
    url  = "s3://${aws_s3_bucket.processed_data.bucket}"
  }
}

output "s3_bucket_model_artifacts" {
  description = "S3 bucket for model artifacts storage"
  value = {
    name = aws_s3_bucket.model_artifacts.bucket
    arn  = aws_s3_bucket.model_artifacts.arn
    url  = "s3://${aws_s3_bucket.model_artifacts.bucket}"
  }
}

output "s3_bucket_logs" {
  description = "S3 bucket for application logs"
  value = {
    name = aws_s3_bucket.logs.bucket
    arn  = aws_s3_bucket.logs.arn
    url  = "s3://${aws_s3_bucket.logs.bucket}"
  }
}

#################
# IAM Resources
#################

output "ec2_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2_role.arn
}

output "ec2_instance_profile_name" {
  description = "Name of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

#################
# VPC and Networking
#################

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "security_group_ec2_id" {
  description = "ID of the EC2 security group"
  value       = aws_security_group.ec2.id
}

#################
# CloudWatch
#################

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

#################
# Cost Management
#################

output "budget_name" {
  description = "Name of the AWS budget"
  value       = aws_budgets_budget.project_budget.name
}

output "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  value       = var.monthly_budget_limit
}

#################
# Environment Configuration
#################

output "environment_config" {
  description = "Environment configuration for applications"
  value = {
    environment = var.environment
    project     = local.project_name
    region      = var.aws_region

    # S3 configuration
    s3_buckets = {
      raw_data        = aws_s3_bucket.raw_data.bucket
      processed_data  = aws_s3_bucket.processed_data.bucket
      model_artifacts = aws_s3_bucket.model_artifacts.bucket
      logs           = aws_s3_bucket.logs.bucket
    }

    # CloudWatch configuration
    cloudwatch = {
      log_group = aws_cloudwatch_log_group.app_logs.name
    }

    # IAM configuration
    iam = {
      ec2_role_arn             = aws_iam_role.ec2_role.arn
      ec2_instance_profile     = aws_iam_instance_profile.ec2_profile.name
    }

    # VPC configuration
    vpc = {
      id               = aws_vpc.main.id
      public_subnet_id = aws_subnet.public.id
      security_group   = aws_security_group.ec2.id
    }
  }
  sensitive = false
}

#################
# Deployment Information
#################

output "deployment_info" {
  description = "Information for deployment scripts"
  value = {
    timestamp       = timestamp()
    terraform_workspace = terraform.workspace
    created_by     = "terraform"
    resource_tags  = local.common_tags
  }
}
