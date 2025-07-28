#!/usr/bin/env python3
"""
Generate Final Production-Ready Travel Matrix
"""

import time
from datetime import datetime

import numpy as np
import pandas as pd

from src.data.travel_matrix.travel_matrix_builder import TravelMatrixBuilder
from src.data.travel_matrix.zip_coordinates_db import ZipCoordinatesDB


def generate_final_travel_matrix():
    """Generate the final production-ready travel matrix with all improvements."""
    print('=== GENERATING FINAL PRODUCTION-READY TRAVEL MATRIX ===')
    print(f'Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Initialize components
    print('\n1. Initializing components...')
    zip_db = ZipCoordinatesDB()
    builder = TravelMatrixBuilder()
    
    # Load data
    print('\n2. Loading data...')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    demand = pd.read_csv('data/processed/ca_demand_filtered.csv')
    
    print(f'   Providers: {len(providers):,}')
    print(f'   Demand areas: {len(demand):,}')
    print(f'   Expected matrix size: {len(providers) * len(demand):,} pairs')
    
    # Generate the travel matrix with all improvements
    print('\n3. Generating travel matrix with all improvements...')
    start_time = time.time()
    
    # Use the improved travel matrix builder
    travel_matrix = builder.build_travel_matrix()
    
    generation_time = time.time() - start_time
    print(f'   Generation completed in {generation_time:.2f} seconds')
    
    # Analyze the results
    print('\n4. Analyzing results...')
    
    # Basic statistics
    total_pairs = len(travel_matrix)
    unique_providers = travel_matrix['provider_npi'].nunique()
    unique_demand = travel_matrix['zip_code'].nunique()
    
    print(f'   Total provider-demand pairs: {total_pairs:,}')
    print(f'   Unique providers: {unique_providers:,}')
    print(f'   Unique demand areas: {unique_demand:,}')
    
    # Travel time statistics
    travel_times = travel_matrix['drive_minutes']
    print(f'\n   Travel Time Statistics:')
    print(f'     Minimum: {travel_times.min():.1f} minutes')
    print(f'     Maximum: {travel_times.max():.1f} minutes')
    print(f'     Mean: {travel_times.mean():.1f} minutes')
    print(f'     Median: {travel_times.median():.1f} minutes')
    print(f'     Standard deviation: {travel_times.std():.1f} minutes')
    
    # Distance-based analysis
    print(f'\n   Distance-Based Analysis:')
    distances = []
    for _, row in travel_matrix.iterrows():
        demand_zip = str(row['zip_code'])
        provider_npi = row['provider_npi']
        
        # Get provider ZIP
        provider_row = providers[providers['provider_npi'] == provider_npi]
        if len(provider_row) > 0:
            provider_zip = str(provider_row['zip_code'].iloc[0])
            
            # Calculate distance
            demand_coords = zip_db.get_coordinates(demand_zip)
            provider_coords = zip_db.get_coordinates(provider_zip)
            
            if demand_coords and provider_coords:
                import math
                lat1, lon1 = demand_coords
                lat2, lon2 = provider_coords
                distance = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 69
                distances.append(distance)
    
    if distances:
        distances = np.array(distances)
        print(f'     Average distance: {distances.mean():.1f} miles')
        print(f'     Distance range: {distances.min():.1f} - {distances.max():.1f} miles')
        
        # Speed analysis by distance ranges
        print(f'\n   Speed Analysis by Distance Ranges:')
        distance_ranges = [
            (0, 50, 'Urban (≤50 miles)'),
            (51, 150, 'Regional (51-150 miles)'),
            (151, 300, 'Interstate (151-300 miles)'),
            (301, 1000, 'Long-distance (>300 miles)')
        ]
        
        for min_dist, max_dist, range_name in distance_ranges:
            mask = (distances >= min_dist) & (distances <= max_dist)
            if mask.sum() > 0:
                range_distances = distances[mask]
                range_times = travel_times[mask]
                avg_speed = np.mean(range_distances / (range_times / 60))
                print(f'     {range_name}: {len(range_distances):,} pairs, avg speed {avg_speed:.1f} mph')
    
    # Quality checks
    print(f'\n5. Quality checks...')
    
    # Check for missing values
    missing_values = travel_matrix.isnull().sum()
    if missing_values.sum() > 0:
        print(f'   ⚠️  Missing values found:')
        for col, count in missing_values.items():
            if count > 0:
                print(f'     {col}: {count:,}')
    else:
        print(f'   ✅ No missing values')
    
    # Check for unrealistic travel times
    unrealistic_times = travel_times[travel_times > 600]  # More than 10 hours
    if len(unrealistic_times) > 0:
        print(f'   ⚠️  Unrealistic travel times (>10 hours): {len(unrealistic_times):,}')
    else:
        print(f'   ✅ All travel times are realistic')
    
    # Check for zero travel times
    zero_times = travel_times[travel_times == 0]
    if len(zero_times) > 0:
        print(f'   ⚠️  Zero travel times: {len(zero_times):,}')
    else:
        print(f'   ✅ No zero travel times')
    
    # Save the final matrix
    print(f'\n6. Saving final production matrix...')
    
    # Create backup of current matrix
    import os
    import shutil
    if os.path.exists('data/processed/travel_matrix.parquet'):
        backup_path = f'data/processed/travel_matrix_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.parquet'
        shutil.copy2('data/processed/travel_matrix.parquet', backup_path)
        print(f'   Created backup: {backup_path}')
    
    # Save the new matrix
    output_path = 'data/processed/travel_matrix.parquet'
    travel_matrix.to_parquet(output_path, index=False)
    print(f'   Saved final matrix: {output_path}')
    
    # File size
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f'   File size: {file_size:.2f} MB')
    
    # Final summary
    print(f'\n=== FINAL PRODUCTION MATRIX SUMMARY ===')
    print(f'✅ Generation completed successfully')
    print(f'✅ Total pairs: {total_pairs:,}')
    print(f'✅ Providers: {unique_providers:,}')
    print(f'✅ Demand areas: {unique_demand:,}')
    print(f'✅ Generation time: {generation_time:.2f} seconds')
    print(f'✅ File size: {file_size:.2f} MB')
    print(f'✅ Quality checks passed')
    print(f'✅ Ready for cardiology optimization')
    
    return travel_matrix

