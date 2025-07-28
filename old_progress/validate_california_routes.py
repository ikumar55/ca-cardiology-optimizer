#!/usr/bin/env python3
"""
Validate travel times against known California routes.
"""

import numpy as np
import pandas as pd

from src.data.travel_matrix.zip_coordinates_db import ZipCoordinatesDB


def validate_california_routes():
    """Validate travel times against known California routes."""
    print('=== VALIDATING AGAINST KNOWN CALIFORNIA ROUTES ===')
    
    # Load data
    df = pd.read_parquet('data/processed/travel_matrix.parquet')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    zip_db = ZipCoordinatesDB()
    
    # Create provider ZIP lookup
    provider_zip_lookup = dict(zip(providers['provider_npi'], providers['zip_code']))
    
    print(f'Total routes in matrix: {len(df):,}')
    print(f'Unique demand ZIP codes: {df["zip_code"].nunique()}')
    print(f'Unique provider NPIs: {df["provider_npi"].nunique()}')
    
    # Test actual routes from our data
    print(f'\n=== TESTING ACTUAL ROUTES FROM DATA ===')
    
    # Get sample routes for validation
    sample_routes = df.sample(min(20, len(df)))
    
    validation_results = []
    
    for _, row in sample_routes.iterrows():
        demand_zip = str(row['zip_code'])
        provider_npi = row['provider_npi']
        calculated_time = row['drive_minutes']
        
        provider_zip = provider_zip_lookup.get(provider_npi, 'Unknown')
        if provider_zip == 'Unknown':
            continue
            
        provider_zip = str(provider_zip)
        
        # Calculate actual distance for reference
        demand_coords = zip_db.get_coordinates(demand_zip)
        provider_coords = zip_db.get_coordinates(provider_zip)
        
        if demand_coords and provider_coords:
            import math
            lat1, lon1 = demand_coords
            lat2, lon2 = provider_coords
            distance = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 69
            
            # Calculate expected travel time based on our speed assumptions
            if distance <= 50:
                expected_time = distance * 1.71
            elif distance <= 150:
                expected_time = distance * 1.09
            elif distance <= 300:
                expected_time = distance * 0.92
            else:
                expected_time = distance * 1.0 * 1.1
            
            # Allow 20% tolerance
            tolerance = expected_time * 0.2
            expected_min = expected_time - tolerance
            expected_max = expected_time + tolerance
            
            status = '✅ PASS' if expected_min <= calculated_time <= expected_max else '❌ FAIL'
            
            validation_results.append({
                'route': f'{demand_zip} to {provider_zip}',
                'distance': distance,
                'expected': expected_time,
                'calculated': calculated_time,
                'status': status
            })
            
            print(f'{status} {demand_zip} to {provider_zip}: {calculated_time:.1f} min (expected {expected_time:.1f} ± {tolerance:.1f} min)')
            print(f'  Distance: {distance:.1f} miles')
    
    # Summary statistics
    if validation_results:
        print(f'\n=== VALIDATION SUMMARY ===')
        passed = sum(1 for r in validation_results if r['status'] == '✅ PASS')
        failed = sum(1 for r in validation_results if r['status'] == '❌ FAIL')
        total = len(validation_results)
        
        print(f'Passed: {passed}/{total} ({passed/total*100:.1f}%)')
        print(f'Failed: {failed}/{total} ({failed/total*100:.1f}%)')
        
        if failed > 0:
            print(f'\n=== FAILED ROUTES ===')
            for result in validation_results:
                if result['status'] == '❌ FAIL':
                    print(f'{result["route"]}: {result["calculated"]:.1f} min (expected {result["expected"]:.1f} min)')
    else:
        print(f'\n=== NO VALIDATION RESULTS ===')
        print('No routes found for validation.')
    
    return validation_results

