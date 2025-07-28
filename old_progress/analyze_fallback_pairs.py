#!/usr/bin/env python3
"""
Analyze fallback travel time pairs to understand distance distribution.
"""

import math

import pandas as pd

from src.data.travel_matrix.zip_coordinates_db import ZipCoordinatesDB


def analyze_fallback_pairs():
    """Analyze pairs that are hitting the 180-minute fallback limit."""
    print('=== ANALYZING FALLBACK TRAVEL TIME PAIRS ===')
    
    # Load data
    df = pd.read_parquet('data/processed/travel_matrix.parquet')
    providers = pd.read_csv('data/processed/ca_providers_filtered.csv')
    zip_db = ZipCoordinatesDB()
    
    # Create provider ZIP lookup
    provider_zip_lookup = dict(zip(providers['provider_npi'], providers['zip_code']))
    
    # Get fallback pairs
    fallback_pairs = df[df['drive_minutes'] == 180]
    print(f'Total fallback pairs: {len(fallback_pairs):,}')
    
    # Analyze distances for a larger sample
    print('\n=== FALLBACK PAIR DISTANCE ANALYSIS ===')
    sample_pairs = fallback_pairs.head(100)  # Increased sample size
    
    distances = []
    for _, row in sample_pairs.iterrows():
        demand_zip = str(row['zip_code'])
        provider_npi = str(row['provider_npi'])
        
        # Get provider ZIP code
        provider_zip = provider_zip_lookup.get(int(provider_npi))
        if not provider_zip:
            continue
            
        provider_zip = str(provider_zip)
        
        # Get coordinates
        demand_coords = zip_db.get_coordinates(demand_zip)
        provider_coords = zip_db.get_coordinates(provider_zip)
        
        if demand_coords and provider_coords:
            lat1, lon1 = demand_coords
            lat2, lon2 = provider_coords
            
            # Calculate distance in miles (approximate)
            distance = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 69
            distances.append(distance)
    
    if distances:
        print(f'Analyzed {len(distances)} fallback pairs')
        print(f'\n=== DISTANCE STATISTICS ===')
        print(f'Mean distance: {sum(distances)/len(distances):.1f} miles')
        print(f'Min distance: {min(distances):.1f} miles')
        print(f'Max distance: {max(distances):.1f} miles')
        print(f'Median distance: {sorted(distances)[len(distances)//2]:.1f} miles')
        
        # Analyze distance distribution
        print(f'\n=== DISTANCE DISTRIBUTION ===')
        under_100 = sum(1 for d in distances if d <= 100)
        under_150 = sum(1 for d in distances if d <= 150)
        under_200 = sum(1 for d in distances if d <= 200)
        under_300 = sum(1 for d in distances if d <= 300)
        under_400 = sum(1 for d in distances if d <= 400)
        over_400 = sum(1 for d in distances if d > 400)
        
        print(f'Under 100 miles: {under_100} pairs ({under_100/len(distances)*100:.1f}%)')
        print(f'Under 150 miles: {under_150} pairs ({under_150/len(distances)*100:.1f}%)')
        print(f'Under 200 miles: {under_200} pairs ({under_200/len(distances)*100:.1f}%)')
        print(f'Under 300 miles: {under_300} pairs ({under_300/len(distances)*100:.1f}%)')
        print(f'Under 400 miles: {under_400} pairs ({under_400/len(distances)*100:.1f}%)')
        print(f'Over 400 miles: {over_400} pairs ({over_400/len(distances)*100:.1f}%)')
        
        # Show some examples
        print(f'\n=== SAMPLE DISTANCES ===')
        sorted_distances = sorted(distances)
        print(f'Shortest 5: {sorted_distances[:5]}')
        print(f'Longest 5: {sorted_distances[-5:]}')

if __name__ == '__main__':
    analyze_fallback_pairs() 