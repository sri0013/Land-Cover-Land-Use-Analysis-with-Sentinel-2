#!/usr/bin/env python3
"""
Extract Sentinel-2 Bands Script
Extracts bands from Sentinel-2 SAFE folders and converts to TIF format
"""

import rasterio
import numpy as np
from pathlib import Path
import glob
import os

def extract_bands_from_safe(safe_path, output_dir):
    """
    Extract bands from Sentinel-2 SAFE folder
    """
    print(f"Extracting bands from: {safe_path}")
    
    # Find the granule folder
    granule_path = Path(safe_path) / "GRANULE"
    if not granule_path.exists():
        print(f"Granule folder not found in {safe_path}")
        return False
    
    # Get the first granule folder
    granule_folders = list(granule_path.glob("*"))
    if not granule_folders:
        print(f"No granule folders found in {granule_path}")
        return False
    
    granule_folder = granule_folders[0]
    
    # Define band mappings with resolutions
    band_mappings = {
        'B2': ('B02', '10m'),   # Blue
        'B3': ('B03', '10m'),   # Green
        'B4': ('B04', '10m'),   # Red
        'B8': ('B08', '10m'),   # NIR
        'B11': ('B11', '20m')   # SWIR
    }
    
    # Extract each band
    for output_name, (sentinel_name, resolution) in band_mappings.items():
        img_data_path = granule_folder / "IMG_DATA" / f"R{resolution}"
        
        if not img_data_path.exists():
            print(f"Image data folder not found: {img_data_path}")
            continue
        
        # Find the band file
        pattern = f"*_{sentinel_name}_{resolution}.jp2"
        band_files = list(img_data_path.glob(pattern))
        
        if not band_files:
            print(f"Warning: {sentinel_name} band not found")
            continue
        
        band_file = band_files[0]
        output_file = output_dir / f"{output_name}.tif"
        
        print(f"Converting {band_file.name} to {output_name}.tif")
        
        # Read and write the band
        with rasterio.open(band_file) as src:
            data = src.read(1)
            profile = src.profile.copy()
            
            # Update profile for output
            profile.update(
                driver='GTiff',
                count=1,
                dtype=data.dtype
            )
            
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(data, 1)
        
        print(f"Saved: {output_file}")
    
    return True

def main():
    """
    Main function to extract bands from both years
    """
    years = ['2021', '2025']
    
    for year in years:
        print(f"\nProcessing {year}...")
        
        # Find SAFE folder
        year_dir = Path(f"data/{year}")
        safe_folders = list(year_dir.glob("*.SAFE"))
        
        if not safe_folders:
            print(f"No SAFE folders found in data/{year}/")
            continue
        
        safe_folder = safe_folders[0]
        print(f"Found SAFE folder: {safe_folder.name}")
        
        # Extract bands
        success = extract_bands_from_safe(safe_folder, year_dir)
        
        if success:
            print(f"Band extraction complete for {year}")
        else:
            print(f"Band extraction failed for {year}")
    
    print("\nBand extraction complete!")
    print("You can now run the analysis scripts.")

if __name__ == "__main__":
    main() 