#!/usr/bin/env python3
"""
Test script to download a small chunk of a single NPPES file to verify the download process works.
"""

import logging
from datetime import datetime
from pathlib import Path

import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_partial_download():
    """Test downloading the first 1 MB of a single NPPES file using HTTP Range header."""
    year = 2020
    month = "01"
    filename = f"npi{year}{int(month)}.csv"  # npi20201.csv
    url = f"https://data.nber.org/npi/{year}/csv/{filename}"
    test_dir = Path("data/raw/nppes_monthly/test")
    test_dir.mkdir(parents=True, exist_ok=True)
    local_path = test_dir / (filename + ".part")

    logger.info(f"Testing partial download of {filename}")
    logger.info(f"URL: {url}")
    logger.info(f"Local path: {local_path}")

    try:
        # Download only the first 1 MB
        headers = {"Range": "bytes=0-1048575"}  # 1 MB
        start_time = datetime.now()
        logger.info("Starting partial download (1 MB)...")
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        file_size = local_path.stat().st_size
        download_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ Partial download successful!")
        logger.info(
            "  File size: {} bytes".format(f"{file_size:,}")
        )
        logger.info(
            "  Download time: {:.2f} seconds".format(download_time)
        )
        # Test reading the first few lines
        logger.info("Testing file readability...")
        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.readline().strip()
            logger.info(
                "  Header: {}...".format(header[:100])
            )
            columns = header.split(',')
            logger.info(
                "  Number of columns: {}".format(len(columns))
            )
            for i in range(3):
                line = f.readline().strip()
                if line:
                    logger.info(
                        "  Row {}: {}...".format(i + 1, line[:100])
                    )
        return True
    except Exception as e:
        logger.error(f"✗ Partial download failed: {e}")
        return False

if __name__ == "__main__":
    success = test_partial_download()
    if success:
        logger.info("Partial download test completed successfully!")
    else:
        logger.error("Partial download test failed!")
