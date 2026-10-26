import numpy as np
from ml.data.generate import create_synthetic
from ml.data.feature_engineering import make_preprocessor
from ml.config import FEATURES

def test_preprocessor_handles_unknown_categories():
    df=create_synthetic(60)
    pre=make_preprocessor().fit(df[FEATURES])
    unknown=df[FEATURES].iloc[:1].copy(); unknown['merchant_category']='never_seen'
    arr=pre.transform(unknown)
    assert arr.shape[0]==1
    assert np.isfinite(arr).all()
