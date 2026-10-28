"""What-if comparison is authenticated, anonymous, and completely stateless."""
import uuid

from fastapi.testclient import TestClient

import backend.app.api.routes.simulate as simulator
from backend.app.main import app
from ml.training.model_integrity import ModelIntegrityError

EXAMPLE = {
    "amount": 500, "hour": 12, "account_age_days": 180, "velocity_24h": 2,
    "prior_chargebacks": 0, "ip_risk_score": 0.2, "is_international": 0,
    "is_new_device": 0, "merchant_category": "retail", "transaction_type": "card",
}


def demo_score(x):
    probability = .8 if x.velocity_24h > 4 else .1
    return {
        "fraud_probability": probability, "risk_score": round(probability * 100),
        "risk_level": "HIGH" if probability > .65 else "LOW",
        "is_flagged": probability > .5, "model_version": "mock-synthetic-v1", "reasons": [],
    }


def test_stateless_scores_and_changed_feature_list(monkeypatch):
    monkeypatch.setattr(simulator, "score", demo_score)
    with TestClient(app) as client:
        before = client.get("/statistics").json()["total_transactions"]
        result = client.post("/simulate/what-if", json={
            "baseline": EXAMPLE, "scenario": {**EXAMPLE, "velocity_24h": 7, "amount": 1500},
        })
        assert result.status_code == 200, result.text
        out = result.json()
        assert out["demo_only"] is True and out["persisted"] is False
        assert out["delta_probability"] == .7
        assert out["delta_risk_score"] == 70
        assert out["changed_features"] == ["amount", "velocity_24h"]
        assert out["flag_changed"] is True and out["direction"] == "increase"
        assert "not causal" in out["disclaimer"]
        assert client.get("/statistics").json()["total_transactions"] == before


def test_invalid_sensitive_ids_and_unknown_features_rejected():
    with TestClient(app) as client:
        for pair in (
            {"baseline": {**EXAMPLE, "transaction_id": "FAKE-123"}, "scenario": EXAMPLE},
            {"baseline": EXAMPLE, "scenario": {**EXAMPLE, "amount": -1}},
            {"baseline": EXAMPLE, "scenario": {**EXAMPLE, "card_number": "0000000000000000"}},
            {"baseline": EXAMPLE, "scenario": EXAMPLE, "unexpected": "not allowed"},
        ):
            assert client.post("/simulate/what-if", json=pair).status_code == 422


def test_unavailable_model_is_private_503(monkeypatch):
    def fail(_):
        raise ModelIntegrityError("internal artifact path should not leak")

    monkeypatch.setattr(simulator, "score", fail)
    with TestClient(app) as client:
        result = client.post("/simulate/what-if", json={"baseline": EXAMPLE, "scenario": EXAMPLE})
    assert result.status_code == 503
    assert "internal artifact" not in result.text


def test_model_mismatch_rejected(monkeypatch):
    def changing_version(tx):
        return {**demo_score(tx), "model_version": str(uuid.uuid4())}

    monkeypatch.setattr(simulator, "score", changing_version)
    with TestClient(app) as client:
        result = client.post("/simulate/what-if", json={"baseline": EXAMPLE, "scenario": EXAMPLE})
    assert result.status_code == 503


def test_real_synthetic_model_scores_without_database_write():
    with TestClient(app) as client:
        before = client.get("/statistics").json()["total_transactions"]
        result = client.post("/simulate/what-if", json={
            "baseline": EXAMPLE, "scenario": {**EXAMPLE, "velocity_24h": 9},
        })
        assert result.status_code == 200, result.text
        assert result.json()["persisted"] is False
        assert 0 <= result.json()["baseline"]["fraud_probability"] <= 1
        assert client.get("/statistics").json()["total_transactions"] == before
