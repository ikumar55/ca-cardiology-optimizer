# AWS Cloud Integration Guide

This guide provides complete instructions for deploying and managing the Cardiology Care Optimization System on AWS cloud infrastructure.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Infrastructure Components](#infrastructure-components)
5. [Deployment Process](#deployment-process)
6. [Cost Management](#cost-management)
7. [Security Considerations](#security-considerations)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## 🌟 Overview

The cloud integration provides:

- **Scalable Storage**: S3 buckets for data, models, and logs
- **Compute Resources**: EC2 instances for model training
- **Monitoring**: CloudWatch for metrics and logging
- **Cost Control**: Budget alerts and resource tagging
- **Infrastructure as Code**: Terraform for reproducible deployments
- **Security**: IAM roles and VPC networking

### Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│   S3 Storage    │───▶│  EC2 Training   │
│  (CMS, CDC, etc)│    │  - Raw Data     │    │   Instances     │
└─────────────────┘    │  - Processed    │    └─────────────────┘
                       │  - Models       │              │
┌─────────────────┐    │  - Logs         │              ▼
│   Streamlit     │◀───┤                 │    ┌─────────────────┐
│   Dashboard     │    └─────────────────┘    │   CloudWatch    │
└─────────────────┘              │            │   Monitoring    │
                                 ▼            └─────────────────┘
                       ┌─────────────────┐              │
                       │   Cost & Budget │              │
                       │   Monitoring    │◀─────────────┘
                       └─────────────────┘
```

## 🔧 Prerequisites

### Required Software

1. **AWS CLI v2**
   ```bash
   # macOS
   brew install awscli

   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Terraform >= 1.0**
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

3. **jq (JSON processor)**
   ```bash
   # macOS
   brew install jq

   # Linux
   sudo apt-get install jq
   ```

### AWS Account Setup

1. **Create AWS Account** (if you don't have one)
   - Go to [aws.amazon.com](https://aws.amazon.com)
   - Sign up for a free account
   - Enable billing alerts

2. **Configure AWS CLI**
   ```bash
   aws configure
   ```
   You'll need:
   - Access Key ID
   - Secret Access Key
   - Default region (recommend: `us-west-2`)
   - Default output format: `json`

3. **Create Key Pair** (for EC2 access)
   ```bash
   aws ec2 create-key-pair --key-name cardiology-optimizer --query 'KeyMaterial' --output text > ~/.ssh/cardiology-optimizer.pem
   chmod 400 ~/.ssh/cardiology-optimizer.pem
   ```

## 🚀 Quick Start

### 1. Configure Variables

```bash
# Copy the example configuration
cp infrastructure/terraform/terraform.tfvars.example infrastructure/terraform/terraform.tfvars

# Edit with your settings
nano infrastructure/terraform/terraform.tfvars
```

**Important**: Update these values in `terraform.tfvars`:
- `budget_alert_email`: Your email for cost alerts
- `s3_bucket_prefix`: Unique prefix (e.g., your-name-cardiology)
- `key_pair_name`: Name of your AWS key pair

### 2. Deploy Infrastructure

```bash
# Deploy the infrastructure
./scripts/deploy_infrastructure.sh

# Or just plan to see what will be created
./scripts/deploy_infrastructure.sh plan
```

### 3. Launch Training Instance

```bash
# Launch a basic training instance
./scripts/launch_training_instance.sh

# Or specify instance type and size
./scripts/launch_training_instance.sh -t c5.xlarge -s 100
```

### 4. Connect and Start Working

```bash
# SSH into your instance
ssh -i ~/.ssh/cardiology-optimizer.pem ec2-user@YOUR_INSTANCE_IP

# Set up the project
./setup_project.sh
git clone YOUR_REPO_URL cardiology-optimizer
cd cardiology-optimizer
pip install -r requirements.txt
```

## 🏗️ Infrastructure Components

### S3 Buckets

| Bucket | Purpose | Lifecycle | Encryption |
|--------|---------|-----------|------------|
| `raw-data` | Source data from CMS, CDC | Permanent | AES-256 |
| `processed-data` | Cleaned, processed datasets | Permanent | AES-256 |
| `model-artifacts` | Trained models, weights | Permanent | AES-256 |
| `logs` | Application and system logs | 90 days | AES-256 |

### Compute Resources

- **EC2 Instances**: On-demand training instances
- **Instance Types**: t3.medium (default) to c5.2xlarge for intensive training
- **AMI**: Amazon Linux 2 with Python 3.8, Docker, PyTorch
- **Storage**: GP3 SSD with configurable size (30GB default)

### Networking

- **VPC**: Dedicated virtual private cloud
- **Subnets**: Public subnet for training instances
- **Security Groups**: SSH (port 22) and Streamlit (port 8501) access
- **Internet Gateway**: For external connectivity

### Monitoring

- **CloudWatch Logs**: Centralized log aggregation
- **CloudWatch Metrics**: Custom metrics for training
- **CloudWatch Dashboard**: Visual monitoring interface
- **Budget Alerts**: Cost monitoring and notifications

## 📋 Deployment Process

### Detailed Deployment Steps

1. **Initialize Terraform**
   ```bash
   cd infrastructure/terraform
   terraform init
   ```

2. **Plan Deployment**
   ```bash
   terraform plan -var-file="terraform.tfvars"
   ```

3. **Apply Infrastructure**
   ```bash
   terraform apply -var-file="terraform.tfvars"
   ```

4. **Verify Deployment**
   ```bash
   terraform output
   ```

### Environment Configuration

#### Development Environment
- Budget limit: $25/month
- Instance type: t3.medium
- No NAT gateway (cost optimization)
- Simple security groups

#### Production Environment
- Budget limit: $200/month
- Instance type: c5.xlarge or larger
- NAT gateway for private subnets
- Restricted security groups
- CloudTrail enabled

## 💰 Cost Management

### Cost Optimization Features

1. **Budget Monitoring**
   - Monthly budget limits with email alerts
   - 80% warning threshold
   - 100% forecasted threshold

2. **Resource Tagging**
   - All resources tagged with Project, Environment, Owner
   - Cost allocation and tracking
   - Automated billing reports

3. **Lifecycle Policies**
   - Log retention: 90 days
   - Automatic cleanup of old data
   - Spot instances for training (optional)

### Expected Costs (Development)

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| S3 Storage | $5-15 | Based on data volume |
| EC2 (t3.medium) | $25-75 | When running 8-24 hours/day |
| CloudWatch | $3-8 | Logs and metrics |
| Data Transfer | $2-5 | Minimal for development |
| **Total** | **$35-103** | Varies by usage |

### Cost Monitoring Commands

```bash
# View current spending
aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)

# Check S3 storage costs
aws s3api list-buckets --query 'Buckets[?contains(Name, `cardiology`)]'

# Monitor running instances
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,InstanceType,LaunchTime]' --output table
```

## 🔒 Security Considerations

### IAM Security

- **Principle of Least Privilege**: EC2 instances have minimal required permissions
- **Role-Based Access**: No hardcoded credentials
- **MFA Recommended**: Enable MFA on your AWS account

### Network Security

- **VPC Isolation**: Resources in dedicated VPC
- **Security Groups**: Restrict access to necessary ports only
- **SSH Key Authentication**: No password authentication

### Data Security

- **Encryption at Rest**: All S3 buckets encrypted with AES-256
- **Encryption in Transit**: HTTPS/TLS for all API calls
- **Access Logging**: CloudTrail for audit trail (optional)

### Security Best Practices

```bash
# Restrict SSH access to your IP only
aws ec2 authorize-security-group-ingress \
  --group-id sg-your-security-group \
  --protocol tcp \
  --port 22 \
  --cidr YOUR.PUBLIC.IP.ADDRESS/32

# Enable MFA (highly recommended)
aws iam enable-mfa-device --user-name your-username --serial-number arn:aws:iam::ACCOUNT:mfa/DEVICE_NAME
```

## 📊 Monitoring & Logging

### CloudWatch Dashboards

Access your dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=cardiology-optimizer-dev-dashboard
```

### Key Metrics to Monitor

1. **S3 Metrics**
   - Bucket size growth
   - Request counts
   - Error rates

2. **EC2 Metrics**
   - CPU utilization
   - Memory usage
   - Network I/O

3. **Training Metrics**
   - Model training loss
   - Training accuracy
   - Epoch completion time

### Using Python AWS Utils

```python
from src.utils.aws_utils import get_aws_helper

# Initialize AWS helper
aws = get_aws_helper()

# Upload training data
aws.s3.upload_dataframe(df, 'processed_data', 'cardiology_providers')

# Log training metrics
aws.log_training_metrics('graphsage_model', epoch=10, loss=0.245, accuracy=0.89)

# Save model artifact
aws.save_model_artifact('model.pth', 'graphsage_v1', '1.0.0')
```

### Log Analysis

```bash
# View recent training logs
aws logs describe-log-streams --log-group-name "/aws/cardiology-optimizer/dev"

# Download logs for analysis
aws logs filter-log-events --log-group-name "/aws/cardiology-optimizer/dev" --start-time 1640995200000
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Terraform Deployment Fails

**Error**: "S3 bucket already exists"
```bash
# Solution: Use a unique bucket prefix
# Edit terraform.tfvars and change s3_bucket_prefix
```

**Error**: "AWS credentials not configured"
```bash
# Solution: Configure AWS CLI
aws configure
aws sts get-caller-identity  # Verify credentials
```

#### 2. EC2 Instance Launch Fails

**Error**: "InvalidKeyPair.NotFound"
```bash
# Solution: Create the key pair
aws ec2 create-key-pair --key-name cardiology-optimizer --query 'KeyMaterial' --output text > ~/.ssh/cardiology-optimizer.pem
chmod 400 ~/.ssh/cardiology-optimizer.pem
```

**Error**: "InsufficientInstanceCapacity"
```bash
# Solution: Try different instance type or region
./scripts/launch_training_instance.sh -t t3.large
```

#### 3. SSH Connection Issues

**Error**: "Permission denied (publickey)"
```bash
# Solution: Check key permissions and path
chmod 400 ~/.ssh/cardiology-optimizer.pem
ssh -i ~/.ssh/cardiology-optimizer.pem ec2-user@INSTANCE_IP
```

#### 4. High Costs

**Check running resources:**
```bash
# List running instances
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`]'

# Terminate unused instances
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

### Debug Commands

```bash
# Check Terraform state
terraform show

# Validate Terraform configuration
terraform validate

# Check AWS CLI configuration
aws configure list

# Test S3 access
aws s3 ls

# Check instance status
aws ec2 describe-instance-status
```

## 📚 Best Practices

### Development Workflow

1. **Use Spot Instances** for training (60-90% cost savings)
2. **Stop instances** when not in use
3. **Use versioned model artifacts** in S3
4. **Monitor costs** weekly
5. **Tag all resources** consistently

### Production Deployment

1. **Enable CloudTrail** for audit logging
2. **Use private subnets** for sensitive workloads
3. **Implement backup strategies** for critical data
4. **Set up monitoring alerts** for key metrics
5. **Regular security reviews** and updates

### Data Management

1. **Lifecycle policies** for data retention
2. **Cross-region replication** for critical data
3. **Data encryption** at rest and in transit
4. **Access logging** for compliance
5. **Regular data audits** and cleanup

### Cost Optimization

1. **Right-size instances** based on actual usage
2. **Use Reserved Instances** for predictable workloads
3. **Implement auto-shutdown** for training instances
4. **Regular cost reviews** and optimization
5. **Use S3 Intelligent Tiering** for long-term storage

## 🆘 Getting Help

### Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)

### Support Channels

1. **AWS Support** (if you have a support plan)
2. **Community Forums** (Stack Overflow, AWS Forums)
3. **Project Issues** (GitHub Issues for this project)

### Emergency Procedures

**High Cost Alert:**
1. Check running EC2 instances immediately
2. Terminate unused instances
3. Review S3 storage usage
4. Check for unexpected data transfer

**Security Incident:**
1. Rotate AWS credentials immediately
2. Review CloudTrail logs
3. Check for unauthorized access
4. Update security groups if needed

---

## 📝 Maintenance

### Regular Tasks

- **Weekly**: Review costs and usage
- **Monthly**: Update security patches on EC2 instances
- **Quarterly**: Review and update infrastructure
- **Annually**: Conduct security audit

### Cleanup Commands

```bash
# Destroy all infrastructure (CAUTION!)
./scripts/deploy_infrastructure.sh destroy

# Or using Terraform directly
cd infrastructure/terraform
terraform destroy
```

**⚠️ Warning**: The destroy command will permanently delete all resources and data. Ensure you have backups before running this command.

---

*For questions or issues with cloud integration, please refer to the troubleshooting section or create an issue in the project repository.*
