"""
Real-time Rockfall Prediction with Earth Engine Integration
===========================================================

This script connects Google Earth Engine data with trained ML models
to predict rockfall risk for any location.

Usage:
    python predict_rockfall_realtime.py --lat 20.95 --lon 85.10
"""

import argparse
import numpy as np
import joblib
import ee
import warnings
warnings.filterwarnings('ignore')


class RockfallPredictor:
    """
    Real-time rockfall prediction using Earth Engine data and trained models.
    """
    
    def __init__(self, model_path="models/randomforest_tabular.joblib"):
        """
        Initialize the predictor with trained model.
        
        Args:
            model_path (str): Path to trained model file
        """
        print("Loading trained model...")
        self.model = joblib.load(model_path)
        print(f"✅ Model loaded from: {model_path}")
        
        # Initialize Earth Engine
        print("Initializing Earth Engine...")
        try:
            ee.Initialize(project='rockfall-project-492810')
            print("✅ Earth Engine initialized successfully")
        except Exception as e:
            print(f"❌ Earth Engine initialization failed: {e}")
            raise
    
    def fetch_features(self, lat, lon):
        """
        Fetch geospatial features from Earth Engine for a given location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
        
        Returns:
            dict: Dictionary containing all features
        """
        print(f"\n🌍 Fetching features for location: ({lat}, {lon})")
        
        # Create point geometry
        point = ee.Geometry.Point([lon, lat])
        
        # DEM (Elevation)
        print("Fetching DEM...")
        dem = ee.Image("USGS/SRTMGL1_003")
        elevation = dem.sample(point, 30).first().get("elevation").getInfo()
        
        # Slope
        print("Calculating slope...")
        slope = ee.Terrain.slope(dem)
        slope_val = slope.sample(point, 30).first().get("slope").getInfo()
        
        # Rainfall (CHIRPS)
        print("Fetching rainfall...")
        rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate('2022-01-01', '2022-12-31') \
                .mean()
        rain_val = rain.sample(point, 5000).first().get("precipitation").getInfo()
        
        # Temperature (ERA5)
        print("Fetching temperature...")
        temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate('2022-01-01', '2022-12-31') \
                .select('temperature_2m') \
                .mean()
        temp_val = temp.sample(point, 1000).first().get("temperature_2m").getInfo()
        
        # Convert temperature from Kelvin to Celsius
        temp_celsius = temp_val - 273.15
        
        # NDVI (Sentinel-2)
        print("Fetching NDVI...")
        try:
            s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterDate('2022-06-01', '2022-09-30') \
                    .filterBounds(point) \
                    .select(['B4', 'B8'])
            
            image = s2.median()
            ndvi = image.normalizedDifference(['B8', 'B4'])
            ndvi_val = ndvi.sample(point, 10).first().get("nd").getInfo()
        except Exception as e:
            print(f"Warning: Could not fetch NDVI: {e}")
            ndvi_val = 0.0  # Default value if NDVI fails
        
        features = {
            'elevation': elevation,
            'slope': slope_val,
            'rainfall': rain_val,
            'temperature': temp_celsius,
            'ndvi': ndvi_val
        }
        
        return features
    
    def format_features(self, features):
        """
        Format features into the exact order expected by the model.
        
        Args:
            features (dict): Dictionary of features
        
        Returns:
            np.array: Formatted feature vector
        """
        # Ensure correct order: elevation, slope, rainfall, temperature, ndvi
        feature_vector = np.array([[
            features['elevation'],
            features['slope'],
            features['rainfall'],
            features['temperature'],
            features['ndvi']
        ]])
        
        return feature_vector
    
    def predict(self, lat, lon):
        """
        Make rockfall prediction for a given location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
        
        Returns:
            dict: Prediction results with probability and risk level
        """
        # Fetch features
        features = self.fetch_features(lat, lon)
        
        # Format features for model
        X = self.format_features(features)
        
        # Make prediction
        print("🔮 Making prediction...")
        probability = self.model.predict_proba(X)[0, 1]
        
        # Convert to risk level
        risk_level = "HIGH RISK" if probability > 0.5 else "LOW RISK"
        
        # Compile results
        results = {
            'location': {'latitude': lat, 'longitude': lon},
            'features': features,
            'prediction': {
                'probability': float(probability),
                'risk_level': risk_level
            }
        }
        
        return results
    
    def print_results(self, results):
        """
        Print prediction results in a formatted way.
        
        Args:
            results (dict): Prediction results
        """
        print("\n" + "=" * 60)
        print("ROCKFALL PREDICTION RESULTS")
        print("=" * 60)
        
        # Location
        loc = results['location']
        print(f"\n📍 Location: ({loc['latitude']:.4f}, {loc['longitude']:.4f})")
        
        # Features
        print("\n📊 Fetched Features:")
        feat = results['features']
        print(f"  Elevation:   {feat['elevation']:.2f} meters")
        print(f"  Slope:       {feat['slope']:.2f} degrees")
        print(f"  Rainfall:    {feat['rainfall']:.2f} mm/year")
        print(f"  Temperature: {feat['temperature']:.2f} °C")
        print(f"  NDVI:        {feat['ndvi']:.4f}")
        
        # Prediction
        pred = results['prediction']
        print("\n🔮 Prediction:")
        print(f"  Probability: {pred['probability']:.4f}")
        print(f"  Risk Level:  {pred['risk_level']}")
        
        print("=" * 60)
        
        # Risk assessment message
        if pred['probability'] > 0.8:
            print("⚠️  WARNING: Very high rockfall risk detected!")
            print("   Immediate action recommended.")
        elif pred['probability'] > 0.5:
            print("⚠️  CAUTION: Moderate rockfall risk detected.")
            print("   Monitor the area closely.")
        else:
            print("✅ Low rockfall risk.")
            print("   Normal operations can continue.")
        
        print("=" * 60)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Real-time rockfall prediction using Earth Engine and trained models'
    )
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--model', type=str, 
                       default='models/randomforest_tabular.joblib',
                       help='Path to trained model (default: models/randomforest_tabular.joblib)')
    
    args = parser.parse_args()
    
    print("🚀 Real-time Rockfall Prediction System")
    print("=" * 60)
    
    try:
        # Initialize predictor
        predictor = RockfallPredictor(model_path=args.model)
        
        # Make prediction
        results = predictor.predict(args.lat, args.lon)
        
        # Print results
        predictor.print_results(results)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure trained model exists at specified path")
        print("2. Verify Earth Engine is initialized")
        print("3. Check internet connection")
        print("4. Verify coordinates are valid")


if __name__ == "__main__":
    main()
