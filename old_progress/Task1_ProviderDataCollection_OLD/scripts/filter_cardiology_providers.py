#!/usr/bin/env python3
"""
Cardiology Provider Data Filter
==============================

This script filters the raw CA Medical Board roster data to identify cardiology providers
and validates the expected provider count.

Author: AI Assistant
Created: July 24, 2025
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "data" / "ca_medical_board_roster_raw.csv"
OUTPUT_FILE = BASE_DIR / "data" / "cardiology_providers_filtered.csv"
REPORT_FILE = BASE_DIR / "results" / "filtering_report.json"

# Ensure results directory exists
(BASE_DIR / "results").mkdir(exist_ok=True)

# Cardiology specialty keywords
CARDIOLOGY_KEYWORDS = [
    'cardiol',  # Catches Cardiology, Cardiologist
    'cardiac',  # Catches Cardiac Surgery, Cardiac
    'cardiovascular',  # Catches Cardiovascular Disease
    'heart',  # Catches Heart Surgery, Heart Disease
]

def load_raw_data() -> pd.DataFrame:
    """Load the raw CSV data."""
    logger.info(f"Loading raw data from {INPUT_FILE}")
    try:
        # Try reading with different delimiters
        for delimiter in ['\t', ',']:
            try:
                df = pd.read_csv(INPUT_FILE, delimiter=delimiter, encoding='utf-8')
                if len(df.columns) > 1:  # Successfully parsed multiple columns
                    logger.info(f"Successfully loaded {len(df):,} records using delimiter: {repr(delimiter)}")
                    return df
            except Exception:
                continue
        
        raise ValueError("Could not parse file with any known delimiter")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def identify_specialty_columns(df: pd.DataFrame) -> List[str]:
    """Identify columns that might contain specialty information."""
    potential_columns = []
    specialty_keywords = ['special', 'practice', 'type', 'license', 'category', 'field']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in specialty_keywords):
            potential_columns.append(col)
    
    logger.info(f"Identified potential specialty columns: {potential_columns}")
    return potential_columns

def filter_cardiology_providers(df: pd.DataFrame, specialty_cols: List[str]) -> pd.DataFrame:
    """Filter for cardiology providers across all potential specialty columns."""
    logger.info("Filtering for cardiology providers")
    
    # Create a mask for each specialty column
    masks = []
    for col in specialty_cols:
        col_mask = df[col].astype(str).str.lower().apply(
            lambda x: any(keyword in x for keyword in CARDIOLOGY_KEYWORDS)
        )
        masks.append(col_mask)
    
    # Combine masks with OR operation
    final_mask = pd.concat(masks, axis=1).any(axis=1)
    filtered_df = df[final_mask].copy()
    
    logger.info(f"Found {len(filtered_df):,} cardiology providers")
    return filtered_df

def validate_provider_count(df: pd.DataFrame, specialty_cols: List[str]) -> Dict[str, Any]:
    """Validate the filtered provider count against expected numbers."""
    provider_count = len(df)
    expected_count = 5200
    margin = 0.2  # Allow 20% deviation from expected count
    
    within_expected = (
        provider_count >= expected_count * (1 - margin) and
        provider_count <= expected_count * (1 + margin)
    )
    
    # Create specialty distribution
    specialty_dist = {}
    for col in specialty_cols:
        value_counts = df[col].value_counts()
        specialty_dist[col] = {str(k): int(v) for k, v in value_counts.items()}
    
    report = {
        "total_providers_found": provider_count,
        "expected_provider_count": expected_count,
        "within_expected_range": within_expected,
        "deviation_percentage": ((provider_count - expected_count) / expected_count) * 100,
        "specialty_distribution": specialty_dist,
        "columns_analyzed": specialty_cols
    }
    
    logger.info(f"Validation complete: found {provider_count:,} providers")
    if not within_expected:
        logger.warning(
            f"Provider count ({provider_count:,}) differs significantly "
            f"from expected ({expected_count:,})"
        )
    
    return report

def save_results(filtered_df: pd.DataFrame, report: Dict[str, Any]) -> None:
    """Save filtered data and validation report."""
    # Save filtered providers
    filtered_df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Saved filtered providers to {OUTPUT_FILE}")
    
    # Save report
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Saved filtering report to {REPORT_FILE}")

def main():
    """Main execution function."""
    try:
        # Load raw data
        df = load_raw_data()
        
        # Show sample of columns and data
        logger.info(f"Columns found: {', '.join(df.columns)}")
        logger.info(f"Sample of first row: {df.iloc[0].to_dict()}")
        
        # Identify specialty columns
        specialty_cols = identify_specialty_columns(df)
        if not specialty_cols:
            raise ValueError("No specialty columns found in the data")
        
        # Filter cardiology providers
        filtered_df = filter_cardiology_providers(df, specialty_cols)
        
        # Validate results
        report = validate_provider_count(filtered_df, specialty_cols)
        
        # Save results
        save_results(filtered_df, report)
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 