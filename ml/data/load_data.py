from pathlib import Path
import pandas as pd
from ml.config import DATA
from ml.data.validate_data import validate_dataframe

def load_data(path=DATA):
    df = pd.read_csv(Path(path), parse_dates=["event_time"])
    validate_dataframe(df, labeled=True)
    return df.sort_values("event_time").reset_index(drop=True)
