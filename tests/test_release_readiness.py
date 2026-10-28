"""Evidence flags remain false, even when source and model checks pass."""
from scripts.release_readiness import report


def test_demo_release_never_claims_banking_or_security_certification():
    result = report()
    assert result["status"] == "demo_artifacts_verified"
    assert result["evidence_gates"]["demo_model_artifact_integrity"] is True
    assert all(not flag for key, flag in result["evidence_gates"].items()
               if key != "demo_model_artifact_integrity")
    assert result["production_release_approved"] is False
    assert result["synthetic_holdout"]["model_eligible_for_banking"] is False
    assert 0 < result["synthetic_holdout"]["pr_auc"] < 1


def test_missing_model_marks_artifact_unverified(tmp_path):
    result = report(model_path=tmp_path / "missing.joblib", metrics_path=tmp_path / "missing.json")
    assert result["status"] == "demo_artifacts_invalid"
    assert result["evidence_gates"]["demo_model_artifact_integrity"] is False
    assert result["production_release_approved"] is False
