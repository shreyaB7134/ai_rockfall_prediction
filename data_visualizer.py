"""
Data Visualization and Validation for Rockfall Prediction System
================================================================

This module provides visualization and validation tools for the processed
geospatial data to ensure data quality and provide insights.

Author: Geospatial AI System
Date: 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import rasterio
from rasterio.plot import show
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class RockfallDataVisualizer:
    """
    Visualization and validation tools for rockfall prediction data
    """
    
    def __init__(self, processed_data=None):
        """
        Initialize visualizer
        
        Args:
            processed_data (dict): Output from RockfallDataPipeline
        """
        self.processed_data = processed_data
        self.regions = processed_data['regions'] if processed_data else []
    
    def plot_raster_overview(self, region, save_path=None):
        """
        Plot overview of all raster layers for a region
        
        Args:
            region (str): Region name
            save_path (str): Path to save the plot
        """
        if not self.processed_data:
            print("No processed data available!")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Load original raster data for visualization
        data_dir = Path("datasets") / region
        raster_types = ['dem', 'slope', 'rainfall', 'temperature', 'ndvi']
        titles = ['DEM (Elevation)', 'Slope', 'Rainfall', 'Temperature', 'NDVI']
        
        for idx, (raster_type, title) in enumerate(zip(raster_types, titles)):
            ax = axes[idx]
            
            # Find the correct file
            if raster_type == 'dem':
                filename = f"DEM_{region}.tif"
            elif raster_type == 'slope':
                filename = f"Slope_{region}.tif"
            elif raster_type == 'rainfall':
                filename = f"Rainfall_{region}_2022.tif"
            elif raster_type == 'temperature':
                filename = f"Temperature_{region}_2022.tif"
            elif raster_type == 'ndvi':
                filename = f"NDVI_{region}_2022.tif"
            
            file_path = data_dir / filename
            if file_path.exists():
                with rasterio.open(file_path) as src:
                    data = src.read(1)
                    
                    # Handle nodata values
                    data = np.where(data == src.nodata, np.nan, data)
                    data = np.where(data == -9999, np.nan, data)
                    
                    # Plot
                    im = ax.imshow(data, cmap='viridis', aspect='auto')
                    ax.set_title(f"{title}\n{region}", fontsize=12, fontweight='bold')
                    ax.axis('off')
                    
                    # Add colorbar
                    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                    cbar.ax.tick_params(labelsize=8)
                    
                    # Add statistics
                    valid_data = data[~np.isnan(data)]
                    if len(valid_data) > 0:
                        stats_text = f"Min: {np.nanmin(data):.2f}\nMax: {np.nanmax(data):.2f}\nMean: {np.nanmean(data):.2f}"
                        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                               fontsize=8, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Remove empty subplot
        axes[5].axis('off')
        
        plt.suptitle(f"Rockfall Prediction Data Overview - {region}", 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved overview plot to: {save_path}")
        
        plt.show()
    
    def plot_data_distribution(self, region, save_path=None):
        """
        Plot distribution of tabular data features
        
        Args:
            region (str): Region name
            save_path (str): Path to save the plot
        """
        if not self.processed_data or region not in self.processed_data['tabular']:
            print(f"No tabular data available for region: {region}")
            return
        
        df = self.processed_data['tabular'][region]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        features = ['elevation', 'slope', 'rainfall', 'temperature', 'ndvi']
        titles = ['Elevation (m)', 'Slope (degrees)', 'Rainfall (mm)', 'Temperature (°C)', 'NDVI']
        
        for idx, (feature, title) in enumerate(zip(features, titles)):
            ax = axes[idx]
            
            if feature in df.columns:
                # Plot histogram
                ax.hist(df[feature], bins=50, alpha=0.7, edgecolor='black')
                ax.set_title(f"{title} Distribution", fontweight='bold')
                ax.set_xlabel(title)
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
                
                # Add statistics
                mean_val = df[feature].mean()
                std_val = df[feature].std()
                ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
                ax.axvline(mean_val + std_val, color='orange', linestyle=':', label=f'+1 STD')
                ax.axvline(mean_val - std_val, color='orange', linestyle=':', label='-1 STD')
                ax.legend(fontsize=8)
        
        # Remove empty subplot
        axes[5].axis('off')
        
        plt.suptitle(f"Feature Distributions - {region}", fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved distribution plot to: {save_path}")
        
        plt.show()
    
    def plot_correlation_matrix(self, region, save_path=None):
        """
        Plot correlation matrix of features
        
        Args:
            region (str): Region name
            save_path (str): Path to save the plot
        """
        if not self.processed_data or region not in self.processed_data['tabular']:
            print(f"No tabular data available for region: {region}")
            return
        
        df = self.processed_data['tabular'][region]
        
        # Select numeric features
        numeric_features = ['elevation', 'slope', 'rainfall', 'temperature', 'ndvi']
        available_features = [f for f in numeric_features if f in df.columns]
        
        if len(available_features) < 2:
            print("Not enough numeric features for correlation matrix")
            return
        
        correlation_matrix = df[available_features].corr()
        
        plt.figure(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='coolwarm', 
                   center=0,
                   square=True,
                   fmt='.2f',
                   cbar_kws={'shrink': 0.8})
        
        plt.title(f'Feature Correlation Matrix - {region}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved correlation matrix to: {save_path}")
        
        plt.show()
    
    def plot_ndvi_patches_sample(self, region, n_samples=16, save_path=None):
        """
        Plot sample NDVI patches
        
        Args:
            region (str): Region name
            n_samples (int): Number of patches to show
            save_path (str): Path to save the plot
        """
        if not self.processed_data or region not in self.processed_data['patches']:
            print(f"No patch data available for region: {region}")
            return
        
        patches = self.processed_data['patches'][region]['patches']
        
        if len(patches) == 0:
            print(f"No NDVI patches found for region: {region}")
            return
        
        # Sample patches
        n_samples = min(n_samples, len(patches))
        sample_indices = np.random.choice(len(patches), n_samples, replace=False)
        sample_patches = patches[sample_indices]
        
        # Calculate grid dimensions
        cols = int(np.ceil(np.sqrt(n_samples)))
        rows = int(np.ceil(n_samples / cols))
        
        fig, axes = plt.subplots(rows, cols, figsize=(12, 12))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for idx in range(n_samples):
            ax = axes[idx]
            patch = sample_patches[idx]
            
            # Plot patch
            im = ax.imshow(patch, cmap='RdYlGn', vmin=-1, vmax=1)
            ax.set_title(f"Patch {idx+1}", fontsize=10)
            ax.axis('off')
            
            # Add NDVI statistics
            ndvi_mean = np.mean(patch)
            ax.text(0.5, -0.15, f"Mean NDVI: {ndvi_mean:.3f}", 
                   transform=ax.transAxes, ha='center', fontsize=8)
        
        # Hide unused subplots
        for idx in range(n_samples, len(axes)):
            axes[idx].axis('off')
        
        plt.suptitle(f'Sample NDVI Patches - {region} (32x32 pixels)', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved patch samples to: {save_path}")
        
        plt.show()
    
    def plot_temporal_features(self, region, save_path=None):
        """
        Plot temporal features
        
        Args:
            region (str): Region name
            save_path (str): Path to save the plot
        """
        if not self.processed_data or region not in self.processed_data['temporal']:
            print(f"No temporal data available for region: {region}")
            return
        
        temporal_data = self.processed_data['temporal'][region]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        feature_names = list(temporal_data.keys())
        titles = ['Current Rainfall', '3-Day Cumulative Rainfall', '7-Day Cumulative Rainfall',
                 'Current Temperature', 'Temperature Mean', 'Rainfall Intensity']
        
        for idx, (feature_name, title) in enumerate(zip(feature_names[:6], titles)):
            ax = axes[idx]
            data = temporal_data[feature_name]
            
            # Plot histogram
            valid_data = data[~np.isnan(data)]
            if len(valid_data) > 0:
                ax.hist(valid_data, bins=50, alpha=0.7, edgecolor='black')
                ax.set_title(f"{title}", fontweight='bold')
                ax.set_xlabel('Value')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
                
                # Add statistics
                mean_val = np.nanmean(data)
                ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {mean_val:.2f}')
                ax.legend(fontsize=8)
            else:
                ax.text(0.5, 0.5, 'No valid data', transform=ax.transAxes, 
                       ha='center', va='center')
                ax.set_title(f"{title}", fontweight='bold')
        
        plt.suptitle(f'Temporal Features - {region}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved temporal features plot to: {save_path}")
        
        plt.show()
    
    def generate_data_quality_report(self, region):
        """
        Generate comprehensive data quality report
        
        Args:
            region (str): Region name
        """
        print(f"\n{'='*60}")
        print(f"DATA QUALITY REPORT - {region.upper()}")
        print(f"{'='*60}")
        
        if not self.processed_data:
            print("No processed data available!")
            return
        
        # Tabular data quality
        if region in self.processed_data['tabular']:
            df = self.processed_data['tabular'][region]
            print(f"\nTABULAR DATA:")
            print(f"  Total samples: {len(df):,}")
            print(f"  Features: {list(df.columns)}")
            print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            print(f"\n  Feature Statistics:")
            for col in ['elevation', 'slope', 'rainfall', 'temperature', 'ndvi']:
                if col in df.columns:
                    print(f"    {col}:")
                    print(f"      Range: [{df[col].min():.2f}, {df[col].max():.2f}]")
                    print(f"      Mean: {df[col].mean():.2f} ± {df[col].std():.2f}")
                    print(f"      Missing: {df[col].isnull().sum()} ({df[col].isnull().sum()/len(df)*100:.2f}%)")
        
        # Patch data quality
        if region in self.processed_data['patches']:
            patch_info = self.processed_data['patches'][region]
            patches = patch_info['patches']
            print(f"\nNDVI PATCHES:")
            print(f"  Total patches: {len(patches):,}")
            print(f"  Patch size: {patch_info['patch_size']}x{patch_info['patch_size']}")
            print(f"  Memory usage: {patches.nbytes / 1024 / 1024:.2f} MB")
            
            if len(patches) > 0:
                print(f"  NDVI Statistics:")
                print(f"    Range: [{np.min(patches):.3f}, {np.max(patches):.3f}]")
                print(f"    Mean: {np.mean(patches):.3f} ± {np.std(patches):.3f}")
        
        # Temporal data quality
        if region in self.processed_data['temporal']:
            temporal_data = self.processed_data['temporal'][region]
            print(f"\nTEMPORAL FEATURES:")
            print(f"  Feature layers: {len(temporal_data)}")
            for feature_name, data in temporal_data.items():
                valid_pixels = np.sum(~np.isnan(data))
                total_pixels = data.size
                print(f"    {feature_name}: {valid_pixels:,}/{total_pixels:,} valid pixels "
                     f"({valid_pixels/total_pixels*100:.1f}%)")
        
        print(f"\n{'='*60}")
    
    def create_all_visualizations(self, output_dir="visualizations"):
        """
        Create all visualizations for all regions
        
        Args:
            output_dir (str): Directory to save visualizations
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"Creating visualizations in: {output_path}")
        
        for region in self.regions:
            print(f"\nProcessing visualizations for: {region}")
            region_dir = output_path / region
            region_dir.mkdir(exist_ok=True)
            
            try:
                # Raster overview
                self.plot_raster_overview(region, 
                    save_path=region_dir / "raster_overview.png")
                
                # Data distribution
                self.plot_data_distribution(region,
                    save_path=region_dir / "data_distribution.png")
                
                # Correlation matrix
                self.plot_correlation_matrix(region,
                    save_path=region_dir / "correlation_matrix.png")
                
                # NDVI patches
                self.plot_ndvi_patches_sample(region,
                    save_path=region_dir / "ndvi_patches.png")
                
                # Temporal features
                self.plot_temporal_features(region,
                    save_path=region_dir / "temporal_features.png")
                
                # Data quality report
                self.generate_data_quality_report(region)
                
                print(f"  All visualizations saved for {region}")
                
            except Exception as e:
                print(f"  Error creating visualizations for {region}: {e}")


def main():
    """
    Main function to demonstrate visualization capabilities
    """
    # Load processed data (assuming pipeline has been run)
    import pickle
    
    try:
        with open("processed_data/processed_data.pkl", "rb") as f:
            processed_data = pickle.load(f)
    except FileNotFoundError:
        print("No processed data found. Please run the pipeline first.")
        return
    
    # Create visualizer
    visualizer = RockfallDataVisualizer(processed_data)
    
    # Generate all visualizations
    visualizer.create_all_visualizations()
    
    print("\nVisualization generation completed!")


if __name__ == "__main__":
    main()
