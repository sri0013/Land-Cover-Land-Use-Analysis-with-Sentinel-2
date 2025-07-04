#!/usr/bin/env python3
"""
Change Detection Script
Detects changes between 2021 and 2025 using NDVI difference and classification comparison
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import box
import shapely

def calculate_ndvi_difference(ndvi_2021_path, ndvi_2025_path, output_path):
    """
    Calculate NDVI difference between two years
    """
    print("Calculating NDVI difference...")
    
    # Read NDVI rasters
    with rasterio.open(ndvi_2021_path) as src_2021:
        ndvi_2021 = src_2021.read(1)
        profile = src_2021.profile.copy()
    
    with rasterio.open(ndvi_2025_path) as src_2025:
        ndvi_2025 = src_2025.read(1)
    
    # Calculate difference
    ndvi_diff = ndvi_2025 - ndvi_2021
    
    # Save difference
    profile.update(dtype=rasterio.float32, count=1, nodata=-9999)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi_diff.astype(np.float32), 1)
    
    print(f"NDVI difference saved to: {output_path}")
    return ndvi_diff

def classify_changes(ndvi_diff, threshold=0.1):
    """
    Classify changes based on NDVI difference
    """
    print("Classifying changes...")
    
    # Create change classification
    changes = np.zeros_like(ndvi_diff, dtype=np.uint8)
    
    # Significant decrease (deforestation, urbanization)
    changes[ndvi_diff < -threshold] = 1
    
    # Significant increase (reforestation, vegetation growth)
    changes[ndvi_diff > threshold] = 2
    
    # No significant change
    changes[(ndvi_diff >= -threshold) & (ndvi_diff <= threshold)] = 3
    
    return changes

def compare_classifications(class_2021_path, class_2025_path, output_path):
    """
    Compare land cover classifications between years
    """
    print("Comparing classifications...")
    
    # Read classification rasters
    with rasterio.open(class_2021_path) as src_2021:
        class_2021 = src_2021.read(1)
        profile = src_2021.profile.copy()
    
    with rasterio.open(class_2025_path) as src_2025:
        class_2025 = src_2025.read(1)
    
    # Create change matrix
    change_matrix = np.zeros_like(class_2021, dtype=np.uint8)
    
    # Identify pixels that changed class
    change_matrix[class_2021 != class_2025] = 1
    
    # Save change matrix
    profile.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(change_matrix, 1)
    
    print(f"Classification change matrix saved to: {output_path}")
    return change_matrix

def plot_changes(ndvi_diff, changes, title, output_path=None):
    """
    Plot change detection results
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot NDVI difference
    im1 = ax1.imshow(ndvi_diff, cmap='RdBu', vmin=-0.5, vmax=0.5)
    ax1.set_title('NDVI Difference (2025 - 2021)')
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, label='NDVI Difference')
    
    # Plot change classification
    colors = ['#FF0000', '#00FF00', '#808080']  # Red: decrease, Green: increase, Gray: no change
    cmap = plt.cm.colors.ListedColormap(colors)
    
    im2 = ax2.imshow(changes, cmap=cmap, vmin=1, vmax=3)
    ax2.set_title('Change Classification')
    ax2.axis('off')
    
    # Create custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#FF0000', label='Decrease'),
        Patch(facecolor='#00FF00', label='Increase'),
        Patch(facecolor='#808080', label='No Change')
    ]
    ax2.legend(handles=legend_elements, loc='upper right')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Change detection plot saved to: {output_path}")
    
    plt.show()

def calculate_change_statistics(ndvi_diff, changes, change_matrix):
    """
    Calculate and print change statistics
    """
    print("\nChange Detection Statistics:")
    print("=" * 40)
    
    # NDVI change statistics
    print(f"NDVI Difference Statistics:")
    print(f"  Min: {np.min(ndvi_diff):.3f}")
    print(f"  Max: {np.max(ndvi_diff):.3f}")
    print(f"  Mean: {np.mean(ndvi_diff):.3f}")
    print(f"  Std: {np.std(ndvi_diff):.3f}")
    
    # Change classification statistics
    unique_changes, counts_changes = np.unique(changes, return_counts=True)
    total_pixels = np.sum(counts_changes)
    
    print(f"\nChange Classification:")
    change_labels = {1: 'Decrease', 2: 'Increase', 3: 'No Change'}
    for change_id, count in zip(unique_changes, counts_changes):
        percentage = (count / total_pixels) * 100
        label = change_labels.get(change_id, f'Class {change_id}')
        print(f"  {label}: {count} pixels ({percentage:.1f}%)")
    
    # Classification change statistics
    if change_matrix is not None:
        changed_pixels = np.sum(change_matrix)
        total_pixels_class = change_matrix.size
        change_percentage = (changed_pixels / total_pixels_class) * 100
        print(f"\nClassification Changes:")
        print(f"  Changed pixels: {changed_pixels} ({change_percentage:.1f}%)")
        print(f"  Unchanged pixels: {total_pixels_class - changed_pixels} ({100-change_percentage:.1f}%)")

def main():
    """
    Main function to perform change detection
    """
    # Create output directory
    Path("data/output").mkdir(parents=True, exist_ok=True)
    
    # Check if NDVI files exist
    ndvi_2021_path = "data/output/ndvi_2021.tif"
    ndvi_2025_path = "data/output/ndvi_2025.tif"
    
    if not Path(ndvi_2021_path).exists() or not Path(ndvi_2025_path).exists():
        print("Warning: NDVI files not found. Run calculate_ndvi.py first.")
        return
    
    # Check if classification files exist
    class_2021_path = "data/output/classification_2021.tif"
    class_2025_path = "data/output/classification_2025.tif"
    
    # Calculate NDVI difference
    ndvi_diff_path = "data/output/ndvi_difference.tif"
    ndvi_diff = calculate_ndvi_difference(ndvi_2021_path, ndvi_2025_path, ndvi_diff_path)
    
    # Classify changes
    changes = classify_changes(ndvi_diff, threshold=0.1)
    changes_path = "data/output/changes.tif"
    
    # Save changes
    with rasterio.open(ndvi_2021_path) as src:
        profile = src.profile.copy()
    profile.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(changes_path, 'w', **profile) as dst:
        dst.write(changes, 1)
    
    # Compare classifications if available
    change_matrix = None
    if Path(class_2021_path).exists() and Path(class_2025_path).exists():
        change_matrix_path = "data/output/classification_changes.tif"
        change_matrix = compare_classifications(class_2021_path, class_2025_path, change_matrix_path)
    
    # Plot results
    plot_changes(
        ndvi_diff, 
        changes, 
        "Change Detection: 2021-2025", 
        "data/output/change_detection_plot.png"
    )
    
    # Calculate and print statistics
    calculate_change_statistics(ndvi_diff, changes, change_matrix)
    
    print(f"\nChange detection complete!")
    print(f"Output files:")
    print(f"  - NDVI difference: {ndvi_diff_path}")
    print(f"  - Change classification: {changes_path}")
    if change_matrix is not None:
        print(f"  - Classification changes: data/output/classification_changes.tif")

if __name__ == "__main__":
    main() 