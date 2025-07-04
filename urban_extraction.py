#!/usr/bin/env python3
"""
Urban Area Extraction Script
Extracts urban areas using NDVI thresholds and built-up area indices
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import geopandas as gpd
from rasterio.mask import mask
from rasterio.enums import Resampling
from pymongo import MongoClient
import gridfs

# Connect to MongoDB (adjust URI as needed)
client = MongoClient("mongodb://localhost:27017/")
db = client["geoprocessing_data"]
fs = gridfs.GridFS(db)

def resample_to_match(src_path, match_path):
    with rasterio.open(src_path) as src:
        with rasterio.open(match_path) as match:
            data = src.read(
                out_shape=(
                    src.count,
                    match.height,
                    match.width
                ),
                resampling=Resampling.bilinear
            )[0]
    return data

def calculate_built_up_index(red_band_path, nir_band_path, swir_band_path, output_path):
    """
    Calculate Built-up Index (BUI) using Red, NIR, and SWIR bands
    
    BUI = ((SWIR - NIR) / (SWIR + NIR)) - ((NIR - Red) / (NIR + Red))
    """
    print("Calculating Built-up Index...")
    
    # Read bands
    with rasterio.open(red_band_path) as red_src:
        red = red_src.read(1).astype(np.float32)
        profile = red_src.profile.copy()
    
    with rasterio.open(nir_band_path) as nir_src:
        nir = nir_src.read(1).astype(np.float32)
    
    # Resample SWIR to match NIR shape
    swir = resample_to_match(swir_band_path, nir_band_path).astype(np.float32)
    
    # Calculate NDVI
    ndvi = np.where((nir + red) != 0, (nir - red) / (nir + red), 0)
    
    # Calculate NDBI (Normalized Difference Built-up Index)
    ndbi = np.where((swir + nir) != 0, (swir - nir) / (swir + nir), 0)
    
    # Calculate BUI
    bui = ndbi - ndvi
    
    # Save BUI
    profile.update(dtype=rasterio.float32, count=1, nodata=-9999)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(bui.astype(np.float32), 1)
    
    print(f"Built-up Index saved to: {output_path}")
    return bui, ndvi, ndbi

def extract_urban_areas(ndvi, bui, ndvi_threshold=0.3, bui_threshold=0.1):
    """
    Extract urban areas using NDVI and BUI thresholds
    """
    print("Extracting urban areas...")
    
    # Create urban mask
    urban_mask = np.zeros_like(ndvi, dtype=np.uint8)
    
    # Urban areas: low NDVI and high BUI
    urban_mask[(ndvi < ndvi_threshold) & (bui > bui_threshold)] = 1
    
    # Vegetation areas: high NDVI
    urban_mask[ndvi > 0.4] = 2
    
    # Water areas: very low NDVI and low BUI
    urban_mask[(ndvi < 0.1) & (bui < 0.05)] = 3
    
    # Bare soil: low NDVI and low BUI
    urban_mask[(ndvi < 0.2) & (bui < 0.1) & (urban_mask == 0)] = 4
    
    return urban_mask

def calculate_urban_statistics(urban_mask, pixel_area_m2=100):
    """
    Calculate urban area statistics
    """
    print("Calculating urban statistics...")
    
    unique_classes, counts = np.unique(urban_mask, return_counts=True)
    total_pixels = np.sum(counts)
    
    class_labels = {
        0: 'Unclassified',
        1: 'Urban',
        2: 'Vegetation', 
        3: 'Water',
        4: 'Bare Soil'
    }
    
    print("\nLand Cover Statistics:")
    print("=" * 30)
    
    for class_id, count in zip(unique_classes, counts):
        percentage = (count / total_pixels) * 100
        area_km2 = (count * pixel_area_m2) / 1e6  # Convert to km²
        label = class_labels.get(class_id, f'Class {class_id}')
        print(f"{label}: {count} pixels ({percentage:.1f}%) - {area_km2:.2f} km²")
    
    # Urban area specifically
    urban_pixels = counts[unique_classes == 1][0] if 1 in unique_classes else 0
    urban_percentage = (urban_pixels / total_pixels) * 100
    urban_area_km2 = (urban_pixels * pixel_area_m2) / 1e6
    
    print(f"\nUrban Area Summary:")
    print(f"  Urban pixels: {urban_pixels}")
    print(f"  Urban percentage: {urban_percentage:.1f}%")
    print(f"  Urban area: {urban_area_km2:.2f} km²")
    
    return urban_pixels, urban_percentage, urban_area_km2

def plot_urban_extraction(ndvi, bui, urban_mask, title, output_path=None):
    """
    Plot urban extraction results
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot NDVI
    im1 = ax1.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    ax1.set_title('NDVI')
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, label='NDVI')
    
    # Plot BUI
    im2 = ax2.imshow(bui, cmap='Reds', vmin=-1, vmax=1)
    ax2.set_title('Built-up Index (BUI)')
    ax2.axis('off')
    plt.colorbar(im2, ax=ax2, label='BUI')
    
    # Plot urban mask
    colors = ['#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#8B4513']
    cmap = plt.cm.colors.ListedColormap(colors)
    
    im3 = ax3.imshow(urban_mask, cmap=cmap, vmin=0, vmax=4)
    ax3.set_title('Land Cover Classification')
    ax3.axis('off')
    
    # Create legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#FFFFFF', label='Unclassified'),
        Patch(facecolor='#FF0000', label='Urban'),
        Patch(facecolor='#00FF00', label='Vegetation'),
        Patch(facecolor='#0000FF', label='Water'),
        Patch(facecolor='#8B4513', label='Bare Soil')
    ]
    ax3.legend(handles=legend_elements, loc='upper right')
    
    # Plot urban areas only
    urban_only = np.where(urban_mask == 1, 1, 0)
    im4 = ax4.imshow(urban_only, cmap='Reds', vmin=0, vmax=1)
    ax4.set_title('Urban Areas Only')
    ax4.axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Urban extraction plot saved to: {output_path}")
    
    plt.show()

