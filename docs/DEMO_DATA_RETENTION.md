# Synthetic demonstration data retention

**Scope:** This repository stores **fictional** scores and **unverified** fictional review feedback in development/test SQLite or PostgreSQL. The maintenance script intentionally **refuses** `ENVIRONMENT=production` (and unknown environments). It is not an enterprise data-retention policy, privacy program, or a substitute for a bank's retention requirements.

## Commands

```bash
# First, point DATABASE_URL at a disposable database containing only synthetic transactions.
# Preview transactions older than 30 days; no rows are changed.
python scripts/purge_demo_data.py --days 30

# Apply the deletion only after independently confirming the DB contains fictional data:
python scripts/purge_demo_data.py --days 30 --apply --confirm-synthetic-only

# Refuse a bulk delete with a lower safety cap:
python scripts/purge_demo_data.py --days 30 --max-records 100
```

## Safeguards and behavior

- **Dry run is the default** and prints only counts; it does not print transaction IDs or stored feature values.
- Deletes use `created_at` and a **strict older-than** cutoff in UTC. Only selected transactions and their associated `demo_review_feedback` rows are deleted, together in one database transaction.
- `--apply` alone does not delete anything; `--confirm-synthetic-only` is additionally required.
- If the candidate count is above `--max-records` (default 1,000), the command **refuses all deletion**, requiring an operator to reconsider the intended scope rather than partially applying a batch.
- Never run this against production financial or customer data. It has no support for tenant boundaries, legal holds, backups, deletion receipts, archived replicas, or regulatory data-retention rules.
- To enforce a real-world retention program, build an independently reviewed, consent- and jurisdiction-aware policy with audit logs, legal holds, backup expiry, and privileged access controls.

## Verification

`pytest -q tests/test_demo_retention.py` covers read-only previews, committed deletion, related review cleanup, production refusal, explicit confirmation, bounded deletion, and input validation.
