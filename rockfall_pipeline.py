"""
Rockfall Prediction System - Multimodal ML Pipeline
====================================================

This pipeline processes geospatial data for rockfall prediction using:
- Tabular data (terrain + climate features)
- Image data (NDVI patches for CNN)
- Temporal data (rainfall & temperature sequences)

Author: Geospatial AI System
Date: 2026
"""

import os
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import geopandas as gpd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class RockfallDataPipeline:
    """
    Complete pipeline for processing multimodal geospatial data for rockfall prediction
    """
    
    def __init__(self, data_dir="datasets"):
        """
        Initialize the pipeline
        
        Args:
            data_dir (str): Path to datasets directory containing region folders
        """
        self.data_dir = Path(data_dir)
        self.regions = []
        self.raster_data = {}
        self.metadata = {}
        
        # Find all regions (subdirectories)
        for item in self.data_dir.iterdir():
            if item.is_dir():
                self.regions.append(item.name)
        
        print(f"Found regions: {self.regions}")

    @staticmethod
    def _minmax_normalize(series, eps=1e-12):
        s = pd.to_numeric(series, errors='coerce')
        smin = s.min(skipna=True)
        smax = s.max(skipna=True)
        denom = (smax - smin)
        if pd.isna(smin) or pd.isna(smax):
            return pd.Series(np.nan, index=series.index, dtype='float64')
        if abs(denom) < eps:
            return pd.Series(0.0, index=series.index, dtype='float64')
        return (s - smin) / denom

    def add_fs_proxy_labels(self, df, create_multiclass=True, eps=1e-12):
        df_out = df.copy()

        elevation_col = 'elevation' if 'elevation' in df_out.columns else ('dem' if 'dem' in df_out.columns else None)
        slope_col = 'slope' if 'slope' in df_out.columns else None
        rainfall_col = 'rainfall' if 'rainfall' in df_out.columns else None
        ndvi_col = 'ndvi' if 'ndvi' in df_out.columns else None

        missing = [name for name, col in [('elevation', elevation_col), ('slope', slope_col), ('rainfall', rainfall_col), ('ndvi', ndvi_col)] if col is None]
        if missing:
            raise KeyError(f"Missing required columns for FS labeling: {missing}")

        df_out['slope_norm'] = self._minmax_normalize(df_out[slope_col], eps=eps)
        df_out['rainfall_norm'] = self._minmax_normalize(df_out[rainfall_col], eps=eps)
        df_out['ndvi_norm'] = self._minmax_normalize(df_out[ndvi_col], eps=eps)
        df_out['elevation_norm'] = self._minmax_normalize(df_out[elevation_col], eps=eps)

        numerator = 0.4 * df_out['ndvi_norm'] + 0.3 * df_out['elevation_norm']
        denominator = 0.2 * df_out['slope_norm'] + 0.3 * df_out['rainfall_norm'] + 0.01
        denominator = denominator.where(np.abs(denominator) > eps, np.nan)
        df_out['FS_proxy'] = numerator / denominator

        risk = np.where(df_out['FS_proxy'] < 1.0, 1, 0).astype('int64')
        df_out['risk_label'] = risk
        df_out.loc[df_out['FS_proxy'].isna(), 'risk_label'] = np.nan

        if create_multiclass:
            df_out['risk_class'] = pd.cut(
                df_out['FS_proxy'],
                bins=[-np.inf, 0.8, 1.2, np.inf],
                labels=['High Risk', 'Medium Risk', 'Low Risk'],
                include_lowest=True,
            ).astype('object')

        return df_out

    def load_all_rasters(self):
        """
        STEP 1: Load all GeoTIFF files for all regions
        """
        print("\n=== STEP 1: LOADING RASTER DATA ===")
        
        for region in self.regions:
            print(f"\nProcessing region: {region}")
            region_path = self.data_dir / region
            self.raster_data[region] = {}
            self.metadata[region] = {}
            
            # Expected file patterns - handle both naming conventions
            if region == 'talcher_data':
                file_patterns = {
                    'dem': 'DEM_Talcher.tif',
                    'slope': 'Slope_Talcher.tif', 
                    'rainfall': 'Rainfall_Talcher_2022.tif',
                    'temperature': 'Temperature_Talcher_2022.tif',
                    'ndvi': 'NDVI_Talcher_2022.tif'
                }
            else:
                if region == 'korba':
                    region_name = 'Korba'
                else:
                    region_name = region
                file_patterns = {
                    'dem': f'DEM_{region_name}.tif',
                    'slope': f'Slope_{region_name}.tif', 
                    'rainfall': f'Rainfall_{region_name}_2022.tif',
                    'temperature': f'Temperature_{region_name}_2022.tif',
                    'ndvi': f'NDVI_{region_name}_2022.tif'
                }
            
            for data_type, filename in file_patterns.items():
                file_path = region_path / filename
                if file_path.exists():
                    try:
                        with rasterio.open(file_path) as src:
                            data = src.read(1)  # Read first band
                            transform = src.transform
                            crs = src.crs
                            
                            self.raster_data[region][data_type] = data
                            self.metadata[region][data_type] = {
                                'shape': data.shape,
                                'transform': transform,
                                'crs': crs,
                                'nodata': src.nodata
                            }
                            
                            print(f"  {data_type}: {data.shape}, dtype: {data.dtype}")
                            
                    except Exception as e:
                        print(f"  Error loading {filename}: {e}")
                else:
                    print(f"  File not found: {filename}")
    
    def check_alignment(self):
        """
        Check if all rasters have the same shape and resolution
        """
        print("\n=== CHECKING RASTER ALIGNMENT ===")
        
        for region in self.regions:
            print(f"\nRegion: {region}")
            shapes = []
            resolutions = []
            
            for data_type, meta in self.metadata[region].items():
                shape = meta['shape']
                transform = meta['transform']
                resolution = (abs(transform[0]), abs(transform[4]))  # pixel size in x, y
                
                shapes.append(shape)
                resolutions.append(resolution)
                print(f"  {data_type}: shape={shape}, resolution={resolution}")
            
            # Check if all shapes are the same
            if len(set(shapes)) > 1:
                print(f"  WARNING: Rasters have different shapes - resampling needed!")
                return False
            else:
                print(f"  All rasters aligned: {shapes[0]}")
                return True
    
    def resample_to_match(self, reference_type='dem'):
        """
        Resample all rasters to match the reference raster (typically DEM)
        
        Args:
            reference_type (str): Reference raster type for resampling
        """
        print("\n=== RESAMPLING RASTERS ===")
        
        for region in self.regions:
            print(f"\nResampling region: {region}")
            
            if reference_type not in self.raster_data[region]:
                print(f"  Reference raster {reference_type} not found!")
                continue
                
            # Get reference metadata
            ref_data = self.raster_data[region][reference_type]
            ref_meta = self.metadata[region][reference_type]
            ref_shape = ref_meta['shape']
            ref_transform = ref_meta['transform']
            
            # Resample each raster to match reference
            for data_type in self.raster_data[region]:
                if data_type == reference_type:
                    continue
                    
                print(f"  Resampling {data_type} to match {reference_type}")
                
                # Create array for resampled data
                resampled = np.empty(ref_shape, dtype=self.raster_data[region][data_type].dtype)
                
                # Get correct filename for resampling
                if region == 'talcher_data':
                    if data_type == 'dem':
                        filename = 'DEM_Talcher.tif'
                    elif data_type == 'slope':
                        filename = 'Slope_Talcher.tif'
                    elif data_type == 'rainfall':
                        filename = 'Rainfall_Talcher_2022.tif'
                    elif data_type == 'temperature':
                        filename = 'Temperature_Talcher_2022.tif'
                    elif data_type == 'ndvi':
                        filename = 'NDVI_Talcher_2022.tif'
                else:
                    if region == 'korba':
                        region_name = 'Korba'
                    else:
                        region_name = region
                    filename = f"{data_type}_{region_name}.tif"
                
                # Get source transform and CRS from metadata
                src_transform = self.metadata[region][data_type]['transform']
                src_crs = self.metadata[region][data_type]['crs']
                
                # Perform resampling using loaded data
                reproject(
                    source=self.raster_data[region][data_type],
                    destination=resampled,
                    src_transform=src_transform,
                    src_crs=src_crs,
                    dst_transform=ref_transform,
                    dst_crs=ref_meta['crs'],
                    resampling=Resampling.bilinear
                )
                
                # Update data and metadata
                self.raster_data[region][data_type] = resampled
                self.metadata[region][data_type]['shape'] = ref_shape
                self.metadata[region][data_type]['transform'] = ref_transform
                
                print(f"    New shape: {resampled.shape}")
    
    def create_tabular_dataset(self):
        """
        STEP 2: Create tabular dataset by extracting pixel-wise values
        
        Returns:
            dict: Dictionary of DataFrames for each region
        """
        print("\n=== STEP 2: CREATING TABULAR DATASET ===")
        
        tabular_data = {}
        
        for region in self.regions:
            print(f"\nCreating tabular data for: {region}")
            
            # Get reference shape and transform
            ref_shape = self.metadata[region]['dem']['shape']
            transform = self.metadata[region]['dem']['transform']
            
            # Create coordinate grids
            rows, cols = np.mgrid[0:ref_shape[0], 0:ref_shape[1]]
            
            # Convert pixel coordinates to geographic coordinates
            lons, lats = rasterio.transform.xy(transform, rows, cols)
            lons = np.array(lons)
            lats = np.array(lats)
            
            # Flatten all arrays
            lons_flat = lons.flatten()
            lats_flat = lats.flatten()
            
            # Extract values for each raster type
            data_dict = {
                'lon': lons_flat,
                'lat': lats_flat
            }
            
            for data_type in ['dem', 'slope', 'rainfall', 'temperature', 'ndvi']:
                if data_type in self.raster_data[region]:
                    values = self.raster_data[region][data_type].flatten()
                    data_dict[data_type] = values
            
            # Create DataFrame
            df = pd.DataFrame(data_dict)
            
            # Remove invalid pixels (where any value is NaN or nodata)
            # Check for common nodata values
            for col in ['dem', 'slope', 'rainfall', 'temperature', 'ndvi']:
                if col in df.columns:
                    # Replace common nodata values with NaN
                    df[col] = df[col].replace([-9999, -999, -32768], np.nan)
            
            # Remove rows with any NaN values
            df_clean = df.dropna()
            
            print(f"  Original pixels: {len(df)}")
            print(f"  Valid pixels: {len(df_clean)}")
            print(f"  Data retention: {len(df_clean)/len(df)*100:.1f}%")
            
            tabular_data[region] = df_clean
            
            # Display sample
            print(f"  Sample data:")
            print(df_clean.head())
        
        return tabular_data
    
    def extract_ndvi_patches(self, patch_size=32):
        """
        STEP 3: Extract NDVI patches for CNN input
        
        Args:
            patch_size (int): Size of square patches (patch_size x patch_size)
            
        Returns:
            dict: Dictionary containing patches and metadata for each region
        """
        print(f"\n=== STEP 3: EXTRACTING NDVI PATCHES (size={patch_size}x{patch_size}) ===")
        
        patch_data = {}
        
        for region in self.regions:
            print(f"\nExtracting patches for: {region}")
            
            ndvi = self.raster_data[region]['ndvi']
            shape = ndvi.shape
            
            # Calculate valid patch centers (avoid edges)
            margin = patch_size // 2
            valid_rows = range(margin, shape[0] - margin)
            valid_cols = range(margin, shape[1] - margin)
            
            patches = []
            centers = []
            
            transform = self.metadata[region]['dem']['transform']
            
            # Extract patches at regular intervals (sample to avoid too many patches)
            step = max(1, min(len(valid_rows), len(valid_cols)) // 100)  # Sample ~100 patches
            
            for row in valid_rows[::step]:
                for col in valid_cols[::step]:
                    # Extract patch
                    patch = ndvi[row-margin:row+margin, col-margin:col+margin]
                    
                    # Skip if patch contains invalid values
                    if np.any(np.isnan(patch)) or np.any(patch == -9999):
                        continue
                    
                    patches.append(patch)
                    
                    # Get center coordinates
                    lon, lat = rasterio.transform.xy(transform, row, col)
                    centers.append((lon, lat))
            
            patches = np.array(patches)
            centers = np.array(centers)
            
            print(f"  Extracted {len(patches)} patches")
            print(f"  Patch shape: {patches.shape}")
            print(f"  Center coordinates shape: {centers.shape}")
            
            patch_data[region] = {
                'patches': patches,
                'centers': centers,
                'patch_size': patch_size
            }
        
        return patch_data
    
    def create_temporal_features(self):
        """
        STEP 4: Create temporal features from rainfall and temperature
        
        Returns:
            dict: Dictionary containing temporal features for each region
        """
        print("\n=== STEP 4: CREATING TEMPORAL FEATURES ===")
        
        temporal_data = {}
        
        for region in self.regions:
            print(f"\nCreating temporal features for: {region}")
            
            # Get current rainfall and temperature data
            rainfall = self.raster_data[region]['rainfall']
            temperature = self.raster_data[region]['temperature']
            
            # Since we only have single time point data, we'll create derived features
            # that could represent temporal patterns
            
            temporal_features = {}
            
            # Rainfall features
            temporal_features['rainfall_current'] = rainfall
            
            # Simulate cumulative rainfall (assuming current represents average)
            temporal_features['rainfall_3day'] = rainfall * 3  # 3-day cumulative
            temporal_features['rainfall_7day'] = rainfall * 7  # 7-day cumulative
            
            # Temperature features
            temporal_features['temperature_current'] = temperature
            temporal_features['temperature_mean'] = temperature  # Same as current for single time point
            
            # Create interaction features
            temporal_features['rainfall_intensity'] = np.where(
                rainfall > np.percentile(rainfall[~np.isnan(rainfall)], 75),
                1, 0  # High rainfall intensity
            )
            
            temporal_features['temperature_stress'] = np.where(
                temperature > np.percentile(temperature[~np.isnan(temperature)], 90),
                1, 0  # High temperature stress
            )
            
            # Store features
            temporal_data[region] = temporal_features
            
            print(f"  Created {len(temporal_features)} temporal feature layers")
            for feature_name, feature_data in temporal_features.items():
                print(f"    {feature_name}: shape={feature_data.shape}, "
                      f"range=[{np.nanmin(feature_data):.2f}, {np.nanmax(feature_data):.2f}]")
        
        return temporal_data
    
    def run_complete_pipeline(self, patch_size=32):
        """
        Run the complete pipeline
        
        Args:
            patch_size (int): Size of NDVI patches
            
        Returns:
            dict: Complete processed data
        """
        print("Starting Rockfall Prediction Pipeline...")
        print("=" * 50)
        
        # Step 1: Load all rasters
        self.load_all_rasters()
        
        # Step 2: Check alignment and resample if needed
        is_aligned = self.check_alignment()
        if not is_aligned:
            self.resample_to_match()
        
        # Step 3: Create tabular dataset
        tabular_data = self.create_tabular_dataset()

        labeled_tabular_data = {}
        for region, df in tabular_data.items():
            labeled_tabular_data[region] = self.add_fs_proxy_labels(df, create_multiclass=True)
        
        # Step 4: Extract NDVI patches
        patch_data = self.extract_ndvi_patches(patch_size)
        
        # Step 5: Create temporal features
        temporal_data = self.create_temporal_features()
        
        # Combine all results
        processed_data = {
            'tabular': tabular_data,
            'tabular_labeled': labeled_tabular_data,
            'patches': patch_data,
            'temporal': temporal_data,
            'metadata': self.metadata,
            'regions': self.regions
        }
        
        print("\n" + "=" * 50)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        return processed_data
    
    def save_processed_data(self, processed_data, output_dir="processed_data"):
        """
        Save processed data to files
        
        Args:
            processed_data (dict): Output from run_complete_pipeline
            output_dir (str): Directory to save processed data
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\nSaving processed data to: {output_path}")
        
        # Save tabular data
        for region, df in processed_data['tabular'].items():
            csv_path = output_path / f"tabular_{region}.csv"
            df.to_csv(csv_path, index=False)
            print(f"  Saved: {csv_path}")

        if 'tabular_labeled' in processed_data:
            for region, df in processed_data['tabular_labeled'].items():
                csv_path = output_path / f"tabular_{region}_labeled.csv"
                df.to_csv(csv_path, index=False)
                print(f"  Saved: {csv_path}")
        
        # Save NDVI patches
        for region, patch_dict in processed_data['patches'].items():
            patches_path = output_path / f"ndvi_patches_{region}.npz"
            centers_path = output_path / f"patch_centers_{region}.npz"
            
            np.savez_compressed(patches_path, patches=patch_dict['patches'])
            np.savez_compressed(centers_path, centers=patch_dict['centers'])
            
            print(f"  Saved: {patches_path}")
            print(f"  Saved: {centers_path}")
        
        # Save temporal features
        for region, temporal_dict in processed_data['temporal'].items():
            temporal_path = output_path / f"temporal_{region}.npz"
            np.savez_compressed(temporal_path, **temporal_dict)
            print(f"  Saved: {temporal_path}")
        
        print("All data saved successfully!")


def main():
    """
    Main function to run the rockfall prediction pipeline
    """
    # Initialize pipeline
    pipeline = RockfallDataPipeline(data_dir="datasets")
    
    # Run complete pipeline
    processed_data = pipeline.run_complete_pipeline(patch_size=32)
    
    # Save processed data
    pipeline.save_processed_data(processed_data)
    
    # Print summary
    print("\n" + "=" * 60)
    print("ROCKFALL PREDICTION PIPELINE SUMMARY")
    print("=" * 60)
    
    for region in pipeline.regions:
        print(f"\n{region.upper()}:")
        print(f"  Tabular samples: {len(processed_data['tabular'][region])}")
        print(f"  NDVI patches: {len(processed_data['patches'][region]['patches'])}")
        print(f"  Temporal features: {len(processed_data['temporal'][region])}")
    
    print("\nReady for machine learning model training!")


if __name__ == "__main__":
    main()