def save_urban_areas(urban_mask, output_path, profile):
    """
    Save urban areas as a binary raster
    """
    print("Saving urban areas...")
    
    # Create binary urban mask
    urban_binary = np.where(urban_mask == 1, 1, 0).astype(np.uint8)
    
    # Save as raster
    profile.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(urban_binary, 1)
    
    print(f"Urban areas saved to: {output_path}")

def upload_file(filepath):
    with open(filepath, "rb") as f:
        fs.put(f, filename=filepath)

def download_file(filename, out_path):
    file = fs.find_one({"filename": filename})
    if file:
        with open(out_path, "wb") as f:
            f.write(file.read())
        print(f"Downloaded {filename} to {out_path}")
    else:
        print(f"{filename} not found in GridFS.")

def main():
    """
    Main function to extract urban areas
    """
    # Create output directory
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    years = ['2021', '2025']
    
    for year in years:
        print(f"\nProcessing {year}...")
        
        # Define band paths - adjust these based on your actual file names
        red_band = f"data/{year}/B4.tif"      # Red
        nir_band = f"data/{year}/B8.tif"      # NIR
        swir_band = f"data/{year}/B11.tif"    # SWIR (adjust band number if needed)
        
        # Check if files exist
        missing_files = []
        for path in [red_band, nir_band, swir_band]:
            if not Path(path).exists():
                missing_files.append(path)
        
        if missing_files:
            print(f"Warning: Missing files for {year}: {missing_files}")
            print("Skipping urban extraction for this year.")
            continue
        
        # Calculate Built-up Index
        bui_output = f"data/output/bui_{year}.tif"
        bui, ndvi, ndbi = calculate_built_up_index(red_band, nir_band, swir_band, bui_output)
        
        # Extract urban areas
        urban_mask = extract_urban_areas(ndvi, bui)
        
        # Save urban areas
        urban_output = f"data/output/urban_areas_{year}.tif"
        with rasterio.open(red_band) as src:
            profile = src.profile.copy()
        save_urban_areas(urban_mask, urban_output, profile)
        
        # Calculate statistics
        urban_pixels, urban_percentage, urban_area = calculate_urban_statistics(urban_mask)
        
        # Plot results
        plot_urban_extraction(
            ndvi, bui, urban_mask,
            f"Urban Area Extraction {year}",
            f"data/output/urban_extraction_{year}_plot.png"
        )
        
        print(f"\nUrban extraction complete for {year}!")
        print(f"Output files:")
        print(f"  - Built-up Index: {bui_output}")
        print(f"  - Urban areas: {urban_output}")
        print(f"  - Urban area: {urban_area:.2f} km² ({urban_percentage:.1f}%)")

if __name__ == "__main__":
    main() 