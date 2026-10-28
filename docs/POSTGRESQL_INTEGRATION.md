# PostgreSQL-backed API integration testing — synthetic only

The project previously ran most API tests against SQLite. PostgreSQL can behave differently around JSON columns, concurrent writes, transactions, time zones, and schema migrations, so GitHub CI now uses a dedicated `postgres:16` service with the **disposable database** `transactionshield_ci`.

The new script `python scripts/smoke_postgres.py --report artifacts/reports/postgres_ci_smoke.json` exercises migrated schema readiness, authentication, one stored score, a two-record atomic batch, duplicate rollback, an unpersisted what-if comparison, demo-review feedback, monitoring, model metrics, and database row counts.

## Safety limits

- The script refuses to run unless `ENVIRONMENT=test`, the backend URL is PostgreSQL, the **exact** database name is `transactionshield_ci`, and a synthetic test API key is supplied.
- The script creates and stores **fictional** transaction attributes only; CI destroys the service when the job ends.
- The integration check proves a disposable PostgreSQL/SQLAlchemy workflow, **not** throughput capacity, a cloud deployment, bank-feed compatibility, an authenticated multi-tenant product, security certification, or valid real-fraud predictions.
- The separate Docker image job checks that the Python backend and React/Nginx image Dockerfiles build. It does not assert the images are publicly deployed or production-hardened.

## Local invocation (use only a disposable database)

1. Start a **fresh** local PostgreSQL instance with a database named `transactionshield_ci`.
2. Set `DATABASE_URL=postgresql+psycopg://shield:YOUR_LOCAL_PASSWORD@127.0.0.1:5432/transactionshield_ci`, `ENVIRONMENT=test`, and `API_KEY=local-synthetic-test-only`.
3. Install the project requirements and run `alembic upgrade head`.
4. Run `python scripts/smoke_postgres.py --report artifacts/reports/postgres_ci_smoke.json`.

Never point this script at an actual bank dataset or any existing environment that must be preserved. Integration report artifacts do not contain customer records or credentials.
