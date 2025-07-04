#!/usr/bin/env python3
"""
Land Cover Classification Script
Performs unsupervised classification using K-means clustering
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import box

def prepare_classification_data(band_paths, roi_path=None, window_size=100):
    """
    Prepare data for classification by stacking a small window from each band
    """
    print("Preparing classification data...")

    # Always use a small window from the center
    bands_data = []
    profile = None

    # Open the first band to get shape
    with rasterio.open(band_paths[0]) as src:
        height, width = src.height, src.width
        center_y = height // 2
        center_x = width // 2
        half_win = window_size // 2
        y1 = max(center_y - half_win, 0)
        y2 = min(center_y + half_win, height)
        x1 = max(center_x - half_win, 0)
        x2 = min(center_x + half_win, width)
        window = rasterio.windows.Window(x1, y1, x2 - x1, y2 - y1)
        profile = src.profile.copy()
        profile.update(height=(y2 - y1), width=(x2 - x1))

    for band_path in band_paths:
        with rasterio.open(band_path) as src:
            band = src.read(1, window=window)
            bands_data.append(band)

    stacked = np.stack(bands_data, axis=0)

    # Reshape for classification (pixels x bands)
    n_bands, height, width = stacked.shape
    reshaped = stacked.reshape(n_bands, -1).T

    # Remove no-data pixels
    valid_pixels = ~np.any(np.isnan(reshaped) | (reshaped == 0), axis=1)
    valid_data = reshaped[valid_pixels]

    print(f"Data shape: {valid_data.shape}")
    return valid_data, valid_pixels, (height, width), profile

def perform_classification(data, n_clusters=5):
    """
    Perform K-means classification
    """
    print(f"Performing K-means classification with {n_clusters} clusters...")
    
    # Standardize the data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data_scaled)
    
    return labels, kmeans, scaler

def create_classification_map(labels, valid_pixels, original_shape, output_path, profile):
    """
    Create classification map and save as raster
    """
    print("Creating classification map...")
    
    # Create full map
    full_map = np.zeros(original_shape[0] * original_shape[1], dtype=np.uint8)
    full_map[valid_pixels] = labels + 1  # Add 1 to avoid 0 (no-data)
    
    # Reshape to original dimensions
    classification_map = full_map.reshape(original_shape)
    
    # Save as raster
    profile.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(classification_map.astype(np.uint8), 1)
    
    print(f"Classification map saved to: {output_path}")
    return classification_map

def plot_classification(classification_map, title, output_path=None):
    """
    Plot classification results
    """
    plt.figure(figsize=(12, 8))
    
    # Create custom colormap for land cover classes
    colors = ['#8B4513', '#228B22', '#32CD32', '#FFD700', '#C0C0C0', '#000080']
    cmap = plt.cm.colors.ListedColormap(colors[:len(np.unique(classification_map))])
    
    im = plt.imshow(classification_map, cmap=cmap)
    plt.colorbar(im, label='Land Cover Class')
    plt.title(title)
    plt.axis('off')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Classification plot saved to: {output_path}")
    
    plt.show()

def main():
    """
    Main function to perform land cover classification
    """
    # Create output directory
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Define band paths (adjust based on your data)
    years = ['2021', '2025']
    
    for year in years:
        print(f"\nProcessing {year}...")
        
        # Define band paths - adjust these based on your actual file names
        band_paths = [
            f"data/{year}/B2.tif",  # Blue
            f"data/{year}/B3.tif",  # Green
            f"data/{year}/B4.tif",  # Red
            f"data/{year}/B8.tif",  # NIR
        ]
        
        # Check if files exist
        missing_files = [path for path in band_paths if not Path(path).exists()]
        if missing_files:
            print(f"Warning: Missing files for {year}: {missing_files}")
            continue
        
        # Force windowed processing: do not use ROI
        roi_path = None
        
        # Prepare data (process only a small window)
        data, valid_pixels, original_shape, profile = prepare_classification_data(
            band_paths, roi_path, window_size=100
        )
        print("Data loaded, shape:", data.shape)
        
        if data is None or len(data) == 0:
            print(f"No valid data for {year}. Skipping...")
            continue
        
        # Perform classification
        labels, kmeans, scaler = perform_classification(data, n_clusters=5)
        
        # Create classification map
        output_path = f"data/output/classification_{year}.tif"
        classification_map = create_classification_map(
            labels, valid_pixels, original_shape, output_path, profile
        )
        
        # Plot results
        plot_classification(
            classification_map, 
            f"Land Cover Classification {year}", 
            f"data/output/classification_{year}_plot.png"
        )
        
        # Print class statistics
        unique, counts = np.unique(labels, return_counts=True)
        print(f"Class distribution for {year}:")
        for class_id, count in zip(unique, counts):
            percentage = (count / len(labels)) * 100
            print(f"  Class {class_id + 1}: {count} pixels ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 