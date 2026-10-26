import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.api.routes.predict as predictor

VALID={'amount':525,'hour':18,'account_age_days':222,'velocity_24h':3,'prior_chargebacks':0,'ip_risk_score':.25,'is_international':0,'is_new_device':0,'merchant_category':'retail','transaction_type':'card'}
DUMMY={'fraud_probability':.12,'risk_score':12,'risk_level':'LOW','is_flagged':False,'model_version':'test-model','reasons':['Demo']}

def test_prediction_and_persistence(monkeypatch):
    monkeypatch.setattr(predictor,'score',lambda txn:DUMMY)
    key='TEST-'+uuid.uuid4().hex[:18]
    with TestClient(app) as client:
        response=client.post('/predict',json={**VALID,'transaction_id':key})
        assert response.status_code==201, response.text
        assert response.json()['risk_score']==12
        detail=client.get(f'/transactions/{key}')
        assert detail.status_code==200
        assert detail.json()['transaction_id']==key
        duplicated=client.post('/predict',json={**VALID,'transaction_id':key})
        assert duplicated.status_code==409

def test_invalid_payload():
    with TestClient(app) as client:
        response=client.post('/predict',json={**VALID,'amount':-3})
        assert response.status_code==422

def test_missing_model_returns_503(monkeypatch):
    monkeypatch.setattr(predictor,'score',lambda txn: (_ for _ in ()).throw(FileNotFoundError('train first')))
    with TestClient(app) as client:
        response=client.post('/predict',json=VALID)
    assert response.status_code==503
