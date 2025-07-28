#!/bin/bash
# download_nppes_multi_year.sh
# Script to download NPPES monthly files for 2018–2023 from the NBER mirror
# Usage: bash scripts/download_nppes_multi_year.sh

set -e

BASE_URL="https://data.nber.org/npi"
START_YEAR=2018
END_YEAR=2023
DATA_DIR="data/raw/nppes_monthly"

mkdir -p "$DATA_DIR"

for YEAR in $(seq $START_YEAR $END_YEAR); do
  YEAR_DIR="$DATA_DIR/$YEAR"
  mkdir -p "$YEAR_DIR"
  for MONTH in $(seq -w 1 12); do
    FILE_URL="$BASE_URL/$YEAR/csv/$YEAR$MONTH_PFile.csv"
    OUT_FILE="$YEAR_DIR/${YEAR}${MONTH}_PFile.csv"
    if [ ! -f "$OUT_FILE" ]; then
      echo "Downloading $FILE_URL ..."
      curl -f -o "$OUT_FILE" "$FILE_URL" || echo "Failed to download $FILE_URL"
    else
      echo "$OUT_FILE already exists, skipping."
    fi
  done
done

echo "NPPES monthly files download complete." 