"""Check recorded synthetic metrics and model without loading any pickle."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.config import MODEL, METRICS
from ml.training.model_integrity import verify_model_artifacts


def main():
    manifest = verify_model_artifacts(MODEL, metrics_path=METRICS)
    print(json.dumps({
        "integrity": "pass",
        "purpose": manifest["purpose"],
        "model": manifest["selected_model"],
        "model_sha256": manifest["model_sha256"],
        "production_approved": False,
    }, indent=2))


if __name__ == "__main__":
    main()
