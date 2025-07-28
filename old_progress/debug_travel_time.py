#!/usr/bin/env python3
"""
Debug travel time calculation issue.
"""

from src.data.travel_matrix.travel_matrix_builder import TravelMatrixBuilder


def debug_travel_time():
    """Debug the travel time calculation."""
    print('=== DEBUGGING TRAVEL TIME CALCULATION ===')
    
    # Initialize builder
    builder = TravelMatrixBuilder()
    builder.load_provider_data()
    builder.load_demand_data()
    
    # Test a few provider-demand pairs
    test_pairs = [
        ('91910', '90001'),  # San Diego to LA
        ('95128', '90002'),  # San Jose to LA
        ('92029', '90003'),  # San Diego area to LA
    ]
    
    for origin, dest in test_pairs:
        print(f'\n--- Testing {origin} to {dest} ---')
        
        # Check if ZIP codes are in database
        origin_coords = builder.zip_db.get_coordinates(origin)
        dest_coords = builder.zip_db.get_coordinates(dest)
        
        print(f'Origin {origin} in database: {origin_coords is not None}')
        print(f'Dest {dest} in database: {dest_coords is not None}')
        
        if origin_coords and dest_coords:
            print(f'Origin coords: {origin_coords}')
            print(f'Dest coords: {dest_coords}')
            
            # Calculate distance
            distance = builder._calculate_distance(origin_coords, dest_coords)
            print(f'Distance: {distance:.2f} miles')
            
            # Calculate travel time
            travel_time = builder._estimate_travel_time(origin, dest)
            print(f'Travel time: {travel_time:.2f} minutes')
            
            # Check if it's hitting the 180-minute cap
            if travel_time >= 180:
                print('⚠️  Hitting 180-minute cap!')
        else:
            print('❌ ZIP codes not found in database')

if __name__ == "__main__":
    debug_travel_time() 