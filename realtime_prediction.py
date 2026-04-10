"""
Real-time Rockfall Prediction using Earth Engine
================================================

This script uses Google Earth Engine to fetch real-time geospatial data
and make rockfall predictions using the trained models.

Usage:
    python realtime_prediction.py --lat 20.95 --lon 85.10
"""

import argparse
import numpy as np
import pandas as pd
import joblib
from earth_engine_integration import EarthEngineDataFetcher
import warnings
warnings.filterwarnings('ignore')


class RealTimeRockfallPredictor:
    """
    Real-time rockfall prediction using Earth Engine data and trained models.
    """
    
    def __init__(self, model_path="models/randomforest_tabular.joblib"):
        """
        Initialize the predictor with trained model.
        
        Args:
            model_path (str): Path to trained model file
        """
        self.model = joblib.load(model_path)
        self.fetcher = EarthEngineDataFetcher()
        print(f"✅ Loaded model from: {model_path}")
        print(f"✅ Using Google Cloud project: rockfall-project-492810")
    
    def predict(self, lat: float, lon: float) -> dict:
        """
        Make rockfall prediction for a given location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
        
        Returns:
            dict: Prediction results with probability and class
        """
        print(f"\n🌍 Fetching real-time data for ({lat}, {lon})...")
        
        # Fetch features from Earth Engine
        features = self.fetcher.fetch_point_features(lat, lon)
        
        # Prepare input for model
        prediction_input = self.fetcher.create_prediction_input(lat, lon)
        
        # Convert to numpy array
        X = np.array([[
            prediction_input['dem'],
            prediction_input['slope'],
            prediction_input['rainfall'],
            prediction_input['temperature'],
            prediction_input['ndvi']
        ]])
        
        print("🔮 Making prediction...")
        
        # Make prediction
        probability = self.model.predict_proba(X)[0, 1]
        prediction_class = int(probability >= 0.5)
        
        # Compile results
        results = {
            'location': {'latitude': lat, 'longitude': lon},
            'features': features,
            'prediction': {
                'probability': float(probability),
                'class': prediction_class,
                'risk_level': 'HIGH RISK' if prediction_class == 1 else 'LOW RISK'
            }
        }
        
        return results
    
    def print_results(self, results: dict):
        """Print prediction results in formatted way."""
        print("\n" + "=" * 60)
        print("ROCKFALL PREDICTION RESULTS")
        print("=" * 60)
        
        # Location
        loc = results['location']
        print(f"\n📍 Location: ({loc['latitude']:.4f}, {loc['longitude']:.4f})")
        
        # Features
        print("\n📊 Fetched Features:")
        feat = results['features']
        print(f"  Elevation:  {feat['elevation']:.2f} meters")
        print(f"  Slope:      {feat['slope']:.2f} degrees")
        print(f"  Rainfall:   {feat['rainfall']:.2f} mm/year")
        print(f"  Temperature: {feat['temperature']:.2f} K")
        print(f"  NDVI:       {feat['ndvi']:.4f}")
        
        # Prediction
        pred = results['prediction']
        print("\n🔮 Prediction:")
        print(f"  Probability: {pred['probability']:.4f}")
        print(f"  Class:       {pred['class']}")
        print(f"  Risk Level:  {pred['risk_level']}")
        
        print("=" * 60)
        
        # Risk assessment
        if pred['probability'] > 0.8:
            print("⚠️  WARNING: Very high rockfall risk detected!")
        elif pred['probability'] > 0.5:
            print("⚠️  CAUTION: Moderate rockfall risk detected.")
        else:
            print("✅ Low rockfall risk.")
        
        print("=" * 60)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Real-time rockfall prediction using Earth Engine'
    )
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--model', type=str, 
                       default='models/randomforest_tabular.joblib',
                       help='Path to trained model')
    
    args = parser.parse_args()
    
    print("🚀 Real-time Rockfall Prediction System")
    print("=" * 60)
    
    try:
        # Initialize predictor
        predictor = RealTimeRockfallPredictor(model_path=args.model)
        
        # Make prediction
        results = predictor.predict(args.lat, args.lon)
        
        # Print results
        predictor.print_results(results)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure trained model exists at specified path")
        print("2. Run: earthengine authenticate")
        print("3. Check internet connection")


if __name__ == "__main__":
    main()
