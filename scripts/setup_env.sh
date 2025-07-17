#!/bin/bash
# Development Environment Setup Script
# Cardiology Care Optimization System

set -e  # Exit on any error

echo "🏥 Setting up Cardiology Care Optimization System development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.9+ is available
check_python() {
    echo "🐍 Checking Python version..."
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        echo "Python version: $python_version"
        
        # Check if version is 3.9 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
            echo -e "${GREEN}✓ Python 3.9+ detected${NC}"
        else
            echo -e "${RED}✗ Python 3.9+ required. Current version: $python_version${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Python 3 not found. Please install Python 3.9+${NC}"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    echo "📦 Creating virtual environment..."
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠ Virtual environment already exists. Removing...${NC}"
        rm -rf venv
    fi
    
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
}

# Activate virtual environment and install dependencies
install_deps() {
    echo "📚 Installing dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install development dependencies
    pip install -r dev-requirements.txt
    
    # Install package in editable mode
    pip install -e .
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Set up pre-commit hooks
setup_precommit() {
    echo "🔧 Setting up pre-commit hooks..."
    source venv/bin/activate
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
}

# Copy environment file
setup_env_file() {
    echo "⚙️  Setting up environment file..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from template${NC}"
        echo -e "${YELLOW}⚠ Please edit .env file with your API keys${NC}"
    else
        echo -e "${YELLOW}⚠ .env file already exists${NC}"
    fi
}

# Create necessary directories
create_dirs() {
    echo "📁 Creating data directories..."
    mkdir -p data/{raw,processed,external}
    mkdir -p models
    mkdir -p logs
    echo -e "${GREEN}✓ Directories created${NC}"
}

# Test installation
test_installation() {
    echo "🧪 Testing installation..."
    source venv/bin/activate
    
    # Test basic imports
    python3 -c "
import pandas as pd
import numpy as np
import torch
import duckdb
print('✓ Core dependencies working')
"
    echo -e "${GREEN}✓ Installation test passed${NC}"
}

# Main execution
main() {
    echo "Starting setup process..."
    
    check_python
    create_venv
    install_deps
    setup_precommit
    setup_env_file
    create_dirs
    test_installation
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo "To activate the environment:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Common commands:"
    echo "  make help           # Show all available commands"
    echo "  make test           # Run tests"
    echo "  make run-dashboard  # Start Streamlit dashboard"
    echo "  make run-notebook   # Start Jupyter Lab"
    echo ""
    echo -e "${YELLOW}⚠ Don't forget to edit .env with your API keys!${NC}"
}

# Run main function
main 