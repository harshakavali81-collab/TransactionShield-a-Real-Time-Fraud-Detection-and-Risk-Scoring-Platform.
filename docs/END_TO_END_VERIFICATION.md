# End-to-end demo verification

The stand-alone command below creates a **fresh temporary SQLite database**, runs the **real Alembic migrations**, exercises an actual FastAPI `TestClient` with an API key, and then deletes the temporary database:

```bash
python scripts/smoke_e2e.py --report artifacts/reports/end_to_end_smoke.json
```

It verifies public liveness/readiness; protected model metrics; rejected unauthenticated requests; one single prediction; a two-transaction atomic batch; duplicate rejection with no partial writes; transaction history and detail; demo reviewer feedback and provenance; monitoring; and statistics consistent with the three accepted predictions.

The output report contains **check names only**, no API keys, request payloads, identifiers or simulated customer details. `records_persisted_after_run` is always zero because the database is destroyed after the test. The test does not contact a bank or external production service.

CI runs this test independently from the unit suite. Existing synthetic metrics are not an assessment of real fraud performance. The test's success means the **demonstration workflow** functions; it does not mean a real banking integration, live availability, compliance, encryption policy or third-party security review has passed.