def analyze_geographic_consistency():
    """Analyze geographic consistency of travel times."""
    print(f'\n=== GEOGRAPHIC CONSISTENCY ANALYSIS ===')
    
    df = pd.read_parquet('data/processed/travel_matrix.parquet')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    zip_db = ZipCoordinatesDB()
    
    # Create provider ZIP lookup
    provider_zip_lookup = dict(zip(providers['provider_npi'], providers['zip_code']))
    
    # Test distance vs travel time correlation
    print('Testing distance vs travel time correlation...')
    
    sample_pairs = df.sample(min(1000, len(df)))
    
    distances = []
    travel_times = []
    
    for _, row in sample_pairs.iterrows():
        demand_zip = str(row['zip_code'])
        provider_npi = row['provider_npi']
        
        provider_zip = provider_zip_lookup.get(provider_npi)
        if not provider_zip:
            continue
            
        provider_zip = str(provider_zip)
        
        demand_coords = zip_db.get_coordinates(demand_zip)
        provider_coords = zip_db.get_coordinates(provider_zip)
        
        if demand_coords and provider_coords:
            import math
            lat1, lon1 = demand_coords
            lat2, lon2 = provider_coords
            distance = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 69
            
            distances.append(distance)
            travel_times.append(row['drive_minutes'])
    
    if distances and travel_times:
        correlation = np.corrcoef(distances, travel_times)[0, 1]
        print(f'Distance vs Travel Time Correlation: {correlation:.3f}')
        
        # Check for outliers
        mean_time = np.mean(travel_times)
        std_time = np.std(travel_times)
        outliers = [t for t in travel_times if abs(t - mean_time) > 2 * std_time]
        print(f'Outliers (>2 std dev): {len(outliers)}/{len(travel_times)} ({len(outliers)/len(travel_times)*100:.1f}%)')
        
        # Analyze by distance ranges
        print(f'\n=== DISTANCE RANGE ANALYSIS ===')
        distance_ranges = [
            (0, 50, 'Urban (≤50 miles)'),
            (51, 150, 'Regional (51-150 miles)'),
            (151, 300, 'Interstate (151-300 miles)'),
            (301, 1000, 'Long-distance (>300 miles)')
        ]
        
        for min_dist, max_dist, range_name in distance_ranges:
            pairs_in_range = [(d, t) for d, t in zip(distances, travel_times) if min_dist <= d <= max_dist]
            if pairs_in_range:
                range_distances, range_times = zip(*pairs_in_range)
                avg_speed = np.mean([d / (t / 60) for d, t in pairs_in_range])  # mph
                print(f'{range_name}: {len(pairs_in_range)} pairs, avg speed {avg_speed:.1f} mph')

def validate_known_city_pairs():
    """Validate against known California city pairs."""
    print(f'\n=== KNOWN CITY PAIR VALIDATION ===')
    
    df = pd.read_parquet('data/processed/travel_matrix.parquet')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    zip_db = ZipCoordinatesDB()
    
    # Create provider ZIP lookup
    provider_zip_lookup = dict(zip(providers['provider_npi'], providers['zip_code']))
    
    # Known city pairs with expected travel times (using actual ZIP codes from our data)
    known_pairs = [
        # LA to Bay Area (using actual ZIP codes)
        (90001, 95128, 'LA to San Jose', 260, 280),  # LA to San Jose
        (90001, 94598, 'LA to Walnut Creek', 320, 340),  # LA to Walnut Creek
        (90002, 95128, 'LA to San Jose', 260, 280),  # LA to San Jose
        
        # San Diego to LA
        (92007, 90029, 'San Diego to LA', 120, 140),  # San Diego to LA
        (92008, 90033, 'San Diego to LA', 120, 140),  # San Diego to LA
        
        # Regional routes
        (90001, 90210, 'LA to Beverly Hills', 15, 25),  # LA to Beverly Hills
        (90001, 92614, 'LA to Irvine', 35, 45),  # LA to Irvine
    ]
    
    print(f'Testing {len(known_pairs)} known city pairs...\n')
    
    validation_results = []
    
    for demand_zip, provider_zip, route_name, expected_min, expected_max in known_pairs:
        # Find this route in our travel matrix
        route_data = df[
            (df['zip_code'] == demand_zip) & 
            (df['provider_npi'].isin(providers[providers['zip_code'] == provider_zip]['provider_npi']))
        ]
        
        if len(route_data) > 0:
            calculated_time = route_data['drive_minutes'].iloc[0]
            status = '✅ PASS' if expected_min <= calculated_time <= expected_max else '❌ FAIL'
            
            validation_results.append({
                'route': route_name,
                'expected_min': expected_min,
                'expected_max': expected_max,
                'calculated': calculated_time,
                'status': status
            })
            
            print(f'{status} {route_name}: {calculated_time:.1f} min (expected {expected_min}-{expected_max} min)')
        else:
            print(f'⚠️  NOT FOUND: {route_name} ({demand_zip} to {provider_zip})')
    
    # Summary
    if validation_results:
        passed = sum(1 for r in validation_results if r['status'] == '✅ PASS')
        failed = sum(1 for r in validation_results if r['status'] == '❌ FAIL')
        total = len(validation_results)
        
        print(f'\nKnown City Pairs: {passed}/{total} passed ({passed/total*100:.1f}%)')

if __name__ == '__main__':
    validation_results = validate_california_routes()
    analyze_geographic_consistency()
    validate_known_city_pairs() 