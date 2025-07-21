"""
Geocoding module for the Cardiology Care Optimization System.

This module handles address geocoding using Nominatim (OpenStreetMap)
and implements caching to avoid redundant API requests.
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import pandas as pd
import requests

try:
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class ProviderGeocoder:
    """Geocode provider addresses using Nominatim (OpenStreetMap)."""

    # Nominatim API endpoint
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, cache_file: str = "geocoding_cache.json"):
        """Initialize the geocoder with caching."""
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        self.request_delay = 1.0  # Respect Nominatim rate limits

    def _load_cache(self) -> dict[str, dict]:
        """Load existing geocoding cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        return {}

    def _save_cache(self):
        """Save geocoding cache to file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save cache: {e}")

    def _simplify_address(self, address: str) -> str:
        """Simplify address for better geocoding success."""
        # Remove suite/unit numbers
        address = re.sub(
            r",?\s*(STE|SUITE|UNIT|APT|#)\s*\w+", "", address, flags=re.IGNORECASE
        )

        # Remove ZIP codes - simpler approach
        address = re.sub(r"\s+\d{5}.*$", "", address)

        # Clean up extra commas and spaces
        address = re.sub(r"\s*,\s*", ", ", address)
        address = address.strip()

        return address

    def _geocode_address(self, address: str) -> Optional[tuple[float, float]]:
        """Geocode a single address using Nominatim."""
        # Check cache first
        if address in self.cache:
            coords = self.cache[address]
            if coords and coords.get("lat") and coords.get("lon"):
                return (coords["lat"], coords["lon"])

        # Simplify address for geocoding
        simplified_address = self._simplify_address(address)
        search_address = f"{simplified_address}, California, USA"
        encoded_address = quote(search_address)

        # Make API request
        url = f"{self.NOMINATIM_BASE_URL}?q={encoded_address}&format=json&limit=1"

        try:
            response = requests.get(
                url, headers={"User-Agent": "CardiologyOptimizer/1.0"}, timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                lat = float(result.get("lat", 0))
                lon = float(result.get("lon", 0))

                # Cache the result
                self.cache[address] = {
                    "lat": lat,
                    "lon": lon,
                    "display_name": result.get("display_name", ""),
                    "confidence": result.get("importance", 0),
                }

                return (lat, lon)
            else:
                # Cache failed attempts to avoid retrying
                self.cache[address] = None
                return None

        except Exception as e:
            logger.error(f"Geocoding failed for {address}: {e}")
            self.cache[address] = None
            return None

    def geocode_providers(
        self, df: pd.DataFrame, address_col: str = "practice_address"
    ) -> pd.DataFrame:
        """Geocode all provider addresses in the dataframe."""
        logger.info(f"🔄 Starting geocoding for {len(df)} providers")

        # Add coordinate columns
        df_geocoded = df.copy()
        df_geocoded["latitude"] = None
        df_geocoded["longitude"] = None
        df_geocoded["geocoding_confidence"] = None

        success_count = 0
        error_count = 0

        for idx, row in df_geocoded.iterrows():
            address = row[address_col]

            if pd.isna(address) or not address:
                continue

            logger.info(f"📍 Geocoding: {address[:50]}...")

            coords = self._geocode_address(address)

            if coords:
                lat, lon = coords
                df_geocoded.at[idx, "latitude"] = lat
                df_geocoded.at[idx, "longitude"] = lon

                # Get confidence from cache
                cache_entry = self.cache.get(address, {})
                df_geocoded.at[idx, "geocoding_confidence"] = cache_entry.get(
                    "confidence", 0
                )

                success_count += 1
                logger.info(f"✅ Geocoded: {lat:.4f}, {lon:.4f}")
            else:
                error_count += 1
                logger.warning(f"❌ Failed to geocode: {address}")

            # Respect rate limits
            time.sleep(self.request_delay)

            # Save cache periodically
            if idx % 10 == 0:
                self._save_cache()

        # Final cache save
        self._save_cache()

        logger.info(f"🎉 Geocoding complete!")
        logger.info(f"✅ Successfully geocoded: {success_count} providers")
        logger.info(f"❌ Failed to geocode: {error_count} providers")
        logger.info(
            f"📊 Success rate: {success_count/(success_count+error_count)*100:.1f}%"
        )

        return df_geocoded

    def validate_geocoding(self, df: pd.DataFrame) -> dict:
        """Validate geocoding results and provide quality metrics."""
        total_providers = len(df)
        geocoded_providers = df[df["latitude"].notna()].shape[0]
        failed_geocoding = total_providers - geocoded_providers

        # Calculate average confidence
        avg_confidence = df["geocoding_confidence"].mean()

        # Check for reasonable coordinate ranges (California bounds)
        ca_bounds = {
            "lat_min": 32.5,
            "lat_max": 42.0,
            "lon_min": -124.5,
            "lon_max": -114.0,
        }

        in_ca_bounds = df[
            (df["latitude"] >= ca_bounds["lat_min"])
            & (df["latitude"] <= ca_bounds["lat_max"])
            & (df["longitude"] >= ca_bounds["lon_min"])
            & (df["longitude"] <= ca_bounds["lon_max"])
        ].shape[0]

        validation_results = {
            "total_providers": total_providers,
            "geocoded_providers": geocoded_providers,
            "failed_geocoding": failed_geocoding,
            "success_rate": geocoded_providers / total_providers * 100,
            "average_confidence": avg_confidence,
            "in_california_bounds": in_ca_bounds,
            "bounds_accuracy": (
                in_ca_bounds / geocoded_providers * 100 if geocoded_providers > 0 else 0
            ),
        }

        logger.info("🔍 Geocoding Validation Results:")
        for key, value in validation_results.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")

        return validation_results


if __name__ == "__main__":
    # Test the geocoder with sample data
    import sys

    sys.path.append("../../..")

    # Load sample data
    sample_file = "data/processed/ca_cardiology_cleaned.csv"
    if Path(sample_file).exists():
        df = pd.read_csv(sample_file)

        # Test with first 5 providers
        test_df = df.head(5).copy()

        geocoder = ProviderGeocoder()
        geocoded_df = geocoder.geocode_providers(test_df)

        # Show results
        print("\n📍 Geocoding Results:")
        for _, row in geocoded_df.iterrows():
            if pd.notna(row["latitude"]):
                print(
                    f"✅ {row['provider_name']}: {row['latitude']:.4f}, {row['longitude']:.4f}"
                )
            else:
                print(f"❌ {row['provider_name']}: Failed to geocode")

        # Validate results
        validation = geocoder.validate_geocoding(geocoded_df)

    else:
        print(f"❌ Sample file not found: {sample_file}")
        print("Please run the data cleaning pipeline first.")
