"""
CDC PLACES data collection module for the Cardiology Care Optimization System.

This module collects ZIP Code Tabulation Area (ZCTA) level cardiovascular health
prevalence data from the CDC PLACES dataset to support demand estimation modeling.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

try:
    from ..utils.aws_utils import CloudWatchManager, S3Manager
    from ..utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class CDCPlacesCollector:
    """
    Collect and process CDC PLACES cardiovascular health data for demand estimation.

    The CDC PLACES dataset provides ZIP Code Tabulation Area (ZCTA) level estimates
    for cardiovascular health outcomes including coronary heart disease, stroke,
    high blood pressure, and asthma prevalence.
    """

    def __init__(
        self, data_dir: str = "data/external/cdc_places", cache_enabled: bool = True
    ):
        """
        Initialize the CDC PLACES data collector.

        Args:
            data_dir: Directory to store downloaded CDC PLACES data
            cache_enabled: Whether to use local caching to avoid redundant downloads
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_enabled = cache_enabled
        self.collection_stats = {
            "start_time": None,
            "end_time": None,
            "total_zctas": 0,
            "california_zctas": 0,
            "cardiovascular_measures": 0,
            "data_quality_checks": {},
            "api_calls": 0,
            "processing_time": 0,
        }

        # CDC PLACES API configuration
        self.base_url = "https://data.cdc.gov/resource/qnzd-25i4.json"
        self.app_token = None  # Optional: Can be set for higher rate limits

        # Cardiovascular health measures to collect (based on CDC PLACES 2024 release)
        self.cardiovascular_measures = {
            "CHD": {
                "measure": "CHD",
                "full_name": "Coronary heart disease among adults",
                "description": "Adults who report ever having been told by a doctor, nurse, or other health professional that they had angina or coronary heart disease",
                "time_period": "Lifetime",
                "priority": "high",  # Primary cardiovascular outcome
            },
            "STROKE": {
                "measure": "STROKE",
                "full_name": "Stroke among adults",
                "description": "Adults who report ever having been told by a doctor, nurse, or other health professional that they have had a stroke",
                "time_period": "Lifetime",
                "priority": "high",  # Primary cardiovascular outcome
            },
            "BPHIGH": {
                "measure": "BPHIGH",
                "full_name": "High blood pressure among adults",
                "description": "Adults who report ever having been told by a doctor, nurse, or other health professional that they have high blood pressure",
                "time_period": "Lifetime",
                "priority": "high",  # Major cardiovascular risk factor
            },
            "CASTHMA": {
                "measure": "CASTHMA",
                "full_name": "Current asthma among adults",
                "description": "Adults who report currently having asthma",
                "time_period": "Current",
                "priority": "medium",  # Related cardiovascular comorbidity
            },
            "HIGHCHOL": {
                "measure": "HIGHCHOL",
                "full_name": "High cholesterol among adults who have ever been screened",
                "description": "Adults who report having been told by a doctor, nurse, or other health professional that they had high cholesterol",
                "time_period": "Lifetime",
                "priority": "high",  # Major cardiovascular risk factor
            },
        }

        # California state FIPS code for filtering
        self.california_fips = "06"

    def collect_california_places_data(self, year: str = "2024") -> pd.DataFrame:
        """
        Collect CDC PLACES cardiovascular health data for California ZCTAs.

        Args:
            year: Data release year (default: 2024 for most recent data)

        Returns:
            DataFrame containing California ZCTA-level cardiovascular health prevalence data
        """
        logger.info(
            f"Starting CDC PLACES data collection for California (Year: {year})"
        )
        self.collection_stats["start_time"] = datetime.now()

        try:
            # Check for cached data first
            cache_file = self.data_dir / f"cdc_places_california_{year}.csv"
            if self.cache_enabled and cache_file.exists():
                logger.info(f"Loading cached CDC PLACES data from {cache_file}")
                df = pd.read_csv(cache_file)
                logger.info(f"Loaded {len(df)} cached records")
                return df

            # Collect data from CDC PLACES API
            places_data = self._fetch_places_api_data()

            if places_data.empty:
                logger.warning("No data retrieved from CDC PLACES API")
                return pd.DataFrame()

            # Filter for California ZCTAs
            ca_places_data = self._filter_california_data(places_data)

            # Filter for cardiovascular measures
            cardio_data = self._filter_cardiovascular_measures(ca_places_data)

            # Clean and standardize the data
            clean_data = self._clean_places_data(cardio_data)

            # Validate data quality
            validated_data = self._validate_data_quality(clean_data)

            # Save to cache
            if self.cache_enabled:
                self._save_to_cache(validated_data, cache_file)

            # Update collection statistics
            self._update_collection_stats(validated_data)

            logger.info(
                f"Successfully collected CDC PLACES data: {len(validated_data)} California ZCTAs with cardiovascular measures"
            )

            return validated_data

        except Exception as e:
            logger.error(f"Error collecting CDC PLACES data: {str(e)}")
            raise
        finally:
            self.collection_stats["end_time"] = datetime.now()
            if self.collection_stats["start_time"]:
                self.collection_stats["processing_time"] = (
                    self.collection_stats["end_time"]
                    - self.collection_stats["start_time"]
                ).total_seconds()

    def _fetch_places_api_data(self) -> pd.DataFrame:
        """
        Fetch data from the CDC PLACES API using Socrata Open Data API.

        Returns:
            DataFrame containing raw CDC PLACES data
        """
        logger.info("Fetching data from CDC PLACES API")

        # Build query parameters for cardiovascular measures and California
        measure_list = list(self.cardiovascular_measures.keys())

        # API query parameters
        measure_filter = ",".join([f"'{m}'" for m in measure_list])
        params = {
            "$limit": 50000,  # Increased limit for comprehensive data collection
            "$offset": 0,
            "$where": f"measureid in ({measure_filter})",
            "$order": "locationid",
            "$$app_token": self.app_token if self.app_token else "",
        }

        all_data = []
        offset = 0

        while True:
            params["$offset"] = offset

            # Make API request with error handling and rate limiting
            try:
                logger.info(f"API request with offset {offset}")
                response = self._make_api_request(params)

                if not response:
                    break

                all_data.extend(response)
                self.collection_stats["api_calls"] += 1

                # If we got fewer records than the limit, we've reached the end
                if len(response) < params["$limit"]:
                    break

                offset += params["$limit"]

                # Rate limiting to be respectful to CDC servers
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"API request failed at offset {offset}: {str(e)}")
                break

        if not all_data:
            logger.warning("No data retrieved from CDC PLACES API")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        logger.info(f"Retrieved {len(df)} total records from CDC PLACES API")

        return df

    def _make_api_request(self, params: dict) -> list[dict]:
        """
        Make a single API request to CDC PLACES with error handling.

        Args:
            params: Query parameters for the API request

        Returns:
            List of records from the API response
        """
        # Clean up empty parameters
        clean_params = {k: v for k, v in params.items() if v}

        # Build the full URL
        url = f"{self.base_url}?{urlencode(clean_params)}"

        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "CardiologyOptimizer/1.0",
                    "Accept": "application/json",
                },
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"API request successful: {len(data)} records returned")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response as JSON: {str(e)}")
            raise

    def _filter_california_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter CDC PLACES data for California ZCTAs using geographic coordinates.

        Args:
            df: Raw CDC PLACES data

        Returns:
            DataFrame filtered for California ZCTAs
        """
        logger.info("Filtering data for California ZCTAs using geographic coordinates")

        if df.empty:
            return df

        # California bounding box coordinates
        ca_lat_min, ca_lat_max = 32.5, 42.0
        ca_lon_min, ca_lon_max = -124.5, -114.0

        # Extract coordinates from geolocation field
        if "geolocation" not in df.columns:
            logger.error("Geolocation column not found in CDC PLACES data")
            return pd.DataFrame()

        # Parse geolocation JSON and extract coordinates
        def extract_coordinates(geoloc):
            try:
                if isinstance(geoloc, str):
                    geoloc_data = json.loads(geoloc)
                elif isinstance(geoloc, dict):
                    geoloc_data = geoloc
                else:
                    return None, None

                if (
                    "coordinates" in geoloc_data
                    and len(geoloc_data["coordinates"]) >= 2
                ):
                    lon, lat = geoloc_data["coordinates"][:2]
                    return float(lat), float(lon)
                return None, None
            except (json.JSONDecodeError, ValueError, TypeError, KeyError):
                return None, None

        # Extract coordinates
        df[["latitude", "longitude"]] = df["geolocation"].apply(
            lambda x: pd.Series(extract_coordinates(x))
        )

        # Filter for California coordinates
        ca_mask = (
            (df["latitude"] >= ca_lat_min)
            & (df["latitude"] <= ca_lat_max)
            & (df["longitude"] >= ca_lon_min)
            & (df["longitude"] <= ca_lon_max)
        )

        ca_data = df[ca_mask].copy()

        logger.info(
            f"Filtered to {len(ca_data)} California records from {len(df)} total records"
        )
        self.collection_stats["california_zctas"] = (
            len(ca_data["locationid"].unique())
            if "locationid" in ca_data.columns
            else 0
        )

        return ca_data

    def _filter_cardiovascular_measures(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for cardiovascular health measures.

        Args:
            df: California CDC PLACES data

        Returns:
            DataFrame filtered for cardiovascular measures
        """
        logger.info("Filtering for cardiovascular health measures")

        measure_column = "measureid" if "measureid" in df.columns else "measure_id"

        if measure_column not in df.columns:
            logger.warning("Measure ID column not found in data")
            return df

        cardio_measures = list(self.cardiovascular_measures.keys())
        cardio_data = df[df[measure_column].isin(cardio_measures)].copy()

        logger.info(f"Filtered to {len(cardio_data)} cardiovascular health records")
        self.collection_stats["cardiovascular_measures"] = len(cardio_data)

        return cardio_data

    def _clean_places_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize CDC PLACES data.

        Args:
            df: Raw cardiovascular CDC PLACES data

        Returns:
            Cleaned and standardized DataFrame
        """
        logger.info("Cleaning and standardizing CDC PLACES data")

        if df.empty:
            return df

        # Standardize column names (handle different API response formats)
        column_mapping = {
            "locationid": "zcta",
            "locationname": "zcta_name",
            "measureid": "measure_id",
            "measure": "measure_name",
            "data_value": "prevalence",
            "data_value_type": "data_type",
            "low_confidence_limit": "ci_lower",
            "high_confidence_limit": "ci_upper",
            "stateabbr": "state",
            "statename": "state_name",
            "totalpopulation": "total_population",
        }

        # Apply column mapping where columns exist
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})

        # Ensure essential columns exist
        essential_columns = ["zcta", "measure_id", "prevalence"]
        missing_columns = [col for col in essential_columns if col not in df.columns]

        if missing_columns:
            logger.error(f"Missing essential columns: {missing_columns}")
            raise ValueError(f"Missing essential columns: {missing_columns}")

        # Convert data types
        df["prevalence"] = pd.to_numeric(df["prevalence"], errors="coerce")
        df["ci_lower"] = pd.to_numeric(df.get("ci_lower", np.nan), errors="coerce")
        df["ci_upper"] = pd.to_numeric(df.get("ci_upper", np.nan), errors="coerce")

        # Clean ZCTA codes (ensure they are strings and properly formatted)
        df["zcta"] = df["zcta"].astype(str).str.strip()
        df["zcta"] = df["zcta"].str.zfill(5)  # Ensure 5-digit ZCTA codes

        # Filter out invalid ZCTAs (should be 5 digits for ZIP codes)
        valid_zcta_mask = df["zcta"].str.match(r"^\d{5}$")
        df = df[valid_zcta_mask].copy()

        # Remove records with missing prevalence data
        df = df.dropna(subset=["prevalence"]).copy()

        # Add data collection metadata
        df["data_source"] = "CDC_PLACES_2024"
        df["collection_date"] = datetime.now().strftime("%Y-%m-%d")
        df["api_version"] = "2024_release"

        logger.info(f"Cleaned data: {len(df)} records remaining")

        return df

    def _validate_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data quality and completeness.

        Args:
            df: Cleaned CDC PLACES data

        Returns:
            Validated DataFrame with quality metrics
        """
        logger.info("Validating CDC PLACES data quality")

        if df.empty:
            logger.warning("Empty dataset provided for validation")
            return df

        quality_checks = {}

        # Check 1: Prevalence values are within valid range (0-100)
        valid_prevalence = (df["prevalence"] >= 0) & (df["prevalence"] <= 100)
        quality_checks["valid_prevalence_range"] = valid_prevalence.sum()
        quality_checks["invalid_prevalence_range"] = (~valid_prevalence).sum()

        # Check 2: Confidence intervals are consistent
        if "ci_lower" in df.columns and "ci_upper" in df.columns:
            valid_ci = (df["ci_lower"] <= df["prevalence"]) & (
                df["prevalence"] <= df["ci_upper"]
            )
            valid_ci = valid_ci.fillna(True)  # Allow missing CI values
            quality_checks["valid_confidence_intervals"] = valid_ci.sum()
            quality_checks["invalid_confidence_intervals"] = (~valid_ci).sum()

        # Check 3: Coverage of cardiovascular measures
        measure_coverage = df["measure_id"].value_counts()
        quality_checks["measure_coverage"] = measure_coverage.to_dict()

        # Check 4: ZCTA coverage (number of unique ZCTAs)
        unique_zctas = df["zcta"].nunique()
        quality_checks["unique_zctas"] = unique_zctas
        quality_checks["total_records"] = len(df)

        # Check 5: Completeness by measure
        completeness_by_measure = {}
        for measure in self.cardiovascular_measures.keys():
            measure_data = df[df["measure_id"] == measure]
            completeness_by_measure[measure] = {
                "zcta_count": len(measure_data),
                "avg_prevalence": (
                    measure_data["prevalence"].mean() if not measure_data.empty else 0
                ),
                "completeness_rate": (
                    len(measure_data) / unique_zctas if unique_zctas > 0 else 0
                ),
            }

        quality_checks["completeness_by_measure"] = completeness_by_measure

        # Store quality metrics
        self.collection_stats["data_quality_checks"] = quality_checks

        # Log quality summary
        logger.info(f"Data quality validation summary:")
        logger.info(f"  - Total records: {quality_checks['total_records']}")
        logger.info(f"  - Unique ZCTAs: {quality_checks['unique_zctas']}")
        logger.info(
            f"  - Valid prevalence values: {quality_checks['valid_prevalence_range']}"
        )
        logger.info(f"  - Measure coverage: {list(measure_coverage.index)}")

        # Filter out invalid records
        if "ci_lower" in df.columns and "ci_upper" in df.columns:
            df = df[valid_prevalence & valid_ci].copy()
        else:
            df = df[valid_prevalence].copy()

        return df

    def _save_to_cache(self, df: pd.DataFrame, cache_file: Path) -> None:
        """
        Save collected data to local cache file.

        Args:
            df: Processed CDC PLACES data
            cache_file: Path to cache file
        """
        try:
            df.to_csv(cache_file, index=False)
            logger.info(f"Saved CDC PLACES data to cache: {cache_file}")

            # Also save metadata
            metadata_file = cache_file.with_suffix(".json")
            metadata = {
                "collection_stats": self.collection_stats,
                "cardiovascular_measures": self.cardiovascular_measures,
                "data_shape": df.shape,
                "column_names": df.columns.tolist(),
            }

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

        except Exception as e:
            logger.warning(f"Failed to save cache file: {str(e)}")

    def _update_collection_stats(self, df: pd.DataFrame) -> None:
        """
        Update collection statistics with final results.

        Args:
            df: Final processed DataFrame
        """
        self.collection_stats.update(
            {
                "total_zctas": df["zcta"].nunique() if not df.empty else 0,
                "final_records": len(df),
                "measures_collected": df["measure_id"].nunique() if not df.empty else 0,
                "avg_prevalence_by_measure": (
                    df.groupby("measure_id")["prevalence"].mean().to_dict()
                    if not df.empty
                    else {}
                ),
                "data_quality_score": self._calculate_quality_score(),
                "success": True,
            }
        )

    def _calculate_quality_score(self) -> float:
        """
        Calculate an overall data quality score based on validation results.

        Returns:
            Quality score between 0 and 1
        """
        if not self.collection_stats.get("data_quality_checks"):
            return 0.0

        checks = self.collection_stats["data_quality_checks"]

        # Calculate component scores
        prevalence_score = checks.get("valid_prevalence_range", 0) / max(
            checks.get("total_records", 1), 1
        )

        ci_score = 1.0  # Default if no CI data
        if checks.get("valid_confidence_intervals") is not None:
            total_ci_records = checks.get("valid_confidence_intervals", 0) + checks.get(
                "invalid_confidence_intervals", 0
            )
            if total_ci_records > 0:
                ci_score = (
                    checks.get("valid_confidence_intervals", 0) / total_ci_records
                )

        # Measure coverage score (fraction of expected measures found)
        expected_measures = len(self.cardiovascular_measures)
        actual_measures = len(checks.get("measure_coverage", {}))
        coverage_score = (
            actual_measures / expected_measures if expected_measures > 0 else 0
        )

        # Weighted average
        quality_score = 0.4 * prevalence_score + 0.3 * ci_score + 0.3 * coverage_score

        return round(quality_score, 3)

    def get_collection_summary(self) -> dict:
        """
        Get a comprehensive summary of the data collection process.

        Returns:
            Dictionary containing collection statistics and data quality metrics
        """
        return {
            "collector_type": "CDC_PLACES",
            "collection_stats": self.collection_stats.copy(),
            "cardiovascular_measures": self.cardiovascular_measures,
            "data_source_info": {
                "name": "CDC PLACES: Local Data for Better Health",
                "description": "ZIP Code Tabulation Area level cardiovascular health prevalence estimates",
                "base_url": self.base_url,
                "geographic_level": "ZCTA (ZIP Code Tabulation Area)",
                "time_period": "2022 BRFSS data (2024 release)",
                "methodology": "Small Area Estimation using multilevel regression and post-stratification",
            },
        }


