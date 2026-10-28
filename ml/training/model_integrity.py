"""Consistency checks for project-controlled synthetic demonstration artifacts.

SHA-256 detects accidental/unreviewed changes. It is not a signature or a
malware scan and never makes it safe to unpickle an untrusted model.
"""
import hashlib
import json
import math
from pathlib import Path


class ModelIntegrityError(RuntimeError):
    """The demo model or its recorded evaluation cannot be trusted."""


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def manifest_path(model_path):
    return Path(model_path).with_name("model_manifest.json")


def build_manifest(model_path, metrics_path, metrics):
    return {
        "schema_version": 1,
        "purpose": "synthetic demonstration model; not approved for financial decisions",
        "model_file": Path(model_path).name,
        "model_sha256": sha256(model_path),
        "metrics_file": Path(metrics_path).name,
        "metrics_sha256": sha256(metrics_path),
        "selected_model": metrics["selected_model"],
        "threshold": float(metrics["test"]["threshold"]),
        "source_dataset": metrics["dataset"],
        "training_rows": int(metrics["rows"]),
    }


def write_manifest(model_path, metrics_path, metrics):
    """Run after trusted training has written both artifacts."""
    output = manifest_path(model_path)
    output.write_text(json.dumps(build_manifest(model_path, metrics_path, metrics), indent=2) + "\n", encoding="utf-8")
    return output


def verify_model_artifacts(model_path, *, metrics_path=None):
    """Verify file consistency before any unpickling.

    The manifest must come from a reviewed, trusted repository.
    """
    model_path = Path(model_path)
    recorded = manifest_path(model_path)
    if not model_path.is_file() or not recorded.is_file():
        raise ModelIntegrityError("Model artifact or manifest unavailable")
    try:
        manifest = json.loads(recorded.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
            raise ModelIntegrityError("Unsupported model manifest schema")
        if manifest.get("model_file") != model_path.name:
            raise ModelIntegrityError("Model manifest filename mismatch")
        if sha256(model_path) != manifest.get("model_sha256"):
            raise ModelIntegrityError("Model SHA-256 mismatch")
        if metrics_path is not None:
            metrics_path = Path(metrics_path)
            if not metrics_path.is_file() or metrics_path.name != manifest.get("metrics_file"):
                raise ModelIntegrityError("Evaluation metrics unavailable or misplaced")
            if sha256(metrics_path) != manifest.get("metrics_sha256"):
                raise ModelIntegrityError("Evaluation metrics SHA-256 mismatch")
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            if metrics.get("dataset") != "synthetic demonstration data":
                raise ModelIntegrityError("Unexpected dataset provenance")
            if (metrics.get("selected_model") != manifest.get("selected_model")
                    or int(metrics.get("rows", -1)) != manifest.get("training_rows")
                    or float(metrics.get("test", {}).get("threshold", -1)) != manifest.get("threshold")):
                raise ModelIntegrityError("Evaluation metrics and manifest disagree")
        threshold = float(manifest["threshold"])
        if not math.isfinite(threshold) or not 0 < threshold <= 1:
            raise ModelIntegrityError("Invalid stored decision threshold")
        if manifest.get("purpose") != "synthetic demonstration model; not approved for financial decisions":
            raise ModelIntegrityError("Unrecognized model purpose")
    except (OSError, KeyError, ValueError, TypeError) as exc:
        raise ModelIntegrityError("Malformed or unreadable model manifest") from exc
    return manifest
