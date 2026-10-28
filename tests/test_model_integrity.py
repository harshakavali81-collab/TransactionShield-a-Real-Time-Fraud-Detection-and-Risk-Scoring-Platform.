"""Synthetic-only regression tests for model/metrics integrity."""
import json
from pathlib import Path
import shutil

import pytest
from ml.config import MODEL, METRICS
from ml.training.model_integrity import (
    ModelIntegrityError, manifest_path, sha256, verify_model_artifacts, write_manifest,
)


def test_checked_in_demo_artifacts_match_manifest():
    actual = verify_model_artifacts(MODEL, metrics_path=METRICS)
    assert actual["model_sha256"] == sha256(MODEL)
    assert actual["source_dataset"] == "synthetic demonstration data"


def test_tampered_model_rejected(tmp_path):
    model = tmp_path / "fraud_model.joblib"
    shutil.copy2(MODEL, model)
    shutil.copy2(manifest_path(MODEL), manifest_path(model))
    verify_model_artifacts(model)
    model.write_bytes(model.read_bytes() + b"modified")
    with pytest.raises(ModelIntegrityError, match="SHA-256"):
        verify_model_artifacts(model)


def test_metrics_mismatch_rejected(tmp_path):
    model = tmp_path / "fraud_model.joblib"
    metrics = tmp_path / "metrics.json"
    shutil.copy2(MODEL, model)
    shutil.copy2(manifest_path(MODEL), manifest_path(model))
    shutil.copy2(METRICS, metrics)
    metrics.write_text(metrics.read_text() + "\n")
    with pytest.raises(ModelIntegrityError, match="metrics SHA-256"):
        verify_model_artifacts(model, metrics_path=metrics)


def test_manifest_writer_reproducible(tmp_path):
    model = tmp_path / "fraud_model.joblib"
    report = tmp_path / "metrics.json"
    model.write_bytes(b"unpickled mock bytes")
    data = {"dataset": "synthetic demonstration data", "selected_model": "mock",
            "rows": 10, "test": {"threshold": .2}}
    report.write_text(json.dumps(data))
    write_manifest(model, report, data)
    initial = manifest_path(model).read_bytes()
    write_manifest(model, report, data)
    assert initial == manifest_path(model).read_bytes()
    assert verify_model_artifacts(model, metrics_path=report)["selected_model"] == "mock"
