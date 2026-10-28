# Fictional what-if scenario lab

TransactionShield includes a **stateless educational scenario comparator** for two fully specified synthetic transactions. The API evaluates both examples with the same saved model and reports how their scores differ. It makes **no changes to the database**, sends no external provider requests, and performs no payment decision.

- `POST /simulate/what-if` accepts `{ "baseline": {...}, "scenario": {...} }`, where each object has the same validated feature schema as `/predict` **without** a `transaction_id`.
- Returns the two risk results, sorted list of changed feature names, difference in predicted score (not calibrated), difference in 0–100 risk score, and whether the review flag changes.
- Scores are rounded by the regular scoring pipeline. The difference is reported in probability units; the React page converts it to percentage points for display.
- Rejects extra fields, identifiers and invalid feature ranges with HTTP 422. A missing or inconsistent model returns a generic HTTP 503.
- `/simulate/what-if` is protected by the same optional `X-API-Key`, body-size limit and demo rate limiter as `/predict`.
- The GitHub Pages preview does not use the ML model: its comparison runs separate **fictional rules in the browser** and is clearly marked as such.

**Limitations:** Changing an input and observing a different model score is *not* a causal explanation. The training dataset is synthetic and its output is not guaranteed to be a calibrated fraud probability. Do not feed real card/account details, make customer decisions, or interpret changes as verified fraud-prevention impact.

### Example (synthetic only)

```bash
curl -X POST http://localhost:8000/simulate/what-if \
  -H 'Content-Type: application/json' \
  -d '{"baseline":{"amount":600,"hour":14,"account_age_days":450,"velocity_24h":2,"prior_chargebacks":0,"ip_risk_score":0.12,"is_international":0,"is_new_device":0,"merchant_category":"retail","transaction_type":"card"},"scenario":{"amount":600,"hour":14,"account_age_days":450,"velocity_24h":10,"prior_chargebacks":0,"ip_risk_score":0.12,"is_international":0,"is_new_device":1,"merchant_category":"retail","transaction_type":"card"}}'
```

The automated tests verify response fields, validation, no database writes, model failure handling and inconsistent model-version rejection.
