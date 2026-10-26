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


## Additional monitoring endpoints
- `GET /ready`: returns HTTP 200 only if a trusted model artifact is present and database connectivity succeeds; otherwise 503.
- `GET /monitoring/overview?limit=200`: bounded recent synthetic feature mean-shift checks (10–1000 rows). Explicitly does **not** claim fraud accuracy.
- `POST /monitoring/demo-feedback`: submit `{ "transaction_id": "...", "review_label": true, "reviewer_note": "demo" }` after a scored transaction. Stores unverified demo-only reviewer input, rejects unknown or duplicate transaction IDs.
- `GET /monitoring/demo-feedback-metrics`: computes provisional metrics against **unverified demonstration reviews only**; never real-world fraud ground truth.

The optional `X-API-Key` header authenticates the API when `API_KEY` is configured. Keep it in a backend proxy or secret manager, not bundled in client-side JavaScript. Production config requires `ENVIRONMENT=production` with an explicit HTTPS CORS origin, a long random API_KEY and PostgreSQL.
