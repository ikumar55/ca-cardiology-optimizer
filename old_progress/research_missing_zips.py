#!/usr/bin/env python3
"""
Research missing ZIP codes to add to California database.
"""

import json
import time

import requests


def research_missing_zips():
    """Research coordinates for missing ZIP codes."""
    missing_zips = ['96001', '96021', '96080', '96150']
    
    print('=== RESEARCHING MISSING ZIP CODES ===')
    print('ZIP codes to add:', missing_zips)
    print('\nResearching coordinates...')
    
    coordinates = {}
    
    for zip_code in missing_zips:
        try:
            print(f'Researching {zip_code}...')
            response = requests.get(f'https://api.zippopotam.us/us/{zip_code}', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lat = float(data['places'][0]['latitude'])
                lon = float(data['places'][0]['longitude'])
                place_name = data['places'][0]['place name']
                state = data['places'][0]['state abbreviation']
                
                coordinates[zip_code] = (lat, lon)
                print(f'✅ {zip_code}: ({lat}, {lon}) - {place_name}, {state}')
            else:
                print(f'❌ {zip_code}: API error - status {response.status_code}')
                
        except Exception as e:
            print(f'❌ {zip_code}: Error - {e}')
        
        time.sleep(1)  # Be nice to the API
    
    print(f'\n=== RESULTS ===')
    print(f'Coordinates found: {len(coordinates)}/{len(missing_zips)}')
    print(f'Coordinates: {coordinates}')
    
    return coordinates

if __name__ == "__main__":
    coordinates = research_missing_zips() 