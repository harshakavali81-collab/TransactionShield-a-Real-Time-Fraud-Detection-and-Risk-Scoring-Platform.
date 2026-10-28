"""Expanding-window diagnostic evaluation of fictional transaction sequences.

Preprocessing and model are refit using past rows inside each fold.
The future test rows cannot influence fitted model or validation F2 threshold.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from ml.config import FEATURES
from ml.data.feature_engineering import make_preprocessor
from ml.training.evaluate import metrics, optimize_threshold


def rolling_origin_report(data: pd.DataFrame, *, min_train: int = 1600,
                          validation_size: int = 400, test_size: int = 400,
                          step: int = 400, max_folds: int = 5) -> dict:
    """Each expanding fold has train -> validation -> test in that order."""
    if min_train < 100 or min(validation_size, test_size, step, max_folds) < 1:
        raise ValueError("Invalid rolling window sizes")
    missing = (set(FEATURES) | {"event_time", "is_fraud"}) - set(data.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    ordered = data.copy()
    ordered["event_time"] = pd.to_datetime(ordered.event_time, utc=True, errors="raise")
    ordered = ordered.sort_values("event_time", kind="stable").reset_index(drop=True)
    if ordered.event_time.isna().any() or ordered.event_time.duplicated().any():
        raise ValueError("Every transaction must have a unique, valid event_time")
    if not ordered.is_fraud.isin([0, 1, False, True]).all():
        raise ValueError("Labels must be binary")
    folds, skipped = [], []
    for index in range(max_folds):
        train_end = min_train + index * step
        val_end = train_end + validation_size
        test_end = val_end + test_size
        if test_end > len(ordered):
            break
        train, val, test = ordered.iloc[:train_end], ordered.iloc[train_end:val_end], ordered.iloc[val_end:test_end]
        if any(part.is_fraud.nunique() != 2 for part in (train, val, test)):
            skipped.append({"fold": index + 1, "reason": "single_class_in_one_or_more_windows"})
            continue
        pipeline = Pipeline([
            ("preprocess", make_preprocessor()),
            ("model", LogisticRegression(max_iter=600, class_weight="balanced", random_state=42)),
        ])
        pipeline.fit(train[FEATURES], train.is_fraud)
        threshold = optimize_threshold(val.is_fraud, pipeline.predict_proba(val[FEATURES])[:, 1])
        prediction = pipeline.predict_proba(test[FEATURES])[:, 1]
        if not np.isfinite(prediction).all():
            raise ValueError("Non-finite model scores")
        results = metrics(test.is_fraud, prediction, threshold)
        folds.append({
            "fold": index + 1, "train_rows": len(train),
            "validation_rows": len(val), "test_rows": len(test),
            "train_through": train.event_time.iloc[-1].isoformat(),
            "validation_from": val.event_time.iloc[0].isoformat(),
            "validation_through": val.event_time.iloc[-1].isoformat(),
            "test_from": test.event_time.iloc[0].isoformat(),
            "test_through": test.event_time.iloc[-1].isoformat(),
            **results,
        })
    if not folds:
        raise ValueError("No valid folds: increase rows or check minority-class coverage")
    return {
        "scope": "synthetic chronological rolling-origin diagnostic",
        "model": "logistic_regression (fixed diagnostic baseline, not serving model)",
        "data_rows": len(ordered), "data_source": "generated fictional transactions",
        "fold_count": len(folds), "skipped": skipped,
        "averages": {
            key: round(float(np.mean([fold[key] for fold in folds])), 6)
            for key in ("precision", "recall", "f1", "pr_auc", "brier_score")
        },
        "folds": folds,
        "limitations": [
            "Synthetic labels and features do not establish performance on real bank data.",
            "Validation thresholds are chosen separately per fold; no test labels influence training or threshold selection.",
            "Test windows may overlap if step is smaller than test_size; fold results are not independent confidence intervals.",
            "These diagnostics do not replace the frozen model held-out report.",
        ],
    }
