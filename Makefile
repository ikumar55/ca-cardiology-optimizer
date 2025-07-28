# Cardiology Optimizer Makefile

.PHONY: install test clean format lint

install:
	pip install -e .
	pip install -r requirements.txt

test:
	pytest tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

format:
	black src/ tests/
	isort src/ tests/

lint:
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
