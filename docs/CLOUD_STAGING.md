# Protected cloud staging (provider account connection required)

A reviewed [Render Blueprint](../deploy/render.yaml) defines a protected, single-instance **API** plus managed PostgreSQL. This is **infrastructure as code, not proof of a running deployment**. No provider account, billing, legal approval, domain or bank connection is provided in the repository.

## Setup (requires an authorized Render owner)

1. Open Render Dashboard → **New → Blueprint**; choose this GitHub repository and the Blueprint path `deploy/render.yaml`.
2. Review service and PostgreSQL **plan/pricing**, region, database retention and access restrictions before approving creation. Costs and feature availability may vary.
3. Render generates a strong `API_KEY` secret and supplies the database connection via `fromDatabase`. **Never put either secret into GitHub or frontend code.** The service normalizes `postgres://`/`postgresql://` to SQLAlchemy's `psycopg` dialect.
4. Configure permitted CORS origins to a real trusted HTTPS origin. `https://example.invalid` intentionally grants no real frontend origin. For a restricted API-only staging service, this can remain unchanged.
5. Render uses `ENVIRONMENT=staging`, deliberately not `production`; the project refuses synthetic-only models in production. Render builds the Docker image with a synthetic-only demo model, applies Alembic migrations and starts Uvicorn on `$PORT`.
6. Test `GET /health` and `GET /ready`; verify that `GET /metrics` returns 401 without `X-API-Key` and succeeds only with the server-side credential. Revoke/rotate secrets if compromised.
7. Put an identity-aware API gateway before staging users. Add enforced rate limits, durable audit/backup/restore and penetration testing before handling approved sensitive information.

The public GitHub Pages preview is **different**: it displays an offline local rule simulation with no real API traffic. Do not embed `API_KEY` in `VITE_` variables, HTML, cookies accessible to arbitrary JavaScript, or GitHub Pages.

## Release and rollback

- Build/validate a new revision in CI. Review migration changes and backup/restore evidence **before** deployment.
- Deploy to staging and test readiness, unauthorized rejection and drift endpoint. Freeze the trained model digest and provenance.
- Use provider's deploy history to roll back code, **but DB schema rollback must be planned separately**; avoid irreversible migrations.
- Treat low PR-AUC/recall or missing authorized labels as a **no-go** for financial decisions. Send to an authorized human review process, not an automated payment block.

## Not completed by checking in this file

There is no Render account/session connected here, no live managed service or domain configured, no independent external fraud validation, and no independent security certification. Those are separate organizational and technical gates requiring real credentials, data, approvals, and specialist assessment.
