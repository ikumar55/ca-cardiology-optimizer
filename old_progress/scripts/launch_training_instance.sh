#!/bin/bash

# Cardiology Care Optimization System - EC2 Training Instance Launcher
# This script launches an EC2 instance configured for model training

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
TERRAFORM_OUTPUTS="$PROJECT_ROOT/infrastructure/terraform_outputs.json"

# Default values
INSTANCE_TYPE="t3.medium"
VOLUME_SIZE="30"
AUTO_TERMINATE="false"

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
        exit 1
    fi

    # Check if jq is installed for JSON parsing
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install it first."
        echo "Install with: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi

    # Check if infrastructure is deployed
    if [ ! -f "$TERRAFORM_OUTPUTS" ]; then
        print_error "Terraform outputs file not found: $TERRAFORM_OUTPUTS"
        print_status "Please deploy the infrastructure first using:"
        echo "  ./scripts/deploy_infrastructure.sh"
        exit 1
    fi

    print_success "All prerequisites met!"
}

get_terraform_output() {
    local key=$1
    jq -r ".$key.value" "$TERRAFORM_OUTPUTS"
}

get_latest_ami() {
    local region=$1

    # Get the latest Amazon Linux 2 AMI
    aws ec2 describe-images \
        --region "$region" \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
                  "Name=state,Values=available" \
        --query 'Images|sort_by(@,&CreationDate)[-1].ImageId' \
        --output text
}

create_user_data_script() {
    cat << 'EOF'
#!/bin/bash

# User data script for Cardiology Optimizer training instance
yum update -y

# Install Python 3.9
amazon-linux-extras install python3.8 -y
yum install python3-pip -y

# Install Docker
yum install docker -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install Git
yum install git -y

# Create working directory
mkdir -p /home/ec2-user/cardiology-optimizer
chown ec2-user:ec2-user /home/ec2-user/cardiology-optimizer

# Install common ML packages
pip3 install --upgrade pip
pip3 install numpy pandas matplotlib seaborn scikit-learn jupyter

# Install PyTorch (CPU version for basic setup)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip3 install duckdb geopandas shapely folium plotly streamlit

# Create a setup script for the user
cat << 'SETUP_EOF' > /home/ec2-user/setup_project.sh
#!/bin/bash
echo "Setting up Cardiology Optimizer project..."

# Clone the project (user will need to provide the Git URL)
echo "To clone your project, run:"
echo "git clone YOUR_REPO_URL cardiology-optimizer"
echo "cd cardiology-optimizer"

# Install project dependencies
echo "Then install dependencies:"
echo "pip3 install -r requirements.txt"

# Set up AWS credentials (if needed)
echo "Configure AWS credentials if needed:"
echo "aws configure"

echo "Setup complete!"
SETUP_EOF

chmod +x /home/ec2-user/setup_project.sh
chown ec2-user:ec2-user /home/ec2-user/setup_project.sh

# Create a monitoring script
cat << 'MONITOR_EOF' > /home/ec2-user/monitor_resources.sh
#!/bin/bash
echo "=== System Resources ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | head -1

echo -e "\nMemory Usage:"
free -h

echo -e "\nDisk Usage:"
df -h

echo -e "\nGPU Usage (if available):"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
else
    echo "No GPU detected"
fi

echo -e "\nRunning Python processes:"
ps aux | grep python | grep -v grep
MONITOR_EOF

chmod +x /home/ec2-user/monitor_resources.sh
chown ec2-user:ec2-user /home/ec2-user/monitor_resources.sh

# Log completion
echo "User data script completed at $(date)" >> /var/log/user-data.log
EOF
}

