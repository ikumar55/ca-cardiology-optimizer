"""
ZIP code coordinates database for California using real data.
Loads ZIP centroids from a CSV file (data/external/uszips_latlon.csv).
"""

import logging
import os
from typing import Dict, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

class ZipCoordinatesDB:
    """
    Loads ZIP code coordinates from a real CSV file.
    Expects columns: zip,lat,lon (ZIP as string, lat/lon as float)
    """
    
    def __init__(self, csv_path: str = "data/external/uszips_latlon.csv"):
        """
        Initialize the ZIP coordinates database from a CSV file.
        Download a real ZIP centroid file (e.g., US Census Gazetteer) and place it at data/external/uszips_latlon.csv.
        Example source: https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gaz_zcta_national.txt
        Required columns: ZCTA5, INTPTLAT, INTPTLONG (tab-delimited)
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"ZIP centroid file not found: {csv_path}\nPlease download a real ZIP centroid file (see docstring) and place it at this path.")
        df = pd.read_csv(csv_path, sep='\t', dtype=str, skip_blank_lines=True)
        df.columns = [c.strip() for c in df.columns]
        if "ZCTA5" in df.columns and "INTPTLAT" in df.columns and "INTPTLONG" in df.columns:
            self.coordinates = dict(zip(df["ZCTA5"].astype(str).str.zfill(5), zip(df["INTPTLAT"].astype(float), df["INTPTLONG"].astype(float))))
        elif "GEOID" in df.columns and "INTPTLAT" in df.columns and "INTPTLONG" in df.columns:
            self.coordinates = dict(zip(df["GEOID"].astype(str).str.zfill(5), zip(df["INTPTLAT"].astype(float), df["INTPTLONG"].astype(float))))
        elif "zip" in df.columns and "lat" in df.columns and "lon" in df.columns:
            self.coordinates = dict(zip(df["zip"], zip(df["lat"], df["lon"])))
        else:
            raise ValueError(f"CSV file {csv_path} must have columns ZCTA5,INTPTLAT,INTPTLONG or GEOID,INTPTLAT,INTPTLONG or zip,lat,lon")
        logger.info(f"Loaded {len(self.coordinates)} ZIP code coordinates from {csv_path}")
    
    def get_coordinates(self, zip_code: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a ZIP code.
        Args:
            zip_code: ZIP code to look up
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        clean_zip = str(zip_code).zfill(5)
        return self.coordinates.get(clean_zip)
    
    def batch_get_coordinates(self, zip_codes: list) -> Dict[str, Tuple[float, float]]:
        """
        Get coordinates for multiple ZIP codes.
        Args:
            zip_codes: List of ZIP codes
        Returns:
            Dictionary mapping ZIP codes to coordinates
        """
        results = {}
        for zip_code in zip_codes:
            coords = self.get_coordinates(zip_code)
            if coords:
                results[str(zip_code)] = coords
        return results
    
    def get_stats(self) -> Dict[str, any]:
        """Get database statistics."""
        return {
            "total_zip_codes": len(self.coordinates),
            "coverage": "Real ZIP code centroids from CSV"
        } 