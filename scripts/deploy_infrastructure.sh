#!/bin/bash

# Cardiology Care Optimization System - AWS Infrastructure Deployment Script
# This script deploys the AWS infrastructure using Terraform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        echo "Install instructions: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi

    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        echo "Install instructions: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi

    # Check if terraform.tfvars exists
    if [ ! -f "$TERRAFORM_DIR/terraform.tfvars" ]; then
        print_error "terraform.tfvars file not found."
        print_status "Please copy terraform.tfvars.example to terraform.tfvars and customize it:"
        echo "  cp $TERRAFORM_DIR/terraform.tfvars.example $TERRAFORM_DIR/terraform.tfvars"
        echo "  # Then edit terraform.tfvars with your settings"
        exit 1
    fi

    print_success "All prerequisites met!"
}

validate_terraform() {
    print_status "Validating Terraform configuration..."

    cd "$TERRAFORM_DIR"

    # Initialize Terraform
    terraform init

    # Validate configuration
    terraform validate

    # Check formatting
    if ! terraform fmt -check=true -diff=true; then
        print_warning "Terraform files are not properly formatted. Auto-formatting..."
        terraform fmt
    fi

    print_success "Terraform configuration is valid!"
}

plan_deployment() {
    print_status "Creating Terraform plan..."

    cd "$TERRAFORM_DIR"

    # Create plan
    terraform plan -out=tfplan -detailed-exitcode

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_warning "No changes detected in Terraform plan."
        return 0
    elif [ $exit_code -eq 2 ]; then
        print_status "Changes detected in Terraform plan."
        return 2
    else
        print_error "Terraform plan failed!"
        exit 1
    fi
}

deploy_infrastructure() {
    print_status "Deploying infrastructure..."

    cd "$TERRAFORM_DIR"

    # Apply the plan
    terraform apply tfplan

    print_success "Infrastructure deployed successfully!"

    # Save outputs to a file for other scripts
    terraform output -json > "$PROJECT_ROOT/infrastructure/terraform_outputs.json"
    print_status "Terraform outputs saved to infrastructure/terraform_outputs.json"
}

show_deployment_info() {
    print_status "Deployment Information:"

    cd "$TERRAFORM_DIR"

    echo ""
    echo "=== AWS Account Info ==="
    terraform output aws_account_id
    terraform output aws_region
    echo ""
    echo "=== S3 Buckets ==="
    terraform output s3_bucket_raw_data
    terraform output s3_bucket_processed_data
    terraform output s3_bucket_model_artifacts
    echo ""
    echo "=== Monitoring ==="
    terraform output cloudwatch_dashboard_url
    terraform output budget_name
    echo ""
    echo "=== Next Steps ==="
    echo "1. Upload your data to the S3 buckets"
    echo "2. Launch an EC2 instance for model training using:"
    echo "   ./scripts/launch_training_instance.sh"
    echo "3. Monitor costs in the AWS Console"
    echo "4. View CloudWatch dashboard for metrics"
}

cleanup_on_exit() {
    # Clean up temporary files
    if [ -f "$TERRAFORM_DIR/tfplan" ]; then
        rm -f "$TERRAFORM_DIR/tfplan"
    fi
}

main() {
    print_status "Starting AWS infrastructure deployment for Cardiology Care Optimization System"

    # Set up cleanup on exit
    trap cleanup_on_exit EXIT

    # Check prerequisites
    check_prerequisites

    # Validate Terraform configuration
    validate_terraform

    # Create deployment plan
    plan_result=$(plan_deployment)
    plan_exit_code=$?

    if [ $plan_exit_code -eq 0 ]; then
        print_warning "No changes to deploy. Infrastructure is up to date."
        show_deployment_info
        exit 0
    fi

    # Confirm deployment
    echo ""
    print_warning "The above plan will be applied to your AWS account."
    print_warning "This may incur AWS costs. Please review the plan carefully."
    echo ""
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled by user."
        exit 0
    fi

    # Deploy infrastructure
    deploy_infrastructure

    # Show deployment information
    show_deployment_info

    print_success "Deployment completed successfully!"
    print_status "Remember to run 'terraform destroy' when you're done to avoid ongoing costs."
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "plan")
        check_prerequisites
        validate_terraform
        plan_deployment
        ;;
    "destroy")
        print_warning "This will destroy ALL infrastructure resources!"
        read -p "Are you sure you want to destroy the infrastructure? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$TERRAFORM_DIR"
            terraform destroy
            print_success "Infrastructure destroyed successfully!"
        else
            print_status "Destroy cancelled by user."
        fi
        ;;
    "output")
        cd "$TERRAFORM_DIR"
        terraform output
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy   Deploy the infrastructure (default)"
        echo "  plan     Show what changes would be made"
        echo "  destroy  Destroy all infrastructure resources"
        echo "  output   Show Terraform outputs"
        echo "  help     Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac
