# Data Directory

This directory contains all data files for the Cardiology Care Optimization System.

## Structure

- **`raw/`** - Original, unmodified source data files
  - NPPES provider bulk files
  - CDC PLACES health data
  - CMS Medicare claims data
  - Census ACS demographics
  - Historical provider movement data

- **`processed/`** - Cleaned and transformed data ready for modeling
  - `providers.parquet` - Processed provider data with geocoding
  - `zip_demand.parquet` - ZIP-level demand estimates
  - `travel_matrix.parquet` - Provider-to-ZIP travel times
  - `movements.parquet` - Historical provider relocations

- **`external/`** - External datasets and reference files
  - Pre-computed travel matrices from academic sources
  - ZIP code shapefiles
  - County boundary data
  - Reference lookups and mappings

## Data Management

- All data files are excluded from git via `.gitignore`
- Use DVC for data version control and pipeline management
- Large files (>100MB) should be stored in cloud storage
- Maintain data lineage documentation in `docs/data-pipeline.md`

## Security

- No PHI (Personal Health Information) should be stored
- API keys and credentials should be in `.env` files (not committed)
- All data should comply with HIPAA and privacy regulations 