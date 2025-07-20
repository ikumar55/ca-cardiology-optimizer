"""
Standalone test script for CMS NPPES data collection without AWS dependencies.
"""

import os
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Correct cardiology taxonomy codes based on research
CARDIOLOGY_TAXONOMY_CODES = [
    "207RC0000X",  # Cardiovascular Disease (main cardiology)
    "207RI0011X",  # Interventional Cardiology
    "207RR0500X",  # Clinical Cardiac Electrophysiology
    "207K00000X",  # Pediatric Cardiology
    "208G00000X",  # Thoracic Surgery (Cardiothoracic Surgery)
]


def get_latest_nppes_url():
    """Get the URL of the latest NPPES bulk data file."""
    print("🔍 Discovering latest CMS NPPES file...")

    BASE_URL = "https://download.cms.gov/nppes/NPI_Files.html"

    try:
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"]
            if (
                "NPPES_Data_Dissemination" in href
                and href.lower().endswith(".zip")
                and "Weekly" not in href
            ):  # Skip weekly updates, get monthly

                if href.startswith("http"):
                    return href
                else:
                    return urljoin(BASE_URL, href)

        return None

    except Exception as e:
        print(f"❌ Failed to get NPPES URL: {e}")
        return None


def download_and_extract_sample(url, sample_rows=50000):
    """Download and extract a sample of NPPES data for testing."""
    print(f"📥 Downloading sample data from: {url}")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Download the file
            zip_path = temp_path / "nppes_data.zip"
            print("⏬ Starting download...")

            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            print(f"📊 Full file size: {total_size / (1024*1024):.1f} MB")

            with open(zip_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if downloaded % (100 * 1024 * 1024) == 0:  # Log every 100MB
                            progress = (
                                (downloaded / total_size * 100) if total_size > 0 else 0
                            )
                            print(f"📈 Download progress: {progress:.1f}%")

            print(f"✅ Downloaded {downloaded / (1024*1024):.1f} MB")

            # Extract the main CSV file
            print("📂 Extracting data...")
            extract_dir = temp_path / "extracted"
            extract_dir.mkdir()

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

                csv_files = list(extract_dir.glob("*.csv"))
                if not csv_files:
                    print("❌ No CSV files found in archive")
                    return None

                # Get the largest CSV file (main provider file)
                main_csv = max(csv_files, key=lambda x: x.stat().st_size)
                print(
                    f"📄 Found main CSV: {main_csv} ({main_csv.stat().st_size / (1024*1024):.1f} MB)"
                )

                # Process a sample of the data
                return process_nppes_sample(main_csv, sample_rows)

    except Exception as e:
        print(f"❌ Download/extract failed: {e}")
        return None


def process_nppes_sample(csv_path, sample_rows=50000):
    """Process a sample of NPPES data to test the filtering logic."""
    print(f"🔬 Processing sample of {sample_rows:,} rows...")
    print(f"💓 Looking for cardiology codes: {', '.join(CARDIOLOGY_TAXONOMY_CODES)}")

    try:
        # Read a sample of the data
        sample_df = pd.read_csv(csv_path, nrows=sample_rows, low_memory=False)
        print(
            f"📊 Sample loaded: {len(sample_df):,} rows, {len(sample_df.columns)} columns"
        )

        # Show key columns
        key_columns = [
            col
            for col in sample_df.columns
            if any(
                keyword in col
                for keyword in [
                    "NPI",
                    "Provider",
                    "Business Practice Location",
                    "Taxonomy Code",
                ]
            )
        ]
        print(f"🔍 Key columns found: {len(key_columns)}")

        # Filter for California providers
        ca_mask = (
            sample_df["Provider Business Practice Location Address State Name"] == "CA"
        )
        ca_providers = sample_df[ca_mask]
        print(f"🌎 California providers in sample: {len(ca_providers):,}")

        if len(ca_providers) == 0:
            print("⚠️ No CA providers in sample")
            return None

        # Check for cardiology taxonomy codes
        taxonomy_columns = [
            col
            for col in sample_df.columns
            if "Healthcare Provider Taxonomy Code" in col
        ]
        print(f"🏥 Taxonomy code columns found: {len(taxonomy_columns)}")

        # Check each cardiology code
        total_cardiology = 0
        cardiology_mask = False

        for code in CARDIOLOGY_TAXONOMY_CODES:
            code_count = 0
            for col in taxonomy_columns:
                if col in ca_providers.columns:
                    col_mask = ca_providers[col] == code
                    cardiology_mask |= col_mask
                    count = col_mask.sum()
                    if count > 0:
                        print(f"   💓 Found {count} providers with {code} in {col}")
                        code_count += count

            if code_count > 0:
                total_cardiology += code_count
                print(f"   ✅ Total for {code}: {code_count} providers")

        cardiology_providers = ca_providers[cardiology_mask]
        print(
            f"🎯 Total CA cardiology providers in sample: {len(cardiology_providers)}"
        )

        if len(cardiology_providers) > 0:
            # Show a sample of the data
            print(f"\n📋 Sample cardiology provider data:")
            display_cols = [
                "NPI",
                "Provider Organization Name (Legal Business Name)",
                "Provider Last Name (Legal Name)",
                "Provider First Name",
                "Provider Business Practice Location Address City Name",
            ]

            # Use available columns
            available_cols = [
                col for col in display_cols if col in cardiology_providers.columns
            ]
            if available_cols:
                sample_display = cardiology_providers[available_cols].head(5)
                for i, row in sample_display.iterrows():
                    row_dict = dict(row)
                    # Clean up the display
                    clean_dict = {
                        k: v for k, v in row_dict.items() if pd.notna(v) and v != ""
                    }
                    print(f"   Provider {i}: {clean_dict}")

            # Check taxonomy codes in the results
            print(f"\n🔬 Taxonomy codes found in cardiology providers:")
            for col in taxonomy_columns:
                if col in cardiology_providers.columns:
                    codes = cardiology_providers[col].dropna().unique()
                    for code in codes:
                        if code in CARDIOLOGY_TAXONOMY_CODES:
                            count = (cardiology_providers[col] == code).sum()
                            print(f"   {code}: {count} providers")

            # Estimate total providers in full dataset
            sample_rate = len(cardiology_providers) / sample_rows
            estimated_total = (
                sample_rate * 8000000
            )  # Roughly 8M total providers in NPPES
            print(
                f"\n📈 Estimated total CA cardiology providers: ~{estimated_total:.0f}"
            )

            return cardiology_providers
        else:
            print("⚠️ No cardiology providers found in sample")

            # Debug: Show some taxonomy codes that are present
            print(f"\n🔍 Sample of taxonomy codes found in CA providers:")
            for col in taxonomy_columns[:3]:  # Check first 3 taxonomy columns
                if col in ca_providers.columns:
                    codes = ca_providers[col].dropna().value_counts().head(5)
                    if len(codes) > 0:
                        print(f"   {col}:")
                        for code, count in codes.items():
                            print(f"     {code}: {count} providers")

            return None

    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return None


def main():
    """Main test function."""
    print("🧪 CMS NPPES Data Collection Test (Updated with Correct Codes)")
    print("=" * 60)

    # Step 1: Get latest file URL
    url = get_latest_nppes_url()
    if not url:
        print("❌ Failed to get NPPES file URL")
        return False

    print(f"✅ Latest file: {url}")
    print()

    # Step 2: Download and process sample
    sample_data = download_and_extract_sample(
        url, sample_rows=200000
    )  # Larger sample for better chance

    if sample_data is not None and len(sample_data) > 0:
        print(
            f"\n🎉 SUCCESS! Found {len(sample_data)} CA cardiology providers in sample"
        )
        print("✅ CMS NPPES data collection is working correctly")

        # Save sample to local file
        output_path = Path("data/raw/cms_nppes_cardiology_sample.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample_data.to_csv(output_path, index=False)
        print(f"💾 Sample saved to: {output_path}")

        return True
    else:
        print("❌ Failed to find cardiology providers in sample")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for full-scale data collection!")
        print("💡 Next steps:")
        print("   1. Configure AWS credentials")
        print("   2. Update main collector with correct taxonomy codes")
        print("   3. Run full data collection with AWS storage")
    else:
        print("\n⚠️ Please check the issues above before proceeding.")
