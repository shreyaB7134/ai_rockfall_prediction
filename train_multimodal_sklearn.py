"""
Rockfall Prediction - Multimodal Training (scikit-learn only)
==============================================================

This version uses only scikit-learn (no xgboost/tensorflow) to avoid installation issues.
It implements:
- Tabular model: RandomForest (instead of XGBoost)
- Image model: Flattened patch features + PCA (instead of CNN)
- Fusion model: Logistic Regression combining both
"""

import os
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline


@dataclass
class DatasetConfig:
    region: str
    processed_dir: Path = Path("processed_data")
    patch_file_prefix: str = "ndvi_patches"
    centers_file_prefix: str = "patch_centers"
    tabular_labeled_prefix: str = "tabular"
    coord_decimals: int = 6


def set_seed(seed: int = 42) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def _round_coords(lon: np.ndarray, lat: np.ndarray, decimals: int) -> np.ndarray:
    lon_r = np.round(lon.astype("float64"), decimals=decimals)
    lat_r = np.round(lat.astype("float64"), decimals=decimals)
    return np.stack([lon_r, lat_r], axis=1)


def load_patches_and_centers(cfg: DatasetConfig):
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
    patches, centers = load_patches_and_centers(cfg)
    df_tab, keep_idx = extract_tabular_for_patch_centers(cfg, centers)

    patches = patches[keep_idx]

    # Image input: flatten patches for PCA
    X_img = patches.reshape(len(patches), -1)  # (N, 1024)

    # Tabular input
    X_tab = df_tab[["dem", "slope", "rainfall", "temperature", "ndvi"]].astype("float32")
    y = df_tab["risk_label"].astype("int64").values

    return X_tab, X_img, y


def train_randomforest(X_train, y_train, X_test, y_test, seed=42):
    """
    Tabular model using RandomForest (sklearn alternative to XGBoost)
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
    }

    return model, proba, pred, metrics


def train_patch_model(X_img_train, y_train, X_img_test, y_test, seed=42):
    """
    Image model using PCA + RandomForest (sklearn alternative to CNN)
    """
    # Pipeline: Standardize -> PCA -> RandomForest
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=50, random_state=seed)),
        ('rf', RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            min_samples_split=10,
            random_state=seed,
            n_jobs=-1,
            class_weight='balanced'
        ))
    ])

    model.fit(X_img_train, y_train)

    proba = model.predict_proba(X_img_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
    }

    return model, proba, pred, metrics


def train_fusion(rf_train_proba, patch_train_proba, y_train, 
                 rf_test_proba, patch_test_proba, y_test, seed=42):
    """
    Fusion model combining both modalities using Logistic Regression
    """
    X_fuse_train = np.vstack([rf_train_proba, patch_train_proba]).T
    X_fuse_test = np.vstack([rf_test_proba, patch_test_proba]).T

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
    }

    return clf, proba, pred, metrics


def run_training(regions=("korba", "talcher_data"), seed: int = 42, test_size: float = 0.2):
    set_seed(seed)

    print("=" * 60)
    print("ROCKFALL PREDICTION - MULTIMODAL TRAINING (sklearn only)")
    print("=" * 60)

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
    print("\n" + "=" * 60)
    print("TRAINING TABULAR MODEL (RandomForest)")
    print("=" * 60)
    rf_model, rf_test_proba, rf_test_pred, rf_metrics = train_randomforest(
        X_tab_train, y_train, X_tab_test, y_test, seed=seed
    )

    # RandomForest train proba for fusion
    rf_train_proba = rf_model.predict_proba(X_tab_train)[:, 1]

    # 2) Image model: PCA + RandomForest
    print("\n" + "=" * 60)
    print("TRAINING IMAGE MODEL (PCA + RandomForest)")
    print("=" * 60)
    patch_model, patch_test_proba, patch_test_pred, patch_metrics = train_patch_model(
        X_img_train, y_train, X_img_test, y_test, seed=seed
    )

    patch_train_proba = patch_model.predict_proba(X_img_train)[:, 1]

    # 3) Fusion model
    print("\n" + "=" * 60)
    print("TRAINING FUSION MODEL (Logistic Regression)")
    print("=" * 60)
    fusion_model, fusion_test_proba, fusion_test_pred, fusion_metrics = train_fusion(
        rf_train_proba,
        patch_train_proba,
        y_train,
        rf_test_proba,
        patch_test_proba,
        y_test,
        seed=seed,
    )

    # Print evaluation
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS (same test split)")
    print("=" * 60)
    print(f"RandomForest (Tabular):  {rf_metrics}")
    print(f"PCA+RF (Image):          {patch_metrics}")
    print(f"Fusion (Combined):       {fusion_metrics}")

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORTS")
    print("=" * 60)

    print("\n--- RandomForest (Tabular) ---")
    print(classification_report(y_test, rf_test_pred, zero_division=0))

    print("\n--- PCA+RF (Image) ---")
    print(classification_report(y_test, patch_test_pred, zero_division=0))

    print("\n--- Fusion (Combined) ---")
    print(classification_report(y_test, fusion_test_pred, zero_division=0))

    # Save models
    out_dir = Path("models")
    out_dir.mkdir(exist_ok=True)

    import joblib

    joblib.dump(rf_model, out_dir / "randomforest_tabular.joblib")
    joblib.dump(patch_model, out_dir / "patch_model_pca_rf.joblib")
    joblib.dump(fusion_model, out_dir / "fusion_logreg.joblib")

    print(f"\nSaved models to: {out_dir.resolve()}")
    print("\n" + "=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_training()
