# SQLite demo backup and recovery drill

**Scope: only explicitly confirmed fictional SQLite data in local/test environments.** This command does **not** back up hosted PostgreSQL, encrypt backups, provide off-site durability, enforce data retention, or substitute for a disaster-recovery plan. Never use it for real cardholder/financial records.

First preview the counts (no file is created):

```bash
python scripts/backup_demo_sqlite.py --source ./transactionshield.sqlite3 --output ./demo-snapshot.sqlite3
```

Then explicitly confirm that the input database contains only fictional test data:

```bash
python scripts/backup_demo_sqlite.py --source ./transactionshield.sqlite3 --output ./demo-snapshot.sqlite3 --confirm-synthetic-only
```

The command takes a transactionally consistent SQLite snapshot via the SQLite backup API, checks SQLite integrity and that `transactions` and `demo_review_feedback` tables exist, and verifies backup row counts. It refuses a missing input, a symlink, an existing output file, a wrong schema, or an environment other than `development`/`test`. It never prints transaction IDs or individual records.

For a recovery **drill**, restore **to a separate, new local test environment**, keeping the original intact. Inspect the snapshot using `sqlite3 demo-snapshot.sqlite3 'PRAGMA quick_check;'` or rerun `inspect_demo_database` in Python and check it reports the expected row counts. Never overwrite a running database with the file.

## Actual production deployment

Use the managed database provider's automatic encrypted backups, point-in-time recovery, tested restore runbooks, scoped IAM, retention and documented RTO/RPO. No such production backup or recovery has been verified by this project.
