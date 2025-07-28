# NPPES Monthly Files (2020-2023)

This directory contains the monthly NPPES (National Plan and Provider Enumeration System) data files from 2020-2023 for historical provider movement analysis.

## Directory Structure

```
nppes_monthly/
├── 2020/          # Monthly files for 2020
├── 2021/          # Monthly files for 2021  
├── 2022/          # Monthly files for 2022
├── 2023/          # Monthly files for 2023
├── metadata/      # Download logs, file manifests, and documentation
└── README.md      # This file
```

## Data Source

- **Primary Source**: NBER mirror for historical files
- **URL Pattern**: https://data.nber.org/npi/YYYY/
- **File Format**: ZIP files containing CSV data
- **Naming Convention**: npidata_pfile_YYYYMMDD-YYYYMMDD.csv.zip

## File Information

- **Total Files**: 48 monthly files (12 per year × 4 years)
- **File Size**: Each file is >1GB when uncompressed
- **Content**: All NPIs (active and deactivated) with provider information
- **Key Fields**: NPI, Provider Name, Address, Taxonomy Codes, Certification Date, Deactivation Date

## Download Process

Files are downloaded using the `download_nppes_monthly.py` script which:
1. Downloads files from NBER mirror
2. Verifies file integrity using checksums
3. Extracts and validates CSV content
4. Logs download metadata for reproducibility

## Usage

The monthly files are used for:
- Tracking provider address changes over time
- Identifying significant inter-county relocations
- Creating the movements.parquet dataset for model validation

## Data Quality

- Files are validated for completeness after download
- Checksums are verified to ensure data integrity
- Download timestamps and source URLs are documented
- Schema changes are tracked and documented

## Contact

For questions about the NPPES data files, contact CMS at: NPIFiles@cms.hhs.gov 