"""Evidence-based, synthetic-only release readiness. NEVER certify production."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.training.model_integrity import ModelIntegrityError, verify_model_artifacts


def report(model_path=None, metrics_path=None):
    model = Path(model_path) if model_path is not None else ROOT / "artifacts/models/fraud_model.joblib"
    metrics_file = Path(metrics_path) if metrics_path is not None else ROOT / "artifacts/models/metrics.json"
    artifact_error = None
    metrics = None
    try:
        manifest = verify_model_artifacts(model, metrics_path=metrics_file)
        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    except (ModelIntegrityError, OSError, ValueError, TypeError, KeyError) as exc:
        manifest = None
        artifact_error = type(exc).__name__
    test = metrics.get("test", {}) if metrics else {}
    support = int(test.get("support", 0))
    positive_cases = int(test.get("positive_cases", 0))
    prevalence = positive_cases / support if support else None
    gates = {
        "demo_model_artifact_integrity": bool(manifest),
        "labeled_real_world_holdout_independently_validated": False,
        "authorized_live_bank_feed_verified": False,
        "public_protected_backend_deployed_and_verified": False,
        "identity_and_tenant_authorization_verified": False,
        "independent_security_assessment_completed": False,
        "financial_decision_use_authorized": False,
    }
    return {
        "schema_version": 1,
        "scope": "repository-contained evidence only; synthetic portfolio demonstration",
        "status": "demo_artifacts_verified" if manifest else "demo_artifacts_invalid",
        "model_purpose": manifest.get("purpose") if manifest else None,
        "synthetic_holdout": {
            "test_rows": support,
            "test_positive_labels": positive_cases,
            "test_prevalence": round(prevalence, 6) if prevalence is not None else None,
            "pr_auc": test.get("pr_auc"),
            "recall": test.get("recall"),
            "precision": test.get("precision"),
            "model_eligible_for_banking": False,
        },
        "evidence_gates": gates,
        "production_release_approved": False,
        "external_validation_is_required": True,
        "artifact_error_type": artifact_error,
        "note": "CI success verifies software checks, not actual fraud effectiveness or production certification.",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Repository-only release evidence; never grants production approval")
    p.add_argument("--output", default="", help="Optional JSON report destination")
    args = p.parse_args(argv)
    result = report()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "demo_artifacts_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
