#!/usr/bin/env python3
"""
Setup configuration for Cardiology Care Optimization System.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def read_requirements(filename):
    """Read requirements from requirements file."""
    with open(filename, "r", encoding="utf-8") as f:
        return [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]

# Get version from environment or default
version = os.getenv("PACKAGE_VERSION", "0.1.0")

setup(
    name="cardiology-care-optimizer",
    version=version,
    author="Cardiology Care Optimization Team",
    author_email="contact@example.com",
    description="A data-driven pipeline for optimizing cardiologist distribution in California",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ca-cardiology-optimizer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ca-cardiology-optimizer/issues",
        "Documentation": "https://github.com/yourusername/ca-cardiology-optimizer/blob/main/docs/",
        "Source Code": "https://github.com/yourusername/ca-cardiology-optimizer",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("dev-requirements.txt"),
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=1.3.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cardiology-optimizer=cardiology_optimizer.cli:main",
            "co-dashboard=cardiology_optimizer.dashboard:main",
            "co-train=cardiology_optimizer.train:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cardiology_optimizer": [
            "config/*.yaml",
            "data/reference/*.json",
        ],
    },
    zip_safe=False,
    keywords=[
        "healthcare",
        "machine-learning", 
        "graph-neural-networks",
        "reinforcement-learning",
        "optimization",
        "geospatial",
        "cardiology",
        "access-to-care",
    ],
) 