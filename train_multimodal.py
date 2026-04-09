import os
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from xgboost import XGBClassifier

import tensorflow as tf
from tensorflow.keras import layers, models


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
    tf.random.set_seed(seed)


def build_cnn(input_shape=(32, 32, 1)) -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Conv2D(16, (3, 3), activation="relu", padding="same"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(64, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _round_coords(lon: np.ndarray, lat: np.ndarray, decimals: int) -> np.ndarray:
    lon_r = np.round(lon.astype("float64"), decimals=decimals)
    lat_r = np.round(lat.astype("float64"), decimals=decimals)
    return np.stack([lon_r, lat_r], axis=1)


def load_patches_and_centers(cfg: DatasetConfig):
    patches_path = cfg.processed_dir / f"{cfg.patch_file_prefix}_{cfg.region}.npz"
    centers_path = cfg.processed_dir / f"{cfg.centers_file_prefix}_{cfg.region}.npz"

    patches = np.load(patches_path)["patches"]
    centers = np.load(centers_path)["centers"]  # (N, 2) -> (lon, lat)

    # ensure float32 for NN
    patches = patches.astype("float32")
    centers = centers.astype("float64")

    return patches, centers


def extract_tabular_for_patch_centers(cfg: DatasetConfig, centers: np.ndarray) -> pd.DataFrame:
    """
    Efficiently reads only those tabular rows that match (rounded) patch centers.

    This avoids loading the full multi-million-row CSV into memory.
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

        # Filter to only candidate rows (cheap)
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

    # CNN input: (N, 32, 32, 1)
    X_img = patches[..., np.newaxis]

    # Tabular input
    X_tab = df_tab[["dem", "slope", "rainfall", "temperature", "ndvi"]].astype("float32")
    y = df_tab["risk_label"].astype("int64").values

    return X_tab, X_img, y


def train_xgboost(X_train, y_train, X_test, y_test, seed=42):
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=seed,
        n_jobs=-1,
        eval_metric="logloss",
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


def train_cnn(X_img_train, y_train, X_img_test, y_test, seed=42):
    model = build_cnn(input_shape=X_img_train.shape[1:])

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    ]

    model.fit(
        X_img_train,
        y_train,
        validation_split=0.2,
        epochs=15,
        batch_size=64,
        verbose=1,
        callbacks=callbacks,
        shuffle=True,
    )

    proba = model.predict(X_img_test, batch_size=128).reshape(-1)
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
    }

    return model, proba, pred, metrics


def train_fusion(xgb_train_proba, cnn_train_proba, y_train, xgb_test_proba, cnn_test_proba, y_test, seed=42):
    X_fuse_train = np.vstack([xgb_train_proba, cnn_train_proba]).T
    X_fuse_test = np.vstack([xgb_test_proba, cnn_test_proba]).T

    clf = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(random_state=seed, max_iter=1000)),
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

    X_tab_train, X_tab_test, X_img_train, X_img_test, y_train, y_test = train_test_split(
        X_tab,
        X_img,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )

    # 1) Tabular model: XGBoost
    xgb_model, xgb_test_proba, xgb_test_pred, xgb_metrics = train_xgboost(
        X_tab_train, y_train, X_tab_test, y_test, seed=seed
    )

    # XGBoost train proba for fusion
    xgb_train_proba = xgb_model.predict_proba(X_tab_train)[:, 1]

    # 2) Image model: CNN
    cnn_model, cnn_test_proba, cnn_test_pred, cnn_metrics = train_cnn(
        X_img_train, y_train, X_img_test, y_test, seed=seed
    )

    cnn_train_proba = cnn_model.predict(X_img_train, batch_size=128).reshape(-1)

    # 3) Fusion model
    fusion_model, fusion_test_proba, fusion_test_pred, fusion_metrics = train_fusion(
        xgb_train_proba,
        cnn_train_proba,
        y_train,
        xgb_test_proba,
        cnn_test_proba,
        y_test,
        seed=seed,
    )

    print("\n=== EVALUATION (same test split) ===")
    print("XGBoost:", xgb_metrics)
    print("CNN:", cnn_metrics)
    print("Fusion:", fusion_metrics)

    print("\n--- Classification Reports ---")
    print("\nXGBoost report:\n", classification_report(y_test, xgb_test_pred, zero_division=0))
    print("\nCNN report:\n", classification_report(y_test, cnn_test_pred, zero_division=0))
    print("\nFusion report:\n", classification_report(y_test, fusion_test_pred, zero_division=0))

    # Save models
    out_dir = Path("models")
    out_dir.mkdir(exist_ok=True)

    import joblib

    joblib.dump(xgb_model, out_dir / "xgboost_tabular.joblib")
    joblib.dump(fusion_model, out_dir / "fusion_logreg.joblib")
    cnn_model.save(out_dir / "cnn_ndvi.keras")

    print(f"\nSaved models to: {out_dir.resolve()}")


if __name__ == "__main__":
    run_training()
