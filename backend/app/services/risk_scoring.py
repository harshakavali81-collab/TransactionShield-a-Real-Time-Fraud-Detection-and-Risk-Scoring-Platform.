def level(probability:float):
    return "HIGH" if probability>=0.65 else "MEDIUM" if probability>=0.30 else "LOW"

def reasons_for_features(x):
    reasons=[]
    if x["velocity_24h"]>=8:reasons.append("Elevated transaction velocity")
    if x["is_international"]:reasons.append("International transaction")
    if x["is_new_device"]:reasons.append("New device")
    if x["ip_risk_score"]>=.65:reasons.append("Higher IP risk indicator")
    if x["prior_chargebacks"]:reasons.append("Past chargeback signal")
    if x["account_age_days"]<=30:reasons.append("New account")
    if x["amount"]>=1000:reasons.append("Larger transaction amount")
    return reasons or ["No configured behavioral rule triggered; model considers all supplied features"]
