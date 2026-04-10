"""
Flask API Server for Rockfall Prediction
========================================

REST API server to handle prediction requests from React frontend.
Integrates with Earth Engine and trained ML models.

Features:
- Realistic feature values (cumulative rainfall, proper scaling)
- Physics-inspired risk scoring
- Normalized feature inputs
- High-risk detection in steep + rainy areas

Usage:
    python api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import ee
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Global predictor instance
predictor = None


class RockfallPredictor:
    """Rockfall prediction using Earth Engine and trained ML models."""
    
    def __init__(self, model_path="models/randomforest_tabular.joblib"):
        """Initialize predictor with trained model."""
        try:
            self.model = joblib.load(model_path)
            ee.Initialize(project='rockfall-project-492810')
            print("✅ Predictor initialized successfully")
        except Exception as e:
            print(f"⚠️ Model not found, using rule-based prediction only: {e}")
            self.model = None
    
    def fetch_features(self, lat, lon):
        """Fetch geospatial features from Earth Engine with realistic values."""
        point = ee.Geometry.Point([lon, lat])
        
        # DEM
        dem = ee.Image("USGS/SRTMGL1_003")
        elevation = dem.sample(point, 30).first().get("elevation").getInfo()
        
        # Slope
        slope = ee.Terrain.slope(dem)
        slope_val = slope.sample(point, 30).first().get("slope").getInfo()
        
        # Rainfall - CRITICAL FIX: Use cumulative sum instead of mean
        rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate('2022-01-01', '2022-12-31') \
                .sum()
        rain_val = rain.sample(point, 5000).first().get("precipitation").getInfo()
        
        # Temperature
        temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate('2022-01-01', '2022-12-31') \
                .select('temperature_2m') \
                .mean()
        temp_val = temp.sample(point, 1000).first().get("temperature_2m").getInfo()
        temp_celsius = temp_val - 273.15
        
        # NDVI
        try:
            s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterDate('2022-06-01', '2022-09-30') \
                    .filterBounds(point) \
                    .select(['B4', 'B8'])
            image = s2.median()
            ndvi = image.normalizedDifference(['B8', 'B4'])
            ndvi_val = ndvi.sample(point, 10).first().get("nd").getInfo()
            if ndvi_val is None or ndvi_val < -1 or ndvi_val > 1:
                ndvi_val = 0.3
        except:
            ndvi_val = 0.3
        
        # Handle missing/invalid values
        if elevation is None: elevation = 100.0
        if slope_val is None: slope_val = 5.0
        if rain_val is None: rain_val = 1000.0
        if temp_celsius is None: temp_celsius = 25.0
        if ndvi_val is None: ndvi_val = 0.3
        
        return {
            'elevation': elevation,
            'slope': slope_val,
            'rainfall': rain_val,
            'temperature': temp_celsius,
            'ndvi': ndvi_val
        }
    
    def normalize_features(self, features):
        """Normalize features to 0-1 scale for consistent scoring."""
        # Normalize each feature based on realistic ranges
        elevation_norm = min(features['elevation'] / 1000.0, 1.0)  # 0-1000m
        slope_norm = min(features['slope'] / 30.0, 1.0)  # 0-30°
        rainfall_norm = min(features['rainfall'] / 1500.0, 1.0)  # 0-1500mm/year
        ndvi_norm = max(0, min(features['ndvi'], 1.0))  # 0-1 (already normalized)
        
        return {
            'elevation_norm': elevation_norm,
            'slope_norm': slope_norm,
            'rainfall_norm': rainfall_norm,
            'ndvi_norm': ndvi_norm
        }
    
    def compute_risk_score(self, features, normalized):
        """Compute physics-inspired risk score."""
        # Risk factors:
        # - High slope increases risk
        # - High rainfall increases risk
        # - Low vegetation (NDVI) increases risk
        
        risk_score = (
            0.40 * normalized['slope_norm'] +      # 40% weight on slope
            0.35 * normalized['rainfall_norm'] +   # 35% weight on rainfall
            0.25 * (1 - normalized['ndvi_norm'])   # 25% weight on lack of vegetation
        )
        
        return risk_score
    
    def determine_risk_level(self, risk_score):
        """Determine risk level based on risk score."""
        if risk_score > 0.6:
            return "HIGH"
        elif risk_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def predict_risk(self, lat, lon):
        """Predict rockfall risk for given coordinates."""
        # Fetch raw features
        features = self.fetch_features(lat, lon)
        
        # Normalize features
        normalized = self.normalize_features(features)
        
        # Compute physics-inspired risk score
        risk_score = self.compute_risk_score(features, normalized)
        
        # Determine risk level
        risk_level = self.determine_risk_level(risk_score)
        
        # Try to use ML model if available
        ml_probability = 0.5  # Default neutral
        if self.model is not None:
            try:
                # Format features for model (use normalized values)
                X = np.array([[
                    normalized['elevation_norm'] * 1000,
                    normalized['slope_norm'] * 30,
                    normalized['rainfall_norm'] * 1500,
                    features['temperature'],
                    normalized['ndvi_norm']
                ]])
                ml_probability = self.model.predict_proba(X)[0, 1]
            except Exception as e:
                print(f"⚠️ ML prediction failed, using rule-based: {e}")
        
        # Combine ML probability with rule-based score
        # This gives us the best of both worlds
        final_probability = (ml_probability + risk_score) / 2.0
        
        return {
            'risk': risk_level,
            'probability': float(final_probability),
            'risk_score': float(risk_score),
            'features': {
                'elevation': round(features['elevation'], 1),
                'slope': round(features['slope'], 1),
                'rainfall': round(features['rainfall'], 1),
                'temperature': round(features['temperature'], 1),
                'ndvi': round(features['ndvi'], 3)
            },
            'normalized_features': {
                'elevation_norm': round(normalized['elevation_norm'], 3),
                'slope_norm': round(normalized['slope_norm'], 3),
                'rainfall_norm': round(normalized['rainfall_norm'], 3),
                'ndvi_norm': round(normalized['ndvi_norm'], 3)
            }
        }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'rockfall-prediction-api',
        'features': ['rule-based-scoring', 'ml-model', 'earth-engine-integration']
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Prediction endpoint."""
    try:
        data = request.json
        lat = data.get('lat')
        lon = data.get('lon')
        
        if lat is None or lon is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Make prediction
        result = predictor.predict_risk(lat, lon)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def initialize_predictor():
    """Initialize the global predictor instance."""
    global predictor
    try:
        predictor = RockfallPredictor()
        print("✅ Predictor initialized on startup")
        print("✅ Using cumulative rainfall (sum) instead of average")
        print("✅ Feature normalization enabled")
        print("✅ Physics-inspired risk scoring enabled")
    except Exception as e:
        print(f"❌ Failed to initialize predictor: {e}")
        raise


if __name__ == '__main__':
    initialize_predictor()
    app.run(host='0.0.0.0', port=5000, debug=True)
