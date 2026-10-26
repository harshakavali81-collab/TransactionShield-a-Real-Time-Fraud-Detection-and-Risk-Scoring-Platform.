"""Simple standardized mean shift for demonstration. Not a validated full drift detector."""
from ml.config import NUMERIC

def evaluate_drift(df,reference,threshold=0.5):
    details={}
    for col in NUMERIC:
        if col not in df or col not in reference:continue
        z=abs(float(df[col].mean())-reference[col]["mean"])/max(reference[col]["std"],1e-6)
        details[col]={"z_mean_shift":round(z,3),"flagged":z>threshold}
    return {"method":"absolute standardized mean shift (demo heuristic)","threshold":threshold,
        "features":details,"flagged_features":[k for k,v in details.items() if v["flagged"]]}