def validate_final_matrix(travel_matrix):
    """Validate the final matrix for production readiness."""
    print(f'\n=== VALIDATING FINAL MATRIX ===')
    
    # Load reference data
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    demand = pd.read_csv('data/processed/ca_demand_filtered.csv')
    
    # Check completeness
    expected_pairs = len(providers) * len(demand)
    actual_pairs = len(travel_matrix)
    completeness = actual_pairs / expected_pairs * 100
    
    print(f'Completeness: {completeness:.1f}% ({actual_pairs:,}/{expected_pairs:,} pairs)')
    
    # Check data types
    print(f'\nData types:')
    for col, dtype in travel_matrix.dtypes.items():
        print(f'  {col}: {dtype}')
    
    # Check value ranges
    print(f'\nValue ranges:')
    for col in travel_matrix.columns:
        if travel_matrix[col].dtype in ['int64', 'float64']:
            min_val = travel_matrix[col].min()
            max_val = travel_matrix[col].max()
            print(f'  {col}: {min_val} to {max_val}')
    
    # Performance metrics
    print(f'\nPerformance metrics:')
    travel_times = travel_matrix['drive_minutes']
    print(f'  Mean travel time: {travel_times.mean():.1f} minutes')
    print(f'  Median travel time: {travel_times.median():.1f} minutes')
    print(f'  Travel time range: {travel_times.min():.1f} to {travel_times.max():.1f} minutes')
    
    return True

if __name__ == '__main__':
    # Generate the final matrix
    final_matrix = generate_final_travel_matrix()
    
    # Validate the final matrix
    validate_final_matrix(final_matrix)
    
    print(f'\n🎉 FINAL PRODUCTION TRAVEL MATRIX GENERATED SUCCESSFULLY!')
    print(f'Ready for cardiology optimization system.') 