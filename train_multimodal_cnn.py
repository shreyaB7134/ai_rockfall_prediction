"""
Rockfall Prediction - Multimodal Training with CNN
===================================================

This version upgrades the image model to a proper CNN using TensorFlow/Keras.
It implements:
- Tabular model: RandomForest (sklearn)
- Image model: CNN with specified architecture (TensorFlow/Keras)
- Fusion model: Logistic Regression combining both
"""

import os
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import tensorflow as tf
from tensorflow.keras import layers, models, callbacks


@dataclass
class DatasetConfig:
    region: str
    processed_dir: Path = Path("processed_data")
    patch_file_prefix: str = "ndvi_patches"
    centers_file_prefix: str = "patch_centers"
    tabular_labeled_prefix: str = "tabular"
    coord_decimals: int = 6


def set_seed(seed: int = 42) -> None:
    """Set random seeds for reproducibility"""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def _round_coords(lon: np.ndarray, lat: np.ndarray, decimals: int) -> np.ndarray:
    """Round coordinates to specified decimal places"""
    lon_r = np.round(lon.astype("float64"), decimals=decimals)
    lat_r = np.round(lat.astype("float64"), decimals=decimals)
    return np.stack([lon_r, lat_r], axis=1)


def load_patches_and_centers(cfg: DatasetConfig):
    """Load NDVI patches and their center coordinates"""
    patches_path = cfg.processed_dir / f"{cfg.patch_file_prefix}_{cfg.region}.npz"
    centers_path = cfg.processed_dir / f"{cfg.centers_file_prefix}_{cfg.region}.npz"

    patches = np.load(patches_path)["patches"]
    centers = np.load(centers_path)["centers"]  # (N, 2) -> (lon, lat)

    patches = patches.astype("float32")
    centers = centers.astype("float64")

    return patches, centers


def extract_tabular_for_patch_centers(cfg: DatasetConfig, centers: np.ndarray) -> pd.DataFrame:
    """
    Efficiently reads only those tabular rows that match (rounded) patch centers.
    Avoids loading the full multi-million-row CSV into memory.
    """
    tabular_path = cfg.processed_dir / f"{cfg.tabular_labeled_prefix}_{cfg.region}_labeled.csv"

    centers_round = _round_coords(centers[:, 0], centers[:, 1], cfg.coord_decimals)
    wanted = set(map(tuple, centers_round))

    usecols = [
        "lon",
        "lat",
        "dem",
        "slope",
        "rainfall",
        "temperature",
        "ndvi",
        "risk_label",
    ]

    found_rows = {}

    for chunk in pd.read_csv(tabular_path, usecols=usecols, chunksize=250_000):
        chunk["lon_r"] = chunk["lon"].round(cfg.coord_decimals)
        chunk["lat_r"] = chunk["lat"].round(cfg.coord_decimals)

        keys = list(zip(chunk["lon_r"].values, chunk["lat_r"].values))
        mask = [k in wanted for k in keys]
        if not any(mask):
            continue

        sub = chunk.loc[mask].copy()
        for _, row in sub.iterrows():
            found_rows[(row["lon_r"], row["lat_r"])] = row

        if len(found_rows) >= len(wanted):
            break

    # Build DataFrame in same order as centers
    ordered = []
    missing = 0
    for k in map(tuple, centers_round):
        r = found_rows.get(k)
        if r is None:
            missing += 1
            ordered.append(None)
        else:
            ordered.append(r)

    if missing > 0:
        print(f"[{cfg.region}] Warning: {missing}/{len(centers)} patch centers not matched in tabular CSV after rounding.")

    df = pd.DataFrame([r for r in ordered if r is not None])

    # keep index mapping from patch index to df row index
    keep_idx = np.array([i for i, r in enumerate(ordered) if r is not None], dtype=int)

    return df.reset_index(drop=True), keep_idx


