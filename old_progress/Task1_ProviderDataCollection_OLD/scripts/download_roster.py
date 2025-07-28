#!/usr/bin/env python3
"""
CA Medical Board Roster Download Script
=======================================

This script downloads the bulk physician roster data from the California Department 
of Consumer Affairs (DCA) public data portal. It implements robust error handling,
progress tracking, and file validation.

Author: AI Assistant  
Created: July 24, 2025
Purpose: Task 1.3 - Provider Data Collection Pipeline
"""

import csv
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DCADataDownloader:
    """Downloads bulk licensee data from California Department of Consumer Affairs"""
    
    def __init__(self, base_dir: str = "Task1_ProviderDataCollection"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.results_dir = self.base_dir / "results"
        
        # DCA Data Portal URLs
        self.dca_portal_url = "https://www.dca.ca.gov/data/index.shtml"
        self.licensee_lists_url = "https://www.dca.ca.gov/consumers/public_info/index.shtml"
        
        # Known patterns for medical board data files
        self.medical_board_patterns = [
            r'medical.*board.*\.csv',
            r'mbc.*\.csv', 
            r'physician.*\.csv',
            r'doctor.*\.csv',
            r'md.*\.csv'
        ]
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_html_for_csv_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract CSV download links from HTML content"""
        logger.info("Parsing HTML content for CSV download links...")
        csv_links = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True).lower()
                
                # Look for CSV files or medical board related links
                if (href.endswith('.csv') or 
                    'csv' in link_text or 
                    'medical' in link_text or
                    'physician' in link_text or
                    'bulk' in link_text or
                    'download' in link_text):
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = f"https://www.dca.ca.gov{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(base_url, href)
                    
                    csv_links.append(full_url)
                    logger.info(f"Found potential link: {link_text} -> {full_url}")
            
        except Exception as e:
            logger.warning(f"Error parsing HTML: {e}")
        
        return csv_links
    
    def find_download_urls(self) -> List[str]:
        """Scrape the DCA website to find bulk data download URLs"""
        logger.info("Searching for bulk data download URLs...")
        download_urls = []
        
        urls_to_check = [
            self.licensee_lists_url,
            self.dca_portal_url,
            "https://www.dca.ca.gov/consumers/public_info/",
        ]
        
        for url in urls_to_check:
            try:
                logger.info(f"Checking URL: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse HTML for CSV links
                csv_links = self.parse_html_for_csv_links(response.text, url)
                download_urls.extend(csv_links)
                
            except Exception as e:
                logger.warning(f"Could not access {url}: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in download_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"Found {len(unique_urls)} potential download URLs")
        return unique_urls
    
    def download_file_with_progress(self, url: str, filepath: Path, chunk_size: int = 8192) -> bool:
        """Download file with progress tracking and validation"""
        logger.info(f"Downloading from: {url}")
        logger.info(f"Saving to: {filepath}")
        
        try:
            # Start download with streaming
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Check if we got HTML instead of CSV
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                logger.warning(f"Received HTML content instead of CSV from {url}")
                return False
            
            # Get content length for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            logger.info(f"File size: {total_size / (1024*1024):.1f} MB")
            
            downloaded = 0
            start_time = time.time()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress reporting every 10MB
                        if downloaded % (10 * 1024 * 1024) == 0 or downloaded == total_size:
                            elapsed = time.time() - start_time
                            speed = downloaded / elapsed / (1024 * 1024) if elapsed > 0 else 0
                            progress = (downloaded / total_size * 100) if total_size > 0 else 0
                            logger.info(f"Progress: {progress:.1f}% ({downloaded/(1024*1024):.1f} MB) - Speed: {speed:.1f} MB/s")
            
            logger.info(f"Download completed in {time.time() - start_time:.1f} seconds")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return False
    
    def validate_csv_file(self, filepath: Path) -> Dict[str, Any]:
        """Validate downloaded CSV file and extract metadata"""
        logger.info(f"Validating CSV file: {filepath}")
        
        validation_results = {
            'valid': False,
            'file_size': 0,
            'row_count': 0,
            'column_count': 0,
            'columns': [],
            'has_medical_data': False,
            'sample_rows': [],
            'file_hash': None
        }
        
        try:
            # Basic file checks
            if not filepath.exists():
                logger.error("File does not exist")
                return validation_results
            
            file_size = filepath.stat().st_size
            validation_results['file_size'] = file_size
            logger.info(f"File size: {file_size / (1024*1024):.1f} MB")
            
            # Check if file is too small (likely an error page)
            if file_size < 1024:  # Less than 1KB
                logger.warning("File is too small, likely an error or HTML page")
                return validation_results
            
            # Calculate file hash for integrity
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            validation_results['file_hash'] = hasher.hexdigest()
            
            # Check if it's actually HTML (common error)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip().lower()
                if first_line.startswith('<!doctype') or first_line.startswith('<html'):
                    logger.warning("File appears to be HTML, not CSV")
                    return validation_results
            
            # CSV structure validation
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                csv_reader = csv.reader(f)
                
                # Get headers
                try:
                    headers = next(csv_reader)
                    validation_results['columns'] = headers
                    validation_results['column_count'] = len(headers)
                    logger.info(f"Columns found: {headers}")
                    
                    # Check for expected medical board columns
                    expected_fields = ['license', 'name', 'address', 'agency', 'type', 'status']
                    medical_indicators = ['medical', 'physician', 'doctor', 'cardio', 'md', 'surgeon']
                    
                    has_expected_structure = any(
                        any(field.lower() in col.lower() for field in expected_fields)
                        for col in headers
                    )
                    
                    # Count rows and get samples
                    row_count = 0
                    sample_rows = []
                    medical_content_found = False
                    
                    for row in csv_reader:
                        row_count += 1
                        if row_count <= 5:  # Keep first 5 rows as samples
                            sample_rows.append(row)
                        
                        # Check for medical-related content in first 100 rows
                        if row_count <= 100:
                            row_text = ' '.join(row).lower()
                            if any(indicator in row_text for indicator in medical_indicators):
                                medical_content_found = True
                    
                    validation_results['row_count'] = row_count
                    validation_results['sample_rows'] = sample_rows
                    validation_results['has_medical_data'] = medical_content_found
                    
                    logger.info(f"Total rows: {row_count}")
                    logger.info(f"Expected structure: {has_expected_structure}")
                    logger.info(f"Contains medical data: {medical_content_found}")
                    
                    # Overall validation - more specific criteria
                    validation_results['valid'] = (
                        file_size > 100 * 1024 and  # At least 100KB
                        row_count > 100 and  # At least 100 records
                        has_expected_structure and
                        medical_content_found
                    )
                    
                except Exception as e:
                    logger.error(f"Error reading CSV content: {e}")
                    
        except Exception as e:
            logger.error(f"File validation failed: {e}")
        
        return validation_results
    
    def save_download_report(self, url: str, filepath: Path, validation_results: Dict[str, Any]) -> None:
        """Save detailed download and validation report"""
        report = {
            'download_timestamp': datetime.now().isoformat(),
            'source_url': url,
            'local_filepath': str(filepath),
            'validation_results': validation_results,
            'download_successful': validation_results['valid']
        }
        
        report_path = self.results_dir / "download_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        logger.info(f"Download report saved to: {report_path}")
    
    def try_download_from_url(self, url: str) -> Optional[Path]:
        """Attempt to download from a specific URL"""
        logger.info(f"Attempting download from: {url}")
        
        # Generate filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or not filename.endswith(('.csv', '.zip')):
            filename = "ca_medical_board_roster_raw.csv"
        
        filepath = self.data_dir / filename
        
        # Attempt download
        if self.download_file_with_progress(url, filepath):
            # Validate downloaded file
            validation_results = self.validate_csv_file(filepath)
            self.save_download_report(url, filepath, validation_results)
            
            if validation_results['valid']:
                logger.info("✅ Download successful and validated!")
                return filepath
            else:
                logger.warning("⚠️ Download completed but validation failed")
                # Keep file for manual inspection but return None
                return None
        
        return None
    
    def create_manual_instructions(self) -> None:
        """Create detailed manual download instructions"""
        instructions_file = self.data_dir / "MANUAL_DOWNLOAD_INSTRUCTIONS.txt"
        
        instructions = """
CA MEDICAL BOARD ROSTER - MANUAL DOWNLOAD INSTRUCTIONS
====================================================

The automated download script was unable to locate the direct CSV download link.
Please follow these steps to manually download the data:

STEP 1: Navigate to DCA Public Information Portal
   URL: https://www.dca.ca.gov/consumers/public_info/index.shtml

STEP 2: Look for Medical Board of California Section
   - Look for folders or links related to "Medical Board of California"
   - The agency code should be "MBC" 
   - May also be listed as "Physician and Surgeon" licenses

STEP 3: Download the Bulk Data File
   - Look for CSV files containing physician/doctor data
   - File should be 50-100MB+ in size
   - Should contain approximately 450,000+ total physician records
   - Download the most recent file (usually monthly updates)

STEP 4: Save the File
   - Save the downloaded file as: ca_medical_board_roster_raw.csv
   - Place it in the directory: Task1_ProviderDataCollection/data/
   - Exact path: Task1_ProviderDataCollection/data/ca_medical_board_roster_raw.csv

STEP 5: Verify the Download
   - File size should be at least 50MB
   - Open the file and verify it contains physician data
   - Should have columns like: License Number, Name, Address, City, County, etc.
   - Should contain various medical specialties including cardiology

ALTERNATIVE SOURCES TO TRY:
1. https://www.dca.ca.gov/data/index.shtml (Main data portal)
2. https://www.mbc.ca.gov/ (Medical Board website - look for public data)
3. Search for "California physician licensee data" or "MBC bulk data"

EXPECTED DATA STRUCTURE:
- Total records: ~450,000 physicians
- Cardiology providers: ~5,200 (our target)
- File format: CSV with headers
- Update frequency: Monthly

If you successfully download the file manually, you can continue with the next 
step in the pipeline (Task 1.4: Filter for cardiology providers).

For questions or issues, check the TaskMaster documentation or implementation diary.
"""
        
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        logger.info(f"Manual download instructions created: {instructions_file}")
        print(f"\n📄 Manual download instructions saved to: {instructions_file}")
    
    def run_download(self) -> Optional[Path]:
        """Main download orchestration method"""
        logger.info("🚀 Starting CA Medical Board roster download...")
        logger.info(f"Target directory: {self.data_dir}")
        
        # Step 1: Try to find download URLs by scraping
        download_urls = self.find_download_urls()
        
        if not download_urls:
            logger.warning("No download URLs found through web scraping")
        
        # Step 2: Try each URL until we find a working one
        for url in download_urls:
            try:
                result = self.try_download_from_url(url)
                if result:
                    logger.info(f"✅ Successfully downloaded from: {url}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue
        
        # Step 3: Create manual download instructions
        logger.error("❌ Automated download failed from all attempted URLs")
        logger.info("Creating manual download instructions...")
        
        self.create_manual_instructions()
        
        print("\n" + "="*60)
        print("🔍 MANUAL DOWNLOAD REQUIRED")
        print("="*60)
        print("The automated script could not find the direct download link.")
        print("This is common with government data portals that change their structure.")
        print("\nWhat to do next:")
        print("1. Follow the manual instructions in: Task1_ProviderDataCollection/data/MANUAL_DOWNLOAD_INSTRUCTIONS.txt")
        print("2. Navigate to: https://www.dca.ca.gov/consumers/public_info/index.shtml")
        print("3. Look for Medical Board of California bulk data")
        print("4. Download the CSV file and save it as 'ca_medical_board_roster_raw.csv'")
        print("5. Place it in: Task1_ProviderDataCollection/data/")
        print("6. Then proceed to task 1.4 (filtering)")
        print("="*60)
        
        return None


def main():
    """Main execution function"""
    # Initialize downloader
    downloader = DCADataDownloader()
    
    # Run download process
    result_file = downloader.run_download()
    
    if result_file:
        print(f"\n✅ SUCCESS: CA Medical Board roster downloaded to: {result_file}")
        print(f"📊 File size: {result_file.stat().st_size / (1024*1024):.1f} MB")
        print("Ready for next step: filtering for cardiology providers")
        return 0
    else:
        print("\n⚠️ AUTOMATED DOWNLOAD UNSUCCESSFUL")
        print("Manual download required - see instructions above")
        print("Once downloaded manually, proceed to task 1.4")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 