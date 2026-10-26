# Operation runbook — demonstration environment

## Preflight
1. Use Python 3.11 and a throwaway database. Run `python scripts/generate_demo.py`, `python -m ml.training.train --fast` and `python scripts/create_report.py`.
2. Run `pytest -q`; run `python scripts/check_release.py`; run `alembic upgrade head` with a **new empty SQLite/PostgreSQL database**.
3. Run `cd frontend && npm install && npm run build`. Run Docker Compose in an environment with Docker Engine.
4. Check `/health` (liveness) and `/ready` (model + DB readiness). Probe `/monitoring/overview` after sending synthetic requests.

## Common failure recovery
- Model unavailable: retrain offline and redeploy trusted model artifact; do not download unknown joblib files.
- Database connection refused: check DATABASE_URL and PostgreSQL health. Stop write traffic before applying migration changes. Back up DB before upgrading.
- API 401: valid gateway-injected `X-API-Key` missing; never hardcode real keys into web bundles.
- 409 duplicate: transaction_id already exists; consumers treat the duplicate as an at-least-once delivery, but audit the source before replaying real messages.
- Drift mean-shift alert: investigate input distribution and upstream changes; **not** direct evidence of fraud or a retraining trigger by itself.
- Missing confirmed labels: true live precision/recall cannot be inferred from reviews or model scores.

## Rollback
Deploy a previous, tested container and model as a matched pair. Coordinate schema compatibility before rolling back a migration. Do not automatically run `alembic downgrade` against a database containing real transactions; obtain backups and a migration plan.

## Backups
For the containerized demo, `pg_dump` can capture the development PostgreSQL DB. Validate restores regularly in a disposable environment; this repository does **not** create or guarantee managed cloud backups.

## Optional Kafka-compatible stream demonstration
1. Run `docker compose --profile streaming up -d broker` to start Redpanda locally (requires Docker and image download).
2. Install `pip install -r requirements-streaming.txt`.
3. Keep backend running, then run `python -m streaming.consumer` in one terminal and `python -m streaming.producer --count 20` in another.
4. Producer emits generated transactions only. Consumer commits offsets after 201 or duplicate 409; other responses stop consumption for operator attention. No dead-letter stream, TLS/SASL, consumer parallelism or exactly-once guarantee is provided. Test infrastructure before claiming live operation.
