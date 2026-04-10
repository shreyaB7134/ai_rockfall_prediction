"""
Earth Engine Integration for Rockfall Prediction
================================================

This module integrates Google Earth Engine API with the rockfall prediction pipeline,
enabling real-time fetching of geospatial data instead of relying on local files.

Author: Geospatial AI System
Date: April 2026
"""

import ee
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class EarthEngineDataFetcher:
    """
    Fetch real-time geospatial data from Google Earth Engine for rockfall prediction.
    """
    
    def __init__(self):
        """Initialize Earth Engine connection."""
        try:
            ee.Initialize(project='rockfall-project-492810')
            print("✅ Earth Engine initialized successfully")
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("Trying alternative authentication method...")
            try:
                ee.Authenticate()
                ee.Initialize(project='rockfall-project-492810')
                print("✅ Earth Engine initialized successfully with authentication!")
            except Exception as e2:
                print(f"❌ Authentication also failed: {e2}")
                raise Exception("Earth Engine authentication failed.")
    
    def fetch_point_features(self, lat: float, lon: float, 
                            start_date: str = '2022-01-01', 
                            end_date: str = '2022-12-31') -> Dict:
        """
        Fetch all features for a single point location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            start_date (str): Start date for temporal data (YYYY-MM-DD)
            end_date (str): End date for temporal data (YYYY-MM-DD)
        
        Returns:
            dict: Dictionary containing all features
        """
        point = ee.Geometry.Point([lon, lat])
        
        # DEM (Elevation)
        dem = ee.Image("USGS/SRTMGL1_003")
        elevation = dem.sample(point, 30).first().get("elevation").getInfo()
        
        # Slope
        slope = ee.Terrain.slope(dem)
        slope_val = slope.sample(point, 30).first().get("slope").getInfo()
        
        # Rainfall (CHIRPS)
        rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate(start_date, end_date) \
                .mean()
        rain_val = rain.sample(point, 5000).first().get("precipitation").getInfo()
        
        # Temperature (ERA5)
        temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate(start_date, end_date) \
                .select('temperature_2m') \
                .mean()
        temp_val = temp.sample(point, 1000).first().get("temperature_2m").getInfo()
        
        # NDVI (Sentinel-2)
        try:
            s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterDate(start_date, end_date) \
                    .filterBounds(point) \
                    .select(['B4', 'B8'])
            
            image = s2.median()
            ndvi = image.normalizedDifference(['B8', 'B4'])
            ndvi_val = ndvi.sample(point, 10).first().get("nd").getInfo()
        except Exception as e:
            print(f"Warning: Could not fetch NDVI: {e}")
            ndvi_val = None
        
        features = {
            'latitude': lat,
            'longitude': lon,
            'elevation': elevation,
            'slope': slope_val,
            'rainfall': rain_val,
            'temperature': temp_val,
            'ndvi': ndvi_val
        }
        
        return features
    
    def fetch_area_features(self, region_coords: List[Tuple[float, float]], 
                           scale: int = 1000) -> Dict:
        """
        Fetch features for an area (bounding box).
        
        Args:
            region_coords (list): List of (lat, lon) tuples defining region
            scale (int): Scale in meters for sampling
        
        Returns:
            dict: Dictionary containing feature arrays for the region
        """
        # Create region geometry
        region = ee.Geometry.Polygon([region_coords])
        
        # DEM
        dem = ee.Image("USGS/SRTMGL1_003")
        elevation = dem.clip(region)
        
        # Slope
        slope = ee.Terrain.slope(dem)
        
        # Rainfall
        rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate('2022-01-01', '2022-12-31') \
                .mean()
        
        # Temperature
        temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate('2022-01-01', '2022-12-31') \
                .select('temperature_2m') \
                .mean()
        
        # NDVI
        try:
            s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterDate('2022-06-01', '2022-09-30') \
                    .filterBounds(region) \
                    .select(['B4', 'B8'])
            
            image = s2.median()
            ndvi = image.normalizedDifference(['B8', 'B4'])
        except Exception as e:
            print(f"Warning: Could not fetch NDVI: {e}")
            ndvi = None
        
        return {
            'dem': elevation,
            'slope': slope,
            'rainfall': rain,
            'temperature': temp,
            'ndvi': ndvi
        }
    
    def fetch_multiple_points(self, coordinates: List[Tuple[float, float]]) -> pd.DataFrame:
        """
        Fetch features for multiple point locations.
        
        Args:
            coordinates (list): List of (lat, lon) tuples
        
        Returns:
            pd.DataFrame: DataFrame with features for all points
        """
        features_list = []
        
        for i, (lat, lon) in enumerate(coordinates):
            print(f"Fetching point {i+1}/{len(coordinates)}: ({lat}, {lon})")
            try:
                features = self.fetch_point_features(lat, lon)
                features_list.append(features)
            except Exception as e:
                print(f"Error fetching point {i+1}: {e}")
        
        return pd.DataFrame(features_list)
    
    def create_prediction_input(self, lat: float, lon: float) -> Dict:
        """
        Create input dictionary ready for model prediction.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
        
        Returns:
            dict: Input dictionary with features formatted for model
        """
        features = self.fetch_point_features(lat, lon)
        
        # Convert temperature from Kelvin to Celsius if needed
        temp_celsius = features['temperature'] - 273.15 if features['temperature'] > 200 else features['temperature']
        
        prediction_input = {
            'dem': features['elevation'],
            'slope': features['slope'],
            'rainfall': features['rainfall'],
            'temperature': temp_celsius,
            'ndvi': features['ndvi']
        }
        
        return prediction_input


def test_earth_engine_integration():
    """Test the Earth Engine integration."""
    print("🌍 Testing Earth Engine Integration")
    print("=" * 60)
    
    try:
        # Initialize fetcher
        fetcher = EarthEngineDataFetcher()
        
        # Test single point
        print("\n📍 Testing single point fetch (Talcher region)...")
        lat, lon = 20.95, 85.10
        features = fetcher.fetch_point_features(lat, lon)
        
        print(f"\n✅ Successfully fetched features for ({lat}, {lon}):")
        for key, value in features.items():
            if value is not None:
                print(f"  {key}: {value:.4f}")
        
        # Test prediction input
        print("\n🔮 Testing prediction input creation...")
        pred_input = fetcher.create_prediction_input(lat, lon)
        print("✅ Prediction input created:")
        for key, value in pred_input.items():
            print(f"  {key}: {value:.4f}")
        
        print("\n" + "=" * 60)
        print("✅ Earth Engine integration test PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Earth Engine integration test FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Run: earthengine authenticate")
        print("2. Complete browser authentication")
        print("3. Check internet connection")
        return False


if __name__ == "__main__":
    test_earth_engine_integration()
