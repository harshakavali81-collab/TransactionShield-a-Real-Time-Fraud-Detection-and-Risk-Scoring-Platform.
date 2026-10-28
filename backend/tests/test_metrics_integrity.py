"""Never serve unverified evaluation metrics as if they are trustworthy."""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.routes import analytics
from ml.training.model_integrity import ModelIntegrityError


def test_published_metrics_are_manifest_verified():
    with TestClient(app) as client:
        result = client.get("/metrics")
        assert result.status_code == 200
        assert result.json()["dataset"] == "synthetic demonstration data"


def test_corrupt_metrics_are_unavailable_and_internal_details_hidden(monkeypatch):
    def bad_integrity(*args, **kwargs):
        raise ModelIntegrityError("sensitive internal path")
    monkeypatch.setattr(analytics, "verify_model_artifacts", bad_integrity)
    with TestClient(app) as client:
        result = client.get("/metrics")
        assert result.status_code == 503
        assert result.json()["detail"] == "Evaluation artifacts unavailable"
        assert "sensitive internal path" not in result.text
