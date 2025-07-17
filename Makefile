# Cardiology Care Optimization System - Makefile
# Common development commands

.PHONY: help install install-dev clean test lint format check setup-env run-dashboard

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  setup-env        Set up development environment"
	@echo "  clean            Clean cache and temporary files"
	@echo "  test             Run tests with coverage"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  check            Run all quality checks"
	@echo "  run-dashboard    Start Streamlit dashboard"
	@echo "  run-notebook     Start Jupyter Lab"
	@echo "  dvc-pull         Pull data with DVC"
	@echo "  dvc-push         Push data with DVC"

# Installation commands
install:
	pip install -r requirements.txt

install-dev:
	pip install -r dev-requirements.txt
	pip install -e .

# Environment setup
setup-env:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # On macOS/Linux"
	@echo "  venv\\Scripts\\activate     # On Windows"
	@echo "Then run: make install-dev"

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Testing
test:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-fast:
	pytest tests/ -x --ff

# Code quality
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/

format:
	black src/ tests/
	isort src/ tests/

check: format lint test

# Development tools
run-dashboard:
	streamlit run src/visualization/dashboard.py

run-notebook:
	jupyter lab

# Data management
dvc-pull:
	dvc pull

dvc-push:
	dvc push

# Documentation
docs:
	mkdocs serve

docs-build:
	mkdocs build

# Docker commands
docker-build:
	docker build -t cardiology-optimizer .

docker-run:
	docker run -p 8501:8501 cardiology-optimizer

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files 