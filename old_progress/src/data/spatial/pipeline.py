"""
Complete spatial analysis pipeline for the Cardiology Care Optimization System.

This module combines geocoding and spatial analysis in a single pipeline.
"""

import logging
from pathlib import Path

import pandas as pd

try:
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)

from .analysis import SpatialAnalyzer
from .geocoder import ProviderGeocoder


class SpatialPipeline:
    """Complete spatial analysis pipeline for provider data."""

    def __init__(self):
        """Initialize the spatial pipeline."""
        self.geocoder = ProviderGeocoder()
        self.analyzer = SpatialAnalyzer()

    def run_pipeline(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """Run the complete spatial analysis pipeline."""
        logger.info("🚀 Starting spatial analysis pipeline...")

        # Load data
        logger.info(f"📂 Loading data from {input_file}")
        df = pd.read_csv(input_file)
        logger.info(f"📊 Loaded {len(df)} providers")

        # Geocode providers
        logger.info("📍 Starting geocoding...")
        df_geocoded = self.geocoder.geocode_providers(df)

        # Validate geocoding
        validation = self.geocoder.validate_geocoding(df_geocoded)

        # Run spatial analysis
        logger.info("🔍 Starting spatial analysis...")
        spatial_report = self.analyzer.generate_spatial_report(df_geocoded)

        # Save results
        if output_file:
            df_geocoded.to_csv(output_file, index=False)
            logger.info(f"💾 Saved geocoded data to {output_file}")

        # Print summary
        self._print_summary(validation, spatial_report)

        return df_geocoded

    def _print_summary(self, validation: dict, spatial_report: dict):
        """Print a summary of the pipeline results."""
        print("\n" + "=" * 60)
        print("🎯 SPATIAL ANALYSIS PIPELINE RESULTS")
        print("=" * 60)

        print(f"\n📍 Geocoding Results:")
        print(f"  • Total providers: {validation['total_providers']}")
        print(f"  • Successfully geocoded: {validation['geocoded_providers']}")
        print(f"  • Success rate: {validation['success_rate']:.1f}%")
        print(f"  • In California bounds: {validation['in_california_bounds']}")

        if "density_analysis" in spatial_report:
            density = spatial_report["density_analysis"]
            print(f"\n📊 Density Analysis:")
            print(
                f"  • Provider density: {density.get('density_per_km2', 0):.6f} providers/km²"
            )
            print(f"  • Coverage area: {density.get('area_km2', 0):.1f} km²")

        if "clustering_analysis" in spatial_report:
            clustering = spatial_report["clustering_analysis"]
            print(f"\n🔍 Clustering Analysis:")
            print(f"  • Number of clusters: {clustering.get('n_clusters', 0)}")
            print(
                f"  • Providers in clusters: {clustering.get('total_providers', 0) - clustering.get('n_noise', 0)}"
            )

        if "coverage_analysis" in spatial_report:
            coverage = spatial_report["coverage_analysis"]
            print(f"\n🌍 Coverage Analysis:")
            print(
                f"  • Coverage percentage: {coverage.get('coverage_percentage', 0):.1f}%"
            )
            print(f"  • Coverage radius: {coverage.get('coverage_radius_km', 0)} km")

        if spatial_report.get("recommendations"):
            print(f"\n💡 Recommendations:")
            for rec in spatial_report["recommendations"]:
                print(f"  • {rec}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test the complete pipeline
    import sys

    sys.path.append("../../..")

    # Run pipeline on sample data
    input_file = "data/processed/ca_cardiology_cleaned.csv"
    output_file = "data/processed/ca_cardiology_geocoded.csv"

    if Path(input_file).exists():
        pipeline = SpatialPipeline()
        df_result = pipeline.run_pipeline(input_file, output_file)

        print(f"\n✅ Pipeline complete! Results saved to {output_file}")

    else:
        print(f"❌ Input file not found: {input_file}")
        print("Please run the data cleaning pipeline first.")
