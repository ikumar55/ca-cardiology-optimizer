"""
Test version of the CMS NPPES collector for development without AWS credentials.
"""

import tempfile
from pathlib import Path

from collect_providers import CMSNPPESCollector


class TestCMSCollector:
    """Test version of CMS NPPES collector that works without AWS."""

    def __init__(self):
        """Initialize without AWS helper."""
        pass

    def test_url_discovery(self):
        """Test if we can discover the latest NPPES file URL."""
        print("🔍 Testing CMS NPPES URL discovery...")

        # Create a collector instance without AWS helper
        collector = CMSNPPESCollector.__new__(CMSNPPESCollector)
        url = collector.get_latest_file_url()

        if url:
            print(f"✅ Found latest NPPES file URL: {url}")
            return url
        else:
            print("❌ Failed to find NPPES file URL")
            return None

    def test_small_download(self, url: str, max_size_mb: int = 50):
        """Test downloading a small portion of the file to verify access."""
        print(f"📥 Testing download access (limiting to {max_size_mb}MB)...")

        import requests

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            print(f"📊 Full file size: {total_size / (1024*1024):.1f} MB")

            # Download only a small portion for testing
            max_bytes = max_size_mb * 1024 * 1024

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                downloaded = 0

                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        break

                    tmp_file.write(chunk)
                    downloaded += len(chunk)

                    if downloaded >= max_bytes:
                        print(
                            f"🛑 Stopping download at {downloaded / (1024*1024):.1f} MB for testing"
                        )
                        break

                print(
                    f"✅ Successfully downloaded {downloaded / (1024*1024):.1f} MB to {tmp_file.name}"
                )
                return tmp_file.name

        except Exception as e:
            print(f"❌ Download test failed: {e}")
            return None

    def run_tests(self):
        """Run all tests."""
        print("🧪 Starting CMS NPPES Data Collection Tests")
        print("=" * 50)

        # Test 1: URL Discovery
        url = self.test_url_discovery()
        if not url:
            return False

        print()

        # Test 2: Download Access
        downloaded_file = self.test_small_download(url)
        if not downloaded_file:
            return False

        print()

        # Test 3: File Inspection
        print("📁 Inspecting downloaded file...")
        try:
            import zipfile

            with zipfile.ZipFile(downloaded_file, "r") as zip_ref:
                file_list = zip_ref.namelist()
                print(f"✅ ZIP file contains {len(file_list)} files:")

                for file_name in file_list[:5]:  # Show first 5 files
                    print(f"   📄 {file_name}")

                if len(file_list) > 5:
                    print(f"   ... and {len(file_list) - 5} more files")

            # Cleanup
            Path(downloaded_file).unlink()
            print("🧹 Cleaned up test file")

        except Exception as e:
            print(f"❌ File inspection failed: {e}")
            return False

        print()
        print("✅ All tests passed! CMS NPPES data collection is ready.")
        return True


def main():
    """Run the tests."""
    test_collector = TestCMSCollector()
    success = test_collector.run_tests()

    if success:
        print("\n🎉 Ready to proceed with full data collection!")
        print("💡 Next steps:")
        print("   1. Configure AWS credentials")
        print("   2. Run full data collection with AWS storage")
    else:
        print("\n❌ Tests failed. Please check the issues above.")


if __name__ == "__main__":
    main()
