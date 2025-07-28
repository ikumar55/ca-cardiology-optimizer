"""
CMS Medicare claims data collection module for the Cardiology Care Optimization System.

This module collects Medicare Provider Utilization and Payment Data to extract
cardiovascular service utilization patterns for demand estimation modeling.
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
    from ...utils.aws_utils import CloudWatchManager, S3Manager
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class CMSMedicareCollector:
    """
    Collect CMS Medicare utilization data for cardiovascular services.

    Processes Medicare Provider Utilization and Payment Data to extract
    cardiology-specific claims (HCPCS codes 93000-93799) and calculate
    service utilization patterns aggregated to ZIP code level.
    """

    def __init__(
        self,
        output_dir: str = "data/external/cms_medicare",
        app_token: Optional[str] = None,
    ):
        """
        Initialize the CMS Medicare data collector.

        Args:
            output_dir: Directory to save collected data
            app_token: Optional Socrata app token for higher rate limits
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.app_token = app_token

        # CMS Medicare API endpoints
        self.api_base = "https://data.cms.gov/data-api/v1/dataset"

        # Medicare Provider Utilization dataset ID
        self.dataset_id = "92396110-2aed-4d63-a6a2-5d6207d46a29"

        # Cardiovascular HCPCS codes (CPT codes 93000-93799)
        self.cardio_hcpcs_codes = self._generate_cardio_hcpcs_codes()

        # Collection statistics
        self.collection_stats = {
            "total_records": 0,
            "cardio_records": 0,
            "california_records": 0,
            "unique_providers": 0,
            "unique_services": 0,
            "processing_time": 0,
            "api_calls": 0,
        }

    def _generate_cardio_hcpcs_codes(self) -> list[str]:
        """Generate list of cardiovascular HCPCS codes (93000-93799)."""
        # Core cardiovascular procedure codes
        cardio_codes = []

        # CPT codes 93000-93799 (Cardiovascular procedures)
        for code in range(93000, 93800):
            cardio_codes.append(str(code))

        # Add common modifier variations that might appear
        base_codes = [
            # Common cardiovascular procedures
            "93010",
            "93015",
            "93017",
            "93018",  # ECG/EKG
            "93050",
            "93051",
            "93052",  # Arterial pressure monitoring
            "93306",
            "93307",
            "93308",
            "93312",  # Echocardiography
            "93350",
            "93351",  # Stress echocardiography
            "93458",
            "93459",
            "93460",
            "93461",  # Cardiac catheterization
            "93571",
            "93572",  # Intravascular ultrasound
            "93583",
            "93584",  # Percutaneous transcatheter
            "93653",
            "93654",
            "93656",  # Electrophysiology
            "93701",
            "93702",  # Bioimpedance analysis
        ]

        cardio_codes.extend(base_codes)

        return sorted(list(set(cardio_codes)))  # Remove duplicates and sort

    def collect_medicare_data(
        self, year: int = 2023, state: str = "CA"
    ) -> pd.DataFrame:
        """
        Collect Medicare Provider Utilization data for cardiovascular services.

        Args:
            year: Year of data to collect
            state: State abbreviation to filter for

        Returns:
            DataFrame with Medicare utilization data
        """
        start_time = time.time()
        logger.info(f"Starting CMS Medicare data collection for {state} (Year: {year})")

        # Check for cached data first
        cache_file = self.output_dir / f"cms_medicare_{state.lower()}_{year}.csv"
        if cache_file.exists():
            logger.info(f"Loading cached Medicare data from {cache_file}")
            cached_df = pd.read_csv(cache_file)
            logger.info(f"Loaded {len(cached_df)} cached records")
            return cached_df

        # Fetch data from CMS API
        logger.info("Fetching data from CMS Medicare API")
        raw_data = self._fetch_medicare_api_data(year, state)

        if raw_data.empty:
            logger.warning("No data retrieved from CMS Medicare API")
            return pd.DataFrame()

        # Filter for cardiovascular services
        logger.info("Filtering for cardiovascular health services")
        cardio_data = self._filter_cardiovascular_services(raw_data)

        # Clean and standardize data
        logger.info("Cleaning and standardizing Medicare data")
        cleaned_data = self._clean_medicare_data(cardio_data)

        # Validate data quality
        logger.info("Validating Medicare data quality")
        validated_data = self._validate_medicare_data(cleaned_data)

        # Calculate collection statistics
        end_time = time.time()
        self.collection_stats["processing_time"] = int(end_time - start_time)

        # Cache the results
        cache_file = self.output_dir / f"cms_medicare_{state.lower()}_{year}.csv"
        validated_data.to_csv(cache_file, index=False)
        logger.info(f"Saved Medicare data to cache: {cache_file}")

        logger.info(
            f"Successfully collected CMS Medicare data: {len(validated_data)} {state} cardiovascular services"
        )

        return validated_data

    def _fetch_medicare_api_data(self, year: int, state: str) -> pd.DataFrame:
        """
        Fetch Medicare data from CMS API with pagination.

        Args:
            year: Year of data to collect
            state: State abbreviation

        Returns:
            DataFrame with raw Medicare data
        """
        all_data = []
        offset = 0
        limit = 50000  # Max records per request

        while True:
            # API query parameters
            params = {
                "size": limit,
                "offset": offset,
                "filter[Rndrng_Prvdr_Geo_Desc]": state,  # Filter by state
                "filter[data_year]": year,  # Filter by year if available
            }

            # Add app token if available
            if self.app_token:
                params["$$app_token"] = self.app_token

            # Construct API URL
            api_url = f"{self.api_base}/{self.dataset_id}/data"

            try:
                logger.info(f"API request with offset {offset}")
                response = requests.get(api_url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                if not data:
                    logger.info("No more data available from API")
                    break

                all_data.extend(data)
                self.collection_stats["api_calls"] += 1

                # Check if we got less than the limit (indicates last page)
                if len(data) < limit:
                    logger.info("Reached end of available data")
                    break

                offset += limit

                # Rate limiting - be respectful to CMS API
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                break

        logger.info(f"Retrieved {len(all_data)} total records from CMS Medicare API")
        self.collection_stats["total_records"] = len(all_data)

        if not all_data:
            return pd.DataFrame()

        return pd.DataFrame(all_data)

    def _filter_cardiovascular_services(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter Medicare data for cardiovascular services using HCPCS codes.

        Args:
            df: Raw Medicare data

        Returns:
            DataFrame filtered for cardiovascular services
        """
        if df.empty:
            return df

        # Look for HCPCS code column (may have different names)
        hcpcs_columns = [
            col for col in df.columns if "hcpcs" in col.lower() or "code" in col.lower()
        ]

        if not hcpcs_columns:
            logger.error("No HCPCS code column found in Medicare data")
            return pd.DataFrame()

        hcpcs_col = hcpcs_columns[0]
        logger.info(f"Using HCPCS column: {hcpcs_col}")

        # Filter for cardiovascular HCPCS codes
        cardio_mask = df[hcpcs_col].astype(str).isin(self.cardio_hcpcs_codes)
        cardio_data = df[cardio_mask].copy()

        logger.info(f"Filtered to {len(cardio_data)} cardiovascular service records")
        self.collection_stats["cardio_records"] = len(cardio_data)

        return cardio_data

    def _clean_medicare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize Medicare data.

        Args:
            df: Raw cardiovascular Medicare data

        Returns:
            Cleaned and standardized DataFrame
        """
        if df.empty:
            return df

        cleaned_df = df.copy()

        # Standardize column names
        column_mapping = {
            "Rndrng_NPI": "provider_npi",
            "Rndrng_Prvdr_Last_Org_Name": "provider_name",
            "Rndrng_Prvdr_First_Name": "provider_first_name",
            "Rndrng_Prvdr_City": "provider_city",
            "Rndrng_Prvdr_State_Abrvtn": "provider_state",
            "Rndrng_Prvdr_Zip5": "provider_zip",
            "HCPCS_Cd": "hcpcs_code",
            "HCPCS_Desc": "service_description",
            "Tot_Srvcs": "total_services",
            "Tot_Benes": "total_beneficiaries",
            "Avg_Medicare_Pymt_Amt": "avg_medicare_payment",
            "Avg_Sbmtd_Chrg": "avg_submitted_charge",
        }

        # Rename columns that exist
        existing_mappings = {
            old: new for old, new in column_mapping.items() if old in cleaned_df.columns
        }
        cleaned_df = cleaned_df.rename(columns=existing_mappings)

        # Ensure numeric columns are properly typed
        numeric_columns = [
            "total_services",
            "total_beneficiaries",
            "avg_medicare_payment",
            "avg_submitted_charge",
        ]
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")

        # Clean provider ZIP codes
        if "provider_zip" in cleaned_df.columns:
            cleaned_df["provider_zip"] = (
                cleaned_df["provider_zip"].astype(str).str.zfill(5)
            )

        # Add metadata
        cleaned_df["data_source"] = "CMS_MEDICARE_PUF"
        cleaned_df["collection_date"] = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Cleaned data: {len(cleaned_df)} records remaining")

        return cleaned_df

    def _validate_medicare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Medicare data quality and consistency.

        Args:
            df: Cleaned Medicare data

        Returns:
            Validated DataFrame
        """
        if df.empty:
            logger.warning("Empty dataset provided for validation")
            return df

        initial_count = len(df)

        # Remove records with invalid data
        if "total_services" in df.columns:
            df = df[df["total_services"] > 0]

        if "provider_npi" in df.columns:
            df = df[df["provider_npi"].notna()]

        if "provider_zip" in df.columns:
            # Keep only valid ZIP codes (5 digits)
            df = df[df["provider_zip"].str.match(r"^\d{5}$", na=False)]

        final_count = len(df)

        # Calculate quality metrics
        self.collection_stats["unique_providers"] = (
            df["provider_npi"].nunique() if "provider_npi" in df.columns else 0
        )
        self.collection_stats["unique_services"] = (
            df["hcpcs_code"].nunique() if "hcpcs_code" in df.columns else 0
        )

        logger.info("Data quality validation summary:")
        logger.info(f"  - Total records: {final_count}")
        logger.info(
            f"  - Unique providers: {self.collection_stats['unique_providers']}"
        )
        logger.info(f"  - Unique services: {self.collection_stats['unique_services']}")
        logger.info(f"  - Records removed: {initial_count - final_count}")

        return df

    def aggregate_to_zip_code(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate Medicare utilization data to ZIP code level.

        Args:
            df: Cleaned Medicare data

        Returns:
            DataFrame aggregated by ZIP code
        """
        if df.empty or "provider_zip" not in df.columns:
            logger.error("Cannot aggregate: missing ZIP code data")
            return pd.DataFrame()

        logger.info("Aggregating Medicare data to ZIP code level")

        # Group by ZIP code and aggregate
        agg_functions = {
            "total_services": "sum",
            "total_beneficiaries": "sum",
            "avg_medicare_payment": "mean",
            "avg_submitted_charge": "mean",
            "provider_npi": "nunique",  # Unique providers per ZIP
            "hcpcs_code": "nunique",  # Unique services per ZIP
        }

        # Filter to only include columns that exist
        available_agg = {
            col: func for col, func in agg_functions.items() if col in df.columns
        }

        zip_aggregated = df.groupby("provider_zip").agg(available_agg).reset_index()

        # Rename aggregated columns
        zip_aggregated.columns = ["zip_code"] + [
            (
                f"{col}_total"
                if func == "sum"
                else f"{col}_avg" if func == "mean" else f"unique_{col}"
            )
            for col, func in available_agg.items()
        ]

        # Calculate additional metrics
        if (
            "total_services_total" in zip_aggregated.columns
            and "unique_provider_npi" in zip_aggregated.columns
        ):
            zip_aggregated["services_per_provider"] = (
                zip_aggregated["total_services_total"]
                / zip_aggregated["unique_provider_npi"]
            )

        # Add metadata
        zip_aggregated["data_source"] = "CMS_MEDICARE_PUF_AGGREGATED"
        zip_aggregated["collection_date"] = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Aggregated to {len(zip_aggregated)} ZIP codes")

        return zip_aggregated


def main():
    """Test the CMS Medicare collector."""
    print("=== CMS Medicare Data Collection Test ===")

    # Initialize collector
    collector = CMSMedicareCollector()

    try:
        # Collect California Medicare data for 2023
        data = collector.collect_medicare_data(year=2023, state="CA")

        if not data.empty:
            print(f"✅ SUCCESS: Collected {len(data)} CMS Medicare records")
            print(f"📊 Data shape: {data.shape}")
            print(
                f"🏥 Unique providers: {collector.collection_stats['unique_providers']}"
            )
            print(
                f"🩺 Unique services: {collector.collection_stats['unique_services']}"
            )

            print(f"\n📋 Sample Data:")
            print(data.head().to_string())

            # Test ZIP code aggregation
            zip_data = collector.aggregate_to_zip_code(data)
            if not zip_data.empty:
                print(f"\n🗺️ ZIP code aggregation: {len(zip_data)} ZIP codes")
                print(zip_data.head().to_string())

            print(f"\n📈 Collection Summary:")
            for key, value in collector.collection_stats.items():
                print(f"  - {key.replace('_', ' ').title()}: {value}")

        else:
            print("❌ No data collected")

    except Exception as e:
        print(f"❌ Error during collection: {e}")
        logger.exception("CMS Medicare collection failed")


if __name__ == "__main__":
    main()
