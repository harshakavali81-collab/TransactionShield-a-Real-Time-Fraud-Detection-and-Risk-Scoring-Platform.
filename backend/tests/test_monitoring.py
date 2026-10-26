"""Monitoring is a synthetic portfolio demo and must never claim ground-truth fraud labels."""
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.api.routes.predict as predictor

VALID = {"amount": 525, "hour": 18, "account_age_days": 222,
         "velocity_24h": 3, "prior_chargebacks": 0, "ip_risk_score": 0.25,
         "is_international": 0, "is_new_device": 0,
         "merchant_category": "retail", "transaction_type": "card"}
DUMMY = {"fraud_probability": 0.12, "risk_score": 12, "risk_level": "LOW",
         "is_flagged": False, "model_version": "test", "reasons": []}


def test_readiness_and_monitoring():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        ready = client.get('/ready')
        assert ready.status_code == 200
        assert ready.json()['database_ready'] is True
        response = client.get('/monitoring/overview')
        assert response.status_code == 200
        assert response.json()['model_performance'] == 'unavailable_without_independent_labels'
        assert client.get('/monitoring/overview?limit=99999').status_code == 422


def test_feedback_is_unverified_and_deduplicated(monkeypatch):
    monkeypatch.setattr(predictor, 'score', lambda txn: DUMMY)
    key = 'REVIEW-' + uuid.uuid4().hex[:18]
    with TestClient(app) as client:
        assert client.post('/predict', json={**VALID, 'transaction_id': key}).status_code == 201
        response = client.post('/monitoring/demo-feedback', json={
            'transaction_id': key, 'review_label': True, 'reviewer_note': 'demo only'})
        assert response.status_code == 201
        assert response.json()['label_provenance'] == 'unverified_demo_reviewer_input'
        assert client.post('/monitoring/demo-feedback', json={
            'transaction_id': key, 'review_label': False}).status_code == 409
        result = client.get('/monitoring/demo-feedback-metrics')
        assert result.status_code == 200
        assert result.json()['not_production_ground_truth'] is True


def test_rejects_invalid_feedback():
    with TestClient(app) as client:
        assert client.post('/monitoring/demo-feedback', json={
            'transaction_id': 'does-not-exist', 'review_label': False}).status_code == 404
        assert client.post('/monitoring/demo-feedback', json={
            'transaction_id': 'does-not-exist', 'review_label': False,
            'unknown_field': 'exfiltrate'}).status_code == 422
