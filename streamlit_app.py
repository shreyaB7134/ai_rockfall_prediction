"""
Streamlit App for Rockfall Risk Prediction
===========================================

Interactive web application with map interface for real-time
rockfall risk prediction using Earth Engine and ML models.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import joblib
import ee
import warnings
warnings.filterwarnings('ignore')


# Page configuration
st.set_page_config(
    page_title="Rockfall Risk Prediction",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)


class RockfallPredictor:
    """
    Rockfall prediction using Earth Engine and trained ML models.
    """
    
    def __init__(self, model_path="models/randomforest_tabular.joblib"):
        """Initialize predictor with trained model."""
        try:
            self.model = joblib.load(model_path)
            ee.Initialize(project='rockfall-project-492810')
        except Exception as e:
            st.error(f"Failed to initialize: {e}")
            raise
    
    def fetch_features(self, lat, lon):
        """Fetch geospatial features from Earth Engine."""
        point = ee.Geometry.Point([lon, lat])
        
        # DEM
        dem = ee.Image("USGS/SRTMGL1_003")
        elevation = dem.sample(point, 30).first().get("elevation").getInfo()
        
        # Slope
        slope = ee.Terrain.slope(dem)
        slope_val = slope.sample(point, 30).first().get("slope").getInfo()
        
        # Rainfall
        rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                .filterDate('2022-01-01', '2022-12-31') \
                .mean()
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
        except:
            ndvi_val = 0.0
        
        return {
            'elevation': elevation,
            'slope': slope_val,
            'rainfall': rain_val,
            'temperature': temp_celsius,
            'ndvi': ndvi_val
        }
    
    def predict_risk(self, lat, lon):
        """
        Predict rockfall risk for given coordinates.
        
        Returns:
            dict: {probability, risk_label, features}
        """
        features = self.fetch_features(lat, lon)
        
        # Format features for model
        X = np.array([[
            features['elevation'],
            features['slope'],
            features['rainfall'],
            features['temperature'],
            features['ndvi']
        ]])
        
        # Make prediction
        probability = self.model.predict_proba(X)[0, 1]
        risk_label = "HIGH RISK" if probability > 0.5 else "LOW RISK"
        
        return {
            'probability': float(probability),
            'risk_label': risk_label,
            'features': features
        }


def create_map(center_lat=20.5937, center_lon=78.9629, zoom=5):
    """
    Create folium map centered on India.
    
    Args:
        center_lat (float): Center latitude
        center_lon (float): Center longitude
        zoom (int): Initial zoom level
    
    Returns:
        folium.Map: Interactive map
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # Add layer control
    folium.TileLayer(
        tiles='Stamen Terrain',
        name='Terrain',
        attr='Stamen Terrain'
    ).add_to(m)
    folium.TileLayer(
        tiles='Stamen Satellite',
        name='Satellite',
        attr='Stamen Satellite'
    ).add_to(m)
    folium.LayerControl().add_to(m)
    
    return m


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("⛰️ Rockfall Risk Prediction")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        
        # Model selection
        model_option = st.selectbox(
            "Select Model",
            ["RandomForest (Tabular)", "Fusion Model"],
            index=0
        )
        
        if model_option == "RandomForest (Tabular)":
            model_path = "models/randomforest_tabular.joblib"
        else:
            model_path = "models/fusion_logreg.joblib"
        
        # Map settings
        st.subheader("🗺️ Map Settings")
        default_lat = st.number_input("Default Latitude", value=20.95, min_value=-90.0, max_value=90.0)
        default_lon = st.number_input("Default Longitude", value=85.10, min_value=-180.0, max_value=180.0)
        zoom_level = st.slider("Zoom Level", 1, 18, 5)
        
        st.markdown("---")
        st.info("💡 Click anywhere on the map to predict rockfall risk")
    
    # Initialize predictor
    @st.cache_resource
    def get_predictor(path):
        return RockfallPredictor(path)
    
    try:
        predictor = get_predictor(model_path)
        st.success("✅ Model loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load model: {e}")
        st.stop()
    
    # Create map
    m = create_map(default_lat, default_lon, zoom_level)
    
    # Display map
    st.subheader("📍 Interactive Map")
    map_data = st_folium(m, width=1200, height=500, returned_objects=True)
    
    # Get clicked location
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        
        st.markdown("---")
        st.subheader("🎯 Selected Location")
        st.write(f"**Latitude:** {clicked_lat:.4f}")
        st.write(f"**Longitude:** {clicked_lon:.4f}")
        
        # Predict button
        if st.button("🔮 Predict Rockfall Risk", use_container_width=True):
            with st.spinner("Fetching data and making prediction..."):
                try:
                    # Make prediction
                    result = predictor.predict_risk(clicked_lat, clicked_lon)
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📊 Prediction Results")
                    
                    # Risk level with color
                    if result['risk_label'] == "HIGH RISK":
                        st.error(f"### ⚠️ {result['risk_label']}")
                    else:
                        st.success(f"### ✅ {result['risk_label']}")
                    
                    # Probability
                    prob_percent = result['probability'] * 100
                    st.metric("Probability", f"{prob_percent:.2f}%")
                    
                    # Progress bar
                    st.progress(result['probability'])
                    
                    # Features
                    st.markdown("---")
                    st.subheader("🌍 Geospatial Features")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Elevation", f"{result['features']['elevation']:.1f} m")
                        st.metric("Slope", f"{result['features']['slope']:.1f}°")
                    with col2:
                        st.metric("Rainfall", f"{result['features']['rainfall']:.1f} mm/yr")
                        st.metric("Temperature", f"{result['features']['temperature']:.1f} °C")
                    with col3:
                        st.metric("NDVI", f"{result['features']['ndvi']:.3f}")
                    
                    # Risk assessment
                    st.markdown("---")
                    st.subheader("💡 Risk Assessment")
                    
                    if result['probability'] > 0.8:
                        st.warning("🚨 **Very High Risk** - Immediate action recommended!")
                    elif result['probability'] > 0.5:
                        st.info("⚠️ **Moderate Risk** - Monitor the area closely.")
                    else:
                        st.success("✅ **Low Risk** - Normal operations can continue.")
                    
                    # Add marker to map
                    marker_color = "red" if result['risk_label'] == "HIGH RISK" else "green"
                    folium.Marker(
                        location=[clicked_lat, clicked_lon],
                        popup=f"Risk: {result['risk_label']} ({prob_percent:.1f}%)",
                        icon=folium.Icon(color=marker_color, icon="mountain")
                    ).add_to(m)
                    
                    # Update map with marker
                    st.subheader("📍 Updated Map with Prediction")
                    st_folium(m, width=1200, height=500)
                    
                except Exception as e:
                    st.error(f"❌ Prediction failed: {e}")
    
    else:
        st.info("👆 Click on the map to select a location for prediction")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🌍 Powered by Google Earth Engine | 🤖 Machine Learning | ⛰️ Rockfall Prediction</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