def main():
    """
    Main function for standalone testing of CDC PLACES data collection.
    """
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("=== CDC PLACES Data Collection Test ===")

    try:
        # Initialize collector
        collector = CDCPlacesCollector()

        # Collect California data
        ca_data = collector.collect_california_places_data()

        if not ca_data.empty:
            print(f"\n✅ SUCCESS: Collected {len(ca_data)} CDC PLACES records")
            print(f"📊 Data shape: {ca_data.shape}")
            print(f"🗺️  Unique ZCTAs: {ca_data['zcta'].nunique()}")
            print(f"📈 Measures: {ca_data['measure_id'].unique().tolist()}")

            # Display sample data
            print(f"\n📋 Sample Data:")
            print(ca_data.head(10).to_string())

            # Display collection summary
            summary = collector.get_collection_summary()
            print(f"\n📈 Collection Summary:")
            print(
                f"  - Processing time: {summary['collection_stats'].get('processing_time', 0):.1f} seconds"
            )
            print(
                f"  - Quality score: {summary['collection_stats'].get('data_quality_score', 0):.3f}"
            )
            print(
                f"  - API calls made: {summary['collection_stats'].get('api_calls', 0)}"
            )

        else:
            print("❌ No data collected")

    except Exception as e:
        print(f"❌ Error during collection: {str(e)}")
        raise


if __name__ == "__main__":
    main()
