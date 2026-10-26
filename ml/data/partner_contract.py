"""Privacy-minimized offline import contract for *authorized* transaction features.

This module does not talk to banks, receive PAN/CVV values or authenticate providers.
Each provider must map its own approved fields to this small schema upstream.
"""
from pathlib import Path
import pandas as pd
from ml.config import FEATURES, LABEL
from ml.data.validate_data import validate_dataframe

META = ["transaction_id", "event_time"]
SENSITIVE_NAMES = {
    "card_number", "pan", "cvv", "cvc", "pin", "password", "email",
    "phone", "mobile", "full_name", "customer_name", "address", "iban",
    "bank_account", "account_number", "aadhaar", "passport", "ssn",
}


def validate_approved_feed(frame: pd.DataFrame, *, labeled: bool = False, minimum_rows: int = 1) -> pd.DataFrame:
    """Reject extra columns, identifiers, malformed time and ambiguous records.

    Full dataset is kept in memory; callers must not log its rows or raw values.
    """
    wanted = set(FEATURES + META + ([LABEL] if labeled else []))
    incoming = set(frame.columns)
    prohibited = {str(k).strip().lower() for k in incoming} & SENSITIVE_NAMES
    if prohibited:
        raise ValueError("Restricted direct identifiers are not accepted by this feed")
    extras = incoming - wanted
    missing = wanted - incoming
    if missing or extras:
        raise ValueError(f"Feed schema mismatch: missing={sorted(missing)}; extra columns={len(extras)}")
    if len(frame) < minimum_rows:
        raise ValueError(f"Feed needs at least {minimum_rows} rows")
    validate_dataframe(frame, labeled=labeled)
    if frame["transaction_id"].isna().any():
        raise ValueError("Missing opaque transaction IDs")
    ids = frame["transaction_id"].astype(str)
    if not ids.str.fullmatch(r"[A-Za-z0-9_-]{1,80}").all():
        raise ValueError("Invalid opaque transaction IDs")
    if ids.duplicated().any():
        raise ValueError("Duplicate transaction IDs")
    times = pd.to_datetime(frame["event_time"], utc=True, errors="coerce")
    if times.isna().any():
        raise ValueError("All event_time values must be parseable timestamps")
    for col in ["merchant_category", "transaction_type"]:
        values = frame[col]
        if not pd.api.types.is_string_dtype(values) and not values.map(lambda v: isinstance(v, str)).all():
            raise ValueError(f"{col} must contain strings")
        if not values.astype(str).str.fullmatch(r"[A-Za-z0-9_-]{1,64}").all():
            raise ValueError(f"{col} contains invalid categories")
    clean = frame[list(META) + FEATURES + ([LABEL] if labeled else [])].copy()
    clean["event_time"] = times
    return clean.sort_values("event_time", kind="stable").reset_index(drop=True)


def read_approved_feed(path: str | Path, *, labeled: bool = False, minimum_rows: int = 1) -> pd.DataFrame:
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != ".csv":
        raise ValueError("Feed must be an existing local CSV file")
    # The application does not fetch external endpoints or hold provider credentials.
    return validate_approved_feed(pd.read_csv(source), labeled=labeled, minimum_rows=minimum_rows)
