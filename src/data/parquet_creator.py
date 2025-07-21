"""
Parquet file creation module for the Cardiology Care Optimization System.

This module creates the final providers.parquet file with optimization-ready schema
including capacity estimation, geographic enrichment, and quality metrics.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

try:
    from ..utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class ProvidersParquetCreator:
    """Create optimization-ready parquet file with capacity estimation and metrics."""

    # Cardiology specialty mapping for capacity estimation
    SPECIALTY_CAPACITY_MAP = {
        "207RC0000X": {
            "name": "Cardiovascular Disease",
            "base_capacity": 2000,
            "complexity_multiplier": 1.0,
        },
        "207RI0011X": {
            "name": "Interventional Cardiology",
            "base_capacity": 1500,
            "complexity_multiplier": 1.3,
        },
        "207RE0101X": {
            "name": "Cardiac Electrophysiology",
            "base_capacity": 1200,
            "complexity_multiplier": 1.5,
        },
        "207RR0500X": {
            "name": "Pediatric Cardiology",
            "base_capacity": 1800,
            "complexity_multiplier": 1.2,
        },
        "207RC0001X": {
            "name": "Clinical Cardiac Electrophysiology",
            "base_capacity": 1200,
            "complexity_multiplier": 1.5,
        },
        "207RA0201X": {
            "name": "Adult Congenital Heart Disease",
            "base_capacity": 1000,
            "complexity_multiplier": 1.8,
        },
        "207V00000X": {
            "name": "Obstetrics & Gynecology",
            "base_capacity": 2500,
            "complexity_multiplier": 0.7,
        },  # Maternal-Fetal Medicine with cardiac
        "207K00000X": {
            "name": "Allergy & Immunology",
            "base_capacity": 2200,
            "complexity_multiplier": 0.8,
        },  # Some do cardiac allergy
        "208000000X": {
            "name": "Pediatric Medicine",
            "base_capacity": 2800,
            "complexity_multiplier": 0.6,
        },  # General peds with cardiac
    }

    # Practice type capacity modifiers
    PRACTICE_TYPE_MODIFIERS = {
        "solo": 1.0,
        "small_group": 1.2,  # 2-5 providers
        "medium_group": 1.4,  # 6-15 providers
        "large_group": 1.6,  # 16+ providers
        "hospital": 1.8,  # Hospital-based
        "academic": 1.5,  # Academic medical center
        "health_system": 1.9,  # Large health system
    }

    # California regions for geographic classification
    CA_REGIONS = {
        "Northern California": [
            "Alameda",
            "Alpine",
            "Amador",
            "Butte",
            "Calaveras",
            "Colusa",
            "Contra Costa",
            "Del Norte",
            "El Dorado",
            "Glenn",
            "Humboldt",
            "Lake",
            "Lassen",
            "Marin",
            "Mendocino",
            "Modoc",
            "Napa",
            "Nevada",
            "Placer",
            "Plumas",
            "Sacramento",
            "San Francisco",
            "San Joaquin",
            "San Mateo",
            "Santa Clara",
            "Shasta",
            "Sierra",
            "Siskiyou",
            "Solano",
            "Sonoma",
            "Stanislaus",
            "Sutter",
            "Tehama",
            "Tuolumne",
            "Yolo",
            "Yuba",
        ],
        "Central California": [
            "Fresno",
            "Imperial",
            "Inyo",
            "Kern",
            "Kings",
            "Madera",
            "Merced",
            "Mono",
            "Monterey",
            "San Benito",
            "San Luis Obispo",
            "Santa Barbara",
            "Santa Cruz",
            "Tulare",
        ],
        "Southern California": [
            "Los Angeles",
            "Orange",
            "Riverside",
            "San Bernardino",
            "San Diego",
            "Ventura",
        ],
    }

    def __init__(self, geocoding_cache_file: str = "geocoding_cache.json"):
        """Initialize the parquet creator."""
        self.geocoding_cache_file = Path(geocoding_cache_file)
        self.geocoding_cache = self._load_geocoding_cache()

    def _load_geocoding_cache(self) -> dict[str, dict]:
        """Load the geocoding cache."""
        if self.geocoding_cache_file.exists():
            try:
                with open(self.geocoding_cache_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load geocoding cache: {e}")
        return {}

    def create_providers_parquet(
        self, input_file: str, output_file: str = "data/processed/providers.parquet"
    ) -> pd.DataFrame:
        """Create the final providers.parquet file with comprehensive schema."""
        logger.info("🚀 Starting providers.parquet creation...")

        # Load cleaned data
        logger.info(f"📂 Loading cleaned data from {input_file}")
        df = pd.read_csv(input_file)
        logger.info(f"📊 Loaded {len(df)} providers")

        # Create optimization-ready schema
        logger.info("🔧 Creating optimization-ready schema...")
        providers_df = self._create_optimized_schema(df)

        # Add geocoding data
        logger.info("📍 Adding geocoding data...")
        providers_df = self._add_geocoding_data(providers_df)

        # Estimate capacity
        logger.info("💊 Estimating provider capacity...")
        providers_df = self._estimate_capacity(providers_df)

        # Add geographic enrichment
        logger.info("🌍 Adding geographic enrichment...")
        providers_df = self._add_geographic_enrichment(providers_df)

        # Calculate optimization metrics
        logger.info("📈 Calculating optimization metrics...")
        providers_df = self._calculate_optimization_metrics(providers_df)

        # Add quality scores
        logger.info("✅ Adding quality scores...")
        providers_df = self._add_quality_scores(providers_df)

        # Validate and save
        logger.info("💾 Validating and saving parquet file...")
        validated_df = self._validate_and_save(providers_df, output_file)

        # Print summary
        self._print_summary(validated_df)

        return validated_df

    def _create_optimized_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create the optimized schema with core provider information."""
        # Extract core provider information
        providers = pd.DataFrame()

        # Core Provider Info
        providers["npi"] = df["NPI"].astype(str)
        providers["provider_name"] = df["provider_name"]
        providers["specialty"] = df["Healthcare Provider Taxonomy Code_1"].fillna(
            "207RC0000X"
        )  # Default to general cardiology
        providers["credentials"] = df["Provider Credential Text"].fillna("M.D.")

        # Location Data
        providers["address"] = df["practice_address"]
        providers["city"] = df["city"]
        providers["state"] = df["state"]
        providers["zip_code"] = df["zip_code"]

        # Initialize coordinate fields (will be filled later)
        providers["latitude"] = np.nan
        providers["longitude"] = np.nan
        providers["county"] = ""
        providers["region"] = ""

        # Initialize capacity and optimization fields (will be calculated later)
        providers["estimated_capacity"] = 0
        providers["practice_type"] = ""
        providers["accessibility_score"] = 0.0
        providers["efficiency_rating"] = 0.0
        providers["coverage_radius_km"] = 0.0

        # Initialize quality fields (will be calculated later)
        providers["data_quality_score"] = 0.0
        providers["geocoding_accuracy"] = "Unknown"
        providers["external_validated"] = False
        providers["last_updated"] = datetime.now().isoformat()

        return providers

    def _add_geocoding_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add geocoding data from the cache."""
        geocoded_count = 0

        for idx, row in df.iterrows():
            address_key = row["address"]

            if address_key and address_key in self.geocoding_cache:
                geocode_result = self.geocoding_cache[address_key]

                # Defensive programming: check if geocode_result is valid
                if geocode_result and isinstance(geocode_result, dict):
                    if "lat" in geocode_result and "lon" in geocode_result:
                        try:
                            df.at[idx, "latitude"] = float(geocode_result["lat"])
                            df.at[idx, "longitude"] = float(geocode_result["lon"])

                            # Determine geocoding accuracy based on confidence
                            confidence = geocode_result.get("confidence", 0)
                            if confidence > 0.1:
                                accuracy = "High"
                            elif confidence > 0.01:
                                accuracy = "Medium"
                            else:
                                accuracy = "Low"

                            df.at[idx, "geocoding_accuracy"] = accuracy
                            geocoded_count += 1
                        except (ValueError, TypeError) as e:
                            logger.warning(
                                f"Invalid coordinates for {address_key}: {e}"
                            )
                            df.at[idx, "geocoding_accuracy"] = "Failed"
                else:
                    logger.warning(
                        f"Invalid geocode result for {address_key}: {geocode_result}"
                    )
                    df.at[idx, "geocoding_accuracy"] = "Failed"

        logger.info(
            f"📍 Added coordinates for {geocoded_count} providers ({geocoded_count/len(df)*100:.1f}%)"
        )
        return df

    def _estimate_capacity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estimate provider capacity based on specialty and practice characteristics."""
        for idx, row in df.iterrows():
            specialty_code = row["specialty"]

            # Get base capacity from specialty
            specialty_info = self.SPECIALTY_CAPACITY_MAP.get(
                specialty_code,
                self.SPECIALTY_CAPACITY_MAP[
                    "207RC0000X"
                ],  # Default to general cardiology
            )

            base_capacity = specialty_info["base_capacity"]
            complexity_multiplier = specialty_info["complexity_multiplier"]

            # Determine practice type from organization name and address
            practice_type = self._infer_practice_type(row)
            practice_modifier = self.PRACTICE_TYPE_MODIFIERS.get(practice_type, 1.0)

            # Calculate estimated capacity
            estimated_capacity = int(
                base_capacity * complexity_multiplier * practice_modifier
            )

            df.at[idx, "estimated_capacity"] = estimated_capacity
            df.at[idx, "practice_type"] = practice_type

        logger.info(f"💊 Estimated capacity for {len(df)} providers")
        return df

    def _infer_practice_type(self, row: pd.Series) -> str:
        """Infer practice type from provider information."""
        address = str(row["address"]).upper()
        provider_name = str(row["provider_name"]).upper()

        # Hospital indicators
        hospital_indicators = [
            "HOSPITAL",
            "MEDICAL CENTER",
            "HEALTH SYSTEM",
            "KAISER",
            "VETERANS",
            "VA MEDICAL",
        ]
        if any(
            indicator in address or indicator in provider_name
            for indicator in hospital_indicators
        ):
            return "hospital"

        # Academic indicators
        academic_indicators = [
            "UNIVERSITY",
            "COLLEGE",
            "SCHOOL OF MEDICINE",
            "ACADEMIC",
            "TEACHING",
        ]
        if any(
            indicator in address or indicator in provider_name
            for indicator in academic_indicators
        ):
            return "academic"

        # Health system indicators
        health_system_indicators = [
            "HEALTH SYSTEM",
            "MEDICAL GROUP",
            "PHYSICIAN GROUP",
            "ASSOCIATES",
        ]
        if any(
            indicator in address or indicator in provider_name
            for indicator in health_system_indicators
        ):
            # Check size indicators for group classification
            if "LARGE" in address or "LARGE" in provider_name:
                return "large_group"
            elif "GROUP" in address or "GROUP" in provider_name:
                return "medium_group"
            else:
                return "health_system"

        # Suite indicators suggest group practice
        if "SUITE" in address or "STE" in address:
            return "small_group"

        # Default to solo practice
        return "solo"

    def _add_geographic_enrichment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add county and region information."""
        # For providers with coordinates, extract county from geocoded display_name
        county_extracted = 0

        for idx, row in df.iterrows():
            if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
                address_key = row["address"]

                if address_key in self.geocoding_cache:
                    display_name = self.geocoding_cache[address_key].get(
                        "display_name", ""
                    )

                    # Extract county from display_name (format: "..., County Name, California, ...")
                    county = self._extract_county_from_display_name(display_name)
                    if county:
                        df.at[idx, "county"] = county
                        df.at[idx, "region"] = self._get_region_from_county(county)
                        county_extracted += 1

        # For providers without coordinates, try to infer from city
        for idx, row in df.iterrows():
            if not row["county"] and row["city"]:
                county = self._infer_county_from_city(row["city"])
                if county:
                    df.at[idx, "county"] = county
                    df.at[idx, "region"] = self._get_region_from_county(county)

        logger.info(f"🌍 Added geographic enrichment for {county_extracted} providers")
        return df

    def _extract_county_from_display_name(self, display_name: str) -> str:
        """Extract county name from geocoded display name."""
        # Pattern: "..., County Name, California, ..."
        parts = display_name.split(", ")

        for i, part in enumerate(parts):
            if "County" in part and i > 0:
                return part.replace(" County", "").strip()

        return ""

    def _infer_county_from_city(self, city: str) -> str:
        """Infer county from city name using common knowledge."""
        city_county_map = {
            "LOS ANGELES": "Los Angeles",
            "SAN FRANCISCO": "San Francisco",
            "SAN DIEGO": "San Diego",
            "SAN JOSE": "Santa Clara",
            "OAKLAND": "Alameda",
            "SACRAMENTO": "Sacramento",
            "FRESNO": "Fresno",
            "LONG BEACH": "Los Angeles",
            "ANAHEIM": "Orange",
            "BAKERSFIELD": "Kern",
            "RIVERSIDE": "Riverside",
            "STOCKTON": "San Joaquin",
            "CHULA VISTA": "San Diego",
            "FREMONT": "Alameda",
            "MODESTO": "Stanislaus",
            "OXNARD": "Ventura",
            "FONTANA": "San Bernardino",
            "SANTA CLARITA": "Los Angeles",
            "MORENO VALLEY": "Riverside",
            "HUNTINGTON BEACH": "Orange",
            "GLENDALE": "Los Angeles",
            "SANTA ANA": "Orange",
            "ESCONDIDO": "San Diego",
            "SUNNYVALE": "Santa Clara",
            "FULLERTON": "Orange",
            "GARDEN GROVE": "Orange",
            "TORRANCE": "Los Angeles",
            "ORANGE": "Orange",
            "OCEANSIDE": "San Diego",
            "EL MONTE": "Los Angeles",
            "PASADENA": "Los Angeles",
            "SALINAS": "Monterey",
            "POMONA": "Los Angeles",
            "HAYWARD": "Alameda",
            "PALMDALE": "Los Angeles",
            "LANCASTER": "Los Angeles",
            "CORONA": "Riverside",
            "VICTORVILLE": "San Bernardino",
            "VALLEJO": "Solano",
            "CONCORD": "Contra Costa",
            "BERKELEY": "Alameda",
            "INGLEWOOD": "Los Angeles",
            "SANTA ROSA": "Sonoma",
            "ANTIOCH": "Contra Costa",
            "FAIRFIELD": "Solano",
            "RICHMOND": "Contra Costa",
            "WEST COVINA": "Los Angeles",
            "NORWALK": "Los Angeles",
            "DALY CITY": "San Mateo",
            "BURBANK": "Los Angeles",
            "VISTA": "San Diego",
            "SAN MATEO": "San Mateo",
            "WALNUT CREEK": "Contra Costa",
        }

        return city_county_map.get(city.upper(), "")

    def _get_region_from_county(self, county: str) -> str:
        """Get California region from county name."""
        for region, counties in self.CA_REGIONS.items():
            if county in counties:
                return region
        return "Unknown"

    def _calculate_optimization_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate optimization metrics for machine learning models."""
        # Create spatial points for distance calculations
        geocoded_providers = df[
            pd.notna(df["latitude"]) & pd.notna(df["longitude"])
        ].copy()

        if len(geocoded_providers) == 0:
            logger.warning("No geocoded providers found for optimization metrics")
            return df

        # Calculate accessibility scores (proximity to other providers)
        for idx, row in geocoded_providers.iterrows():
            accessibility_score = self._calculate_accessibility_score(
                row, geocoded_providers
            )
            efficiency_rating = self._calculate_efficiency_rating(row)
            coverage_radius = self._calculate_coverage_radius(row)

            df.at[idx, "accessibility_score"] = accessibility_score
            df.at[idx, "efficiency_rating"] = efficiency_rating
            df.at[idx, "coverage_radius_km"] = coverage_radius

        logger.info(
            f"📈 Calculated optimization metrics for {len(geocoded_providers)} providers"
        )
        return df

    def _calculate_accessibility_score(
        self, provider: pd.Series, all_providers: pd.DataFrame
    ) -> float:
        """Calculate accessibility score based on proximity to other providers."""
        provider_point = Point(provider["longitude"], provider["latitude"])

        # Calculate distances to other providers
        distances = []
        for _, other_provider in all_providers.iterrows():
            if other_provider["npi"] != provider["npi"]:
                other_point = Point(
                    other_provider["longitude"], other_provider["latitude"]
                )
                # Approximate distance in km (rough conversion from degrees)
                distance_km = provider_point.distance(other_point) * 111.32
                distances.append(distance_km)

        if not distances:
            return 0.5  # Neutral score for single provider

        # Accessibility decreases with distance to nearest providers
        avg_distance_to_nearest_5 = np.mean(sorted(distances)[:5])

        # Normalize to 0-1 scale (closer = higher accessibility)
        if avg_distance_to_nearest_5 < 10:  # Very accessible
            return 1.0
        elif avg_distance_to_nearest_5 < 25:  # Moderately accessible
            return 0.8
        elif avg_distance_to_nearest_5 < 50:  # Somewhat accessible
            return 0.6
        elif avg_distance_to_nearest_5 < 100:  # Low accessibility
            return 0.4
        else:  # Very low accessibility
            return 0.2

    def _calculate_efficiency_rating(self, provider: pd.Series) -> float:
        """Calculate efficiency rating based on provider characteristics."""
        # Base efficiency score
        efficiency = 0.5

        # Specialty efficiency modifiers
        specialty_code = provider["specialty"]
        specialty_info = self.SPECIALTY_CAPACITY_MAP.get(specialty_code, {})
        complexity_multiplier = specialty_info.get("complexity_multiplier", 1.0)

        # Higher complexity specialties are more efficient for complex cases
        if complexity_multiplier > 1.3:
            efficiency += 0.2
        elif complexity_multiplier > 1.0:
            efficiency += 0.1

        # Practice type efficiency modifiers
        practice_type = provider["practice_type"]
        if practice_type in ["hospital", "health_system"]:
            efficiency += 0.2  # Higher efficiency due to resources
        elif practice_type in ["academic"]:
            efficiency += 0.1  # Moderate efficiency due to teaching load
        elif practice_type in ["large_group", "medium_group"]:
            efficiency += 0.15  # Group practice efficiency

        # Capacity efficiency
        capacity = provider["estimated_capacity"]
        if capacity > 2500:
            efficiency += 0.1  # High-capacity providers
        elif capacity < 1000:
            efficiency -= 0.1  # Low-capacity providers may be less efficient

        # Ensure score stays in 0-1 range
        return max(0.0, min(1.0, efficiency))

    def _calculate_coverage_radius(self, provider: pd.Series) -> float:
        """Calculate estimated coverage radius in km."""
        # Base radius depends on practice type and specialty
        base_radius = 25.0  # km, reasonable for specialty care

        specialty_code = provider["specialty"]
        specialty_info = self.SPECIALTY_CAPACITY_MAP.get(specialty_code, {})
        complexity_multiplier = specialty_info.get("complexity_multiplier", 1.0)

        # More specialized providers have larger coverage areas
        radius = base_radius * complexity_multiplier

        # Practice type modifiers
        practice_type = provider["practice_type"]
        if practice_type in ["hospital", "health_system"]:
            radius *= 1.5  # Larger coverage for hospital systems
        elif practice_type in ["academic"]:
            radius *= 1.3  # Academic centers serve wider areas
        elif practice_type == "solo":
            radius *= 0.8  # Solo practitioners have smaller coverage

        # Rural areas (low accessibility) have larger coverage radii
        accessibility = provider["accessibility_score"]
        if accessibility < 0.4:
            radius *= 1.5  # Rural areas need larger coverage

        return round(radius, 1)

    def _add_quality_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add data quality scores."""
        for idx, row in df.iterrows():
            quality_score = self._calculate_data_quality_score(row)
            df.at[idx, "data_quality_score"] = quality_score

            # External validation (simplified - would need actual validation logic)
            # For now, assume some percentage are validated based on geocoding success
            if pd.notna(row["latitude"]) and row["geocoding_accuracy"] in [
                "High",
                "Medium",
            ]:
                df.at[idx, "external_validated"] = True

        return df

    def _calculate_data_quality_score(self, provider: pd.Series) -> float:
        """Calculate overall data quality score (0-1)."""
        score = 0.0

        # Core data completeness (40% weight)
        core_fields = ["npi", "provider_name", "address", "city", "state", "zip_code"]
        core_completeness = sum(
            1
            for field in core_fields
            if pd.notna(provider[field]) and provider[field] != ""
        ) / len(core_fields)
        score += 0.4 * core_completeness

        # Geocoding quality (30% weight)
        if pd.notna(provider["latitude"]) and pd.notna(provider["longitude"]):
            geocoding_score = 1.0
            if provider["geocoding_accuracy"] == "High":
                geocoding_score = 1.0
            elif provider["geocoding_accuracy"] == "Medium":
                geocoding_score = 0.8
            elif provider["geocoding_accuracy"] == "Low":
                geocoding_score = 0.6
            score += 0.3 * geocoding_score

        # Geographic enrichment (20% weight)
        geo_completeness = (
            sum(1 for field in ["county", "region"] if provider[field] != "") / 2
        )
        score += 0.2 * geo_completeness

        # Capacity estimation (10% weight)
        if provider["estimated_capacity"] > 0:
            score += 0.1

        return round(score, 3)

    def _validate_and_save(self, df: pd.DataFrame, output_file: str) -> pd.DataFrame:
        """Validate the data and save to parquet format."""
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Validate required columns
        required_columns = [
            "npi",
            "provider_name",
            "specialty",
            "credentials",
            "address",
            "city",
            "county",
            "region",
            "latitude",
            "longitude",
            "estimated_capacity",
            "practice_type",
            "accessibility_score",
            "efficiency_rating",
            "coverage_radius_km",
            "data_quality_score",
            "geocoding_accuracy",
            "external_validated",
            "last_updated",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Ensure correct data types
        df["npi"] = df["npi"].astype(str)
        df["estimated_capacity"] = df["estimated_capacity"].astype(int)
        df["accessibility_score"] = df["accessibility_score"].astype(float)
        df["efficiency_rating"] = df["efficiency_rating"].astype(float)
        df["coverage_radius_km"] = df["coverage_radius_km"].astype(float)
        df["data_quality_score"] = df["data_quality_score"].astype(float)
        df["external_validated"] = df["external_validated"].astype(bool)

        # Save to parquet with compression
        df.to_parquet(output_file, compression="snappy", index=False)
        logger.info(f"💾 Saved {len(df)} providers to {output_file}")

        return df

    def _print_summary(self, df: pd.DataFrame):
        """Print a comprehensive summary of the parquet file creation."""
        print("\n" + "=" * 80)
        print("🎯 PROVIDERS.PARQUET CREATION SUMMARY")
        print("=" * 80)

        print(f"\n📊 Dataset Overview:")
        print(f"  • Total providers: {len(df)}")
        print(f"  • File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        print(f"  • Schema columns: {len(df.columns)}")

        # Geocoding summary
        geocoded = df[pd.notna(df["latitude"]) & pd.notna(df["longitude"])]
        print(f"\n📍 Geographic Coverage:")
        print(
            f"  • Geocoded providers: {len(geocoded)} ({len(geocoded)/len(df)*100:.1f}%)"
        )
        print(f"  • High accuracy: {len(df[df['geocoding_accuracy'] == 'High'])}")
        print(f"  • Medium accuracy: {len(df[df['geocoding_accuracy'] == 'Medium'])}")
        print(f"  • Low accuracy: {len(df[df['geocoding_accuracy'] == 'Low'])}")

        # Regional distribution
        print(f"\n🌍 Regional Distribution:")
        for region in df["region"].value_counts().head(3).index:
            if region:
                count = len(df[df["region"] == region])
                print(f"  • {region}: {count} providers")

        # Capacity summary
        print(f"\n💊 Capacity Estimation:")
        print(
            f"  • Total estimated capacity: {df['estimated_capacity'].sum():,} patients/year"
        )
        print(
            f"  • Average capacity per provider: {df['estimated_capacity'].mean():.0f} patients/year"
        )
        print(
            f"  • Capacity range: {df['estimated_capacity'].min()} - {df['estimated_capacity'].max()}"
        )

        # Practice types
        print(f"\n🏥 Practice Types:")
        for practice_type in df["practice_type"].value_counts().head(5).index:
            count = len(df[df["practice_type"] == practice_type])
            print(f"  • {practice_type.replace('_', ' ').title()}: {count} providers")

        # Quality metrics
        print(f"\n✅ Quality Metrics:")
        print(f"  • Average data quality score: {df['data_quality_score'].mean():.3f}")
        print(f"  • High quality (>0.8): {len(df[df['data_quality_score'] > 0.8])}")
        print(
            f"  • External validated: {len(df[df['external_validated']])} ({len(df[df['external_validated']])/len(df)*100:.1f}%)"
        )

        # Optimization readiness
        print(f"\n📈 Optimization Readiness:")
        optimization_ready = df[
            pd.notna(df["latitude"])
            & pd.notna(df["longitude"])
            & (df["estimated_capacity"] > 0)
            & (df["data_quality_score"] > 0.5)
        ]
        print(
            f"  • Optimization-ready providers: {len(optimization_ready)} ({len(optimization_ready)/len(df)*100:.1f}%)"
        )
        print(
            f"  • Average accessibility score: {optimization_ready['accessibility_score'].mean():.3f}"
        )
        print(
            f"  • Average efficiency rating: {optimization_ready['efficiency_rating'].mean():.3f}"
        )
        print(
            f"  • Average coverage radius: {optimization_ready['coverage_radius_km'].mean():.1f} km"
        )

        print("\n" + "=" * 80)
        print("✅ providers.parquet file creation complete!")
        print("🚀 Ready for demand modeling and optimization algorithms!")
        print("=" * 80)


if __name__ == "__main__":
    # Test the parquet creator
    import sys

    sys.path.append("../..")

    # Create providers.parquet from cleaned data
    input_file = "data/processed/ca_cardiology_cleaned.csv"
    output_file = "data/processed/providers.parquet"

    if Path(input_file).exists():
        creator = ProvidersParquetCreator()
        result_df = creator.create_providers_parquet(input_file, output_file)

        print(f"\n✅ Parquet creation complete!")
        print(f"📁 File location: {output_file}")
        print(f"📊 Shape: {result_df.shape}")

    else:
        print(f"❌ Input file not found: {input_file}")
        print("Please run the data cleaning pipeline first.")
