"""Only use attributes available at request time. No target leakage."""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from ml.config import NUMERIC, CATEGORICAL

def make_preprocessor():
    return ColumnTransformer([
        ("num", Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]), NUMERIC),
        ("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False), CATEGORICAL)
    ], sparse_threshold=0)
