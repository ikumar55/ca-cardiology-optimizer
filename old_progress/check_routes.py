#!/usr/bin/env python3
"""
Check what routes actually exist in our travel matrix.
"""

import pandas as pd


def check_actual_routes():
    """Check what routes actually exist in our travel matrix."""
    print('=== CHECKING ACTUAL ROUTES IN TRAVEL MATRIX ===')
    
    # Load data
    df = pd.read_parquet('data/processed/travel_matrix.parquet')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    
    # Create provider ZIP lookup
    provider_zip_lookup = dict(zip(providers['provider_npi'], providers['zip_code']))
    
    print(f'Total routes in matrix: {len(df):,}')
    print(f'Unique demand ZIP codes: {df["zip_code"].nunique()}')
    print(f'Unique provider NPIs: {df["provider_npi"].nunique()}')
    
    # Show sample routes
    print(f'\n=== SAMPLE ROUTES ===')
    sample_routes = df.head(10)
    
    for _, row in sample_routes.iterrows():
        provider_zip = provider_zip_lookup.get(row['provider_npi'], 'Unknown')
        print(f'Demand {row["zip_code"]} to Provider {provider_zip} (NPI: {row["provider_npi"]}): {row["drive_minutes"]:.1f} min')
    
    # Check for specific routes
    print(f'\n=== CHECKING SPECIFIC ROUTES ===')
    
    # Check LA to Bay Area routes
    la_demand = df[df['zip_code'].astype(str).str.startswith('900')]
    bay_providers = [npi for npi, zip_code in provider_zip_lookup.items() if str(zip_code).startswith('94') or str(zip_code).startswith('95')]
    
    la_to_bay = la_demand[la_demand['provider_npi'].isin(bay_providers)]
    print(f'LA to Bay Area routes: {len(la_to_bay)}')
    
    if len(la_to_bay) > 0:
        print('Sample LA to Bay Area routes:')
        for _, row in la_to_bay.head(5).iterrows():
            provider_zip = provider_zip_lookup.get(row['provider_npi'], 'Unknown')
            print(f'  {row["zip_code"]} to {provider_zip}: {row["drive_minutes"]:.1f} min')

if __name__ == '__main__':
    check_actual_routes() 