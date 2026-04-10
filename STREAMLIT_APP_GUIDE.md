# Streamlit Rockfall Prediction App - User Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit folium streamlit-folium
```

### 2. Run the App
```bash
streamlit run streamlit_app.py
```

### 3. Open Browser
The app will automatically open in your default browser at:
```
http://localhost:8501
```

---

## 🎯 How to Use

### Step 1: View the Map
- The app displays an interactive map centered on India
- You can zoom, pan, and switch between different map layers (Terrain, Satellite)

### Step 2: Select Location
- **Click anywhere on the map** to select a location
- The latitude and longitude will be displayed below the map

### Step 3: Predict Risk
- Click the **"🔮 Predict Rockfall Risk"** button
- The app will:
  - Fetch real-time geospatial data from Google Earth Engine
  - Run the trained ML model
  - Display prediction results

### Step 4: View Results
- **Risk Level**: HIGH RISK (red) or LOW RISK (green)
- **Probability**: Percentage confidence of the prediction
- **Geospatial Features**: Elevation, slope, rainfall, temperature, NDVI
- **Risk Assessment**: Actionable recommendations

### Step 5: Updated Map
- A marker will be added to the clicked location
- Red marker = HIGH RISK
- Green marker = LOW RISK

---

## 🎨 Features

### Sidebar Settings
- **Model Selection**: Choose between RandomForest or Fusion model
- **Map Settings**: Adjust default location and zoom level

### Map Layers
- **OpenStreetMap**: Standard street map
- **Terrain**: Topographic map
- **Satellite**: Satellite imagery

### Prediction Display
- Color-coded risk levels
- Probability with progress bar
- Detailed feature breakdown
- Risk assessment messages

---

## 📊 Example Workflow

1. **Open the app**: `streamlit run streamlit_app.py`
2. **Navigate to mining area**: Use map controls to zoom to your region
3. **Click on location**: Select a specific point of interest
4. **Click predict**: Wait for Earth Engine data fetch and ML prediction
5. **Review results**: Check risk level and recommendations
6. **Repeat**: Click another location for additional predictions

---

## 🔧 Technical Details

### Data Sources
- **Elevation**: USGS SRTM (30m resolution)
- **Slope**: Derived from DEM
- **Rainfall**: CHIRPS Daily (0.05° resolution)
- **Temperature**: ERA5-Land (0.1° resolution)
- **NDVI**: Sentinel-2 (10m resolution)

### ML Model
- **Default**: RandomForest (Tabular features)
- **Alternative**: Fusion Model (Tabular + Image features)
- **Training Data**: 18,503 samples from Korba and Talcher regions

### Performance
- **Accuracy**: 98.3%
- **Precision**: 80.0%
- **Recall**: 96.0%

---

## ⚠️ Requirements

- Python 3.8 or higher
- Trained model in `models/` directory
- Google Earth Engine authentication
- Internet connection for real-time data fetching

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check if Streamlit is installed
pip show streamlit

# Reinstall if needed
pip install --upgrade streamlit
```

### Model loading error
```bash
# Ensure model file exists
ls models/randomforest_tabular.joblib

# If missing, run training script
python train_multimodal_sklearn.py
```

### Earth Engine error
```bash
# Re-authenticate
earthengine authenticate

# Test connection
python gee_test.py
```

### Map not displaying
- Check internet connection
- Try refreshing the browser
- Clear browser cache

---

## 🎯 Tips for Best Results

1. **Zoom in close**: Select specific points of interest
2. **Use Terrain layer**: Better for understanding slope
3. **Check NDVI**: Vegetation affects rockfall risk
4. **Monitor high-risk areas**: Pay attention to red markers
5. **Compare locations**: Test multiple points in same area

---

## 📱 Mobile Usage

The Streamlit app is responsive and works on mobile devices:
- Use touch to select locations
- Swipe to navigate the map
- Pinch to zoom in/out

---

## 🔒 Security Notes

- The app runs locally on your machine
- No data is sent to external servers (except Earth Engine API)
- Google Cloud project ID is required for Earth Engine access

---

## 🚀 Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

### Custom Server
```bash
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

---

## 📞 Support

For issues or questions:
1. Check the main README.md
2. Review COMPLETE_DOCUMENTATION.md
3. Check Earth Engine setup guide (EARTH_ENGINE_SETUP.md)

---

**Happy Predicting! 🌍⛰️🤖**
