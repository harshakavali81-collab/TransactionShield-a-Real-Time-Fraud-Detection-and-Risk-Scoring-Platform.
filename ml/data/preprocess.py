from ml.config import FEATURES
from ml.data.validate_data import validate_dataframe

def prepare_features(df):
    validate_dataframe(df)
    return df[FEATURES].copy()
