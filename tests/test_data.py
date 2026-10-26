import pytest
import pandas as pd
from ml.data.generate import create_synthetic
from ml.data.validate_data import validate_dataframe

def test_synthetic_deterministic_and_minority_class():
    a=create_synthetic(1400)
    b=create_synthetic(1400)
    pd.testing.assert_frame_equal(a,b)
    assert 0<a.is_fraud.mean()<0.25
    assert validate_dataframe(a,labeled=True)

def test_invalid_range():
    a=create_synthetic(20)
    a.loc[0,"hour"]=25
    with pytest.raises(ValueError,match="hour"):validate_dataframe(a,labeled=True)

def test_missing_feature():
    a=create_synthetic(20).drop(columns="ip_risk_score")
    with pytest.raises(ValueError,match="Missing"):validate_dataframe(a)

def test_no_label_in_features():
    from ml.config import FEATURES
    assert 'is_fraud' not in FEATURES
