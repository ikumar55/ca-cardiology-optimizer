"""
Provider data collection module for the Cardiology Care Optimization System.

This module implements the de-risked provider data collection strategy using
reliable government data sources like CMS NPPES and CA HHS directories.
"""

import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    from ..utils.aws_utils import get_aws_helper
    from ..utils.logging import get_logger
except ImportError:
    # Fallback for standalone testing
    import logging

    def get_logger(name):
        return logging.getLogger(name)

    def get_aws_helper():
        return None


logger = get_logger(__name__)


class CMSNPPESCollector:
    """Collector for CMS National Plan and Provider Enumeration System data."""

    BASE_URL = "https://download.cms.gov/nppes/NPI_Files.html"

    # Correct cardiology taxonomy codes based on research
    CARDIOLOGY_TAXONOMY_CODES = [
        "207RC0000X",  # Cardiovascular Disease (main cardiology)
        "207RI0011X",  # Interventional Cardiology
        "207RR0500X",  # Clinical Cardiac Electrophysiology
        "207K00000X",  # Pediatric Cardiology
        "208G00000X",  # Thoracic Surgery (Cardiothoracic Surgery)
    ]

    def __init__(self, aws_helper=None):
        """Initialize the CMS NPPES collector.

        Args:
            aws_helper: AWS helper instance for cloud storage
        """
        self.aws_helper = aws_helper or get_aws_helper()

    def get_latest_file_url(self) -> Optional[str]:
        """Get the URL of the latest NPPES bulk data file.

        Returns:
            URL string if found, None if failed
        """
        try:
            logger.info("Fetching latest NPPES file URL from CMS website")
            response = requests.get(self.BASE_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for bulk data download links
            # NPPES files are typically named like "NPPES_Data_Dissemination_January_2025.zip"
            links = soup.find_all("a", href=True)

            for link in links:
                href = link["href"]
                if "NPPES_Data_Dissemination" in href and href.lower().endswith(".zip"):

                    # Convert relative URLs to absolute
                    if href.startswith("http"):
                        return href
                    else:
                        return urljoin(self.BASE_URL, href)

            logger.error("No NPPES bulk data file found on CMS website")
            return None

        except Exception as e:
            logger.error(f"Failed to get latest NPPES file URL: {e}")
            return None

    def download_nppes_file(self, url: str, local_path: Path) -> bool:
        """Download NPPES bulk data file.

        Args:
            url: URL of the NPPES file
            local_path: Path to save the downloaded file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading NPPES file from {url}")

            # Create directory if it doesn't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)

            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            logger.info(f"Downloading {total_size / (1024*1024):.1f} MB NPPES file")

            with open(local_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Log progress every 100MB
                        if downloaded % (100 * 1024 * 1024) == 0:
                            progress = (
                                (downloaded / total_size * 100) if total_size > 0 else 0
                            )
                            logger.info(f"Download progress: {progress:.1f}%")

            logger.info(f"NPPES file downloaded to {local_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download NPPES file: {e}")
            return False

    def extract_nppes_file(self, zip_path: Path, extract_dir: Path) -> Optional[Path]:
        """Extract NPPES ZIP file and find the main CSV file.

        Args:
            zip_path: Path to the ZIP file
            extract_dir: Directory to extract files

        Returns:
            Path to the main CSV file if found, None otherwise
        """
        try:
            logger.info(f"Extracting NPPES file from {zip_path}")

            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

                # Find the main CSV file (usually largest)
                csv_files = list(extract_dir.glob("*.csv"))

                if not csv_files:
                    logger.error("No CSV files found in NPPES archive")
                    return None

                # The main provider file is typically the largest
                main_csv = max(csv_files, key=lambda x: x.stat().st_size)

                logger.info(f"Found main NPPES CSV file: {main_csv}")
                logger.info(
                    f"File size: {main_csv.stat().st_size / (1024*1024):.1f} MB"
                )

                return main_csv

        except Exception as e:
            logger.error(f"Failed to extract NPPES file: {e}")
            return None

    def parse_nppes_data(self, csv_path: Path, chunk_size: int = 10000) -> pd.DataFrame:
        """Parse NPPES CSV file and extract relevant provider information.

        Args:
            csv_path: Path to the NPPES CSV file
            chunk_size: Number of rows to process at a time

        Returns:
            DataFrame with parsed provider information
        """
        try:
            logger.info(f"Parsing NPPES data from {csv_path}")

            # NPPES CSV files are typically very large, so we process in chunks
            providers = []
            total_rows = 0
            ca_providers = 0

            # Define the columns we need (based on NPPES file format)
            required_columns = [
                "NPI",
                "Entity Type Code",
                "Provider Last Name (Legal Name)",
                "Provider First Name",
                "Provider Middle Name",
                "Provider Organization Name (Legal Business Name)",
                "Provider First Line Business Practice Location Address",
                "Provider Second Line Business Practice Location Address",
                "Provider Business Practice Location Address City Name",
                "Provider Business Practice Location Address State Name",
                "Provider Business Practice Location Address Postal Code",
                "Healthcare Provider Taxonomy Code_1",
                "Healthcare Provider Taxonomy Code_2",
                "Healthcare Provider Taxonomy Code_3",
                "Healthcare Provider Taxonomy Code_4",
                "Healthcare Provider Taxonomy Code_5",
                "Healthcare Provider Taxonomy Code_6",
                "Healthcare Provider Taxonomy Code_7",
                "Healthcare Provider Taxonomy Code_8",
                "Healthcare Provider Taxonomy Code_9",
                "Healthcare Provider Taxonomy Code_10",
                "Healthcare Provider Taxonomy Code_11",
                "Healthcare Provider Taxonomy Code_12",
                "Healthcare Provider Taxonomy Code_13",
                "Healthcare Provider Taxonomy Code_14",
                "Healthcare Provider Taxonomy Code_15",
            ]

            # Read file in chunks to handle large files
            for chunk_num, chunk in enumerate(
                pd.read_csv(csv_path, chunksize=chunk_size)
            ):
                total_rows += len(chunk)

                if chunk_num % 100 == 0:  # Log progress every 100 chunks
                    logger.info(f"Processed {total_rows:,} rows so far")

                # Filter for California providers
                ca_chunk = chunk[
                    chunk["Provider Business Practice Location Address State Name"]
                    == "CA"
                ]

                if len(ca_chunk) == 0:
                    continue

                # Check for cardiology taxonomy codes in any of the taxonomy fields
                taxonomy_columns = [
                    col
                    for col in chunk.columns
                    if "Healthcare Provider Taxonomy Code" in col
                ]

                cardiology_mask = False
                for col in taxonomy_columns:
                    if col in ca_chunk.columns:
                        for code in self.CARDIOLOGY_TAXONOMY_CODES:
                            cardiology_mask |= ca_chunk[col] == code

                cardiology_providers = ca_chunk[cardiology_mask]

                if len(cardiology_providers) > 0:
                    ca_providers += len(cardiology_providers)
                    providers.append(cardiology_providers)

            logger.info(
                f"Finished parsing NPPES data: {total_rows:,} total rows processed"
            )
            logger.info(f"Found {ca_providers} California cardiology providers")

            if not providers:
                logger.warning("No cardiology providers found in California")
                return pd.DataFrame()

            # Combine all chunks
            result_df = pd.concat(providers, ignore_index=True)

            # Clean and standardize the data
            result_df = self._clean_provider_data(result_df)

            logger.info(f"Final dataset: {len(result_df)} providers after cleaning")

            return result_df

        except Exception as e:
            logger.error(f"Failed to parse NPPES data: {e}")
            return pd.DataFrame()

    def _clean_provider_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize provider data.

        Args:
            df: Raw provider DataFrame

        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning provider data")

        # Create standardized columns
        cleaned_df = pd.DataFrame()

        # NPI (unique identifier)
        cleaned_df["npi"] = df["NPI"].astype(str).str.strip()

        # Provider name (handle both individual and organization)
        cleaned_df["provider_name"] = ""

        # For organizations
        org_mask = df["Entity Type Code"] == 2
        cleaned_df.loc[org_mask, "provider_name"] = df.loc[
            org_mask, "Provider Organization Name (Legal Business Name)"
        ].fillna("")

        # For individuals
        individual_mask = df["Entity Type Code"] == 1
        first_name = df.loc[individual_mask, "Provider First Name"].fillna("")
        middle_name = df.loc[individual_mask, "Provider Middle Name"].fillna("")
        last_name = df.loc[individual_mask, "Provider Last Name (Legal Name)"].fillna(
            ""
        )

        cleaned_df.loc[individual_mask, "provider_name"] = (
            (last_name + ", " + first_name + " " + middle_name)
            .str.replace("  ", " ")
            .str.strip(", ")
        )

        # Practice address
        address_parts = [
            df["Provider First Line Business Practice Location Address"].fillna(""),
            df["Provider Second Line Business Practice Location Address"].fillna(""),
        ]

        cleaned_df["practice_address"] = (
            address_parts[0] + " " + address_parts[1]
        ).str.strip()

        # City, state, zip
        cleaned_df["city"] = df[
            "Provider Business Practice Location Address City Name"
        ].fillna("")
        cleaned_df["state"] = df[
            "Provider Business Practice Location Address State Name"
        ].fillna("")
        cleaned_df["zip_code"] = df[
            "Provider Business Practice Location Address Postal Code"
        ].fillna("")

        # Full address for geocoding
        cleaned_df["full_address"] = (
            cleaned_df["practice_address"]
            + ", "
            + cleaned_df["city"]
            + ", "
            + cleaned_df["state"]
            + " "
            + cleaned_df["zip_code"]
        ).str.strip(", ")

        # Entity type
        cleaned_df["entity_type"] = df["Entity Type Code"].map(
            {1: "Individual", 2: "Organization"}
        )

        # Remove duplicates based on NPI
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(subset=["npi"], keep="first")
        final_count = len(cleaned_df)

        if initial_count != final_count:
            logger.info(f"Removed {initial_count - final_count} duplicate providers")

        # Remove providers with missing critical information
        before_filter = len(cleaned_df)
        cleaned_df = cleaned_df[
            (cleaned_df["npi"].str.len() > 0)
            & (cleaned_df["provider_name"].str.len() > 0)
            & (cleaned_df["practice_address"].str.len() > 0)
            & (cleaned_df["city"].str.len() > 0)
        ]
        after_filter = len(cleaned_df)

        if before_filter != after_filter:
            logger.info(
                f"Removed {before_filter - after_filter} providers with missing critical data"
            )

        return cleaned_df

    def collect_and_store(self, force_download: bool = False) -> bool:
        """Main method to collect NPPES data and store in S3.

        Args:
            force_download: Whether to force download even if data exists

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if data already exists in S3
            if not force_download:
                existing_files = self.aws_helper.s3.list_objects(
                    "raw_data", "providers/cms_nppes"
                )
                if existing_files:
                    logger.info(
                        "NPPES data already exists in S3. Use force_download=True to re-download."
                    )
                    return True

            # Get latest file URL
            file_url = self.get_latest_file_url()
            if not file_url:
                return False

            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Download file
                zip_path = temp_path / "nppes_data.zip"
                if not self.download_nppes_file(file_url, zip_path):
                    return False

                # Extract file
                extract_dir = temp_path / "extracted"
                csv_path = self.extract_nppes_file(zip_path, extract_dir)
                if not csv_path:
                    return False

                # Parse data
                provider_df = self.parse_nppes_data(csv_path)
                if provider_df.empty:
                    logger.error("No provider data extracted")
                    return False

                # Store raw data in S3
                logger.info("Uploading parsed provider data to S3")
                success = self.aws_helper.s3.upload_dataframe(
                    provider_df,
                    "raw_data",
                    "providers/cms_nppes_ca_cardiology_raw",
                    format="parquet",
                )

                if success:
                    # Log to CloudWatch
                    self.aws_helper.cloudwatch.put_log_events(
                        "data-collection",
                        [
                            f"Successfully collected {len(provider_df)} CA cardiology providers from CMS NPPES"
                        ],
                    )

                    # Send metrics
                    self.aws_helper.cloudwatch.put_metric_data(
                        "CardiologyOptimizer/DataCollection",
                        "ProvidersCollected",
                        len(provider_df),
                        dimensions={"Source": "CMS_NPPES", "State": "CA"},
                    )

                    logger.info(
                        f"Successfully collected and stored {len(provider_df)} providers"
                    )
                    return True
                else:
                    logger.error("Failed to upload data to S3")
                    return False

        except Exception as e:
            logger.error(f"Failed to collect NPPES data: {e}")

            # Log error to CloudWatch
            self.aws_helper.cloudwatch.put_log_events(
                "data-collection", [f"Failed to collect CMS NPPES data: {str(e)}"]
            )

            return False


def download_nppes_monthly_files(start_year=2020, end_year=2023, output_dir="data/raw/nppes_monthly"):
    """
    Download NPPES monthly files from NBER mirror for historical provider movement analysis.
    
    Args:
        start_year (int): Start year for downloads (default: 2020)
        end_year (int): End year for downloads (default: 2023)
        output_dir (str): Base directory for storing downloaded files
    
    Returns:
        dict: Download summary with success/failure counts and file paths
    """
    import hashlib
    import json
    import os
    import zipfile
    from datetime import datetime
    from pathlib import Path

    import requests

    # Create output directories
    base_dir = Path(output_dir)
    metadata_dir = base_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # Download log
    download_log = {
        "download_date": datetime.now().isoformat(),
        "source": "NBER mirror (https://data.nber.org/npi/)",
        "files": [],
        "summary": {"total": 0, "successful": 0, "failed": 0}
    }
    
    # NBER URL pattern
    base_url = "https://data.nber.org/npi"
    
    for year in range(start_year, end_year + 1):
        year_dir = base_dir / str(year)
        year_dir.mkdir(exist_ok=True)
        
        # Get list of files for this year
        year_url = f"{base_url}/{year}/"
        print(f"Processing year {year}...")
        
        try:
            # For now, we'll use a simplified approach
            # In practice, we'd need to scrape the directory or have a known file list
            # For this implementation, we'll create a template for the expected files
            
            # Expected monthly files (this would need to be updated with actual file names)
            monthly_files = [
                f"npidata_pfile_{year}0101-{year}0131.csv.zip",
                f"npidata_pfile_{year}0201-{year}0228.csv.zip",
                f"npidata_pfile_{year}0301-{year}0331.csv.zip",
                f"npidata_pfile_{year}0401-{year}0430.csv.zip",
                f"npidata_pfile_{year}0501-{year}0531.csv.zip",
                f"npidata_pfile_{year}0601-{year}0630.csv.zip",
                f"npidata_pfile_{year}0701-{year}0731.csv.zip",
                f"npidata_pfile_{year}0801-{year}0831.csv.zip",
                f"npidata_pfile_{year}0901-{year}0930.csv.zip",
                f"npidata_pfile_{year}1001-{year}1031.csv.zip",
                f"npidata_pfile_{year}1101-{year}1130.csv.zip",
                f"npidata_pfile_{year}1201-{year}1231.csv.zip"
            ]
            
            for filename in monthly_files:
                file_url = f"{year_url}{filename}"
                local_path = year_dir / filename
                
                file_info = {
                    "filename": filename,
                    "url": file_url,
                    "local_path": str(local_path),
                    "status": "pending",
                    "download_time": None,
                    "file_size": None,
                    "checksum": None,
                    "error": None
                }
                
                print(f"  Downloading {filename}...")
                
                try:
                    # Download file
                    start_time = datetime.now()
                    response = requests.get(file_url, stream=True)
                    response.raise_for_status()
                    
                    # Save file
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Verify download
                    if local_path.exists():
                        file_size = local_path.stat().st_size
                        
                        # Calculate checksum
                        with open(local_path, 'rb') as f:
                            file_hash = hashlib.md5()
                            for chunk in iter(lambda: f.read(4096), b""):
                                file_hash.update(chunk)
                            checksum = file_hash.hexdigest()
                        
                        # Update file info
                        file_info.update({
                            "status": "success",
                            "download_time": (datetime.now() - start_time).total_seconds(),
                            "file_size": file_size,
                            "checksum": checksum
                        })
                        
                        download_log["summary"]["successful"] += 1
                        print(f"    ✓ Downloaded successfully ({file_size:,} bytes)")
                    else:
                        raise Exception("File not found after download")
                        
                except Exception as e:
                    file_info.update({
                        "status": "failed",
                        "error": str(e)
                    })
                    download_log["summary"]["failed"] += 1
                    print(f"    ✗ Download failed: {e}")
                
                download_log["files"].append(file_info)
                download_log["summary"]["total"] += 1
                
        except Exception as e:
            print(f"Error processing year {year}: {e}")
    
    # Save download log
    log_file = metadata_dir / f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(download_log, f, indent=2)
    
    print(f"\nDownload Summary:")
    print(f"  Total files: {download_log['summary']['total']}")
    print(f"  Successful: {download_log['summary']['successful']}")
    print(f"  Failed: {download_log['summary']['failed']}")
    print(f"  Log saved to: {log_file}")
    
    return download_log


def main():
    """Main function for testing the collector."""
    collector = CMSNPPESCollector()
    success = collector.collect_and_store(force_download=False)

    if success:
        print("✅ CMS NPPES data collection completed successfully")
    else:
        print("❌ CMS NPPES data collection failed")


if __name__ == "__main__":
    main()
