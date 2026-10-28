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

## Full workflow and snapshot recovery (additional checks)

- `python scripts/smoke_e2e.py --report artifacts/reports/end_to_end_smoke.json` creates and migrates an isolated temporary SQLite DB, requires API-key authentication on protected endpoints, verifies the full single/batch scoring and review journey, and removes all data after testing.
- `python scripts/backup_demo_sqlite.py --source ./transactionshield.sqlite3 --output ./demo-snapshot.sqlite3` previews a consistent local demo-only backup. Add `--confirm-synthetic-only` to write a new verified snapshot; production environments and existing destinations are refused.
- The CI workflow runs both the ephemeral API smoke test and a synthetic SQLite backup snapshot check, and uploads an end-to-end evidence JSON report.
- Neither check establishes compliance with payment/financial regulations or substitutes for a managed PostgreSQL PITR backup and restore test.

## Rolling-origin time-series checks

Unit tests verify sorted window boundaries, minority label handling, and no crossover of train/validation/test rows. CI regenerates synthetic rolling diagnostics separately after unit tests.
