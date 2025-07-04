#!/usr/bin/env python3
"""
NDVI Calculation Script
Calculates NDVI from satellite imagery using Red and NIR bands
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import geopandas as gpd

def calculate_ndvi(red_band_path, nir_band_path, output_path):
    """
    Calculate NDVI from Red and NIR bands
    
    NDVI = (NIR - Red) / (NIR + Red)
    """
    print(f"Calculating NDVI...")
    
    # Read Red band (B4 for Sentinel-2, B4 for Landsat)
    with rasterio.open(red_band_path) as red_src:
        red = red_src.read(1).astype(np.float32)
        profile = red_src.profile.copy()
    
    # Read NIR band (B8 for Sentinel-2, B5 for Landsat)
    with rasterio.open(nir_band_path) as nir_src:
        nir = nir_src.read(1).astype(np.float32)
    
    # Calculate NDVI
    ndvi = np.where((nir + red) != 0, (nir - red) / (nir + red), 0)
    
    # Save NDVI
    profile.update(dtype=rasterio.float32, count=1, nodata=-9999)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi.astype(np.float32), 1)
    
    print(f"NDVI saved to: {output_path}")
    return ndvi

def plot_ndvi(ndvi, title, output_path=None):
    """Plot NDVI with colorbar"""
    plt.figure(figsize=(12, 8))
    im = plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(im, label='NDVI')
    plt.title(title)
    plt.axis('off')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"NDVI plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main function to calculate NDVI for both years"""
    
    # Create output directory
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Define band paths (adjust based on your data)
    years = ['2021', '2025']
    
    for year in years:
        print(f"\nProcessing {year}...")
        
        # Adjust these paths based on your actual file names
        red_band = f"data/{year}/B4.tif"  # Red band
        nir_band = f"data/{year}/B8.tif"  # NIR band
        
        # Check if files exist
        if not Path(red_band).exists() or not Path(nir_band).exists():
            print(f"Warning: Missing bands for {year}. Skipping...")
            continue
        
        # Calculate NDVI
        ndvi_output = f"data/output/ndvi_{year}.tif"
        ndvi = calculate_ndvi(red_band, nir_band, ndvi_output)
        
        # Plot NDVI
        plot_ndvi(ndvi, f"NDVI {year}", f"data/output/ndvi_{year}_plot.png")
        
        # Print statistics
        print(f"NDVI Statistics for {year}:")
        print(f"  Min: {np.min(ndvi):.3f}")
        print(f"  Max: {np.max(ndvi):.3f}")
        print(f"  Mean: {np.mean(ndvi):.3f}")
        print(f"  Std: {np.std(ndvi):.3f}")

    # Check raster CRS and bounds
    with rasterio.open(f"data/{years[0]}/B2.tif") as src:
        print("Raster CRS:", src.crs)
        print("Raster bounds:", src.bounds)

    # Check shapefile CRS and bounds
    roi = gpd.read_file('data/roi/ne_10m_admin_0_countries.shp')
    print("Shapefile CRS:", roi.crs)
    print("Shapefile bounds:", roi.total_bounds)

    with rasterio.open('data/2021/B2.tif') as src:
        raster_crs = src.crs

    roi = gpd.read_file('data/roi/ne_10m_admin_0_countries.shp')
    if roi.crs != raster_crs:
        roi = roi.to_crs(raster_crs)
        print("Reprojected ROI to match raster CRS.")

    print("Raster bounds:", src.bounds)
    print("ROI bounds:", roi.total_bounds)

if __name__ == "__main__":
    main() 