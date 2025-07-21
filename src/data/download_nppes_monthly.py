#!/usr/bin/env python3
"""
NPPES Monthly Files Download Script

This script downloads NPPES monthly files from the NBER mirror for historical
provider movement analysis (Task 15.1).

- By default, only downloads the year 2020 for local development and testing.
- For full-scale production (all years), update start_year/end_year and consider running on cloud infrastructure.

Usage:
    python src/data/download_nppes_monthly.py
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_nppes_monthly_files(start_year=2020, end_year=2020, output_dir="data/raw/nppes_monthly"):
    """
    Download NPPES monthly files from NBER mirror for historical provider movement analysis.
    By default, only downloads 2020 for local development. For full-scale, update years and use cloud.
    """
    base_dir = Path(output_dir)
    metadata_dir = base_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    download_log = {
        "download_date": datetime.now().isoformat(),
        "source": "NBER mirror (https://data.nber.org/npi/)",
        "files": [],
        "summary": {"total": 0, "successful": 0, "failed": 0}
    }
    base_url = "https://data.nber.org/npi"
    for year in range(start_year, end_year + 1):
        year_dir = base_dir / str(year)
        year_dir.mkdir(exist_ok=True)
        year_url = f"{base_url}/{year}/csv/"
        logger.info(f"Processing year {year}...")
        monthly_files = [f"npi{year}{month}.csv" for month in range(1, 13)]
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
            logger.info(f"  Downloading {filename}...")
            try:
                start_time = datetime.now()
                response = requests.get(file_url, stream=True, timeout=60)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                if local_path.exists():
                    file_size = local_path.stat().st_size
                    with open(local_path, 'rb') as f:
                        # Bandit: MD5 is fine for file integrity, not security
                        file_hash = hashlib.md5()  # nosec
                        while True:
                            chunk = f.read(4096)
                            if not chunk:
                                break
                            file_hash.update(chunk)
                        checksum = file_hash.hexdigest()
                    file_info.update({
                        "status": "success",
                        "download_time": (datetime.now() - start_time).total_seconds(),
                        "file_size": file_size,
                        "checksum": checksum
                    })
                    download_log["summary"]["successful"] += 1
                    logger.info(
                        "    ✓ Downloaded successfully ({} bytes)".format(
                            f"{file_size:,}"
                        )
                    )
                else:
                    raise Exception("File not found after download")
            except Exception as e:
                file_info.update({
                    "status": "failed",
                    "error": str(e)
                })
                download_log["summary"]["failed"] += 1
                logger.error(f"    ✗ Download failed: {e}")
            download_log["files"].append(file_info)
            download_log["summary"]["total"] += 1
    log_file = metadata_dir / (
        "download_log_{}.json".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
    )
    with open(log_file, 'w') as f:
        json.dump(download_log, f, indent=2)
    logger.info("\nDownload Summary:")
    logger.info(f"  Total files: {download_log['summary']['total']}")
    logger.info(f"  Successful: {download_log['summary']['successful']}")
    logger.info(f"  Failed: {download_log['summary']['failed']}")
    logger.info(f"  Log saved to: {log_file}")
    return download_log

def main():
    logger.info(
        "Starting NPPES monthly files download (2020 only, for local dev)..."
    )
    download_nppes_monthly_files()
    logger.info("NPPES monthly files download completed.")

if __name__ == "__main__":
    main()
