# API reference

Local interactive OpenAPI at <http://localhost:8000/docs>.

| Method | Path | Function |
|---|---|---|
| GET | `/health` | Health and presence of trained model |
| POST | `/predict` | Score and persist a transaction, returns HTTP 201 |
| GET | `/history?limit=50` | Latest stored scored transactions, max 500 |
| GET | `/transactions/{transaction_id}` | Retrieve one persisted transaction |
| GET | `/statistics` | Total/flagged/rate/mean score |
| GET | `/analytics` | Distribution of latest 500 risk levels |
| GET | `/metrics` | Held-out synthetic model benchmark |

Example scoring request:

```bash
curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{"amount":1500,"hour":2,"account_age_days":10,"velocity_24h":11,"prior_chargebacks":1,"ip_risk_score":0.85,"is_international":1,"is_new_device":1,"merchant_category":"gaming","transaction_type":"card"}'
```

`fraud_probability` is the fitted model score (not guaranteed calibrated). `risk_score` is rounded score ×100. `is_flagged` tests the separate validation-tuned F2 threshold; it need not match the fixed HIGH risk category. `reasons` list heuristic rule-based review hints, NOT SHAP values. Input validation errors return 422; duplicate transaction IDs return 409; missing model returns 503. Optional `API_KEY` enforces an `X-API-Key` header except for docs/health; not suitable as sole production authorization. Database defaults to SQLite locally; supply `DATABASE_URL` for PostgreSQL.