launch_instance() {
    local instance_type=$1
    local volume_size=$2
    local auto_terminate=$3

    print_status "Launching EC2 instance for model training..."

    # Get configuration from Terraform outputs
    local region=$(get_terraform_output "aws_region")
    local subnet_id=$(get_terraform_output "environment_config.vpc.public_subnet_id")
    local security_group=$(get_terraform_output "environment_config.vpc.security_group")
    local instance_profile=$(get_terraform_output "ec2_instance_profile_name")

    # Get latest AMI
    local ami_id=$(get_latest_ami "$region")

    print_status "Configuration:"
    echo "  Region: $region"
    echo "  Instance Type: $instance_type"
    echo "  AMI ID: $ami_id"
    echo "  Subnet: $subnet_id"
    echo "  Security Group: $security_group"
    echo "  Instance Profile: $instance_profile"
    echo "  Volume Size: ${volume_size}GB"
    echo "  Auto Terminate: $auto_terminate"

    # Create user data script
    local user_data=$(create_user_data_script | base64 -w 0)

    # Build the run-instances command
    local run_instances_args=(
        "--image-id" "$ami_id"
        "--instance-type" "$instance_type"
        "--subnet-id" "$subnet_id"
        "--security-group-ids" "$security_group"
        "--iam-instance-profile" "Name=$instance_profile"
        "--user-data" "$user_data"
        "--block-device-mappings" "DeviceName=/dev/xvda,Ebs={VolumeSize=$volume_size,VolumeType=gp3,DeleteOnTermination=true}"
        "--tag-specifications" "ResourceType=instance,Tags=[{Key=Name,Value=cardiology-optimizer-training},{Key=Project,Value=cardiology-optimizer},{Key=Purpose,Value=model-training}]"
        "--monitoring" "Enabled=true"
    )

    # Add auto-termination if requested
    if [ "$auto_terminate" = "true" ]; then
        run_instances_args+=("--instance-initiated-shutdown-behavior" "terminate")
    fi

    # Launch the instance
    local response=$(aws ec2 run-instances "${run_instances_args[@]}")
    local instance_id=$(echo "$response" | jq -r '.Instances[0].InstanceId')

    if [ "$instance_id" = "null" ] || [ -z "$instance_id" ]; then
        print_error "Failed to launch instance"
        echo "$response"
        exit 1
    fi

    print_success "Instance launched: $instance_id"

    # Wait for instance to be running
    print_status "Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids "$instance_id"

    # Get instance details
    local instance_info=$(aws ec2 describe-instances --instance-ids "$instance_id")
    local public_ip=$(echo "$instance_info" | jq -r '.Reservations[0].Instances[0].PublicIpAddress')
    local private_ip=$(echo "$instance_info" | jq -r '.Reservations[0].Instances[0].PrivateIpAddress')

    print_success "Instance is now running!"
    echo ""
    echo "=== Instance Details ==="
    echo "Instance ID: $instance_id"
    echo "Public IP: $public_ip"
    echo "Private IP: $private_ip"
    echo ""
    echo "=== Connection Instructions ==="
    echo "SSH: ssh -i YOUR_KEY.pem ec2-user@$public_ip"
    echo ""
    echo "=== Getting Started ==="
    echo "1. SSH into the instance"
    echo "2. Run: ./setup_project.sh"
    echo "3. Clone your project repository"
    echo "4. Start training your models!"
    echo ""
    echo "=== Monitoring ==="
    echo "Monitor resources: ./monitor_resources.sh"
    echo "CloudWatch logs: Available in AWS Console"
    echo ""
    echo "=== Cost Management ==="
    echo "Remember to terminate the instance when done:"
    echo "aws ec2 terminate-instances --instance-ids $instance_id"
    echo ""

    if [ "$auto_terminate" = "true" ]; then
        print_warning "Auto-termination is enabled. Instance will terminate when shutdown."
    else
        print_warning "Auto-termination is disabled. Remember to terminate manually to avoid charges."
    fi
}

show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE        Instance type (default: t3.medium)"
    echo "  -s, --size SIZE        Root volume size in GB (default: 30)"
    echo "  -a, --auto-terminate   Enable auto-termination on shutdown"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Launch t3.medium with 30GB storage"
    echo "  $0 -t c5.xlarge -s 100      # Launch c5.xlarge with 100GB storage"
    echo "  $0 -t t3.large -a           # Launch t3.large with auto-termination"
    echo ""
    echo "Instance Types for ML:"
    echo "  t3.medium   - 2 vCPU, 4GB RAM    (good for light workloads)"
    echo "  t3.large    - 2 vCPU, 8GB RAM    (better for data processing)"
    echo "  c5.xlarge   - 4 vCPU, 8GB RAM    (compute optimized)"
    echo "  c5.2xlarge  - 8 vCPU, 16GB RAM   (more intensive training)"
    echo "  m5.xlarge   - 4 vCPU, 16GB RAM   (balanced compute/memory)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            INSTANCE_TYPE="$2"
            shift 2
            ;;
        -s|--size)
            VOLUME_SIZE="$2"
            shift 2
            ;;
        -a|--auto-terminate)
            AUTO_TERMINATE="true"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

main() {
    print_status "Starting EC2 training instance launcher for Cardiology Care Optimization System"

    # Check prerequisites
    check_prerequisites

    # Confirm launch
    echo ""
    print_warning "This will launch an EC2 instance which will incur AWS costs."
    print_status "Instance type: $INSTANCE_TYPE"
    print_status "Volume size: ${VOLUME_SIZE}GB"
    print_status "Auto-terminate: $AUTO_TERMINATE"
    echo ""
    read -p "Do you want to proceed? (y/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Launch cancelled by user."
        exit 0
    fi

    # Launch the instance
    launch_instance "$INSTANCE_TYPE" "$VOLUME_SIZE" "$AUTO_TERMINATE"
}

main
