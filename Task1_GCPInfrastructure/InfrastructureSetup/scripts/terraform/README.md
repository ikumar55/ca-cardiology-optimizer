# CA Cardiology Optimizer - GCP Infrastructure

This directory contains Terraform configurations for deploying the GCP infrastructure required for the CA Cardiology Optimizer project.

## Prerequisites
- Terraform v1.0+ installed
- GCP account with appropriate permissions
- gcloud CLI configured

## Deployment Instructions

1. Copy terraform.tfvars.example to terraform.tfvars and update with your project-specific values
2. Initialize Terraform:
```
terraform init
```
3. Validate the configuration:
```
terraform validate
terraform fmt
```
4. Preview the changes:
```
terraform plan
```
5. Apply the configuration:
```
terraform apply
```

## Module Structure
- bigquery/: BigQuery datasets and tables for healthcare data
- storage/: Cloud Storage buckets for data and artifacts
- vertex_ai/: ML pipeline components
- security/: IAM and security configurations
- networking/: VPC and network configurations
- cloud_run/: Containerized services

## Maintenance
- Use `terraform state list` to view managed resources
- Use `terraform destroy` to tear down infrastructure when needed 