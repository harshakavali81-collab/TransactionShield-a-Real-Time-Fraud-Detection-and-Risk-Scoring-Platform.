# Production-readiness audit

| Area | Implemented and testable | Still requires an external environment / real evidence |
|---|---|---|
| Fraud modeling | Synthetic chronological holdout, model leaderboard, PR-AUC, recall, demo threshold | Consent-based real transactions, reliable chargeback labels, calibration, drift-aware replay and third-party validation |
| Backend | Validation, optional shared key, response headers, request logs, REST API | OAuth/OIDC, RBAC, tenancy, rate limiting behind gateway, SAST/DAST, pen test |
| Database | SQLAlchemy, PostgreSQL Compose, Alembic initial schema migration | Managed HA Postgres, migrations from legacy live tables, PITR backups, retention enforcement |
| Monitoring | API readiness, heuristic mean-shift endpoint and demo reviewer metrics | Prometheus/OTel, SLOs, alarm routing, labeled production review outcomes |
| Ingestion | Synthetic REST simulator and optional Kafka-compatible producer/consumer | Event contracts, schema registry, partition scale, retries/DLQ, secure Kafka cluster |
| Frontend | React UI with monitoring tab and frontend GitHub CI build | Secure identity-aware hosted access, accessibility audit, cross-browser acceptance |
| Deployment | Multi-service Docker Compose and build workflows | Cloud provider selection, real domain/TLS, secrets, infrastructure provisioning, staging and rollback |

**Safety gate:** The repository is a complete *demonstration application*, not a certified real-time banking fraud service. No actual fraud prevention effectiveness or production-level security should be claimed.

## Latest reproducible safety improvements

- External labeled holdout evaluator (operator-attested authorization, frozen threshold, bootstrap intervals and support-aware subgroup summaries), but **no real dataset currently supplied or independently evaluated**.
- Strict approved CSV validation rejects direct identifiers, extra columns and duplicate opaque transaction tokens; **not connected to a bank feed**.
- Actual request-stream byte accounting (including absent Content-Length) in FastAPI. This is only one protective measure, not penetration testing.
- GitHub Pages workflow for a public **offline fictional simulation**; whether a public URL exists depends on GitHub Pages settings and the deployment run.
- Render Blueprint for optional protected API staging with provider-managed HTTPS ingress and DB, and generated server-side API key; **not provisioned until Render is connected by an authorized owner**.

## Explicit synthetic model production gate (October 2026)
The optional Render Blueprint is staging-only. `ENVIRONMENT=production` is rejected by configuration because the repository contains no independently validated banking model. See [release readiness](RELEASE_READINESS.md) and the JSON evidence report.
