#!/usr/bin/env python3
"""
Master Script for LULC Analysis
Runs all analyses: NDVI, Classification, Change Detection, and Urban Extraction
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """
    Run a Python script and handle errors
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Script {script_name} not found!")
        return False

def check_dependencies():
    """
    Check if required packages are installed
    """
    print("Checking dependencies...")
    
    required_packages = [
        'rasterio', 'numpy', 'matplotlib', 'geopandas', 
        'sklearn', 'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}: OK")
        except ImportError:
            missing_packages.append(package)
            print(f"  {package}: MISSING")
    
    if missing_packages:
        print(f"\nMissing packages: {missing_packages}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("All dependencies are installed!")
    return True

def check_data_files():
    """
    Check if required data files exist
    """
    print("\nChecking data files...")
    
    years = ['2021', '2025']
    required_bands = ['B2', 'B3', 'B4', 'B8']  # Basic bands
    optional_bands = ['B11']  # SWIR for urban extraction
    
    missing_files = []
    
    for year in years:
        year_path = Path(f"data/{year}")
        if not year_path.exists():
            print(f"  data/{year}/: MISSING")
            missing_files.append(f"data/{year}/")
            continue
        
        print(f"  data/{year}/: OK")
        
        # Check required bands
        for band in required_bands:
            band_path = year_path / f"{band}.tif"
            if band_path.exists():
                print(f"    {band}.tif: OK")
            else:
                print(f"    {band}.tif: MISSING")
                missing_files.append(str(band_path))
        
        # Check optional bands
        for band in optional_bands:
            band_path = year_path / f"{band}.tif"
            if band_path.exists():
                print(f"    {band}.tif: OK (optional)")
            else:
                print(f"    {band}.tif: MISSING (optional)")
    
    # Check ROI
    roi_path = Path("data/roi")
    if roi_path.exists() and any(roi_path.glob("*.shp")):
        print("  data/roi/: OK (shapefile found)")
    else:
        print("  data/roi/: MISSING or no shapefile")
        missing_files.append("data/roi/ (shapefile)")
    
    if missing_files:
        print(f"\nMissing files: {len(missing_files)}")
        print("Some analyses may be skipped.")
        return False
    
    print("All required data files found!")
    return True

def main():
    """
    Main function to run all analyses
    """
    print("LULC Analysis Pipeline")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        return
    
    # Check data files
    data_ok = check_data_files()
    
    # Create output directory
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Define analysis scripts and their descriptions
    analyses = [
        ("calculate_ndvi.py", "NDVI Calculation"),
        ("land_cover_classification.py", "Land Cover Classification"),
        ("change_detection.py", "Change Detection"),
        ("urban_extraction.py", "Urban Area Extraction")
    ]
    
    # Run each analysis
    results = {}
    
    for script, description in analyses:
        success = run_script(script, description)
        results[description] = success
        
        if not success:
            print(f"\nWarning: {description} failed. Continuing with next analysis...")
    
    # Summary
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(results.values())
    total = len(results)
    
    for description, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"{description}: {status}")
    
    print(f"\nOverall: {successful}/{total} analyses completed successfully")
    
    if successful == total:
        print("\nAll analyses completed! Check the data/output/ folder for results.")
    else:
        print(f"\n{total - successful} analysis(es) failed. Check the error messages above.")
    
    print(f"\nOutput files are saved in: data/output/")
    print("Generated files include:")
    print("  - NDVI rasters and plots")
    print("  - Land cover classification maps")
    print("  - Change detection results")
    print("  - Urban area extractions")

if __name__ == "__main__":
    main() 