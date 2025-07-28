#!/bin/bash

# Clean Slate Script - Preserve Task Master and Core Files Only
# This script removes all experimental work while keeping essential project structure

echo "🧹 CARDIOLOGY OPTIMIZER - CLEAN SLATE OPERATION"
echo "=============================================="
echo ""
echo "This will DELETE all experimental work and keep only:"
echo "  ✅ Task Master configuration (.taskmaster/)"
echo "  ✅ Cursor configuration (.cursor/)"  
echo "  ✅ Git history (.git/)"
echo "  ✅ Core project files (README.md, LICENSE, .gitignore)"
echo ""

# Get confirmation
read -p "Are you sure you want to proceed? (type 'YES' to confirm): " confirmation
if [ "$confirmation" != "YES" ]; then
    echo "❌ Operation cancelled."
    exit 1
fi

echo ""
echo "🚀 Starting clean slate operation..."

# Create backup of essential files
echo "📦 Creating backup of essential files..."
mkdir -p .temp_backup
cp -r .taskmaster .temp_backup/ 2>/dev/null || true
cp -r .cursor .temp_backup/ 2>/dev/null || true
cp README.md .temp_backup/ 2>/dev/null || true
cp LICENSE .temp_backup/ 2>/dev/null || true
cp .gitignore .temp_backup/ 2>/dev/null || true

# List what will be deleted (everything except preserved files)
echo ""
echo "🗑️  Files/directories to be DELETED:"
find . -maxdepth 1 -type f -not -name "clean_slate.sh" -not -name "README.md" -not -name "LICENSE" -not -name ".gitignore" | sort
find . -maxdepth 1 -type d -not -name "." -not -name ".git" -not -name ".taskmaster" -not -name ".cursor" | sort

echo ""
read -p "Proceed with deletion? (type 'DELETE' to confirm): " delete_confirmation
if [ "$delete_confirmation" != "DELETE" ]; then
    echo "❌ Deletion cancelled."
    rm -rf .temp_backup
    exit 1
fi

# Remove all files except preserved ones
echo ""
echo "🗑️  Deleting experimental files..."

# Remove all top-level files except preserved ones
find . -maxdepth 1 -type f \
    -not -name "clean_slate.sh" \
    -not -name "README.md" \
    -not -name "LICENSE" \
    -not -name ".gitignore" \
    -delete

# Remove all directories except preserved ones  
find . -maxdepth 1 -type d \
    -not -name "." \
    -not -name ".git" \
    -not -name ".taskmaster" \
    -not -name ".cursor" \
    -exec rm -rf {} +

# Restore essential files from backup
echo "📁 Restoring essential files..."
cp -r .temp_backup/.taskmaster . 2>/dev/null || true
cp -r .temp_backup/.cursor . 2>/dev/null || true
cp .temp_backup/README.md . 2>/dev/null || true
cp .temp_backup/LICENSE . 2>/dev/null || true
cp .temp_backup/.gitignore . 2>/dev/null || true

# Clean up backup
rm -rf .temp_backup

# Create basic project structure for fresh start
echo "📁 Creating clean project structure..."
mkdir -p src/
mkdir -p data/{raw,processed,external}
mkdir -p docs/
mkdir -p tests/
mkdir -p notebooks/
mkdir -p models/
mkdir -p config/

# Create basic files
echo "📄 Creating basic project files..."

# Basic requirements.txt
cat > requirements.txt << 'EOF'
# Core Data Science
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Machine Learning  
scikit-learn>=1.3.0
torch>=2.0.0
torch-geometric>=2.3.0

# Geospatial
geopandas>=0.13.0
folium>=0.14.0
osmnx>=1.6.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0

# Development
jupyter>=1.0.0
pytest>=7.4.0
black>=23.0.0
isort>=5.12.0
EOF

# Basic setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="ca-cardiology-optimizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "torch>=2.0.0",
        "scikit-learn>=1.3.0",
        "geopandas>=0.13.0",
    ],
    author="Your Name",
    description="Cardiology Care Optimization System for California",
    python_requires=">=3.9",
)
EOF

# Data README
cat > data/README.md << 'EOF'
# Data Directory

## Structure
- `raw/` - Original, unprocessed data files
- `processed/` - Cleaned and processed data files  
- `external/` - External data sources and references

## Guidelines
- Never commit raw data files > 100MB
- Document all data sources and processing steps
- Use consistent naming conventions
EOF

# Source README
cat > src/README.md << 'EOF'
# Source Code

## Structure
- `data/` - Data processing and collection modules
- `models/` - Machine learning model implementations  
- `utils/` - Utility functions and helpers
- `visualization/` - Plotting and visualization code

## Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include unit tests for core functionality
EOF

echo ""
echo "✅ CLEAN SLATE COMPLETED!"
echo ""
echo "📁 Current project structure:"
find . -type d -not -path "./.git*" -not -path "./.taskmaster*" | sort

echo ""
echo "🎯 Next steps:"
echo "  1. Task Master is preserved and ready to use"
echo "  2. Clean project structure created" 
echo "  3. Basic requirements.txt and setup.py added"
echo "  4. Ready for fresh implementation following streamlined plan"
echo ""
echo "💡 Run 'rm clean_slate.sh' to remove this cleanup script" 