"""Batch input safeguards and transactional persistence tests."""
import uuid

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import batch as batch_route
from ml.training.model_integrity import ModelIntegrityError

VALID = {
    "amount": 525, "hour": 18, "account_age_days": 222, "velocity_24h": 3,
    "prior_chargebacks": 0, "ip_risk_score": .25, "is_international": 0,
    "is_new_device": 0, "merchant_category": "retail", "transaction_type": "card",
}
MOCK = {
    "fraud_probability": .12, "risk_score": 12, "risk_level": "LOW",
    "is_flagged": False, "model_version": "synthetic-test", "reasons": [],
}


def new_key():
    return "BATCH-" + uuid.uuid4().hex[:18]


def test_atomic_batch_success_and_history(monkeypatch):
    monkeypatch.setattr(batch_route, "score", lambda item: MOCK)
    keys = [new_key(), new_key()]
    with TestClient(app) as client:
        response = client.post("/predict/batch", json={"transactions": [
            {**VALID, "transaction_id": key} for key in keys]})
        assert response.status_code == 201, response.text
        result = response.json()
        assert result["count"] == 2 and result["demo_only"] is True
        assert [r["transaction_id"] for r in result["results"]] == keys
        assert all(client.get(f"/transactions/{key}").status_code == 200 for key in keys)
        assert client.post("/predict/batch", json={"transactions": [
            {**VALID, "transaction_id": keys[0]}, {**VALID, "transaction_id": new_key()}
        ]}).status_code == 409


def test_duplicate_inside_batch_is_rejected_without_persistence(monkeypatch):
    monkeypatch.setattr(batch_route, "score", lambda item: MOCK)
    key = new_key()
    with TestClient(app) as client:
        response = client.post("/predict/batch", json={"transactions": [
            {**VALID, "transaction_id": key}, {**VALID, "transaction_id": key}]})
        assert response.status_code == 409
        assert client.get(f"/transactions/{key}").status_code == 404


def test_batch_validation_and_size():
    with TestClient(app) as client:
        assert client.post("/predict/batch", json={"transactions": []}).status_code == 422
        assert client.post("/predict/batch", json={"transactions": [{**VALID, "amount": -1}]}).status_code == 422
        assert client.post("/predict/batch", json={"transactions": [VALID] * 26}).status_code == 422
        assert client.post("/predict/batch", json={"transactions": [VALID], "card_number": "1234"}).status_code == 422


def test_batch_rolls_back_if_later_model_fails(monkeypatch):
    key1, key2 = new_key(), new_key()
    calls = 0

    def failure_on_second(item):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ModelIntegrityError("private internal diagnostic")
        return MOCK

    monkeypatch.setattr(batch_route, "score", failure_on_second)
    with TestClient(app) as client:
        response = client.post("/predict/batch", json={"transactions": [
            {**VALID, "transaction_id": key1}, {**VALID, "transaction_id": key2}]})
        assert response.status_code == 503
        assert "private internal diagnostic" not in response.text
        assert client.get(f"/transactions/{key1}").status_code == 404
        assert client.get(f"/transactions/{key2}").status_code == 404
