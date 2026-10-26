import pandas as pd
from ml.config import FEATURES, LABEL
NUM_LIMITS = {"amount": (0, 1_000_000), "hour":(0,23), "account_age_days":(0,100_000), "velocity_24h":(0,10_000), "prior_chargebacks":(0,100), "ip_risk_score":(0,1), "is_international":(0,1), "is_new_device":(0,1)}

def validate_dataframe(df:pd.DataFrame, labeled=False):
    cols=FEATURES+([LABEL] if labeled else [])
    missing=set(cols)-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    if df[cols].isnull().any().any(): raise ValueError("Null values require remediation before training or prediction")
    for col,(a,b) in NUM_LIMITS.items():
        values=pd.to_numeric(df[col],errors="coerce")
        if values.isnull().any() or not values.between(a,b).all():raise ValueError(f"Invalid range or type: {col}")
    if labeled and not df[LABEL].isin([0,1]).all():raise ValueError("Labels must be binary")
    return True
