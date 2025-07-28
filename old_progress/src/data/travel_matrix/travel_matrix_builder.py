"""
Travel Matrix Builder Implementation

This module implements the hybrid interpolation approach for constructing
comprehensive travel time matrices between healthcare providers and demand areas.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import NearestNeighbors

from .interpolation_methods import InterpolationMethods
from .zip_coordinates_db import ZipCoordinatesDB

logger = logging.getLogger(__name__)


class TravelMatrixBuilder:
    """
    Hybrid travel matrix builder that combines academic datasets with custom calculations.
    
    This class implements a three-phase approach:
    1. Academic dataset foundation (Hu et al., 2020)
    2. Custom OSRM calculations for missing data
    3. Advanced interpolation for remaining gaps
    """
    
    def __init__(self, 
                 data_dir: str = "data",
                 output_dir: str = "data/processed",
                 max_error_rate: float = 0.15,
                 min_coverage: float = 0.95):
        """
        Initialize the Travel Matrix Builder.
        
        Args:
            data_dir: Directory containing input data
            output_dir: Directory for output files
            max_error_rate: Maximum acceptable error rate (default: 15%)
            min_coverage: Minimum required coverage (default: 95%)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.max_error_rate = max_error_rate
        self.min_coverage = min_coverage
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize interpolation methods
        self.interpolation = InterpolationMethods()
        
        # Initialize ZIP coordinates database
        self.zip_db = ZipCoordinatesDB()
        
        # Data storage
        self.provider_data = None
        self.demand_data = None
        self.academic_matrix = None
        self.final_matrix = None
        
        logger.info(f"TravelMatrixBuilder initialized with max_error_rate={max_error_rate}, min_coverage={min_coverage}")
    
    def load_provider_data(self) -> pd.DataFrame:
        """
        Load provider data from Task 12 output.
        
        Returns:
            DataFrame with provider information including ZIP codes
        """
        provider_file = self.data_dir / "processed" / "ca_providers_filtered.csv"
        
        if not provider_file.exists():
            raise FileNotFoundError(f"Provider data not found: {provider_file}")
        
        self.provider_data = pd.read_csv(provider_file)
        
        # Validate required columns
        required_cols = ['provider_npi', 'zip_code']
        missing_cols = [col for col in required_cols if col not in self.provider_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in provider data: {missing_cols}")
        
        # Rename provider_npi to NPI for consistency with existing code
        self.provider_data = self.provider_data.rename(columns={'provider_npi': 'NPI'})
        
        # Clean ZIP codes (ensure 5-digit format)
        self.provider_data['zip_code'] = self.provider_data['zip_code'].astype(str).str.zfill(5)
        
        logger.info(f"Loaded {len(self.provider_data)} providers from {provider_file}")
        return self.provider_data
    
    def load_demand_data(self) -> pd.DataFrame:
        """
        Load demand data from Task 13 output.
        
        Returns:
            DataFrame with demand information including ZIP codes
        """
        demand_file = self.data_dir / "processed" / "ca_demand_filtered.csv"
        
        if not demand_file.exists():
            raise FileNotFoundError(f"Demand data not found: {demand_file}")
        
        self.demand_data = pd.read_csv(demand_file)
        
        # Validate required columns
        required_cols = ['zip_code', 'demand_score']
        missing_cols = [col for col in required_cols if col not in self.demand_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in demand data: {missing_cols}")
        
        # Rename demand_score to ensemble_demand_score for consistency with existing code
        self.demand_data = self.demand_data.rename(columns={'demand_score': 'ensemble_demand_score'})
        
        # Clean ZIP codes (ensure 5-digit format)
        self.demand_data['zip_code'] = self.demand_data['zip_code'].astype(str).str.zfill(5)
        
        logger.info(f"Loaded {len(self.demand_data)} demand areas from {demand_file}")
        return self.demand_data
    
    def download_academic_dataset(self) -> pd.DataFrame:
        """
        Download and load the academic travel time dataset (Hu et al., 2020).
        
        Returns:
            DataFrame with academic travel time matrix
        """
        # Note: In a real implementation, this would download from the academic source
        # For now, we'll create a placeholder and document the process
        
        academic_file = self.data_dir / "external" / "travel_matrices" / "academic_travel_matrix.csv"
        
        if academic_file.exists():
            logger.info(f"Loading existing academic dataset from {academic_file}")
            self.academic_matrix = pd.read_csv(academic_file)
        else:
            logger.warning("Academic dataset not found. Creating placeholder for demonstration.")
            # Create a placeholder matrix for demonstration
            self._create_placeholder_academic_matrix()
        
        return self.academic_matrix
    
    def _create_placeholder_academic_matrix(self):
        """
        Create a placeholder academic matrix for demonstration purposes.
        In production, this would be replaced with actual academic dataset download.
        """
        # Get unique ZIP codes from provider and demand data
        provider_zips = set(self.provider_data['zip_code'].unique())
        demand_zips = set(self.demand_data['zip_code'].unique())
        all_zips = list(provider_zips | demand_zips)
        
        # Create a sample matrix (in reality, this would be the full academic dataset)
        # For demonstration, we'll create a subset
        sample_size = min(1000, len(all_zips) * len(all_zips))
        
        # Create random travel times for demonstration
        np.random.seed(42)  # For reproducible results
        origins = np.random.choice(all_zips, size=sample_size)
        destinations = np.random.choice(all_zips, size=sample_size)
        travel_times = np.random.exponential(30, size=sample_size)  # Exponential distribution
        
        self.academic_matrix = pd.DataFrame({
            'origin_zip': origins,
            'destination_zip': destinations,
            'travel_time_minutes': travel_times
        })
        
        # Remove self-loops (same origin and destination)
        self.academic_matrix = self.academic_matrix[
            self.academic_matrix['origin_zip'] != self.academic_matrix['destination_zip']
        ]
        
        logger.info(f"Created placeholder academic matrix with {len(self.academic_matrix)} entries")
    
    def build_travel_matrix(self) -> pd.DataFrame:
        """
        Build the complete travel matrix using the hybrid approach.
        
        Returns:
            DataFrame with complete travel time matrix
        """
        logger.info("Starting travel matrix construction using hybrid approach")
        
        # Phase 1: Load data
        self.load_provider_data()
        self.load_demand_data()
        self.download_academic_dataset()
        
        # Phase 2: Create target matrix structure
        target_matrix = self._create_target_matrix()
        
        # Phase 3: Fill with academic data
        target_matrix = self._fill_with_academic_data(target_matrix)
        
        # Phase 4: Calculate missing values with OSRM (placeholder)
        target_matrix = self._fill_with_osrm_data(target_matrix)
        
        # Phase 5: Interpolate remaining gaps
        target_matrix = self._interpolate_remaining_gaps(target_matrix)
        
        # Phase 6: Validate and save
        self._validate_matrix(target_matrix)
        self._save_matrix(target_matrix)
        
        self.final_matrix = target_matrix
        logger.info("Travel matrix construction completed successfully")
        
        return target_matrix
    
    def _create_target_matrix(self) -> pd.DataFrame:
        """
        Create the target matrix structure with all provider-demand pairs.
        
        Returns:
            DataFrame with all required provider-demand pairs
        """
        # Get provider NPIs and ZIP codes
        if self.provider_data is None or self.demand_data is None:
            raise ValueError("Provider data or demand data not loaded. Run load_provider_data() and load_demand_data() first.")
            
        # Extract 5-digit ZIP codes from 9-digit postal codes
        provider_data_clean = self.provider_data.copy()
        provider_data_clean['zip_5digit'] = provider_data_clean['zip_code'].astype(str).str[:5]
        
        provider_info = provider_data_clean[['NPI', 'zip_5digit']].drop_duplicates()
        demand_zips = self.demand_data['zip_code'].unique()
        
        # Create all combinations
        zip_codes = []
        provider_npis = []
        
        for _, provider in provider_info.iterrows():
            provider_npi = provider['NPI']
            provider_zip = provider['zip_5digit']
            
            for demand_zip in demand_zips:
                zip_codes.append(demand_zip)  # Demand ZIP code
                provider_npis.append(provider_npi)
        
        target_matrix = pd.DataFrame({
            'zip_code': zip_codes,
            'provider_npi': provider_npis,
            'drive_minutes': np.nan
        })
        
        logger.info(f"Created target matrix with {len(target_matrix)} provider-demand pairs")
        return target_matrix
    
    def _fill_with_academic_data(self, target_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Fill target matrix with available academic data.
        
        Args:
            target_matrix: Target matrix to fill
            
        Returns:
            Updated target matrix with academic data filled
        """
        # For now, we'll use placeholder academic data
        # In a real implementation, this would merge with actual academic dataset
        logger.info("Using placeholder academic data (real implementation would merge with Hu et al. dataset)")
        
        # Since we don't have the actual academic dataset yet, we'll skip this step
        # and rely on OSRM calculations for all pairs
        coverage = 0.0
        logger.info(f"Academic data coverage: {coverage:.2%}")
        
        return target_matrix
    
    def _fill_with_osrm_data(self, target_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values using OSRM calculations (placeholder implementation).
        
        Args:
            target_matrix: Target matrix to fill
            
        Returns:
            Updated target matrix with OSRM data filled
        """
        # In a real implementation, this would use OSRM API or local OSRM server
        # For now, we'll create realistic placeholder values
        
        missing_mask = target_matrix['drive_minutes'].isna()
        missing_count = missing_mask.sum()
        
        if missing_count == 0:
            logger.info("No missing values to fill with OSRM data")
            return target_matrix
        
        logger.info(f"Filling {missing_count} missing values with OSRM calculations (placeholder)")
        
        # Create realistic travel times based on ZIP code patterns
        # In reality, this would be actual OSRM API calls
        np.random.seed(42)
        
        # Generate travel times based on ZIP code distance patterns
        for idx in target_matrix[missing_mask].index:
            zip_code = target_matrix.loc[idx, 'zip_code']
            provider_npi = target_matrix.loc[idx, 'provider_npi']
            
            # Get provider ZIP code from provider data
            if self.provider_data is not None:
                provider_row = self.provider_data[self.provider_data['NPI'] == provider_npi]
                if not provider_row.empty:
                    provider_zip = str(provider_row.iloc[0]['zip_code'])[:5]  # Extract 5-digit ZIP
                    
                    # Simple distance-based estimation (placeholder)
                    # In reality, this would be actual OSRM API call
                    travel_time = self._estimate_travel_time(str(provider_zip), str(zip_code))
                    target_matrix.loc[idx, 'drive_minutes'] = travel_time
        
        coverage = 1 - target_matrix['drive_minutes'].isna().mean()
        logger.info(f"After OSRM filling, coverage: {coverage:.2%}")
        
        return target_matrix
    
    def _estimate_travel_time(self, origin_zip: str, dest_zip: str) -> float:
        """
        Estimate travel time between two ZIP codes using real geocoding.
        
        Args:
            origin_zip: Origin ZIP code
            dest_zip: Destination ZIP code
            
        Returns:
            Estimated travel time in minutes
        """
        # Convert 3-digit ZIP codes to 5-digit format for database lookup
        origin_zip_5digit = str(origin_zip).zfill(5)
        dest_zip_5digit = str(dest_zip).zfill(5)
        
        # Get coordinates using ZIP coordinates database
        origin_coords = self.zip_db.get_coordinates(origin_zip_5digit)
        dest_coords = self.zip_db.get_coordinates(dest_zip_5digit)
        
        if not origin_coords or not dest_coords:
            logger.warning(f"Could not geocode ZIP codes: {origin_zip} or {dest_zip}")
            # Fallback to simple estimation
            return self._fallback_travel_time_estimation(origin_zip, dest_zip)
        
        # Calculate distance using Haversine formula
        distance = self._calculate_distance(origin_coords, dest_coords)
        
        # Estimate travel time with distance-based speed assumptions
        if distance <= 50:
            # Urban travel: 35 mph average
            travel_time = distance * 1.71  # minutes (35 mph = 0.58 miles per minute)
        elif distance <= 150:
            # Regional travel: 55 mph average
            travel_time = distance * 1.09  # minutes (55 mph = 0.91 miles per minute)
        elif distance <= 300:
            # Interstate travel: 65 mph average
            travel_time = distance * 0.92  # minutes (65 mph = 1.08 miles per minute)
        else:
            # Long-distance travel: 60 mph average with rest stops
            travel_time = distance * 1.0  # minutes (60 mph = 1 mile per minute)
            # Add 10% for rest stops on long trips
            travel_time *= 1.1
        
        # Add some randomness to make it more realistic
        travel_time += np.random.normal(0, 5)
        travel_time = max(5, travel_time)  # Minimum 5 minutes
        travel_time = min(600, travel_time)  # Maximum 10 hours (for very long distances)
        
        return travel_time
    
    def _fallback_travel_time_estimation(self, origin_zip: str, dest_zip: str) -> float:
        """
        Fallback travel time estimation when geocoding fails.
        
        Args:
            origin_zip: Origin ZIP code
            dest_zip: Destination ZIP code
            
        Returns:
            Estimated travel time in minutes
        """
        # Check if either ZIP code is in California
        origin_is_ca = str(origin_zip).startswith(('90', '91', '92', '93', '94', '95', '96'))
        dest_is_ca = str(dest_zip).startswith(('90', '91', '92', '93', '94', '95', '96'))
        
        # If both are non-California, return a high travel time (cross-country)
        if not origin_is_ca and not dest_is_ca:
            return 180.0  # Cross-country travel
        
        # If one is California and one isn't, return a medium-high travel time
        if origin_is_ca != dest_is_ca:
            return 120.0  # Interstate travel
        
        # If both are California but not in our database, use a more reasonable estimation
        try:
            # Extract first 2 digits for rough geographic estimation
            origin_region = int(str(origin_zip)[:2])
            dest_region = int(str(dest_zip)[:2])
            
            # Calculate rough distance based on ZIP code regions
            # California ZIP codes are roughly 90-96
            if 90 <= origin_region <= 96 and 90 <= dest_region <= 96:
                # Both are California ZIP codes
                distance = abs(origin_region - dest_region) * 10  # Rough miles
                travel_time = distance * 1.5  # Assume 40 mph average
                travel_time += np.random.normal(0, 10)  # Add some variability
                travel_time = max(10, travel_time)  # Minimum 10 minutes
                travel_time = min(120, travel_time)  # Maximum 2 hours within CA
                return travel_time
            else:
                # One or both are non-California
                return 150.0
        except (ValueError, IndexError):
            # If ZIP code parsing fails, return a reasonable default
            return 45.0
    
    def _calculate_distance(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            coords1: First coordinate (lat, lon)
            coords2: Second coordinate (lat, lon)
            
        Returns:
            Distance in miles
        """
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Earth's radius in miles
        r = 3959
        
        return c * r
    
    def _interpolate_remaining_gaps(self, target_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Use advanced interpolation to fill any remaining gaps.
        
        Args:
            target_matrix: Target matrix to fill
            
        Returns:
            Updated target matrix with interpolated values
        """
        missing_mask = target_matrix['drive_minutes'].isna()
        missing_count = missing_mask.sum()
        
        if missing_count == 0:
            logger.info("No remaining gaps to interpolate")
            return target_matrix
        
        logger.info(f"Interpolating {missing_count} remaining gaps using advanced methods")
        
        # Use nearest neighbor interpolation for remaining gaps
        target_matrix = self.interpolation.nearest_neighbor_interpolation(target_matrix)
        
        coverage = 1 - target_matrix['drive_minutes'].isna().mean()
        logger.info(f"After interpolation, final coverage: {coverage:.2%}")
        
        return target_matrix
    
    def _validate_matrix(self, matrix: pd.DataFrame):
        """
        Validate the constructed travel matrix.
        
        Args:
            matrix: Travel matrix to validate
        """
        logger.info("Validating travel matrix...")
        
        # Check coverage
        coverage = 1 - matrix['drive_minutes'].isna().mean()
        if coverage < self.min_coverage:
            raise ValueError(f"Matrix coverage {coverage:.2%} below minimum {self.min_coverage:.2%}")
        
        # Check for negative travel times
        negative_count = (matrix['drive_minutes'] < 0).sum()
        if negative_count > 0:
            logger.warning(f"Found {negative_count} negative travel times, correcting...")
            matrix.loc[matrix['drive_minutes'] < 0, 'drive_minutes'] = 5
        
        # Check for unreasonably high travel times
        high_count = (matrix['drive_minutes'] > 300).sum()  # > 5 hours
        if high_count > 0:
            logger.warning(f"Found {high_count} travel times > 5 hours")
        
        # Basic statistics
        stats = matrix['drive_minutes'].describe()
        logger.info(f"Travel time statistics:\n{stats}")
        
        logger.info("Matrix validation completed successfully")
    
    def _save_matrix(self, matrix: pd.DataFrame):
        """
        Save the travel matrix to disk.
        
        Args:
            matrix: Travel matrix to save
        """
        # Save as CSV (primary format)
        csv_file = self.output_dir / "travel_matrix.csv"
        matrix.to_csv(csv_file, index=False)
        
        # Try to save as parquet if pyarrow is available
        try:
            output_file = self.output_dir / "travel_matrix.parquet"
            matrix.to_parquet(output_file, index=False)
            logger.info(f"Travel matrix saved to {output_file} and {csv_file}")
        except ImportError:
            logger.warning("pyarrow not available, saving only CSV format")
            logger.info(f"Travel matrix saved to {csv_file}")
        
        # Save summary statistics
        summary_file = self.output_dir / "travel_matrix_summary.json"
        summary = {
            'total_pairs': len(matrix),
            'coverage': 1 - matrix['drive_minutes'].isna().mean(),
            'mean_travel_time': matrix['drive_minutes'].mean(),
            'median_travel_time': matrix['drive_minutes'].median(),
            'min_travel_time': matrix['drive_minutes'].min(),
            'max_travel_time': matrix['drive_minutes'].max(),
            'providers_count': matrix['provider_npi'].nunique(),
            'demand_areas_count': matrix['zip_code'].nunique()
        }
        
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Matrix summary saved to {summary_file}")
    
    def get_matrix_summary(self) -> Dict:
        """
        Get a summary of the constructed travel matrix.
        
        Returns:
            Dictionary with matrix statistics
        """
        if self.final_matrix is None:
            raise ValueError("No matrix has been constructed yet. Run build_travel_matrix() first.")
        
        return {
            'total_pairs': len(self.final_matrix),
            'coverage': 1 - self.final_matrix['drive_minutes'].isna().mean(),
            'mean_travel_time': self.final_matrix['drive_minutes'].mean(),
            'median_travel_time': self.final_matrix['drive_minutes'].median(),
            'providers_count': self.final_matrix['provider_npi'].nunique(),
            'demand_areas_count': self.final_matrix['zip_code'].nunique()
        } 