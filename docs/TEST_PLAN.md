# Test plan
- Range and required feature validation (negative amounts, illegal hours and missing columns).
- Synthetic generation deterministic reproducibility and minority class presence.
- Train/validation/test splitting by monotonically increasing event time, model/pipeline serialization.
- Risk boundaries and rule hints correctness.
- `/health` when model absent/present; `GET /metrics` with and without training output.
- Scoring a transaction and database persistence; duplicate IDs return HTTP 409.
- Invalid scoring input yields HTTP 422; missing model yields HTTP 503.
- Frontend `npm run build` and E2E API reachability via `scripts/simulate_stream.py`.
- CI includes Python lint, pytest, local synthetic training, report chart generation, frontend build.

Not yet covered: performance/load testing, protected payment data handling, real-world drift, live label adjudication, migrations under traffic, cloud disaster recovery and security pen testing. Never claim production readiness from these checks.


## Extended test coverage
- `/health` and `/ready`: liveness, database/model readiness
- Monitoring: bounded feature snapshots and explicit absence of verified fraud outcome labels
- Feedback: duplicate protection, schema validation, unverified-label provenance
- Security: oversized requests, response headers, fail-closed production configuration
- Streaming: stable synthetic IDs, JSON roundtrip, ack and replay behavior through fakes
- Migrations: `alembic upgrade head` plus API release smoke tests in GitHub Actions
- Frontend: production asset compilation with `npm run build` in GitHub Actions
These tests do not replace host-level Kafka, cloud deployment, pentest or real-data backtesting.
