"""Modular training pipeline for the BDHS-2022 stunting risk model."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, brier_score_loss
from xgboost import XGBClassifier

NUMERIC     = ["b19", "bord", "b11_filled", "v445_filled"]
BINARY      = ["female", "firstborn", "urban", "v445_missing"]
CATEGORICAL = ["v106", "v190", "v024", "v113", "v116"]
FEATURES    = NUMERIC + BINARY + CATEGORICAL


def load_cohort(path):
    return pd.read_parquet(path, engine="pyarrow")


def build_preprocessor():
    return ColumnTransformer([
        ("num", StandardScaler(), NUMERIC),
        ("bin", "passthrough", BINARY),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
    ])


def build_logistic():
    return Pipeline([
        ("prep", build_preprocessor()),
        ("clf", LogisticRegression(max_iter=5000, solver="lbfgs", C=1.0)),
    ])


def build_xgboost():
    return Pipeline([
        ("prep", build_preprocessor()),
        ("clf", XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=42, eval_metric="logloss", n_jobs=-1,
        )),
    ])


def grouped_split(df, test_size=0.2, random_state=42):
    X = df[FEATURES]
    y = df["stunted"]
    groups = df["v001"]
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    return train_idx, test_idx


def train_and_save(output_dir, test_size=0.2, random_state=42):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_cohort(output_dir / "cohort_analysable.parquet")
    train_idx, test_idx = grouped_split(df, test_size, random_state)

    X = df[FEATURES]
    y = df["stunted"]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(f"Train: {len(X_train)} children in {df.iloc[train_idx]['v001'].nunique()} clusters")
    print(f"Test:  {len(X_test)} children in {df.iloc[test_idx]['v001'].nunique()} clusters")

    overlap = set(df.iloc[train_idx]["v001"]) & set(df.iloc[test_idx]["v001"])
    print(f"Clusters in both arms: {len(overlap)}")
    assert len(overlap) == 0, "Cluster leakage detected"

    results = {}
    for name, builder in [("logistic", build_logistic), ("xgboost", build_xgboost)]:
        model = builder()
        model.fit(X_train, y_train)
        p = model.predict_proba(X_test)[:, 1]
        results[name] = {
            "auroc": roc_auc_score(y_test, p),
            "brier": brier_score_loss(y_test, p),
            "pred": p,
        }
        print(f"{name:10s}  AUROC: {results[name]['auroc']:.4f}  "
              f"Brier: {results[name]['brier']:.4f}")

    np.savez(
        output_dir / "test_predictions.npz",
        y_test=y_test.values,
        p_logit=results["logistic"]["pred"],
        p_xgb=results["xgboost"]["pred"],
        v001=df.iloc[test_idx]["v001"].values,
        urban=df.iloc[test_idx]["urban"].values,
        wealth=df.iloc[test_idx]["v190"].values,
        female=df.iloc[test_idx]["female"].values,
    )
    np.savez(output_dir / "split_grouped.npz",
             train_idx=train_idx, test_idx=test_idx)
    print(f"\nSaved predictions and split to {output_dir}")
    return results
