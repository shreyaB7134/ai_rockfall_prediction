"""
Earth Engine Real-time Data Fetching
=====================================

This script fetches real-time geospatial data from Google Earth Engine
for rockfall prediction at a given location.

Features fetched:
- DEM (Elevation)
- Slope
- Rainfall (CHIRPS)
- Temperature (ERA5)
- NDVI (Sentinel-2)

Usage:
    python gee_fetch_features.py
"""

import ee

def fetch_all_features(lat, lon):
    """
    Fetch all geospatial features for a given location using Earth Engine.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        dict: Dictionary containing all fetched features
    """
    print(f"Fetching features for location: ({lat}, {lon})")
    
    # Initialize Earth Engine
    try:
        ee.Initialize(project='rockfall-project-492810')
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("Trying alternative authentication method...")
        ee.Authenticate()
        ee.Initialize(project='rockfall-project-492810')
    
    # Create point geometry
    point = ee.Geometry.Point([lon, lat])
    
    # ========== DEM (Elevation) ==========
    print("Fetching DEM...")
    dem = ee.Image("USGS/SRTMGL1_003")
    elevation = dem.sample(point, 30).first().get("elevation")
    elevation_val = elevation.getInfo()
    
    # ========== Slope ==========
    print("Calculating slope...")
    slope = ee.Terrain.slope(dem)
    slope_val = slope.sample(point, 30).first().get("slope").getInfo()
    
    # ========== Rainfall (CHIRPS) ==========
    print("Fetching rainfall data...")
    rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate('2022-01-01', '2022-12-31') \
            .mean()
    rain_val = rain.sample(point, 5000).first().get("precipitation").getInfo()
    
    # ========== Temperature (ERA5) ==========
    print("Fetching temperature data...")
    temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
            .filterDate('2022-01-01', '2022-12-31') \
            .select('temperature_2m') \
            .mean()
    temp_val = temp.sample(point, 1000).first().get("temperature_2m").getInfo()
    
    # ========== NDVI (Sentinel-2) ==========
    print("Fetching NDVI data...")
    s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
            .filterDate('2022-06-01', '2022-09-30') \
            .filterBounds(point) \
            .select(['B4', 'B8'])
    
    image = s2.median()
    ndvi = image.normalizedDifference(['B8', 'B4'])
    ndvi_val = ndvi.sample(point, 10).first().get("nd").getInfo()
    
    # ========== Compile Results ==========
    features = {
        'latitude': lat,
        'longitude': lon,
        'elevation': elevation_val,
        'slope': slope_val,
        'rainfall': rain_val,
        'temperature': temp_val,
        'ndvi': ndvi_val
    }
    
    return features


def print_features(features):
    """Print fetched features in a formatted way."""
    print("\n" + "=" * 50)
    print("FETCHED FEATURES")
    print("=" * 50)
    print(f"Location: ({features['latitude']}, {features['longitude']})")
    print("-" * 50)
    print(f"Elevation:  {features['elevation']:.2f} meters")
    print(f"Slope:      {features['slope']:.2f} degrees")
    print(f"Rainfall:   {features['rainfall']:.2f} mm/year")
    print(f"Temperature: {features['temperature']:.2f} Kelvin")
    print(f"NDVI:       {features['ndvi']:.4f}")
    print("=" * 50)


def main():
    """Main function to test Earth Engine data fetching."""
    
    # Example: Talcher location
    lat = 20.95
    lon = 85.10
    
    print("🌍 Earth Engine Real-time Data Fetching")
    print("=" * 50)
    
    try:
        features = fetch_all_features(lat, lon)
        print_features(features)
        
        print("\n✅ Successfully fetched all features!")
        print("🔥 You can now use real-time Earth Engine data!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Run: earthengine authenticate")
        print("2. Completed the authentication process")
        print("3. Have internet connection")


if __name__ == "__main__":
    main()
