"""Audit a frozen model on separately supplied, approved and labeled data.

No retraining, threshold selection, model promotion or individual row output.
This procedure does NOT independently certify the labels or the deployment.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score, recall_score

from ml.config import FEATURES, MODEL
from ml.data.partner_contract import read_approved_feed
from ml.training.save_model import load_model
from ml.training.evaluate import metrics


def bootstrap_intervals(y, probability, threshold, draws: int = 200, seed: int = 17):
    """Stratified resampling of existing cases; limited by label provenance/shift."""
    y = np.asarray(y, dtype=int)
    probability = np.asarray(probability, dtype=float)
    rng = np.random.default_rng(seed)
    indices = [np.flatnonzero(y == k) for k in (0, 1)]
    if any(len(part) < 5 for part in indices):
        return {"status": "insufficient_positive_or_negative_cases"}
    ap_samples, recall_samples = [], []
    for _ in range(draws):
        sample = np.concatenate([rng.choice(part, size=len(part), replace=True) for part in indices])
        ap_samples.append(float(average_precision_score(y[sample], probability[sample])))
        recall_samples.append(float(recall_score(y[sample], probability[sample] >= threshold, zero_division=0)))
    return {
        "method": "stratified_case_bootstrap_95_percentile_interval",
        "draws": draws,
        "pr_auc": [float(x) for x in np.percentile(ap_samples, [2.5, 97.5])],
        "recall": [float(x) for x in np.percentile(recall_samples, [2.5, 97.5])],
        "limitations": "Intervals ignore entity clustering, delayed labels and temporal dependence.",
    }


def audit(path, *, model_path=MODEL, provenance: str, approved: bool, min_cases: int = 100,
          min_positives: int = 5, draws: int = 200):
    if not approved:
        raise ValueError("Explicit data approval is required; no third-party feed is assumed authorized")
    if len(provenance.strip()) < 10:
        raise ValueError("Describe the authorized labeling/provenance process (10+ characters)")
    data = read_approved_feed(path, labeled=True, minimum_rows=min_cases)
    if data["transaction_id"].astype(str).str.startswith("DEMO-").any():
        raise ValueError("Bundled synthetic demo IDs are not accepted as an external independent holdout")
    y = data["is_fraud"].astype(int).to_numpy()
    positives = int(y.sum())
    if positives < min_positives or len(y) - positives < 5:
        raise ValueError("Not enough confirmed positive/negative cases for meaningful metrics")
    model_path = Path(model_path).resolve(strict=True)
    payload = load_model(model_path)  # Only use a trusted project-controlled joblib file.
    if set(payload["features"]) != set(FEATURES):
        raise ValueError("Frozen model feature contract mismatch")
    probability = payload["pipeline"].predict_proba(data[FEATURES])[:, 1]
    threshold = float(payload["threshold"])  # Frozen: NEVER tune on holdout.
    result = {
        "status": "external_holdout_evaluated_labels_not_independently_verified",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": payload["model_name"],
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "declared_provenance": provenance.strip(),
        "approval_attested_by_operator_not_verified": True,
        "no_retraining_or_threshold_tuning": True,
        "population": {"rows": len(y), "labeled_positives": positives, "label_rate": float(y.mean())},
        "metrics": metrics(y, probability, threshold),
        "confidence_intervals": bootstrap_intervals(y, probability, threshold, draws=draws),
        "group_audit": {},
        "limitations": [
            "Data consent, independence, labeling accuracy and representativeness are not verified by code",
            "No production certification, approval or operational safety guarantee",
            "Only aggregates are emitted; full labels and identifiers are never included in the report",
        ],
    }
    for field in ["transaction_type", "merchant_category"]:
        groups = {}
        for name, subset in data.groupby(field, sort=True):
            idx = subset.index.to_numpy()
            npos = int(y[idx].sum())
            if len(idx) < 30 or npos < 5 or len(idx) - npos < 5:
                groups[str(name)] = {"status": "insufficient_support", "rows": len(idx)}
            else:
                groups[str(name)] = metrics(y[idx], probability[idx], threshold)
        result["group_audit"][field] = groups
    return result


def main():
    parser = argparse.ArgumentParser(description="Frozen-model evaluation of an authorized labeled holdout")
    parser.add_argument("--csv", required=True, help="Local, approved, labeled CSV; not uploaded anywhere")
    parser.add_argument("--provenance", required=True, help="Who supplied verified labels and permission (descriptive only)")
    parser.add_argument("--data-approved", action="store_true", help="Attest authorization to process this dataset")
    parser.add_argument("--model", default=str(MODEL))
    parser.add_argument("--output", default="", help="Optional local JSON report; do not publish if sensitive")
    args = parser.parse_args()
    report = audit(args.csv, model_path=args.model, provenance=args.provenance, approved=args.data_approved)
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
