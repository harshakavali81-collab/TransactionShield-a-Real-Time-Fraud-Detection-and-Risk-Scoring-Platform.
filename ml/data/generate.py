"""Deterministic synthetic examples; NOT operational payment data."""
import numpy as np
import pandas as pd

def create_synthetic(n=4000, seed=42):
    rng = np.random.default_rng(seed)
    hour = rng.integers(0, 24, n)
    amount = np.round(np.exp(rng.normal(4.4, 1.15, n)), 2)
    age = rng.integers(1, 3650, n)
    velocity = rng.poisson(2.2, n)
    prior = rng.binomial(2, 0.035, n)
    ip_risk = rng.beta(2, 7, n)
    abroad = rng.binomial(1, 0.08, n)
    new_device = rng.binomial(1, 0.14, n)
    merchant = rng.choice(["retail", "travel", "digital", "groceries", "gaming"], size=n, p=[.29,.12,.22,.27,.10])
    kind = rng.choice(["card", "bank_transfer", "wallet", "ecommerce"], size=n)
    # Deliberately makes minority labels from genuine feature signals, not a label-derived feature.
    logit = -5.4 + 0.9 * (amount > 700) + 0.7 * ((hour <= 5)) + 0.6 * (age < 45) + 0.14 * velocity + 1.0 * prior + 1.0 * abroad + 0.9 * new_device + 2.2 * ip_risk + 0.55 * (merchant == "gaming")
    prob = 1 / (1 + np.exp(-np.clip(logit, -20, 20)))
    y = rng.binomial(1, prob)
    df = pd.DataFrame({"transaction_id": [f"DEMO-{i:07d}" for i in range(n)],
        "event_time": pd.date_range("2025-01-01", periods=n, freq="30min").astype(str),
        "amount": amount, "hour":hour, "account_age_days":age,
        "velocity_24h":velocity, "prior_chargebacks":prior, "ip_risk_score":ip_risk,
        "is_international":abroad, "is_new_device":new_device,
        "merchant_category":merchant, "transaction_type":kind, "is_fraud":y})
    return df
