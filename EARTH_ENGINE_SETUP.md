# Google Earth Engine Integration Setup Guide

## 🚀 Phase 1: Setup Earth Engine API

This guide will help you set up Google Earth Engine API for real-time geospatial data fetching in your rockfall prediction system.

---

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection
- Google account (for Earth Engine authentication)
- **Earth Engine account signup** (see Step 0 below)

---

## 🔴 STEP 0: SIGN UP FOR EARTH ENGINE (CRITICAL)

Before installing anything, you must sign up for Google Earth Engine:

1. Visit: https://code.earthengine.google.com/
2. Click "Sign Up" 
3. Sign in with your Google account
4. Fill out the registration form
5. Wait for approval (usually instant for non-commercial use)
6. You'll receive an email when your account is ready

**⚠️ Without this step, Earth Engine will not work!**

---

## 🧩 Step 1: Install Required Tools

Open terminal/command prompt and run:

```bash
pip install earthengine-api
pip install geemap
pip install numpy pandas
```

**Expected Output**: Packages should install successfully without errors.

---

## 🔐 Step 2: Authentication (VERY IMPORTANT)

This is the most critical step. You need to authenticate your system with Google Earth Engine.

### Run Authentication Command:
```bash
earthengine authenticate
```

### What This Does:
1. Opens your default web browser
2. Asks you to sign in with your Google account
3. Requests permission to access Earth Engine
4. Provides an authentication code
5. Asks you to paste the code back in the terminal

### Example Process:
```
earthengine authenticate

Opening browser...
Please sign in with your Google account...
After authorization, paste the code here: 1/ABcDeFgHiJkLmNoPqRsTuVwXyZ
Successfully saved credentials
```

✅ **After successful authentication**, your system can access Earth Engine APIs.

---

## 🧠 Step 3: Test Initialization

Create and run the test script to verify Earth Engine is working.

### Test Script (`gee_test.py`):
```python
import ee

ee.Initialize()
print("✅ Earth Engine initialized successfully!")
```

### Run Test:
```bash
python gee_test.py
```

### Expected Output:
```
✅ Earth Engine initialized successfully!
```

❌ **If you get an error**, make sure you completed Step 2 (authentication).

---

## 🎯 Step 4: Test Data Fetching

Now test fetching real elevation data from a location.

### Test Script (`gee_fetch_features.py`):
```python
import ee

ee.Initialize()

# Example: Talcher location
lat = 20.95
lon = 85.10

point = ee.Geometry.Point([lon, lat])

# DEM dataset
dem = ee.Image("USGS/SRTMGL1_003")

# Get elevation value
value = dem.sample(point, 30).first().get("elevation")

print("Elevation:", value.getInfo())
```

### Run Test:
```bash
python gee_fetch_features.py
```

### Expected Output:
```
Elevation: 250 (example value)
```

✅ **Now you are fetching real data!** 🔥

---

## 🧠 Step 5: Fetch All Features

The complete script fetches all required features for rockfall prediction:

### Features Fetched:
- **DEM (Elevation)**: Terrain height in meters
- **Slope**: Terrain slope angle in degrees
- **Rainfall**: Annual precipitation from CHIRPS dataset
- **Temperature**: Surface temperature from ERA5 dataset
- **NDVI**: Vegetation index from Sentinel-2

### Complete Script (`gee_fetch_features.py`):
```python
import ee

ee.Initialize()

lat = 20.95
lon = 85.10

point = ee.Geometry.Point([lon, lat])

# DEM
dem = ee.Image("USGS/SRTMGL1_003")
elevation = dem.sample(point, 30).first().get("elevation")

# Slope
slope = ee.Terrain.slope(dem)
slope_val = slope.sample(point, 30).first().get("slope")

# Rainfall (CHIRPS)
rain = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate('2022-01-01', '2022-12-31') \
        .mean()

rain_val = rain.sample(point, 5000).first().get("precipitation")

# Temperature (ERA5)
temp = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
        .filterDate('2022-01-01', '2022-12-31') \
        .select('temperature_2m') \
        .mean()

temp_val = temp.sample(point, 1000).first().get("temperature_2m")

# NDVI (Sentinel)
s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterDate('2022-06-01', '2022-09-30') \
        .filterBounds(point) \
        .select(['B4', 'B8'])

image = s2.median()
ndvi = image.normalizedDifference(['B8', 'B4'])

ndvi_val = ndvi.sample(point, 10).first().get("nd")

# Print all
print("Elevation:", elevation.getInfo())
print("Slope:", slope_val.getInfo())
print("Rainfall:", rain_val.getInfo())
print("Temperature:", temp_val.getInfo())
print("NDVI:", ndvi_val.getInfo())
```

### Run Complete Test:
```bash
python gee_fetch_features.py
```

### Expected Output:
```
Elevation: 250.5
Slope: 15.2
Rainfall: 1200.8
Temperature: 300.5
NDVI: 0.45
```

---

## 🎯 What You Have Now

After completing these steps, you have:

```
User Input (lat, lon)
        ↓
Earth Engine API
        ↓
Real-time Data Fetching
        ↓
Features: elevation, slope, rainfall, temperature, ndvi
        ↓
Model Input (exactly what your model needs!)
        ↓
Rockfall Prediction
```

---

## 🚀 Next Steps

### Option A: Single Point Prediction
Use real-time data to predict rockfall risk for specific locations:

```bash
python realtime_prediction.py --lat 20.95 --lon 85.10
```

### Option B: Area Analysis
Fetch data for entire regions and generate risk maps:

```python
from earth_engine_integration import EarthEngineDataFetcher

fetcher = EarthEngineDataFetcher()
region_data = fetcher.fetch_area_features(region_coords)
```

### Option C: Batch Processing
Process multiple locations automatically:

```python
coordinates = [(20.95, 85.10), (21.20, 82.50), ...]
results = fetcher.fetch_multiple_points(coordinates)
```

---

## ⚠️ Important Notes

### Data Sources Used:
- **DEM**: USGS SRTM (30m resolution)
- **Rainfall**: CHIRPS Daily (0.05° resolution)
- **Temperature**: ERA5-Land (0.1° resolution)
- **NDVI**: Sentinel-2 (10m resolution)

### Limitations:
- **Internet Required**: Real-time fetching needs internet connection
- **API Limits**: Earth Engine has usage limits (generous for research)
- **Data Freshness**: Some datasets may have 1-2 day latency
- **Coverage**: Some areas may have limited data availability

### Troubleshooting:

**Error: "Earth Engine initialization failed"**
- Run: `earthengine authenticate`
- Complete browser authentication
- Check internet connection

**Error: "No data found for location"**
- Verify coordinates are correct
- Check if area is covered by datasets
- Try nearby locations

**Error: "Quota exceeded"**
- Wait a few minutes and retry
- Reduce request frequency
- Contact Earth Engine support for increased quota

---

## 📚 Additional Resources

- **Earth Engine Documentation**: https://developers.google.com/earth-engine
- **Earth Engine Data Catalog**: https://developers.google.com/earth-engine/datasets
- **geemap Documentation**: https://geemap.org/

---

## ✅ Setup Checklist

- [ ] Install earthengine-api and geemap
- [ ] Run `earthengine authenticate`
- [ ] Complete browser authentication
- [ ] Test with `gee_test.py`
- [ ] Test data fetching with `gee_fetch_features.py`
- [ ] Test integration with `earth_engine_integration.py`
- [ ] Test real-time prediction with `realtime_prediction.py`

---

**🎉 Congratulations!** You now have a fully functional real-time geospatial data fetching system integrated with your rockfall prediction models!
