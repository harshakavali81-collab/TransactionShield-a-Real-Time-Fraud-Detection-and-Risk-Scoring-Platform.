from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "synthetic_transactions.csv"
MODEL = ROOT / "artifacts" / "models" / "fraud_model.joblib"
METRICS = ROOT / "artifacts" / "models" / "metrics.json"
REPORTS = ROOT / "artifacts" / "reports"
NUMERIC = ["amount", "hour", "account_age_days", "velocity_24h", "prior_chargebacks", "ip_risk_score", "is_international", "is_new_device"]
CATEGORICAL = ["merchant_category", "transaction_type"]
FEATURES = NUMERIC + CATEGORICAL
LABEL = "is_fraud"
