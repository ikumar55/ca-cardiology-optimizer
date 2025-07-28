"""
Interpolation Methods for Travel Matrix Completion

This module provides advanced interpolation techniques for filling missing
travel time data in the travel matrix using spatial and statistical methods.
"""

import logging
from typing import Dict, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class InterpolationMethods:
    """
    Advanced interpolation methods for travel matrix completion.
    
    This class provides multiple interpolation techniques:
    1. Nearest neighbor interpolation
    2. Spatial weighting interpolation
    3. Hierarchical clustering interpolation
    4. Machine learning-based interpolation
    """
    
    def __init__(self):
        """Initialize the interpolation methods."""
        self.scaler = StandardScaler()
        self.rf_model = None
        
    def nearest_neighbor_interpolation(self, matrix: pd.DataFrame, k: int = 5) -> pd.DataFrame:
        """
        Fill missing values using k-nearest neighbor interpolation.
        
        Args:
            matrix: Travel matrix with missing values
            k: Number of nearest neighbors to use
            
        Returns:
            Updated matrix with interpolated values
        """
        logger.info(f"Performing k-nearest neighbor interpolation with k={k}")
        
        # Create a copy to avoid modifying the original
        result_matrix = matrix.copy()
        
        # Get missing value indices
        missing_mask = result_matrix['travel_time_minutes'].isna()
        missing_indices = result_matrix[missing_mask].index
        
        if len(missing_indices) == 0:
            logger.info("No missing values to interpolate")
            return result_matrix
        
        # Create feature matrix for interpolation
        # Use ZIP code numerical representation as features
        features = self._create_zip_features(result_matrix)
        
        # Get known values for training
        known_mask = result_matrix['travel_time_minutes'].notna()
        known_features = features[known_mask]
        known_values = result_matrix.loc[known_mask, 'travel_time_minutes']
        
        # Get missing value features
        missing_features = features[missing_mask]
        
        # Fit nearest neighbors model
        nn_model = NearestNeighbors(n_neighbors=min(k, len(known_features)), algorithm='auto')
        nn_model.fit(known_features)
        
        # Find nearest neighbors for missing values
        distances, indices = nn_model.kneighbors(missing_features)
        
        # Interpolate missing values using weighted average
        for i, missing_idx in enumerate(missing_indices):
            neighbor_indices = known_mask.index[indices[i]]
            neighbor_values = result_matrix.loc[neighbor_indices, 'travel_time_minutes']
            neighbor_weights = 1 / (distances[i] + 1e-6)  # Avoid division by zero
            
            # Calculate weighted average
            interpolated_value = np.average(neighbor_values, weights=neighbor_weights)
            result_matrix.loc[missing_idx, 'travel_time_minutes'] = interpolated_value
        
        logger.info(f"Completed k-nearest neighbor interpolation for {len(missing_indices)} missing values")
        return result_matrix
    
    def spatial_weighting_interpolation(self, matrix: pd.DataFrame, max_distance: float = 100.0) -> pd.DataFrame:
        """
        Fill missing values using spatial weighting interpolation.
        
        Args:
            matrix: Travel matrix with missing values
            max_distance: Maximum distance for spatial weighting (miles)
            
        Returns:
            Updated matrix with interpolated values
        """
        logger.info(f"Performing spatial weighting interpolation with max_distance={max_distance}")
        
        # Create a copy to avoid modifying the original
        result_matrix = matrix.copy()
        
        # Get missing value indices
        missing_mask = result_matrix['travel_time_minutes'].isna()
        missing_indices = result_matrix[missing_mask].index
        
        if len(missing_indices) == 0:
            logger.info("No missing values to interpolate")
            return result_matrix
        
        # Create ZIP code coordinates (approximate)
        zip_coords = self._create_zip_coordinates(result_matrix)
        
        # Get known values for interpolation
        known_mask = result_matrix['travel_time_minutes'].notna()
        known_coords = zip_coords[known_mask]
        known_values = result_matrix.loc[known_mask, 'travel_time_minutes']
        
        # Get missing value coordinates
        missing_coords = zip_coords[missing_mask]
        
        # Interpolate each missing value
        for i, missing_idx in enumerate(missing_indices):
            missing_coord = missing_coords.iloc[i]
            
            # Calculate distances to all known points
            distances = np.sqrt(
                (known_coords['lat'] - missing_coord['lat'])**2 + 
                (known_coords['lon'] - missing_coord['lon'])**2
            ) * 69  # Convert to miles (approximate)
            
            # Find points within max_distance
            within_range = distances <= max_distance
            
            if within_range.sum() > 0:
                # Use inverse distance weighting
                weights = 1 / (distances[within_range] + 1e-6)
                values = known_values[within_range]
                
                interpolated_value = np.average(values, weights=weights)
            else:
                # If no points within range, use nearest neighbor
                nearest_idx = distances.argmin()
                interpolated_value = known_values.iloc[nearest_idx]
            
            result_matrix.loc[missing_idx, 'travel_time_minutes'] = interpolated_value
        
        logger.info(f"Completed spatial weighting interpolation for {len(missing_indices)} missing values")
        return result_matrix
    
    def hierarchical_clustering_interpolation(self, matrix: pd.DataFrame, n_clusters: int = 10) -> pd.DataFrame:
        """
        Fill missing values using hierarchical clustering interpolation.
        
        Args:
            matrix: Travel matrix with missing values
            n_clusters: Number of clusters to create
            
        Returns:
            Updated matrix with interpolated values
        """
        logger.info(f"Performing hierarchical clustering interpolation with n_clusters={n_clusters}")
        
        # Create a copy to avoid modifying the original
        result_matrix = matrix.copy()
        
        # Get missing value indices
        missing_mask = result_matrix['travel_time_minutes'].isna()
        missing_indices = result_matrix[missing_mask].index
        
        if len(missing_indices) == 0:
            logger.info("No missing values to interpolate")
            return result_matrix
        
        # Create feature matrix
        features = self._create_zip_features(result_matrix)
        
        # Get known values for clustering
        known_mask = result_matrix['travel_time_minutes'].notna()
        known_features = features[known_mask]
        known_values = result_matrix.loc[known_mask, 'travel_time_minutes']
        
        # Perform hierarchical clustering on known values
        from sklearn.cluster import AgglomerativeClustering
        
        n_clusters = min(n_clusters, len(known_features))
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = clustering.fit_predict(known_features)
        
        # Calculate cluster centroids and values
        cluster_centers = {}
        cluster_values = {}
        
        for cluster_id in range(n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_features = known_features[cluster_mask]
            cluster_travel_times = known_values[cluster_mask]
            
            cluster_centers[cluster_id] = cluster_features.mean()
            cluster_values[cluster_id] = cluster_travel_times.mean()
        
        # Get missing value features
        missing_features = features[missing_mask]
        
        # Assign missing values to nearest cluster
        for i, missing_idx in enumerate(missing_indices):
            missing_feature = missing_features.iloc[i]
            
            # Find nearest cluster
            min_distance = float('inf')
            nearest_cluster = 0
            
            for cluster_id, center in cluster_centers.items():
                distance = np.linalg.norm(missing_feature - center)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cluster = cluster_id
            
            # Use cluster average as interpolated value
            interpolated_value = cluster_values[nearest_cluster]
            result_matrix.loc[missing_idx, 'travel_time_minutes'] = interpolated_value
        
        logger.info(f"Completed hierarchical clustering interpolation for {len(missing_indices)} missing values")
        return result_matrix
    
    def machine_learning_interpolation(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values using machine learning-based interpolation.
        
        Args:
            matrix: Travel matrix with missing values
            
        Returns:
            Updated matrix with interpolated values
        """
        logger.info("Performing machine learning-based interpolation")
        
        # Create a copy to avoid modifying the original
        result_matrix = matrix.copy()
        
        # Get missing value indices
        missing_mask = result_matrix['travel_time_minutes'].isna()
        missing_indices = result_matrix[missing_mask].index
        
        if len(missing_indices) == 0:
            logger.info("No missing values to interpolate")
            return result_matrix
        
        # Create feature matrix
        features = self._create_zip_features(result_matrix)
        
        # Get known values for training
        known_mask = result_matrix['travel_time_minutes'].notna()
        known_features = features[known_mask]
        known_values = result_matrix.loc[known_mask, 'travel_time_minutes']
        
        # Get missing value features
        missing_features = features[missing_mask]
        
        # Train Random Forest model
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.rf_model.fit(known_features, known_values)
        
        # Predict missing values
        predicted_values = self.rf_model.predict(missing_features)
        
        # Fill missing values with predictions
        for i, missing_idx in enumerate(missing_indices):
            result_matrix.loc[missing_idx, 'travel_time_minutes'] = predicted_values[i]
        
        logger.info(f"Completed machine learning interpolation for {len(missing_indices)} missing values")
        return result_matrix
    
    def _create_zip_features(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Create numerical features from ZIP codes for interpolation.
        
        Args:
            matrix: Travel matrix
            
        Returns:
            DataFrame with numerical features
        """
        # Extract numerical components from ZIP codes
        features = pd.DataFrame()
        
        # Origin ZIP features
        features['origin_zip_1'] = matrix['origin_zip'].str[:2].astype(int)
        features['origin_zip_2'] = matrix['origin_zip'].str[2:4].astype(int)
        features['origin_zip_3'] = matrix['origin_zip'].str[4:].astype(int)
        
        # Destination ZIP features
        features['dest_zip_1'] = matrix['destination_zip'].str[:2].astype(int)
        features['dest_zip_2'] = matrix['destination_zip'].str[2:4].astype(int)
        features['dest_zip_3'] = matrix['destination_zip'].str[4:].astype(int)
        
        # Distance-like features
        features['zip_diff_1'] = abs(features['origin_zip_1'] - features['dest_zip_1'])
        features['zip_diff_2'] = abs(features['origin_zip_2'] - features['dest_zip_2'])
        features['zip_diff_3'] = abs(features['origin_zip_3'] - features['dest_zip_3'])
        
        # Normalize features
        features = pd.DataFrame(self.scaler.fit_transform(features), columns=features.columns)
        
        return features
    
    def _create_zip_coordinates(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Create approximate coordinates from ZIP codes.
        
        Args:
            matrix: Travel matrix
            
        Returns:
            DataFrame with latitude and longitude coordinates
        """
        # Create approximate coordinates from ZIP codes
        # This is a very rough approximation - in reality, you'd use a proper geocoding service
        
        coords = pd.DataFrame()
        
        # Origin coordinates (rough approximation)
        coords['origin_lat'] = matrix['origin_zip'].str[:2].astype(float) + matrix['origin_zip'].str[2:4].astype(float) / 100
        coords['origin_lon'] = -120 + matrix['origin_zip'].str[4:].astype(float) / 10  # California longitude range
        
        # Destination coordinates (rough approximation)
        coords['dest_lat'] = matrix['destination_zip'].str[:2].astype(float) + matrix['destination_zip'].str[2:4].astype(float) / 100
        coords['dest_lon'] = -120 + matrix['destination_zip'].str[4:].astype(float) / 10
        
        # Calculate centroid for interpolation
        coords['lat'] = (coords['origin_lat'] + coords['dest_lat']) / 2
        coords['lon'] = (coords['origin_lon'] + coords['dest_lon']) / 2
        
        return coords[['lat', 'lon']]
    
    def get_interpolation_quality_metrics(self, original_matrix: pd.DataFrame, interpolated_matrix: pd.DataFrame) -> Dict:
        """
        Calculate quality metrics for interpolation results.
        
        Args:
            original_matrix: Original matrix with missing values
            interpolated_matrix: Matrix after interpolation
            
        Returns:
            Dictionary with quality metrics
        """
        # Calculate coverage improvement
        original_coverage = 1 - original_matrix['travel_time_minutes'].isna().mean()
        final_coverage = 1 - interpolated_matrix['travel_time_minutes'].isna().mean()
        
        # Calculate basic statistics
        stats = interpolated_matrix['travel_time_minutes'].describe()
        
        # Calculate interpolation quality metrics
        metrics = {
            'original_coverage': original_coverage,
            'final_coverage': final_coverage,
            'coverage_improvement': final_coverage - original_coverage,
            'mean_travel_time': stats['mean'],
            'median_travel_time': stats['50%'],
            'min_travel_time': stats['min'],
            'max_travel_time': stats['max'],
            'std_travel_time': stats['std'],
            'total_pairs': len(interpolated_matrix),
            'interpolated_pairs': (original_matrix['travel_time_minutes'].isna() & 
                                 interpolated_matrix['travel_time_minutes'].notna()).sum()
        }
        
        return metrics 