from setuptools import find_packages, setup

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
        "stable-baselines3>=2.0.0",
        "torch-geometric>=2.3.0",
    ],
    author="Your Name",
    description="LA County Cardiology Access Optimization System",
    python_requires=">=3.9",
)
