"""
Spatial analysis module for the Cardiology Care Optimization System.

This module provides spatial analysis capabilities including:
- Provider density analysis
- Geographic clustering
- Distance calculations
- Coverage area analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN

try:
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class SpatialAnalyzer:
    """Perform spatial analysis on geocoded provider data."""

    def __init__(self):
        """Initialize the spatial analyzer."""
        self.analysis_results = {}

    def calculate_provider_density(
        self, df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"
    ) -> dict:
        """Calculate provider density by geographic regions."""
        logger.info("📊 Calculating provider density...")

        # Filter for geocoded providers
        geocoded_df = df[df[lat_col].notna()].copy()

        if len(geocoded_df) == 0:
            logger.warning("❌ No geocoded providers found for density analysis")
            return {}

        # Calculate basic statistics
        total_providers = len(geocoded_df)

        # Calculate geographic bounds
        lat_min, lat_max = geocoded_df[lat_col].min(), geocoded_df[lat_col].max()
        lon_min, lon_max = geocoded_df[lon_col].min(), geocoded_df[lon_col].max()

        # Calculate area (approximate)
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        area_km2 = lat_range * lon_range * 111 * 111  # Rough conversion to km²

        # Calculate density
        density_per_km2 = total_providers / area_km2 if area_km2 > 0 else 0

        # Calculate density by regions (divide into grid)
        grid_size = 0.1  # ~11km grid cells
        geocoded_df["lat_grid"] = (geocoded_df[lat_col] // grid_size).astype(int)
        geocoded_df["lon_grid"] = (geocoded_df[lon_col] // grid_size).astype(int)

        grid_density = (
            geocoded_df.groupby(["lat_grid", "lon_grid"])
            .size()
            .reset_index(name="provider_count")
        )

        density_stats = {
            "total_providers": total_providers,
            "geographic_bounds": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lon_min": lon_min,
                "lon_max": lon_max,
            },
            "area_km2": area_km2,
            "density_per_km2": density_per_km2,
            "grid_density_stats": {
                "mean_providers_per_grid": grid_density["provider_count"].mean(),
                "max_providers_per_grid": grid_density["provider_count"].max(),
                "grids_with_providers": len(grid_density),
                "total_grids": len(grid_density),
            },
        }

        self.analysis_results["density"] = density_stats
        logger.info(
            f"✅ Density analysis complete: {density_per_km2:.4f} providers/km²"
        )

        return density_stats

    def identify_clusters(
        self,
        df: pd.DataFrame,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        eps: float = 0.05,  # ~5.5km radius
        min_samples: int = 3,
    ) -> dict:
        """Identify geographic clusters of providers using DBSCAN."""
        logger.info("🔍 Identifying provider clusters...")

        # Filter for geocoded providers
        geocoded_df = df[df[lat_col].notna()].copy()

        if len(geocoded_df) < min_samples:
            logger.warning("❌ Insufficient providers for clustering analysis")
            return {}

        # Prepare coordinates for clustering
        coords = geocoded_df[[lat_col, lon_col]].values

        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)

        # Add cluster labels
        geocoded_df["cluster"] = clustering.labels_

        # Analyze clusters
        n_clusters = len(set(clustering.labels_)) - (
            1 if -1 in clustering.labels_ else 0
        )
        n_noise = list(clustering.labels_).count(-1)

        cluster_stats = []
        for cluster_id in range(n_clusters):
            cluster_providers = geocoded_df[geocoded_df["cluster"] == cluster_id]
            cluster_center_lat = cluster_providers[lat_col].mean()
            cluster_center_lon = cluster_providers[lon_col].mean()

            cluster_stats.append(
                {
                    "cluster_id": cluster_id,
                    "provider_count": len(cluster_providers),
                    "center_lat": cluster_center_lat,
                    "center_lon": cluster_center_lon,
                    "providers": cluster_providers["provider_name"].tolist(),
                }
            )

        clustering_results = {
            "total_providers": len(geocoded_df),
            "n_clusters": n_clusters,
            "n_noise": n_noise,
            "clustering_parameters": {"eps": eps, "min_samples": min_samples},
            "clusters": cluster_stats,
        }

        self.analysis_results["clustering"] = clustering_results
        logger.info(f"✅ Clustering complete: {n_clusters} clusters identified")

        return clustering_results

    def calculate_coverage_gaps(
        self,
        df: pd.DataFrame,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        coverage_radius_km: float = 25.0,
    ) -> dict:
        """Identify areas with limited provider coverage."""
        logger.info("🌍 Analyzing coverage gaps...")

        # Filter for geocoded providers
        geocoded_df = df[df[lat_col].notna()].copy()

        if len(geocoded_df) == 0:
            logger.warning("❌ No geocoded providers for coverage analysis")
            return {}

        # Convert coverage radius to degrees (approximate)
        coverage_radius_deg = coverage_radius_km / 111.0

        # Create a grid of potential demand points
        lat_min, lat_max = geocoded_df[lat_col].min(), geocoded_df[lat_col].max()
        lon_min, lon_max = geocoded_df[lon_col].min(), geocoded_df[lon_col].max()

        # Expand bounds slightly for analysis
        lat_min -= 0.1
        lat_max += 0.1
        lon_min -= 0.1
        lon_max += 0.1

        # Create grid points
        grid_step = 0.01  # ~1.1km grid
        lat_grid = np.arange(lat_min, lat_max, grid_step)
        lon_grid = np.arange(lon_min, lon_max, grid_step)

        # Calculate distances from each grid point to all providers
        provider_coords = geocoded_df[[lat_col, lon_col]].values

        coverage_gaps = []
        covered_points = 0
        total_points = 0

        for lat in lat_grid:
            for lon in lon_grid:
                total_points += 1

                # Calculate distance to nearest provider
                distances = np.sqrt(
                    (provider_coords[:, 0] - lat) ** 2
                    + (provider_coords[:, 1] - lon) ** 2
                )
                min_distance = np.min(distances)

                if min_distance > coverage_radius_deg:
                    coverage_gaps.append(
                        {
                            "lat": lat,
                            "lon": lon,
                            "min_distance_km": min_distance * 111.0,
                            "nearest_provider_distance_km": min_distance * 111.0,
                        }
                    )
                else:
                    covered_points += 1

        coverage_analysis = {
            "coverage_radius_km": coverage_radius_km,
            "total_grid_points": total_points,
            "covered_points": covered_points,
            "uncovered_points": len(coverage_gaps),
            "coverage_percentage": (
                (covered_points / total_points) * 100 if total_points > 0 else 0
            ),
            "coverage_gaps": coverage_gaps[:100],  # Limit to first 100 for performance
        }

        self.analysis_results["coverage"] = coverage_analysis
        logger.info(
            f"✅ Coverage analysis complete: {coverage_analysis['coverage_percentage']:.1f}% coverage"
        )

        return coverage_analysis

    def generate_spatial_report(self, df: pd.DataFrame) -> dict:
        """Generate comprehensive spatial analysis report."""
        logger.info("📋 Generating spatial analysis report...")

        # Run all analyses
        density_results = self.calculate_provider_density(df)
        clustering_results = self.identify_clusters(df)
        coverage_results = self.calculate_coverage_gaps(df)

        # Compile comprehensive report
        spatial_report = {
            "summary": {
                "total_providers": len(df),
                "geocoded_providers": df["latitude"].notna().sum(),
                "geocoding_success_rate": (df["latitude"].notna().sum() / len(df))
                * 100,
            },
            "density_analysis": density_results,
            "clustering_analysis": clustering_results,
            "coverage_analysis": coverage_results,
            "recommendations": self._generate_recommendations(),
        }

        logger.info("✅ Spatial analysis report complete")
        return spatial_report

    def _generate_recommendations(self) -> list[str]:
        """Generate optimization recommendations based on spatial analysis."""
        recommendations = []

        if "density" in self.analysis_results:
            density = self.analysis_results["density"]
            if density.get("density_per_km2", 0) < 0.001:
                recommendations.append(
                    "Low provider density detected - consider expanding provider network"
                )

        if "clustering" in self.analysis_results:
            clustering = self.analysis_results["clustering"]
            if clustering.get("n_clusters", 0) < 5:
                recommendations.append(
                    "Limited geographic distribution - focus on underserved areas"
                )

        if "coverage" in self.analysis_results:
            coverage = self.analysis_results["coverage"]
            if coverage.get("coverage_percentage", 100) < 80:
                recommendations.append(
                    "Significant coverage gaps identified - prioritize expansion in uncovered areas"
                )

        return recommendations


if __name__ == "__main__":
    # Test the spatial analyzer with sample data
    import sys

    sys.path.append("../../..")

    # Load sample data
    sample_file = "data/processed/ca_cardiology_cleaned.csv"
    if Path(sample_file).exists():
        df = pd.read_csv(sample_file)

        # Test with first 10 providers (if geocoded)
        test_df = df.head(10).copy()

        analyzer = SpatialAnalyzer()
        report = analyzer.generate_spatial_report(test_df)

        print("\n📊 Spatial Analysis Report:")
        print(f"Total providers: {report['summary']['total_providers']}")
        print(f"Geocoded providers: {report['summary']['geocoded_providers']}")
        print(f"Success rate: {report['summary']['geocoding_success_rate']:.1f}%")

        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")

    else:
        print(f"❌ Sample file not found: {sample_file}")
        print("Please run the data cleaning pipeline first.")
