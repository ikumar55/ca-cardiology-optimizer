"""
CA Health and Human Services Provider Directory validator.

This module validates our CMS NPPES provider data against the official
CA HHS Provider Directory to ensure data accuracy and completeness.
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests

try:
    from ...utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class CAHHSValidator:
    """Validate provider data against CA Health and Human Services Provider Directory."""

    # CA HHS Provider Directory API endpoints
    CA_HHS_BASE_URL = "https://data.chhs.ca.gov/api/3/action"
    PROVIDER_DATASET_ID = "profile-of-enrolled-medi-cal-fee-for-service-ffs-providers"

    def __init__(self):
        """Initialize the CA HHS validator."""
        self.validation_stats = {
            "total_providers": 0,
            "matched_providers": 0,
            "unmatched_providers": 0,
            "validation_errors": 0,
            "match_rate": 0.0,
        }

    def download_ca_hhs_data(
        self, output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Download the latest CA HHS Provider Directory data.

        Args:
            output_path: Path to save the downloaded data

        Returns:
            Path to downloaded file or None if failed
        """
        logger.info("📥 Downloading CA HHS Provider Directory data")

        if output_path is None:
            output_path = Path("data/external/ca_hhs/medi_cal_providers.csv")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Try to get the dataset metadata first
            metadata_url = (
                f"{self.CA_HHS_BASE_URL}/package_show?id={self.PROVIDER_DATASET_ID}"
            )

            logger.info(f"🔍 Fetching dataset metadata from: {metadata_url}")
            response = requests.get(metadata_url, timeout=30)
            response.raise_for_status()

            metadata = response.json()

            if not metadata.get("success"):
                logger.error("❌ Failed to get dataset metadata")
                return None

            # Find the latest CSV resource
            resources = metadata["result"]["resources"]
            csv_resources = [
                r for r in resources if r.get("format", "").upper() == "CSV"
            ]

            if not csv_resources:
                logger.error("❌ No CSV resources found in dataset")
                return None

            # Get the most recent CSV resource
            latest_resource = max(
                csv_resources, key=lambda x: x.get("last_modified", "")
            )
            download_url = latest_resource["url"]

            logger.info(f"📥 Downloading from: {download_url}")

            # Download the file
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"✅ CA HHS data downloaded to: {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to download CA HHS data: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error downloading CA HHS data: {e}")
            return None

    def load_ca_hhs_data(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load and preprocess CA HHS provider data.

        Args:
            file_path: Path to CA HHS CSV file

        Returns:
            DataFrame with CA HHS provider data or None if failed
        """
        logger.info(f"📖 Loading CA HHS data from: {file_path}")

        try:
            # Load the CSV file
            df = pd.read_csv(file_path)

            logger.info(f"✅ Loaded {len(df):,} CA HHS provider records")
            logger.info(f"📋 Columns: {list(df.columns)}")

            # Show sample data
            logger.info(f"📋 Sample CA HHS data:")
            logger.info(df.head(2).to_string())

            return df

        except Exception as e:
            logger.error(f"❌ Failed to load CA HHS data: {e}")
            return None

    def validate_providers(
        self, cms_providers: pd.DataFrame, ca_hhs_data: pd.DataFrame
    ) -> tuple[pd.DataFrame, dict]:
        """
        Validate CMS providers against CA HHS data.

        Args:
            cms_providers: Cleaned CMS NPPES provider data
            ca_hhs_data: CA HHS provider directory data

        Returns:
            Tuple of (validated_providers, validation_report)
        """
        logger.info("🔍 Starting provider validation against CA HHS directory")

        self.validation_stats["total_providers"] = len(cms_providers)

        # Create a copy for validation results
        validated_providers = cms_providers.copy()
        validated_providers["ca_hhs_match"] = False
        validated_providers["ca_hhs_confidence"] = 0.0
        validated_providers["validation_notes"] = ""

        # Try different matching strategies
        matched_indices = set()

        # Strategy 1: Exact NPI match
        if "NPI" in cms_providers.columns and "NPI" in ca_hhs_data.columns:
            logger.info("🔍 Strategy 1: Exact NPI matching")
            npi_matches = self._match_by_npi(cms_providers, ca_hhs_data)
            matched_indices.update(npi_matches)
            logger.info(f"✅ NPI matches: {len(npi_matches)}")

        # Strategy 2: Name and location matching
        logger.info("🔍 Strategy 2: Name and location matching")
        name_matches = self._match_by_name_location(
            cms_providers, ca_hhs_data, exclude_indices=matched_indices
        )
        matched_indices.update(name_matches)
        logger.info(f"✅ Name/location matches: {len(name_matches)}")

        # Update validation results
        validated_providers.loc[list(matched_indices), "ca_hhs_match"] = True
        validated_providers.loc[list(matched_indices), "ca_hhs_confidence"] = 0.9

        self.validation_stats["matched_providers"] = len(matched_indices)
        self.validation_stats["unmatched_providers"] = len(cms_providers) - len(
            matched_indices
        )
        self.validation_stats["match_rate"] = (
            (len(matched_indices) / len(cms_providers)) * 100
            if len(cms_providers) > 0
            else 0
        )

        # Generate validation report
        validation_report = self._generate_validation_report()

        logger.info(f"✅ Validation complete!")
        logger.info(f"📊 Match rate: {self.validation_stats['match_rate']:.1f}%")
        logger.info(f"📊 Matched: {self.validation_stats['matched_providers']:,}")
        logger.info(f"📊 Unmatched: {self.validation_stats['unmatched_providers']:,}")

        return validated_providers, validation_report

    def _match_by_npi(
        self, cms_providers: pd.DataFrame, ca_hhs_data: pd.DataFrame
    ) -> list[int]:
        """Match providers by exact NPI."""
        matches = []

        # Create NPI sets for fast lookup
        cms_npis = set(cms_providers["NPI"].astype(str))
        ca_hhs_npis = set(ca_hhs_data["NPI"].astype(str))

        # Find exact matches
        common_npis = cms_npis.intersection(ca_hhs_npis)

        for npi in common_npis:
            cms_indices = cms_providers[cms_providers["NPI"].astype(str) == npi].index
            matches.extend(cms_indices.tolist())

        return matches

    def _match_by_name_location(
        self,
        cms_providers: pd.DataFrame,
        ca_hhs_data: pd.DataFrame,
        exclude_indices: set,
    ) -> list[int]:
        """Match providers by name and location similarity."""
        matches = []

        # Get unmatched CMS providers
        unmatched_mask = ~cms_providers.index.isin(exclude_indices)
        unmatched_cms = cms_providers[unmatched_mask]

        if len(unmatched_cms) == 0:
            return matches

        # Try to match by name similarity and location
        for idx, cms_provider in unmatched_cms.iterrows():
            best_match = None
            best_score = 0.0

            # Get provider name and location
            cms_name = str(cms_provider.get("provider_name", "")).lower()
            cms_city = str(cms_provider.get("city", "")).lower()
            cms_zip = str(cms_provider.get("zip_code", "")).strip()

            if not cms_name or cms_name == "nan":
                continue

            # Look for matches in CA HHS data
            for _, ca_hhs_provider in ca_hhs_data.iterrows():
                # Get CA HHS provider info (column names may vary)
                ca_hhs_name = str(ca_hhs_provider.get("Provider Name", "")).lower()
                ca_hhs_city = str(ca_hhs_provider.get("City", "")).lower()
                ca_hhs_zip = str(ca_hhs_provider.get("ZIP Code", "")).strip()

                if not ca_hhs_name or ca_hhs_name == "nan":
                    continue

                # Calculate similarity score
                name_similarity = self._calculate_name_similarity(cms_name, ca_hhs_name)
                location_match = (cms_city == ca_hhs_city) or (cms_zip == ca_hhs_zip)

                # Combined score
                score = name_similarity * 0.8 + (0.2 if location_match else 0.0)

                if score > best_score and score > 0.7:  # High confidence threshold
                    best_score = score
                    best_match = ca_hhs_provider

            if best_match is not None:
                matches.append(idx)

        return matches

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two provider names."""
        # Simple similarity calculation
        # In a real implementation, you might use more sophisticated algorithms

        # Clean names
        name1 = re.sub(r"[^\w\s]", "", name1.lower())
        name2 = re.sub(r"[^\w\s]", "", name2.lower())

        # Split into words
        words1 = set(name1.split())
        words2 = set(name2.split())

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _generate_validation_report(self) -> dict:
        """Generate validation report."""
        report = {
            "validation_summary": {
                "total_providers": self.validation_stats["total_providers"],
                "matched_providers": self.validation_stats["matched_providers"],
                "unmatched_providers": self.validation_stats["unmatched_providers"],
                "match_rate": self.validation_stats["match_rate"],
            },
            "data_quality_assessment": {
                "high_confidence_matches": self.validation_stats["matched_providers"],
                "validation_coverage": self.validation_stats["match_rate"],
                "data_reliability": (
                    "High" if self.validation_stats["match_rate"] > 70 else "Medium"
                ),
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        if self.validation_stats["match_rate"] < 50:
            recommendations.append(
                "Low match rate suggests data quality issues or different provider populations"
            )
        elif self.validation_stats["match_rate"] < 70:
            recommendations.append(
                "Moderate match rate - consider additional validation sources"
            )
        else:
            recommendations.append("High match rate indicates good data quality")

        if self.validation_stats["unmatched_providers"] > 100:
            recommendations.append(
                "Consider implementing additional matching strategies"
            )

        return recommendations


def main():
    """Main function for testing the CA HHS validator."""
    from pathlib import Path

    import pandas as pd

    # Load cleaned CMS data
    cleaned_path = Path("data/processed/ca_cardiology_cleaned.csv")
    if not cleaned_path.exists():
        print(f"❌ Cleaned data not found at: {cleaned_path}")
        print("Please run provider_cleaner.py first")
        return

    cms_providers = pd.read_csv(cleaned_path)
    print(f"📊 Loaded {len(cms_providers):,} cleaned CMS providers")

    # Initialize validator
    validator = CAHHSValidator()

    # Try to download CA HHS data
    ca_hhs_path = validator.download_ca_hhs_data()

    if ca_hhs_path and ca_hhs_path.exists():
        # Load CA HHS data
        ca_hhs_data = validator.load_ca_hhs_data(ca_hhs_path)

        if ca_hhs_data is not None:
            # Validate providers
            validated_providers, report = validator.validate_providers(
                cms_providers, ca_hhs_data
            )

            print(f"\n🎉 Validation complete!")
            print(f"📊 Match rate: {report['validation_summary']['match_rate']:.1f}%")
            print(
                f"📊 Matched providers: {report['validation_summary']['matched_providers']:,}"
            )
            print(
                f"📊 Unmatched providers: {report['validation_summary']['unmatched_providers']:,}"
            )

            # Save validated data
            output_path = Path("data/processed/ca_cardiology_validated.csv")
            validated_providers.to_csv(output_path, index=False)
            print(f"💾 Validated data saved to: {output_path}")

            # Show recommendations
            if report["recommendations"]:
                print(f"\n💡 Recommendations:")
                for rec in report["recommendations"]:
                    print(f"   • {rec}")
        else:
            print("❌ Failed to load CA HHS data")
    else:
        print("❌ Failed to download CA HHS data")
        print("Continuing with CMS data only...")


if __name__ == "__main__":
    main()