def prepare_region_dataset(cfg: DatasetConfig):
    """Load and prepare dataset for a single region"""
    patches, centers = load_patches_and_centers(cfg)
    df_tab, keep_idx = extract_tabular_for_patch_centers(cfg, centers)

    patches = patches[keep_idx]

    # CNN input: (N, 32, 32, 1) - will be normalized later
    X_img = patches[..., np.newaxis]

    # Tabular input
    X_tab = df_tab[["dem", "slope", "rainfall", "temperature", "ndvi"]].astype("float32")
    y = df_tab["risk_label"].astype("int64").values

    return X_tab, X_img, y


def normalize_ndvi_patches(X_img):
    """
    Normalize NDVI values to [0, 1] range
    NDVI typically ranges from -1 to 1, but we'll normalize based on actual data range
    """
    # Normalize per sample to [0, 1]
    X_normalized = np.zeros_like(X_img)
    for i in range(len(X_img)):
        patch = X_img[i]
        min_val = patch.min()
        max_val = patch.max()
        if max_val > min_val:
            X_normalized[i] = (patch - min_val) / (max_val - min_val)
        else:
            X_normalized[i] = patch  # constant patch
    return X_normalized


def build_cnn_model(input_shape=(32, 32, 1)):
    """
    Build CNN model with the specified architecture:
    Conv2D(32, 3x3) -> ReLU -> MaxPool -> Conv2D(64, 3x3) -> ReLU -> MaxPool -> 
    Flatten -> Dense(64) -> ReLU -> Dropout(0.5) -> Dense(1) -> Sigmoid
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    return model


def train_randomforest(X_train, y_train, X_test, y_test, seed=42):
    """
    Tabular model using RandomForest
    """
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=seed,
        n_jobs=-1,
        class_weight='balanced'
    )

    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0))
    }

    return model, proba, pred, metrics


def train_cnn(X_img_train, y_train, X_img_test, y_test, seed=42, epochs=15):
    """
    Image model using CNN with specified architecture
    """
    # Normalize NDVI patches to [0, 1]
    X_img_train_norm = normalize_ndvi_patches(X_img_train)
    X_img_test_norm = normalize_ndvi_patches(X_img_test)
    
    # Build model
    model = build_cnn_model(input_shape=X_img_train_norm.shape[1:])
    
    # Compile model with specified loss, optimizer, and metrics
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='binary_crossentropy',
        metrics=[
            'accuracy',
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    # Callbacks for training
    early_stopping = callbacks.EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
    
    # Train model
    print(f"\nTraining CNN for up to {epochs} epochs...")
    history = model.fit(
        X_img_train_norm,
        y_train,
        validation_split=0.2,
        epochs=epochs,
        batch_size=32,
        callbacks=[early_stopping, reduce_lr],
        verbose=1,
        shuffle=True
    )
    
    # Make predictions
    proba = model.predict(X_img_test_norm, batch_size=64).reshape(-1)
    pred = (proba >= 0.5).astype(int)
    
    # Calculate metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0))
    }
    
    return model, proba, pred, metrics, history


def train_fusion(rf_train_proba, cnn_train_proba, y_train, 
                 rf_test_proba, cnn_test_proba, y_test, seed=42):
    """
    Fusion model combining both modalities using Logistic Regression
    """
    X_fuse_train = np.vstack([rf_train_proba, cnn_train_proba]).T
    X_fuse_test = np.vstack([rf_test_proba, cnn_test_proba]).T

    clf = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(random_state=seed, max_iter=1000, class_weight='balanced')),
        ]
    )

    clf.fit(X_fuse_train, y_train)

    proba = clf.predict_proba(X_fuse_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0))
    }

    return clf, proba, pred, metrics


def run_training(regions=("korba", "talcher_data"), seed: int = 42, test_size: float = 0.2, epochs: int = 15):
    """
    Run complete multimodal training with CNN
    """
    set_seed(seed)

    print("=" * 70)
    print("ROCKFALL PREDICTION - MULTIMODAL TRAINING WITH CNN")
    print("=" * 70)

    # Load data from all regions
    all_X_tab = []
    all_X_img = []
    all_y = []

    for region in regions:
        cfg = DatasetConfig(region=region)
        X_tab, X_img, y = prepare_region_dataset(cfg)
        print(f"[{region}] Matched samples for multimodal training: {len(y)}")
        all_X_tab.append(X_tab)
        all_X_img.append(X_img)
        all_y.append(y)

    # Combine all regions
    X_tab = pd.concat(all_X_tab, axis=0).reset_index(drop=True)
    X_img = np.concatenate(all_X_img, axis=0)
    y = np.concatenate(all_y, axis=0)

    print(f"\nTotal combined samples: {len(y)}")
    print(f"Class distribution: {np.bincount(y)}")

    # Train/test split (same for all models)
    X_tab_train, X_tab_test, X_img_train, X_img_test, y_train, y_test = train_test_split(
        X_tab,
        X_img,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )

    print(f"\nTrain samples: {len(y_train)}, Test samples: {len(y_test)}")

    # 1) Tabular model: RandomForest
    print("\n" + "=" * 70)
    print("TRAINING TABULAR MODEL (RandomForest)")
    print("=" * 70)
    rf_model, rf_test_proba, rf_test_pred, rf_metrics = train_randomforest(
        X_tab_train, y_train, X_tab_test, y_test, seed=seed
    )

    # RandomForest train proba for fusion
    rf_train_proba = rf_model.predict_proba(X_tab_train)[:, 1]

    # 2) Image model: CNN
    print("\n" + "=" * 70)
    print("TRAINING IMAGE MODEL (CNN)")
    print("=" * 70)
    cnn_model, cnn_test_proba, cnn_test_pred, cnn_metrics, history = train_cnn(
        X_img_train, y_train, X_img_test, y_test, seed=seed, epochs=epochs
    )

    # CNN train proba for fusion
    X_img_train_norm = normalize_ndvi_patches(X_img_train)
    cnn_train_proba = cnn_model.predict(X_img_train_norm, batch_size=64).reshape(-1)

    # 3) Fusion model
    print("\n" + "=" * 70)
    print("TRAINING FUSION MODEL (Logistic Regression)")
    print("=" * 70)
    fusion_model, fusion_test_proba, fusion_test_pred, fusion_metrics = train_fusion(
        rf_train_proba,
        cnn_train_proba,
        y_train,
        rf_test_proba,
        cnn_test_proba,
        y_test,
        seed=seed,
    )

    # Print evaluation
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS (same test split)")
    print("=" * 70)
    print(f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
    print("-" * 70)
    print(f"{'RandomForest (Tabular)':<25} {rf_metrics['accuracy']:>10.4f} {rf_metrics['precision']:>10.4f} {rf_metrics['recall']:>10.4f} {rf_metrics['f1']:>10.4f}")
    print(f"{'CNN (Image)':<25} {cnn_metrics['accuracy']:>10.4f} {cnn_metrics['precision']:>10.4f} {cnn_metrics['recall']:>10.4f} {cnn_metrics['f1']:>10.4f}")
    print(f"{'Fusion (Combined)':<25} {fusion_metrics['accuracy']:>10.4f} {fusion_metrics['precision']:>10.4f} {fusion_metrics['recall']:>10.4f} {fusion_metrics['f1']:>10.4f}")

    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORTS")
    print("=" * 70)

    print("\n--- RandomForest (Tabular) ---")
    print(classification_report(y_test, rf_test_pred, zero_division=0))

    print("\n--- CNN (Image) ---")
    print(classification_report(y_test, cnn_test_pred, zero_division=0))

    print("\n--- Fusion (Combined) ---")
    print(classification_report(y_test, fusion_test_pred, zero_division=0))

    # Save models
    out_dir = Path("models")
    out_dir.mkdir(exist_ok=True)

    import joblib

    joblib.dump(rf_model, out_dir / "randomforest_tabular.joblib")
    joblib.dump(fusion_model, out_dir / "fusion_logreg.joblib")
    cnn_model.save(out_dir / "cnn_ndvi.keras")

    print(f"\nSaved models to: {out_dir.resolve()}")
    
    # Save training history for CNN
    np.save(out_dir / "cnn_training_history.npy", history.history)
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    return {
        'rf_metrics': rf_metrics,
        'cnn_metrics': cnn_metrics,
        'fusion_metrics': fusion_metrics,
        'history': history
    }


if __name__ == "__main__":
    # Run training with 15 epochs for CNN
    results = run_training(epochs=15)
