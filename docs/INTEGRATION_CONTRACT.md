# Authorized transaction feed contract (offline)

`ml/data/partner_contract.py` is a **privacy-minimized ingestion interface**, not a live bank connection. It accepts only local CSV files from a source whose owner has separately authorized processing. It intentionally rejects payment card numbers, CVV, PIN, bank accounts, names, phone numbers, and all extra columns.

## Required fields

- Metadata: `transaction_id` (unique opaque token; `[A-Za-z0-9_-]` only), `event_time` (unambiguous parseable timestamp; normalized to UTC).
- Numeric features: `amount`, `hour`, `account_age_days`, `velocity_24h`, `prior_chargebacks`, `ip_risk_score`, `is_international`, `is_new_device`.
- Categoricals: `merchant_category`, `transaction_type` (short alphanumeric labels).
- **For model validation only:** `is_fraud` with 0/1 independently investigated outcome, mature enough to capture chargeback/report delays.

`amount` is a demonstration monetary feature without currency normalization. Real payment events need a legally reviewed currency conversion, timezone, label provenance and schema mapping maintained by the actual bank/source owner. An application does not obtain permission to ingest a feed merely because its schema validates.

## Usage

```bash
# Explicitly attest the rights to process the data. No network transfer or re-training occurs.
python -m scripts.validate_partner_feed --csv /secure/approved_features.csv --labeled --data-approved
```

Feed validation prevents accidental raw PII inclusion and duplicate IDs; it **does not** authenticate banks, attest consent, encrypt upstream traffic, or certify a financial institution's agreement. Keep incoming real data outside the repository and away from public CI. The imported CSV never gets committed to GitHub.

For independent model evaluation see [INDEPENDENT_VALIDATION.md](INDEPENDENT_VALIDATION.md).
