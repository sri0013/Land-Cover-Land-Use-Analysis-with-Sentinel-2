# Land-Cover-Land-Use-Analysis-with-Sentinel-2
Analyzing land cover and land use changes using Sentinel-2 satellite imagery. NDVI Calculation for multi-year vegetation health, Unsupervised Land Cover Classification , Change Detection between time periods ( 2021 vs 2025), Urban Area Extraction using spectral indices, Visualization of NDVI, classification maps, and change results.


## Download Data

The raw input data of can be downloaded from:

 [Google Drive Link]([https://drive.google.com/your-link](https://drive.google.com/drive/folders/1wHNhRj7kpoR9U4EOCyMhxCf2JfOL9Dc4?usp=drive_link))

After downloading, place the contents(2021,2025,roi,output) into the `data/` folder. 

the output folder looks like  [Google Drive Link]([https://drive.google.com/your-link](https://drive.google.com/drive/folders/1wHNhRj7kpoR9U4EOCyMhxCf2JfOL9Dc4?usp=drive_link)](https://drive.google.com/drive/folders/1rjko3JXvV64uUh1Sy02nnNvGH6sTV333?usp=drive_link)) after running run_all_analyses.py

data/
├── 2021/
│   ├── B2.tif
│   ├── B3.tif
│   ├── B4.tif
│   ├── B8.tif
│   ├── B11.tif
│   └── S2B_MSIL2A_20210707T050659_N0500_R019_T44QKE_20230202T205520.SAFE/
│       └── ... (Sentinel-2 SAFE structure)
├── 2025/
│   ├── B2.tif
│   ├── B3.tif
│   ├── B4.tif
│   ├── B8.tif
│   ├── B11.tif
│   └── S2C_MSIL2A_20250512T050711_N0511_R019_T43QHV_20250512T110716.SAFE/
│       └── ... (Sentinel-2 SAFE structure)
├── output/
│   ├── bui_2021.tif
│   ├── bui_2025.tif
│   ├── change_detection_plot.png
│   ├── changes.tif
│   ├── classification_2021_plot.png
│   ├── classification_2021.tif
│   ├── classification_2025_plot.png
│   ├── classification_2025.tif
│   ├── classification_changes.tif
│   ├── ndvi_2021_plot.png
│   ├── ndvi_2021.tif
│   ├── ndvi_2025_plot.png
│   ├── ndvi_2025.tif
│   ├── ndvi_difference.tif
│   ├── urban_areas_2021.tif
│   ├── urban_areas_2025.tif
│   ├── urban_extraction_2021_plot.png
│   └── urban_extraction_2025_plot.png
└── roi/
    ├── ne_10m_admin_0_countries.shp
    ├── ne_10m_admin_0_countries.shx
    ├── ne_10m_admin_1_states_provinces.dbf
    └── ne_10m_admin_1_states_provinces.prj
