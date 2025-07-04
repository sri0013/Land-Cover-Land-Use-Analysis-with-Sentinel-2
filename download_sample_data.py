#!/usr/bin/env python3
"""
Sample Data Download Script for LULC Project
This script helps download sample satellite data for testing
"""

import os
import requests
import zipfile
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.mask import mask

def create_sample_data_structure():
    """Create the required folder structure"""
    folders = [
        'data/2021',
        'data/2025', 
        'data/roi',
        'data/output'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f" Created folder: {folder}")

def download_sample_roi():
    """Download a sample ROI shapefile"""
    # Sample ROI URL (you can replace with your own)
    roi_url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip"
    
    try:
        print(" Downloading sample ROI...")
        response = requests.get(roi_url, stream=True)
        response.raise_for_status()
        
        # Save to roi folder
        roi_file = "data/roi/sample_countries.zip"
        with open(roi_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract
        with zipfile.ZipFile(roi_file, 'r') as zip_ref:
            zip_ref.extractall("data/roi/")
        
        print(" Sample ROI downloaded and extracted")
        
    except Exception as e:
        print(f"Error downloading ROI: {e}")
        print("You can manually download a shapefile from:")
        print("   - https://gadm.org/")
        print("   - https://www.naturalearthdata.com/")

def create_sample_raster_data():
    """Create sample raster data for testing"""
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    
    print("Creating sample raster data...")
    
    # Create sample data
    height, width = 100, 100
    
    # Sample bands (simulated satellite data)
    bands = {
        'B2': np.random.randint(0, 255, (height, width), dtype=np.uint8),  # Blue
        'B3': np.random.randint(0, 255, (height, width), dtype=np.uint8),  # Green  
        'B4': np.random.randint(0, 255, (height, width), dtype=np.uint8),  # Red
        'B8': np.random.randint(0, 255, (height, width), dtype=np.uint8)   # NIR
    }
    
    # Create geotransform (sample coordinates)
    bounds = (23.0, 77.0, 23.5, 77.5)  # Sample bounds for Bhopal area
    transform = from_bounds(*bounds, width, height)
    
    # Save each band
    for year in ['2021', '2025']:
        for band_name, data in bands.items():
            output_path = f"data/{year}/{band_name}.tif"
            
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=height,
                width=width,
                count=1,
                dtype=data.dtype,
                crs='EPSG:4326',
                transform=transform
            ) as dst:
                dst.write(data, 1)
    
    print("Sample raster data created")

def main():
    """Main function to set up sample data"""
    print("Setting up sample data for LULC Project...")
    print("=" * 50)
    
    # Create folder structure
    create_sample_data_structure()
    
    # Download sample ROI
    download_sample_roi()
    
    # Create sample raster data
    try:
        create_sample_raster_data()
    except ImportError:
        print("Rasterio not available. Install with: pip install rasterio")
        print("You can manually add satellite data to the data/ folders")
    
    print("=" * 50)
    print("Sample data setup complete!")
    print("\n Your project structure:")
    print("data/")
    print("├── 2021/     # Add your 2021 satellite imagery here")
    print("├── 2025/     # Add your 2025 satellite imagery here")
    print("├── roi/      # Add your region of interest shapefile here")
    print("└── output/   # Generated results will be saved here")
    
    print("\n Next steps:")
    print("1. Download real satellite data from:")
    print("   - Sentinel-2: https://scihub.copernicus.eu/")
    print("   - Landsat: https://earthexplorer.usgs.gov/")
    print("2. Place the data in the appropriate folders")
    print("3. Run your Jupyter notebook: jupyter notebook")

    # Read your ROI shapefile
    roi = gpd.read_file('data/roi/your_shapefile.shp')
    print(f"Shapefile contains {len(roi)} features")
    print(roi.head())

    # Plot the shapefile
    fig, ax = plt.subplots(figsize=(10, 8))
    roi.plot(ax=ax)
    plt.title('Region of Interest')
    plt.show()

    # Read a satellite band
    with rasterio.open('data/2021/B2.tif') as src:
        band = src.read(1)
        plt.imshow(band, cmap='gray')
        plt.title('2021 Band 2 (Blue)')
        plt.colorbar()
        plt.show()

    # Clip raster to ROI
    clipped, transform = mask(src, roi.geometry, crop=True)
    
    # Save clipped raster
    with rasterio.open('data/output/clipped_2021_B2.tif', 'w',
                      driver='GTiff', height=clipped.shape[1], width=clipped.shape[2],
                      count=1, dtype=clipped.dtype, crs=src.crs, transform=transform) as dst:
        dst.write(clipped)

if __name__ == "__main__":
    main() 