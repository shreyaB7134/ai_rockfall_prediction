"""
Rockfall Prediction System - Demo Script
==========================================

This script demonstrates the complete pipeline functionality
and creates visualizations for data analysis.

Author: Geospatial AI System
Date: 2026
"""

import numpy as np
import pickle
from pathlib import Path
from rockfall_pipeline import RockfallDataPipeline
from data_visualizer import RockfallDataVisualizer

def run_demo():
    """
    Run complete demo of the rockfall prediction system
    """
    print("ROCKFALL PREDICTION SYSTEM - DEMO")
    print("=" * 50)
    
    # Step 1: Run the complete pipeline
    print("\n1. Running data processing pipeline...")
    pipeline = RockfallDataPipeline(data_dir="datasets")
    processed_data = pipeline.run_complete_pipeline(patch_size=32)
    
    # Save processed data for later use
    with open("processed_data/processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)
    print("   Processed data saved!")
    
    # Step 2: Create visualizations
    print("\n2. Creating visualizations...")
    visualizer = RockfallDataVisualizer(processed_data)
    
    # Create visualization directory
    viz_dir = Path("visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    for region in processed_data['regions']:
        print(f"   Processing {region}...")
        region_dir = viz_dir / region
        region_dir.mkdir(exist_ok=True)
        
        try:
            # Generate individual visualizations
            visualizer.plot_raster_overview(region, 
                save_path=region_dir / "raster_overview.png")
            
            visualizer.plot_data_distribution(region,
                save_path=region_dir / "data_distribution.png")
            
            visualizer.plot_correlation_matrix(region,
                save_path=region_dir / "correlation_matrix.png")
            
            visualizer.plot_ndvi_patches_sample(region,
                save_path=region_dir / "ndvi_patches.png")
            
            visualizer.plot_temporal_features(region,
                save_path=region_dir / "temporal_features.png")
            
            # Generate quality report
            visualizer.generate_data_quality_report(region)
            
            print(f"   All visualizations created for {region}")
            
        except Exception as e:
            print(f"   Error with {region}: {e}")
    
    # Step 3: Display summary statistics
    print("\n3. Data Summary:")
    print("-" * 30)
    
    for region in processed_data['regions']:
        print(f"\n{region.upper()}:")
        
        # Tabular data stats
        if region in processed_data['tabular']:
            df = processed_data['tabular'][region]
            print(f"  Tabular samples: {len(df):,}")
            
            # Feature ranges
            for col in ['dem', 'slope', 'rainfall', 'temperature', 'ndvi']:
                if col in df.columns:
                    print(f"    {col}: [{df[col].min():.2f}, {df[col].max():.2f}]")
        
        # Patch data stats
        if region in processed_data['patches']:
            patches = processed_data['patches'][region]['patches']
            print(f"  NDVI patches: {len(patches):,}")
            print(f"  Patch shape: {patches.shape[1:]}")
        
        # Temporal data stats
        if region in processed_data['temporal']:
            temporal = processed_data['temporal'][region]
            print(f"  Temporal features: {len(temporal)} layers")
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nFiles created:")
    print("- processed_data/: All processed datasets")
    print("- visualizations/: Data analysis plots")
    print("\nReady for ML model training!")
    
    return processed_data

def quick_data_inspection():
    """
    Quick inspection of processed data without running full pipeline
    """
    print("QUICK DATA INSPECTION")
    print("=" * 30)
    
    try:
        # Load existing processed data
        with open("processed_data/processed_data.pkl", "rb") as f:
            processed_data = pickle.load(f)
        
        print(f"Loaded data for regions: {processed_data['regions']}")
        
        for region in processed_data['regions']:
            print(f"\n{region.upper()}:")
            
            # Check tabular data
            if region in processed_data['tabular']:
                df = processed_data['tabular'][region]
                print(f"  Tabular: {len(df):,} samples, {len(df.columns)} features")
                print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
            
            # Check patch data
            if region in processed_data['patches']:
                patches = processed_data['patches'][region]['patches']
                print(f"  Patches: {len(patches):,} patches, {patches.nbytes / 1024 / 1024:.1f} MB")
            
            # Check temporal data
            if region in processed_data['temporal']:
                temporal = processed_data['temporal'][region]
                total_size = sum(data.nbytes for data in temporal.values())
                print(f"  Temporal: {len(temporal)} layers, {total_size / 1024 / 1024:.1f} MB")
        
    except FileNotFoundError:
        print("No processed data found. Run the full demo first.")
    
    print("\n" + "=" * 30)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_data_inspection()
    else:
        run_demo()
