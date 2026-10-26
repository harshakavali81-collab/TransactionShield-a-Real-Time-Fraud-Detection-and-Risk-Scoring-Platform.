from backend.app.services.risk_scoring import level,reasons_for_features
from ml.monitoring.data_drift import evaluate_drift

def test_risk_bands():
    assert level(.01)=='LOW'
    assert level(.3)=='MEDIUM'
    assert level(.65)=='HIGH'

def test_hints_not_model_attributions():
    assert 'International transaction' in reasons_for_features({'velocity_24h':0,'is_international':1,'is_new_device':0,'ip_risk_score':.0,'prior_chargebacks':0,'account_age_days':100,'amount':30})

def test_drift_flags_mean_shift():
    import pandas as pd
    output=evaluate_drift(pd.DataFrame({'amount':[15,16]}),{'amount':{'mean':2.0,'std':2.0}})
    assert output['flagged_features']==['amount']
