# Security policy and threat model

**Scope:** public educational code using generated transactions. Never send PAN, CVV, PIN, credentials, personal financial data, or production payment payloads to this demo. Model artifacts are trusted Python/joblib pickle files; load only artifacts produced by your build pipeline.

## Defenses added
- Environment validation makes an accidental production launch fail without a >=32-character API key, HTTPS-only explicit CORS origins and PostgreSQL.
- Timing-resistant shared key comparison (`X-API-Key`); this is **not** user login, RBAC or tenancy. Public `/health` and `/ready` reveal no customer data. Docs are disabled in production configuration.
- Endpoint input validation via Pydantic; enforce byte limits for both declared and streamed bodies; retain bounded history/monitoring queries.
- Optional `DEMO_RATE_LIMIT` token bucket per transport peer and process (default 0, examples 60/minute), with 429 + `Retry-After`. Public `/health`, `/ready`, and CORS preflight are exempt. Client-supplied forwarding headers are ignored. Storage is capped to 4096 peer entries.
- This is **not distributed**, not authenticated per-user, and can group users behind the same NAT or proxy. Require a trusted identity-aware rate-limiting gateway/WAF for internet-facing traffic.
- SQLAlchemy parameterized queries, duplicate transaction ID rejection, simple response hardening headers, request IDs and latency logging without payload content.
- A synthetic feature snapshot supports drift visualization; do not store equivalent raw fields for actual users without legal, retention and minimization design.
- Feedback entries are explicitly unverified human review examples; the API never calls them verified fraud ground truth.

- Synthetic development-data cleanup is opt-in via a dry-run-first bounded CLI; it **cannot** be used against `ENVIRONMENT=production`. This is not a general privacy compliance or production retention system.
- The `/metrics` API verifies the manifest before publishing stored demonstration evaluation numbers. This verifies consistency, not scientific validity or cryptographic authenticity.

## Security boundaries *not* implemented
A production system needs an identity provider, per-tenant permission checks, a rate-limiting gateway, TLS at every hop, private networks, encrypted backups, secrets management, audit integrity and rotation, threat detection, model registry controls, data retention policies and independent penetration testing. The API key should be injected server-side by a trusted proxy, **not embedded in React client assets**. No financial decisions may be automated using this demonstration.

## Reporting issues
Do not open public issues with secrets or personal data. Rotate any accidentally disclosed API keys and revoke any compromised infrastructure credentials. See [deployment](DEPLOYMENT.md).
