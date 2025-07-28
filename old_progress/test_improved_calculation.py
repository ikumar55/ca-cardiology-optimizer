#!/usr/bin/env python3
"""
Test the improved travel time calculation.
"""

def test_improved_calculation():
    """Test the new travel time calculation logic."""
    print('=== TESTING IMPROVED TRAVEL TIME CALCULATION ===')
    
    test_distances = [25, 75, 200, 500]
    
    for distance in test_distances:
        if distance <= 50:
            # Urban travel: 35 mph average
            travel_time = distance * 1.71  # minutes (35 mph = 0.58 miles per minute)
            speed = '35 mph (urban)'
        elif distance <= 150:
            # Regional travel: 55 mph average
            travel_time = distance * 1.09  # minutes (55 mph = 0.91 miles per minute)
            speed = '55 mph (regional)'
        elif distance <= 300:
            # Interstate travel: 65 mph average
            travel_time = distance * 0.92  # minutes (65 mph = 1.08 miles per minute)
            speed = '65 mph (interstate)'
        else:
            # Long-distance travel: 60 mph average with rest stops
            travel_time = distance * 1.0  # minutes (60 mph = 1 mile per minute)
            # Add 10% for rest stops on long trips
            travel_time *= 1.1
            speed = '60 mph (long-distance)'
        
        print(f'{distance} miles: {travel_time:.1f} minutes ({speed})')
    
    print('\n=== COMPARISON WITH OLD CALCULATION ===')
    for distance in test_distances:
        old_time = min(180, distance * 1.0)  # Old calculation capped at 180
        if distance <= 50:
            new_time = distance * 1.71
        elif distance <= 150:
            new_time = distance * 1.09
        elif distance <= 300:
            new_time = distance * 0.92
        else:
            new_time = distance * 1.0 * 1.1
        
        print(f'{distance} miles: Old={old_time:.1f}min, New={new_time:.1f}min')

if __name__ == '__main__':
    test_improved_calculation() 