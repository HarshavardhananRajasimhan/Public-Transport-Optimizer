"""
Download and extract GTFS data from Delhi Open Transit Data portal
"""

import requests
import zipfile
import os
from pathlib import Path

GTFS_STATIC_URL = "https://otd.delhi.gov.in/data/static/GTFS.zip"
GTFS_DATA_DIR = Path(__file__).parent.parent / "gtfs_data"

def download_gtfs_data(force=False):
    """
    Download GTFS static data from Delhi Open Transit Data
    
    Args:
        force: If True, re-download even if data exists
    
    Returns:
        Path to extracted GTFS data directory
    """
    GTFS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = GTFS_DATA_DIR / "GTFS.zip"
    
    # Check if data already exists
    required_files = ['routes.txt', 'stops.txt', 'trips.txt', 'stop_times.txt']
    if not force and all((GTFS_DATA_DIR / f).exists() for f in required_files):
        print(f"✓ GTFS data already exists in {GTFS_DATA_DIR}")
        return GTFS_DATA_DIR
    
    print(f"Downloading GTFS data from {GTFS_STATIC_URL}...")
    
    try:
        response = requests.get(GTFS_STATIC_URL, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save zip file
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Extract zip file
        print("Extracting GTFS files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(GTFS_DATA_DIR)
        
        # Remove zip file
        zip_path.unlink()
        
        # List extracted files
        files = list(GTFS_DATA_DIR.glob('*.txt'))
        print(f"✓ Extracted {len(files)} GTFS files:")
        for f in sorted(files):
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.1f} KB)")
        
        return GTFS_DATA_DIR
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading GTFS data: {e}")
        print("\nAlternative: Download manually from https://otd.delhi.gov.in/data/static/")
        print(f"and extract to: {GTFS_DATA_DIR}")
        raise
    except Exception as e:
        print(f"✗ Error extracting GTFS data: {e}")
        raise

if __name__ == "__main__":
    # Test the downloader
    try:
        data_dir = download_gtfs_data()
        print(f"\n✓ GTFS data ready at: {data_dir}")
    except Exception as e:
        print(f"\n✗ Failed: {e}")
