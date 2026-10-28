"""API must fail closed on corrupt model state or invalid predictions."""
from types import SimpleNamespace
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.training.model_integrity import ModelIntegrityError
import backend.app.api.routes.health as readiness
from backend.app.services import prediction_service


def test_ready_rejects_invalid_model(monkeypatch):
    def failure(*args, **kwargs):
        raise ModelIntegrityError("modified file")
    monkeypatch.setattr(readiness, "verify_model_artifacts", failure)
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["model_ready"] is False
    assert "modified file" not in response.text


def test_nonfinite_scores_rejected(monkeypatch):
    monkeypatch.setattr(prediction_service, "get_payload", lambda: {
        "pipeline": SimpleNamespace(predict_proba=lambda frame: [[0, float("nan")]]),
        "threshold": .2,
    })
    data = {"amount": 200, "hour": 2, "account_age_days": 22,
            "velocity_24h": 3, "prior_chargebacks": 0, "ip_risk_score": .3,
            "is_international": 1, "is_new_device": 1,
            "merchant_category": "retail", "transaction_type": "card"}
    with TestClient(app) as client:
        response = client.post("/predict", json=data)
    assert response.status_code == 503
    assert "nan" not in response.text.lower()
