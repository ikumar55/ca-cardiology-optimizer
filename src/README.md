# Source Code Directory

Contains all source code for the Cardiology Care Optimization System.

## Structure

- **`data/`** - Data collection, processing, and ETL pipelines
  - `collectors/` - Scripts to fetch data from APIs and sources
  - `processors/` - Data cleaning and transformation modules
  - `validators/` - Data quality checks and validation

- **`features/`** - Feature engineering and preprocessing
  - `engineering.py` - Feature creation and selection
  - `spatial.py` - Geospatial feature processing
  - `temporal.py` - Time-series feature engineering

- **`models/`** - Machine learning model implementations
  - `baselines/` - Classical models (SARIMA, XGBoost)
  - `gnn/` - Graph neural network models (GraphSAGE)
  - `rl/` - Reinforcement learning (PPO environment and agent)
  - `ensemble/` - Model combination and stacking

- **`visualization/`** - Dashboard and plotting modules
  - `dashboard.py` - Main Streamlit application
  - `maps.py` - Interactive map components
  - `plots.py` - Chart and graph generation
  - `components/` - Reusable UI components

- **`utils/`** - Utility functions and helpers
  - `config.py` - Configuration management
  - `logging.py` - Logging setup
  - `metrics.py` - Evaluation metrics
  - `io.py` - File I/O operations

## Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Maintain >80% test coverage
- Document all modules with docstrings
- Use conventional commit messages 