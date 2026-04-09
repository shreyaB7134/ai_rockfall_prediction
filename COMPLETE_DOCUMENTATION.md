# Rockfall Prediction System - Complete Technical Documentation

**Version:** 1.0  
**Date:** April 2026  
**Authors:** Geospatial AI Development Team  
**Repository:** https://github.com/shreyaB7134/ai_rockfall_prediction

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Processing Pipeline](#3-data-processing-pipeline)
4. [Machine Learning Models](#4-machine-learning-models)
5. [Implementation Details](#5-implementation-details)
6. [Results and Performance](#6-results-and-performance)
7. [Installation and Setup](#7-installation-and-setup)
8. [Usage Instructions](#8-usage-instructions)
9. [File Structure](#9-file-structure)
10. [Technical Specifications](#10-technical-specifications)
11. [Future Enhancements](#11-future-enhancements)
12. [Troubleshooting](#12-troubleshooting)
13. [References](#13-references)

---

## 1. Project Overview

### 1.1 Objective

Develop a comprehensive multimodal machine learning system for predicting rockfall risk in open-pit mines using geospatial data, terrain analysis, climate data, and satellite imagery.

### 1.2 Problem Statement

Rockfall events in open-pit mines pose significant safety risks to personnel and equipment. Traditional risk assessment methods are often subjective, time-consuming, and lack the ability to process large-scale geospatial data efficiently. This project aims to leverage artificial intelligence and machine learning to create an automated, data-driven rockfall prediction system.

### 1.3 Key Features

- **Multimodal Data Integration**: Combines tabular (terrain + climate), image (NDVI patches), and temporal data
- **Automated Pipeline**: End-to-end processing from raw GeoTIFF files to trained models
- **Physics-Informed Labeling**: Uses Factor of Safety (FS) proxy for realistic risk labeling
- **Multiple Model Architectures**: Supports both traditional ML (RandomForest) and deep learning (CNN) approaches
- **Fusion Learning**: Combines multiple modalities for improved prediction accuracy
- **Scalable Design**: Handles multiple mining regions with different data formats

### 1.4 Target Applications

- Real-time rockfall risk monitoring
- Mine safety planning and hazard mitigation
- Emergency response planning
- Operational decision support
- Historical risk analysis

---

## 2. System Architecture

### 2.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Rockfall Prediction System                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Data       │    │  Processing  │    │   ML Models  │  │
│  │   Ingestion  │───▶│   Pipeline   │───▶│   Training   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  GeoTIFF     │    │  Alignment   │    │  RandomForest│  │
│  │  Files       │    │  Resampling  │    │  CNN         │  │
│  │  (DEM,       │    │  Feature     │    │  Fusion      │  │
│  │   Slope,     │    │  Extraction  │    │  Models      │  │
│  │   Climate,   │    │  Labeling    │    │              │  │
│  │   NDVI)      │    │              │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Input**: Raw GeoTIFF files from multiple regions
2. **Processing**: Raster alignment, feature extraction, label generation
3. **Training**: Multiple model architectures with cross-validation
4. **Output**: Trained models, predictions, risk maps

### 2.3 Component Breakdown

#### 2.3.1 Data Processing Module
- **Input**: GeoTIFF raster files
- **Processing**: Alignment, resampling, feature extraction
- **Output**: Structured datasets for ML training

#### 2.3.2 Label Generation Module
- **Input**: Tabular features
- **Processing**: Physics-based FS proxy calculation
- **Output**: Binary and multi-class risk labels

#### 2.3.3 Model Training Module
- **Input**: Labeled datasets
- **Processing**: Multiple model architectures
- **Output**: Trained models with performance metrics

#### 2.3.4 Fusion Module
- **Input**: Predictions from multiple models
- **Processing**: Ensemble learning
- **Output**: Combined predictions

---

## 3. Data Processing Pipeline

### 3.1 Overview

The data processing pipeline consists of 6 sequential steps that transform raw geospatial data into machine learning-ready datasets.

### 3.2 Step 1: Data Loading and Alignment

#### 3.2.1 Purpose
Load all GeoTIFF files from multiple regions and ensure spatial alignment.

#### 3.2.2 Input Data
- **DEM (Digital Elevation Model)**: Terrain elevation data
- **Slope**: Derived terrain slope angles
- **Rainfall**: Precipitation measurements
- **Temperature**: Surface temperature data
- **NDVI**: Normalized Difference Vegetation Index

#### 3.2.3 Processing Details

**File Naming Conventions**
- Korba region: `DEM_Korba.tif`, `Slope_Korba.tif`, etc.
- Talcher region: `DEM_Talcher.tif`, `Slope_Talcher.tif`, etc.

**Alignment Process**
1. Load all rasters using `rasterio`
2. Check spatial resolution and extent
3. Identify reference raster (typically DEM)
4. Resample mismatched rasters using bilinear interpolation
5. Ensure consistent Coordinate Reference System (CRS)

**Technical Implementation**
```python
# Key operations
- Rasterio for GeoTIFF reading
- Rasterio.warp.reproject for resampling
- Bilinear resampling for continuous data
- CRS validation and transformation
```

#### 3.2.4 Output
- Aligned rasters with consistent resolution and extent
- Metadata including transform, CRS, and nodata values

### 3.3 Step 2: Tabular Data Creation

#### 3.3.1 Purpose
Extract pixel-wise values from all rasters and create a structured tabular dataset.

#### 3.3.2 Processing Steps

**Coordinate Generation**
- Convert pixel coordinates to geographic coordinates (lat/lon)
- Use raster transform for accurate georeferencing
- Generate coordinate grids for entire raster extent

**Feature Extraction**
- Flatten raster grids into 1D arrays
- Extract values for each pixel location
- Create feature columns: lat, lon, dem, slope, rainfall, temperature, ndvi

**Data Cleaning**
- Replace common nodata values (-9999, -999, -32768) with NaN
- Remove pixels with any missing values
- Calculate data retention statistics

#### 3.3.3 Output Format
```csv
lat,lon,dem,slope,rainfall,temperature,ndvi
22.599546,82.500388,672,18.159536,1451.929129,24.945824,0.382862
22.599546,82.500658,676,20.190853,1451.522366,24.945824,0.401718
...
```

#### 3.3.4 Statistics
- **Korba**: 2,728,458 valid pixels (79.2% retention)
- **Talcher**: 3,426,104 valid pixels (99.4% retention)

### 3.4 Step 3: Image Data Extraction (CNN Input)

#### 3.4.1 Purpose
Extract NDVI image patches for convolutional neural network processing.

#### 3.4.2 Patch Extraction Process

**Patch Parameters**
- **Size**: 32×32 pixels
- **Sampling**: Regular interval sampling to avoid excessive patches
- **Margin**: 16 pixels from edges to ensure complete patches

**Extraction Algorithm**
1. Calculate valid patch center coordinates
2. Extract 32×32 patches around each center
3. Skip patches containing invalid/NaN values
4. Store patches as numpy arrays
5. Record center coordinates for alignment with tabular data

#### 3.4.3 Output Structure
```python
patches: (N, 32, 32)  # N patches, 32x32 pixels each
centers: (N, 2)       # (lon, lat) for each patch center
```

#### 3.4.4 Statistics
- **Korba**: 8,192 patches
- **Talcher**: 10,331 patches
- **Total**: 18,523 patches for training

### 3.5 Step 4: Temporal Feature Generation

#### 3.5.1 Purpose
Create temporal features from rainfall and temperature data to capture time-series patterns.

#### 3.5.2 Feature Engineering

**Rainfall Features**
- `rainfall_current`: Current rainfall measurement
- `rainfall_3day`: 3-day cumulative rainfall (current × 3)
- `rainfall_7day`: 7-day cumulative rainfall (current × 7)
- `rainfall_intensity`: Binary indicator for high rainfall (>75th percentile)

**Temperature Features**
- `temperature_current`: Current temperature measurement
- `temperature_mean`: Mean temperature (same as current for single time point)
- `temperature_stress`: Binary indicator for high temperature (>90th percentile)

#### 3.5.3 Rationale
- Cumulative rainfall captures saturation effects
- High rainfall intensity indicates flash flood risk
- Temperature stress affects rock stability through thermal expansion

### 3.6 Step 5: Physics-Informed Label Generation

#### 3.6.1 Purpose
Generate realistic risk labels using a physics-inspired Factor of Safety (FS) proxy.

#### 3.6.2 Factor of Safety Theory

**Traditional FS Formula**
```
FS = Resisting Forces / Driving Forces
```

**Our Proxy Formula**
```
FS_proxy = (0.4 × NDVI_norm + 0.3 × Elevation_norm) / 
           (0.2 × Slope_norm + 0.3 × Rainfall_norm + 0.01)
```

**Component Interpretation**
- **NDVI_norm**: Vegetation stabilizes slopes (resisting force)
- **Elevation_norm**: Higher elevation may indicate more stable rock (resisting force)
- **Slope_norm**: Steeper slopes increase instability (driving force)
- **Rainfall_norm**: Water reduces friction (driving force)
- **0.01**: Constant to prevent division by zero

#### 3.6.3 Normalization Process

**Min-Max Normalization**
```
value_norm = (value - min) / (max - min)
```

**Applied to**
- Slope
- Rainfall
- NDVI
- Elevation (DEM)

#### 3.6.4 Label Classification

**Binary Labels**
- `risk_label = 1` (High Risk): FS_proxy < 1.0
- `risk_label = 0` (Low Risk): FS_proxy ≥ 1.0

**Multi-class Labels**
- `risk_class = "High Risk"`: FS_proxy < 0.8
- `risk_class = "Medium Risk"`: 0.8 ≤ FS_proxy ≤ 1.2
- `risk_class = "Low Risk"`: FS_proxy > 1.2

#### 3.6.5 Class Distribution
- **Stable (0)**: 17,369 samples (93.9%)
- **Unstable (1)**: 1,134 samples (6.1%)

### 3.7 Step 6: Multimodal Model Training

#### 3.7.1 Purpose
Train machine learning models using multiple data modalities and combine them for improved prediction.

#### 3.7.2 Training Approaches

**Approach 1: sklearn-only (No TensorFlow)**
- Tabular: RandomForest
- Image: PCA + RandomForest
- Fusion: Logistic Regression

**Approach 2: Deep Learning (with TensorFlow)**
- Tabular: RandomForest
- Image: CNN
- Fusion: Logistic Regression

---

## 4. Machine Learning Models

### 4.1 Tabular Model (RandomForest)

#### 4.1.1 Architecture
```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)
```

#### 4.1.2 Input Features
- DEM (elevation)
- Slope
- Rainfall
- Temperature
- NDVI

#### 4.1.3 Advantages
- Handles non-linear relationships
- Robust to outliers
- Provides feature importance
- Works well with small datasets

#### 4.1.4 Performance
- **Accuracy**: 98.3%
- **Precision**: 80.0%
- **Recall**: 96.0%
- **F1-Score**: 87.0%

### 4.2 Image Model (CNN)

#### 4.2.1 Architecture
```
Input (32, 32, 1)
    ↓
Conv2D(32, 3×3) + ReLU
    ↓
MaxPooling2D(2×2)
    ↓
Conv2D(64, 3×3) + ReLU
    ↓
MaxPooling2D(2×2)
    ↓
Flatten
    ↓
Dense(64) + ReLU
    ↓
Dropout(0.5)
    ↓
Dense(1) + Sigmoid
    ↓
Output (probability)
```

#### 4.2.2 Preprocessing
- Normalize NDVI values to [0, 1] range
- Reshape to (N, 32, 32, 1) for CNN input
- Per-sample normalization to handle varying NDVI ranges

#### 4.2.3 Training Configuration
- **Loss**: Binary cross-entropy
- **Optimizer**: Adam (learning_rate=1e-3)
- **Metrics**: Accuracy, Precision, Recall
- **Epochs**: 15 (with early stopping)
- **Batch Size**: 32
- **Callbacks**: Early stopping, learning rate reduction

#### 4.2.4 Advantages
- Learns spatial patterns from NDVI patches
- Automatic feature extraction
- Handles translation invariance
- State-of-the-art for image classification

### 4.3 Alternative Image Model (PCA + RandomForest)

#### 4.3.1 Architecture
```python
Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=50)),
    ('rf', RandomForestClassifier(n_estimators=150))
])
```

#### 4.3.2 Process
1. Flatten 32×32 patches to 1024-dimensional vectors
2. Standardize features
3. Reduce dimensionality with PCA (50 components)
4. Train RandomForest on reduced features

#### 4.3.3 Performance
- **Accuracy**: 83.8%
- **Precision**: 20.7%
- **Recall**: 57.7%
- **F1-Score**: 30.0%

#### 4.3.4 Limitations
- Loses spatial information
- Lower precision on minority class
- Requires manual feature engineering

### 4.4 Fusion Model

#### 4.4.1 Purpose
Combine predictions from tabular and image models for improved performance.

#### 4.4.2 Architecture
```python
Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    ))
])
```

#### 4.4.3 Input Features
- Tabular model probability (P_risk|tabular)
- Image model probability (P_risk|image)

#### 4.4.4 Training Process
1. Get probability predictions from both models on training data
2. Stack probabilities as feature vectors
3. Train Logistic Regression to combine them
4. Apply same transformation to test data

#### 4.4.5 Performance (sklearn version)
- **Accuracy**: 98.5%
- **Precision**: 82.2%
- **Recall**: 95.6%
- **F1-Score**: 88.0%

#### 4.4.6 Benefits
- Leverages strengths of both modalities
- Simple and interpretable
- Improves over individual models
- Robust to modality-specific failures

---

## 5. Implementation Details

### 5.1 Code Structure

#### 5.1.1 Main Pipeline Script
**File**: `rockfall_pipeline.py`

**Classes**:
- `RockfallDataPipeline`: Main pipeline orchestrator

**Key Methods**:
- `load_all_rasters()`: Load GeoTIFF files
- `check_alignment()`: Verify raster alignment
- `resample_to_match()`: Align mismatched rasters
- `create_tabular_dataset()`: Extract tabular features
- `extract_ndvi_patches()`: Create image patches
- `create_temporal_features()`: Generate temporal features
- `add_fs_proxy_labels()`: Physics-informed labeling
- `run_complete_pipeline()`: Execute full pipeline
- `save_processed_data()`: Save processed datasets

#### 5.1.2 Training Scripts

**sklearn Version**: `train_multimodal_sklearn.py`
- Uses only scikit-learn
- No TensorFlow required
- RandomForest for both tabular and image models
- Logistic Regression for fusion

**CNN Version**: `train_multimodal_cnn.py`
- Requires TensorFlow/Keras
- CNN architecture for image model
- Same tabular and fusion approach
- Enhanced metrics and callbacks

#### 5.1.3 Visualization Script
**File**: `data_visualizer.py`

**Classes**:
- `RockfallDataVisualizer`: Visualization and validation

**Key Methods**:
- `plot_raster_overview()`: Display all raster layers
- `plot_data_distribution()`: Feature distribution plots
- `plot_correlation_matrix()`: Feature correlation heatmap
- `plot_ndvi_patches_sample()`: Sample NDVI patches
- `plot_temporal_features()`: Temporal feature visualization
- `generate_data_quality_report()`: Comprehensive quality report

### 5.2 Data Alignment Strategy

#### 5.2.1 Reference Selection
- DEM used as reference raster
- Highest resolution among all layers
- Complete coverage of study area

#### 5.2.2 Resampling Method
- **Bilinear interpolation** for continuous data
- Preserves general trends
- Computationally efficient
- Suitable for elevation, slope, climate data

#### 5.2.3 Coordinate System
- All rasters converted to matching CRS
- Geographic coordinates (lat/lon) for tabular data
- Pixel coordinates for patch extraction

### 5.3 Memory Management

#### 5.3.1 Large File Handling
- **Chunked CSV reading**: Process 250,000 rows at a time
- **Lazy loading**: Load only required data
- **Memory mapping**: Use numpy memory mapping for large arrays

#### 5.3.2 Optimization Techniques
- **Coordinate rounding**: Reduce precision for matching
- **Set-based lookups**: O(1) coordinate matching
- **Selective loading**: Load only matching rows

### 5.4 Reproducibility

#### 5.4.1 Random Seed Setting
```python
def set_seed(seed=42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
```

#### 5.4.2 Deterministic Operations
- Fixed train/test split with stratification
- Consistent preprocessing order
- Deterministic model initialization

---

## 6. Results and Performance

### 6.1 Model Comparison (sklearn Version)

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| RandomForest (Tabular) | 98.3% | 80.0% | 96.0% | 87.0% |
| PCA+RF (Image) | 83.8% | 20.7% | 57.7% | 30.0% |
| Fusion (Combined) | 98.5% | 82.2% | 95.6% | 88.0% |

### 6.2 Key Findings

#### 6.2.1 Tabular Model Performance
- Excellent overall accuracy (98.3%)
- High recall (96.0%) - catches most unstable cases
- Good precision (80.0%) - reasonable false positive rate
- Terrain and climate features are highly predictive

#### 6.2.2 Image Model Performance
- Lower accuracy (83.8%) compared to tabular
- Poor precision (20.7%) - many false positives
- Moderate recall (57.7%) - misses some unstable cases
- NDVI patches alone are insufficient for reliable prediction

#### 6.2.3 Fusion Model Performance
- Best overall accuracy (98.5%)
- Improved precision (82.2%) over tabular alone
- Maintained high recall (95.6%)
- Best F1-score (88.0%) - balanced performance

### 6.3 Class Imbalance Handling

#### 6.3.1 Imbalance Ratio
- Stable: 17,369 (93.9%)
- Unstable: 1,134 (6.1%)
- Ratio: 15.3:1

#### 6.3.2 Mitigation Strategies
- **Class weighting**: `class_weight='balanced'` in all models
- **Stratified splitting**: Maintain ratio in train/test
- **Precision-recall focus**: Monitor both metrics
- **Threshold tuning**: Adjust decision threshold if needed

### 6.4 Feature Importance (RandomForest)

Based on the RandomForest model, the most important features for rockfall prediction are:

1. **Slope**: Steeper slopes increase risk
2. **Elevation**: Higher elevation correlates with stability
3. **Rainfall**: Water saturation reduces stability
4. **NDVI**: Vegetation provides stabilizing effect
5. **Temperature**: Thermal effects on rock stability

### 6.5 Regional Performance

#### 6.5.1 Korba Region
- **Samples**: 8,192 patches matched
- **Characteristics**: Higher elevation, steeper slopes
- **Risk Level**: Moderate to high instability

#### 6.5.2 Talcher Region
- **Samples**: 10,311 patches matched
- **Characteristics**: Lower elevation, gentler slopes
- **Risk Level**: Generally more stable

---

## 7. Installation and Setup

### 7.1 System Requirements

#### 7.1.1 Hardware
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB minimum, 16GB recommended for large datasets
- **Storage**: 10GB+ free space for data and models
- **GPU**: Optional (for CNN training acceleration)

#### 7.1.2 Software
- **Python**: 3.8 or higher
- **Operating System**: Windows, Linux, or macOS
- **Package Manager**: pip or conda

### 7.2 Dependencies

#### 7.2.1 Core Dependencies
```txt
numpy>=1.21.0
pandas>=1.3.0
rasterio>=1.3.0
geopandas>=0.11.0
```

#### 7.2.2 Machine Learning Dependencies
```txt
scikit-learn>=1.1.0
xgboost>=1.5.0
tensorflow>=2.9.0
```

#### 7.2.3 Visualization Dependencies
```txt
matplotlib>=3.5.0
seaborn>=0.11.0
```

#### 7.2.4 Utility Dependencies
```txt
joblib>=1.1.0
```

### 7.3 Installation Steps

#### 7.3.1 Clone Repository
```bash
git clone https://github.com/shreyaB7134/ai_rockfall_prediction.git
cd ai_rockfall_prediction
```

#### 7.3.2 Install Dependencies

**Option 1: Using pip**
```bash
pip install -r requirements.txt
```

**Option 2: Using conda**
```bash
conda create -n rockfall python=3.8
conda activate rockfall
pip install -r requirements.txt
```

**Option 3: Minimal installation (sklearn only)**
```bash
pip install numpy pandas rasterio geopandas scikit-learn joblib matplotlib seaborn
```

### 7.4 Data Setup

#### 7.4.1 Directory Structure
```
ai_rockfall_prediction/
├── datasets/
│   ├── korba/
│   │   ├── DEM_Korba.tif
│   │   ├── Slope_Korba.tif
│   │   ├── Rainfall_Korba_2022.tif
│   │   ├── Temperature_Korba_2022.tif
│   │   └── NDVI_Korba_2022.tif
│   └── talcher_data/
│       ├── DEM_Talcher.tif
│       ├── Slope_Talcher.tif
│       ├── Rainfall_Talcher_2022.tif
│       ├── Temperature_Talcher_2022.tif
│       └── NDVI_Talcher_2022.tif
```

#### 7.4.2 Data Preparation
1. Place GeoTIFF files in appropriate directories
2. Ensure file naming matches expected patterns
3. Verify all rasters have valid CRS information
4. Check for missing or corrupted files

---

## 8. Usage Instructions

### 8.1 Running the Complete Pipeline

#### 8.1.1 Basic Usage
```bash
python rockfall_pipeline.py
```

#### 8.1.2 Expected Output
- Processed data in `processed_data/` directory
- Labeled CSV files for each region
- NDVI patch arrays and center coordinates
- Temporal feature arrays
- Pipeline summary statistics

### 8.2 Training Models

#### 8.2.1 sklearn-only Training
```bash
python train_multimodal_sklearn.py
```

**Advantages**:
- No TensorFlow required
- Faster training
- Lower memory usage
- Works with limited resources

#### 8.2.2 CNN Training
```bash
python train_multimodal_cnn.py
```

**Requirements**:
- TensorFlow installed
- More memory (8GB+ recommended)
- Longer training time
- GPU recommended for speed

### 8.3 Generating Visualizations

#### 8.3.1 Complete Visualization Suite
```python
from data_visualizer import RockfallDataVisualizer
import pickle

# Load processed data
with open("processed_data/processed_data.pkl", "rb") as f:
    processed_data = pickle.load(f)

# Create visualizer
visualizer = RockfallDataVisualizer(processed_data)
visualizer.create_all_visualizations()
```

#### 8.3.2 Individual Visualizations
```python
# Raster overview
visualizer.plot_raster_overview("korba")

# Data distribution
visualizer.plot_data_distribution("korba")

# Correlation matrix
visualizer.plot_correlation_matrix("korba")

# NDVI patches
visualizer.plot_ndvi_patches_sample("korba")

# Temporal features
visualizer.plot_temporal_features("korba")

# Quality report
visualizer.generate_data_quality_report("korba")
```

### 8.4 Making Predictions

#### 8.4.1 Load Trained Models
```python
import joblib
import tensorflow as tf

# Load tabular model
rf_model = joblib.load("models/randomforest_tabular.joblib")

# Load CNN model (if available)
cnn_model = tf.keras.models.load_model("models/cnn_ndvi.keras")

# Load fusion model
fusion_model = joblib.load("models/fusion_logreg.joblib")
```

#### 8.4.2 Prepare Input Data
```python
# Tabular features
X_tab = [[elevation, slope, rainfall, temperature, ndvi]]

# Image patches
X_img = patch_array.reshape(1, 32, 32, 1)
X_img = normalize_ndvi_patches(X_img)
```

#### 8.4.3 Make Predictions
```python
# Tabular prediction
rf_proba = rf_model.predict_proba(X_tab)[:, 1]

# CNN prediction (if available)
cnn_proba = cnn_model.predict(X_img).reshape(-1)

# Fusion prediction
X_fuse = np.vstack([rf_proba, cnn_proba]).T
fusion_proba = fusion_model.predict_proba(X_fuse)[:, 1]
```

### 8.5 Custom Configuration

#### 8.5.1 Modify Pipeline Parameters
```python
from rockfall_pipeline import RockfallDataPipeline

# Initialize with custom data directory
pipeline = RockfallDataPipeline(data_dir="custom_data_path")

# Run with custom patch size
processed_data = pipeline.run_complete_pipeline(patch_size=64)

# Save to custom location
pipeline.save_processed_data(processed_data, output_dir="custom_output")
```

#### 8.5.2 Modify Training Parameters
```python
# In train_multimodal_sklearn.py or train_multimodal_cnn.py

# Custom regions
run_training(regions=["korba"], seed=123, test_size=0.3)

# Custom epochs for CNN
run_training(epochs=20)
```

---

## 9. File Structure

### 9.1 Project Directory Layout

```
ai_rockfall_prediction/
├── datasets/                          # Raw GeoTIFF data
│   ├── korba/
│   └── talcher_data/
├── processed_data/                    # Processed datasets
│   ├── tabular_korba.csv
│   ├── tabular_korba_labeled.csv
│   ├── tabular_talcher_data.csv
│   ├── tabular_talcher_data_labeled.csv
│   ├── ndvi_patches_korba.npz
│   ├── ndvi_patches_talcher_data.npz
│   ├── patch_centers_korba.npz
│   ├── patch_centers_talcher_data.npz
│   ├── temporal_korba.npz
│   ├── temporal_talcher_data.npz
│   └── processed_data.pkl
├── models/                           # Trained models
│   ├── randomforest_tabular.joblib
│   ├── patch_model_pca_rf.joblib
│   ├── cnn_ndvi.keras
│   ├── fusion_logreg.joblib
│   └── cnn_training_history.npy
├── visualizations/                   # Generated plots
│   ├── korba/
│   └── talcher_data/
├── rockfall_pipeline.py             # Main pipeline script
├── train_multimodal_sklearn.py       # sklearn training script
├── train_multimodal_cnn.py           # CNN training script
├── train_multimodal.py               # Original XGBoost+TensorFlow script
├── data_visualizer.py                # Visualization tools
├── demo.py                           # Demonstration script
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── COMPLETE_DOCUMENTATION.md          # This file
└── .gitignore                        # Git ignore rules
```

### 9.2 File Descriptions

#### 9.2.1 Core Scripts
- **rockfall_pipeline.py**: Main data processing pipeline
- **train_multimodal_sklearn.py**: sklearn-only model training
- **train_multimodal_cnn.py**: CNN-based model training
- **data_visualizer.py**: Data visualization and validation

#### 9.2.2 Utility Scripts
- **demo.py**: Complete demonstration of pipeline functionality
- **train_multimodal.py**: Original XGBoost+TensorFlow implementation

#### 9.2.3 Documentation
- **README.md**: Quick start guide and overview
- **COMPLETE_DOCUMENTATION.md**: Comprehensive technical documentation
- **requirements.txt**: Python package dependencies

#### 9.2.4 Data Files
- **datasets/**: Raw GeoTIFF raster files
- **processed_data/**: Processed datasets and labels
- **models/**: Trained machine learning models
- **visualizations/**: Generated plots and analysis

---

## 10. Technical Specifications

### 10.1 Data Specifications

#### 10.1.1 Input Data Format
- **File Format**: GeoTIFF (.tif)
- **Coordinate System**: Geographic (lat/lon) or projected
- **Data Type**: Float32 or Int16
- **Nodata Values**: -9999, -999, -32768 (common conventions)

#### 10.1.2 Raster Specifications
- **DEM Resolution**: ~0.00027 degrees (~30 meters)
- **Slope Resolution**: Same as DEM
- **Climate Resolution**: Variable (resampled to match DEM)
- **NDVI Resolution**: ~0.00009 degrees (~10 meters, resampled)

#### 10.1.3 Output Data Format
- **Tabular**: CSV with lat, lon, features, labels
- **Image**: NumPy arrays (.npz format)
- **Temporal**: NumPy arrays (.npz format)
- **Models**: Joblib (.joblib) or Keras (.keras)

### 10.2 Model Specifications

#### 10.2.1 RandomForest Parameters
```python
n_estimators: 200
max_depth: 10
min_samples_split: 10
min_samples_leaf: 5
class_weight: balanced
random_state: 42
n_jobs: -1
```

#### 10.2.2 CNN Architecture
```
Input: (32, 32, 1)
Conv2D: 32 filters, 3×3 kernel, ReLU activation
MaxPooling2D: 2×2 pool size
Conv2D: 64 filters, 3×3 kernel, ReLU activation
MaxPooling2D: 2×2 pool size
Flatten
Dense: 64 units, ReLU activation
Dropout: 0.5
Dense: 1 unit, Sigmoid activation
```

#### 10.2.3 Training Parameters
```python
Loss: binary_crossentropy
Optimizer: Adam (lr=1e-3)
Metrics: accuracy, precision, recall
Epochs: 15 (with early stopping)
Batch size: 32
Validation split: 0.2
Early stopping patience: 5
Learning rate reduction factor: 0.5
```

### 10.3 Performance Metrics

#### 10.3.1 Evaluation Metrics
- **Accuracy**: Overall correctness
- **Precision**: True positive rate (minimize false alarms)
- **Recall**: True positive rate (catch all unstable cases)
- **F1-Score**: Harmonic mean of precision and recall

#### 10.3.2 Baseline Performance
- **Random guessing**: 50% accuracy (binary)
- **Majority class**: 93.9% accuracy (always predict stable)
- **Our models**: 98.5% accuracy (significant improvement)

### 10.4 Computational Requirements

#### 10.4.1 Processing Time Estimates
- **Data loading**: 2-5 minutes per region
- **Alignment/resampling**: 5-10 minutes per region
- **Tabular extraction**: 1-2 minutes per region
- **Patch extraction**: 2-3 minutes per region
- **Label generation**: <1 minute per region
- **Model training**: 5-15 minutes (sklearn), 15-30 minutes (CNN)

#### 10.4.2 Memory Usage
- **Pipeline**: 2-4 GB RAM
- **sklearn training**: 4-8 GB RAM
- **CNN training**: 8-16 GB RAM
- **Storage**: 500 MB - 2 GB for processed data

---

## 11. Future Enhancements

### 11.1 Data Improvements

#### 11.1.1 Additional Data Sources
- **Historical rockfall records**: Actual event data for supervised learning
- **Lithology maps**: Rock type information for improved physics modeling
- **Seismic data**: Ground vibration monitoring
- **Weather forecasts**: Real-time risk prediction
- **LiDAR data**: High-resolution terrain models

#### 11.1.2 Temporal Data Enhancement
- **Time-series climate data**: Actual historical rainfall/temperature
- **Seasonal patterns**: Monthly/seasonal risk variations
- **Real-time monitoring**: Live data integration

### 11.2 Model Improvements

#### 11.2.1 Advanced Architectures
- **Attention mechanisms**: Focus on relevant image regions
- **Graph neural networks**: Model spatial relationships
- **Ensemble methods**: Combine multiple model types
- **Transfer learning**: Use pre-trained models for NDVI analysis

#### 11.2.2 Physics-Informed ML
- **Hybrid models**: Combine physics-based FS with ML
- **Constrained learning**: Enforce physical constraints
- **Uncertainty quantification**: Bayesian approaches
- **Explainable AI**: Model interpretation tools

### 11.3 System Enhancements

#### 11.3.1 Real-time Prediction
- **API development**: REST API for predictions
- **Web interface**: User-friendly dashboard
- **Mobile app**: Field risk assessment tool
- **Alert system**: Automated risk notifications

#### 11.3.2 Deployment
- **Cloud deployment**: AWS/GCP/Azure integration
- **Edge computing**: On-site processing
- **Model serving**: TensorFlow Serving, ONNX
- **Monitoring**: Model performance tracking

### 11.3.3 Validation
- **Cross-validation**: K-fold validation across regions
- **External validation**: Test on new mining sites
- **Field validation**: Ground truth verification
- **A/B testing**: Compare with existing methods

---

## 12. Troubleshooting

### 12.1 Common Issues

#### 12.1.1 Import Errors
**Problem**: `ModuleNotFoundError: No module named 'rasterio'`

**Solution**:
```bash
pip install rasterio
```

**Note**: On Windows, rasterio may require GDAL to be installed separately.

#### 12.1.2 Memory Errors
**Problem**: `MemoryError` during data loading

**Solutions**:
- Reduce patch size in pipeline
- Process one region at a time
- Increase system RAM
- Use chunked processing

#### 12.1.3 Alignment Errors
**Problem**: Rasters have different shapes/resolutions

**Solution**:
- Pipeline automatically resamples to match DEM
- Check CRS consistency across rasters
- Verify nodata values are correctly specified

#### 12.1.4 Training Errors
**Problem**: TensorFlow installation fails

**Solutions**:
- Use sklearn-only version: `train_multimodal_sklearn.py`
- Install TensorFlow when internet is available
- Use conda for TensorFlow installation
- Consider using Docker container

### 12.2 Performance Issues

#### 12.2.1 Slow Processing
**Problem**: Pipeline takes too long

**Solutions**:
- Reduce sampling rate for patches
- Process regions sequentially
- Use faster storage (SSD)
- Optimize chunk size for CSV reading

#### 12.2.2 Poor Model Performance
**Problem**: Low accuracy or high false positive rate

**Solutions**:
- Check data quality and labels
- Adjust class weights
- Tune hyperparameters
- Try different model architectures
- Increase training data

### 12.3 Data Issues

#### 12.3.1 Missing Files
**Problem**: File not found errors

**Solutions**:
- Verify file naming conventions
- Check directory structure
- Ensure all required files are present
- Update file patterns in code

#### 12.3.2 Corrupted Data
**Problem**: NaN or invalid values in rasters

**Solutions**:
- Check source GeoTIFF files
- Verify nodata values are correctly specified
- Use data validation tools
- Repair or replace corrupted files

---

## 13. References

### 13.1 Scientific Literature

#### 13.1.1 Rockfall Mechanics
- Hungr, O., et al. (2014). "Rockfall hazard analysis." Landslides: Evaluating Hazard, Risk, and Remediation.
- Dorren, L. K. A. (2003). "A review of rockfall mechanics and modelling approaches." Progress in Physical Geography.

#### 13.1.2 Geospatial AI
- Zhu, X. X., et al. (2017). "Deep learning in remote sensing." International Journal of Remote Sensing.
- Ma, L., et al. (2019). "Deep learning in remote sensing: A comprehensive review." IEEE Geoscience and Remote Sensing Magazine.

#### 13.1.3 Multimodal Learning
- Ramachandram, D., & Taylor, G. W. (2017). "Deep multimodal learning." arXiv preprint.
- Baltrušaitis, T., et al. (2018). "Multimodal machine learning." IEEE Transactions on Pattern Analysis and Machine Intelligence.

### 13.2 Technical Documentation

#### 13.2.1 Software Libraries
- Rasterio Documentation: https://rasterio.readthedocs.io/
- Scikit-learn Documentation: https://scikit-learn.org/
- TensorFlow Documentation: https://www.tensorflow.org/
- XGBoost Documentation: https://xgboost.readthedocs.io/

#### 13.2.2 Data Standards
- GeoTIFF Format Specification: https://www.opengis.net/standards/geotiff
- NDVI Calculation: https://www.usgs.gov/landsat-missions/normalized-difference-vegetation-index

### 13.3 Best Practices

#### 13.3.1 Machine Learning
- "Machine Learning Yearning" by Andrew Ng
- "Deep Learning" by Ian Goodfellow, Yoshua Bengio, Aaron Courville
- "Hands-On Machine Learning" by Aurélien Géron

#### 13.3.2 Geospatial Analysis
- "Geographic Information Systems and Science" by Paul Longley
- "Python Geospatial Development" by Erik Westra

---

## Appendix A: Quick Reference

### A.1 Command Summary

```bash
# Run complete pipeline
python rockfall_pipeline.py

# Train sklearn models
python train_multimodal_sklearn.py

# Train CNN models
python train_multimodal_cnn.py

# Generate visualizations
python demo.py

# Install dependencies
pip install -r requirements.txt
```

### A.2 Key File Locations

| Component | File Path |
|----------|-----------|
| Pipeline | `rockfall_pipeline.py` |
| sklearn Training | `train_multimodal_sklearn.py` |
| CNN Training | `train_multimodal_cnn.py` |
| Visualization | `data_visualizer.py` |
| Processed Data | `processed_data/` |
| Trained Models | `models/` |
| Raw Data | `datasets/` |

### A.3 Performance Summary

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| RandomForest | 98.3% | 80.0% | 96.0% | 87.0% |
| CNN | TBD | TBD | TBD | TBD |
| Fusion | 98.5% | 82.2% | 95.6% | 88.0% |

---

## Appendix B: Glossary

- **DEM**: Digital Elevation Model - 3D representation of terrain surface
- **NDVI**: Normalized Difference Vegetation Index - Measure of vegetation health
- **CRS**: Coordinate Reference System - System for identifying locations
- **GeoTIFF**: Geographic Tagged Image File Format - Standard for geospatial raster data
- **CNN**: Convolutional Neural Network - Deep learning architecture for image processing
- **FS**: Factor of Safety - Ratio of resisting to driving forces in slope stability
- **PCA**: Principal Component Analysis - Dimensionality reduction technique
- **ROC**: Receiver Operating Characteristic - Performance metric for binary classification
- **AUC**: Area Under Curve - Summary metric for ROC analysis

---

## Appendix C: Contact and Support

### C.1 Project Information
- **Repository**: https://github.com/shreyaB7134/ai_rockfall_prediction
- **Version**: 1.0
- **Last Updated**: April 2026

### C.2 Support Channels
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: This file and README.md
- **Examples**: demo.py and inline code comments

---

**End of Complete Documentation**

*This document provides comprehensive technical documentation for the Rockfall Prediction System. For quick start information, please refer to README.md. For implementation details, refer to the inline code documentation.*
