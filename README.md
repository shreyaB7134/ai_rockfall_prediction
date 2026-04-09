# Rockfall Prediction System - Multimodal ML Pipeline

A comprehensive geospatial AI system for predicting rockfall risk in open-pit mines using multimodal data including terrain, climate, and vegetation indices.

## Overview

This system processes geospatial raster data to create three types of machine learning inputs:
- **Tabular Data**: Pixel-wise terrain and climate features
- **Image Data**: NDVI patches for CNN processing  
- **Temporal Data**: Derived rainfall and temperature sequences

## Features

- **Automated Data Loading**: Loads and aligns GeoTIFF files from multiple regions
- **Raster Processing**: Handles resampling and alignment of mismatched rasters
- **Multimodal Feature Extraction**: Creates tabular, image, and temporal datasets
- **Data Validation**: Comprehensive quality checks and visualization
- **Scalable Pipeline**: Processes multiple regions simultaneously

## Supported Data Types

| Data Type | Format | Description |
|-----------|--------|-------------|
| DEM | GeoTIFF | Digital Elevation Model (terrain height) |
| Slope | GeoTIFF | Terrain slope angle |
| Rainfall | GeoTIFF | Precipitation data |
| Temperature | GeoTIFF | Surface temperature |
| NDVI | GeoTIFF | Normalized Difference Vegetation Index |

## Installation

1. Clone or download the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure your data is organized as:
```
datasets/
  korba/
    DEM_Korba.tif
    NDVI_Korba_2022.tif
    Rainfall_Korba_2022.tif
    Slope_Korba.tif
    Temperature_Korba_2022.tif
  talcher_data/
    DEM_Talcher.tif
    NDVI_Talcher_2022.tif
    Rainfall_Talcher_2022.tif
    Slope_Talcher.tif
    Temperature_Talcher_2022.tif
```

## Quick Start

### Run the Complete Pipeline

```python
from rockfall_pipeline import RockfallDataPipeline

# Initialize and run pipeline
pipeline = RockfallDataPipeline(data_dir="datasets")
processed_data = pipeline.run_complete_pipeline(patch_size=32)

# Save results
pipeline.save_processed_data(processed_data)
```

### Generate Visualizations

```python
from data_visualizer import RockfallDataVisualizer

# Create visualizations
visualizer = RockfallDataVisualizer(processed_data)
visualizer.create_all_visualizations()
```

## Pipeline Components

### Step 1: Data Loading
- Automatically discovers regions and data files
- Loads all GeoTIFF files using rasterio
- Extracts metadata (CRS, transform, nodata values)

### Step 2: Raster Alignment
- Checks if all rasters have matching resolution and extent
- Automatically resamples mismatched rasters to match DEM
- Uses bilinear resampling for continuous data

### Step 3: Tabular Data Creation
Extracts pixel-wise features:
```
lat, lon, elevation, slope, rainfall, temperature, ndvi
```
- Converts pixel coordinates to geographic coordinates
- Removes invalid pixels (NaN, nodata values)
- Creates clean dataset for ML models

### Step 4: Image Data (CNN Input)
- Extracts 32x32 pixel NDVI patches
- Each patch corresponds to a center pixel location
- Patches stored as numpy arrays for deep learning

### Step 5: Temporal Features
Creates derived temporal features:
- `rainfall_3day`: 3-day cumulative rainfall
- `rainfall_7day`: 7-day cumulative rainfall  
- `temperature_mean`: Mean temperature
- `rainfall_intensity`: High rainfall indicator
- `temperature_stress`: High temperature indicator

## Output Structure

The pipeline generates the following outputs:

### Tabular Data
- `processed_data/tabular_korba.csv`
- `processed_data/tabular_talcher.csv`

### Image Data
- `processed_data/ndvi_patches_korba.npz`
- `processed_data/ndvi_patches_talcher.npz`
- `processed_data/patch_centers_korba.npz`
- `processed_data/patch_centers_talcher.npz`

### Temporal Data
- `processed_data/temporal_korba.npz`
- `processed_data/temporal_talcher.npz`

### Visualizations
- `visualizations/korba/` - All plots for Korba region
- `visualizations/talcher_data/` - All plots for Talcher region

## Data Quality Reports

The system automatically generates comprehensive quality reports including:
- Data completeness statistics
- Feature distributions and correlations
- Memory usage analysis
- Valid pixel percentages

## Advanced Usage

### Custom Patch Sizes

```python
# Use different patch sizes for CNN
processed_data = pipeline.run_complete_pipeline(patch_size=64)
```

### Manual Data Processing

```python
# Load data only
pipeline.load_all_rasters()

# Check alignment
is_aligned = pipeline.check_alignment()
if not is_aligned:
    pipeline.resample_to_match()

# Extract specific components
tabular_data = pipeline.create_tabular_dataset()
patch_data = pipeline.extract_ndvi_patches(patch_size=32)
temporal_data = pipeline.create_temporal_features()
```

### Integration with ML Models

```python
# Access processed data for ML
for region in processed_data['regions']:
    # Tabular data for traditional ML
    X_tabular = processed_data['tabular'][region][['elevation', 'slope', 'rainfall', 'temperature', 'ndvi']]
    
    # Image data for CNN
    X_images = processed_data['patches'][region]['patches']
    
    # Temporal features
    temporal_features = processed_data['temporal'][region]
```

## Performance Considerations

- **Memory Usage**: Large rasters may require significant RAM
- **Processing Time**: Resampling and patch extraction are computationally intensive
- **Storage**: Processed data can be several GB for large regions

### Optimization Tips
1. Use appropriate patch sizes (32x32 is usually optimal)
2. Consider sampling for very large datasets
3. Use Dask for out-of-core processing with massive datasets

## Troubleshooting

### Common Issues

**Alignment Errors**
- Ensure all rasters have the same CRS
- Check for missing nodata values
- Verify file naming conventions

**Memory Issues**
- Reduce patch size
- Process one region at a time
- Use sampling for large areas

**Missing Data**
- Verify file paths and names
- Check for corrupted GeoTIFF files
- Ensure valid nodata values

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "File not found" | Incorrect file naming | Check naming convention in README |
| "Rasters have different shapes" | Misaligned data | Run resampling step |
| "No valid pixels" | All data is nodata | Check data quality and CRS |

## System Requirements

- **Python**: 3.8+
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: 10GB+ free space
- **GPU**: Optional (for deep learning models)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this system in your research, please cite:

```
Rockfall Prediction System - Multimodal ML Pipeline
Geospatial AI System, 2026
```

## Support

For questions and support:
- Check the troubleshooting section
- Review the code documentation
- Create an issue on the repository

---

**Note**: This system is designed for research and educational purposes. For production use, additional validation and testing may be required.
