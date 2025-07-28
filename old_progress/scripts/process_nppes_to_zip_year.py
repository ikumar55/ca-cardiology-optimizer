import os
from glob import glob

import pandas as pd

# Directory containing NPPES monthly files
data_dir = 'data/raw/nppes_monthly'
output_file = 'data/processed/providers_by_zip_year.csv'

# NPPES ZIP column name (update if needed)
ZIP_COLS = ['Provider Business Practice Location Address Postal Code', 'provider_zip', 'zip']

records = []
for year in range(2018, 2024):
    year_dir = os.path.join(data_dir, str(year))
    if not os.path.isdir(year_dir):
        print(f"Skipping {year_dir}, not found.")
        continue
    files = sorted(glob(os.path.join(year_dir, '*.csv')))
    print(f"Processing {len(files)} files for {year}...")
    for f in files:
        try:
            df = pd.read_csv(f, dtype=str, low_memory=False)
            # Find the ZIP column
            zip_col = next((col for col in ZIP_COLS if col in df.columns), None)
            if not zip_col:
                print(f"No ZIP column found in {f}, skipping.")
                continue
            # Clean ZIPs to 5 digits
            df['zip_code'] = df[zip_col].str[:5].str.zfill(5)
            # Count unique providers per ZIP
            counts = df.groupby('zip_code').size().reset_index(name='provider_count')
            counts['year'] = year
            records.append(counts)
        except Exception as e:
            print(f"Error processing {f}: {e}")

if records:
    all_counts = pd.concat(records, ignore_index=True)
    # Aggregate by year, zip_code (sum over months)
    panel = all_counts.groupby(['year', 'zip_code'])['provider_count'].sum().reset_index()
    panel.to_csv(output_file, index=False)
    print(f"Saved provider counts by ZIP and year to {output_file}")
else:
    print("No provider data processed.")

# Usage:
# python scripts/process_nppes_to_zip_year.py
# Ensure NPPES files are downloaded to data/raw/nppes_monthly/<YEAR>/*.csv 