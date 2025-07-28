"""
Geocoding service for ZIP code to coordinate conversion.
Uses free geocoding services with caching to minimize API calls.
"""

import json
import logging
import os
import time
from typing import Dict, Optional, Tuple

import pandas as pd
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Cost-effective geocoding service using free APIs with caching.
    """
    
    def __init__(self, cache_file: str = "data/processed/zip_coordinates_cache.json"):
        """
        Initialize the geocoding service.
        
        Args:
            cache_file: Path to cache file for storing coordinates
        """
        self.cache_file = cache_file
        self.geolocator = Nominatim(user_agent="ca_cardiology_optimizer")
        self.cache = self._load_cache()
        self.rate_limit_delay = 1.0  # 1 second delay between requests
        
    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load cached coordinates from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert string keys back to tuples
                    return {zip_code: tuple(coords) for zip_code, coords in cache_data.items()}
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save coordinates to cache file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def geocode_zip(self, zip_code: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a ZIP code to coordinates with caching.
        
        Args:
            zip_code: ZIP code to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        # Check cache first
        if zip_code in self.cache:
            logger.debug(f"Using cached coordinates for {zip_code}")
            return self.cache[zip_code]
        
        # Geocode with rate limiting
        try:
            logger.info(f"Geocoding {zip_code}...")
            location = self.geolocator.geocode(f"{zip_code}, CA, USA")
            
            if location:
                coords = (location.latitude, location.longitude)
                self.cache[zip_code] = coords
                self._save_cache()
                logger.info(f"Successfully geocoded {zip_code} to {coords}")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                return coords
            else:
                logger.warning(f"No location found for {zip_code}")
                return None
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding service unavailable for {zip_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error geocoding {zip_code}: {e}")
            return None
    
    def batch_geocode(self, zip_codes: list) -> Dict[str, Tuple[float, float]]:
        """
        Geocode multiple ZIP codes efficiently.
        
        Args:
            zip_codes: List of ZIP codes to geocode
            
        Returns:
            Dictionary mapping ZIP codes to coordinates
        """
        results = {}
        
        for zip_code in zip_codes:
            coords = self.geocode_zip(zip_code)
            if coords:
                results[zip_code] = coords
            else:
                logger.warning(f"Failed to geocode {zip_code}")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics."""
        return {
            "cached_entries": len(self.cache),
            "cache_file": self.cache_file
        }


def create_zip_coordinates_lookup(providers_df: pd.DataFrame, demand_df: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
    """
    Create a comprehensive ZIP code to coordinates lookup.
    
    Args:
        providers_df: DataFrame with provider ZIP codes
        demand_df: DataFrame with demand ZIP codes
        
    Returns:
        Dictionary mapping ZIP codes to coordinates
    """
    # Extract unique ZIP codes
    provider_zips = set(providers_df['zip_code'].dropna().astype(str))
    demand_zips = set(demand_df['zip_code'].dropna().astype(str))
    all_zips = provider_zips.union(demand_zips)
    
    logger.info(f"Found {len(all_zips)} unique ZIP codes to geocode")
    
    # Initialize geocoding service
    geocoder = GeocodingService()
    
    # Geocode all ZIP codes
    coordinates = geocoder.batch_geocode(list(all_zips))
    
    logger.info(f"Successfully geocoded {len(coordinates)} out of {len(all_zips)} ZIP codes")
    
    return coordinates 