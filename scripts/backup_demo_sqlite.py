"""Consistent SQLite backup for *fictional local demo* records only.

This is not an encrypted, offsite, enterprise or PostgreSQL backup solution.
Dry-run previews by default. Creation refuses production and never overwrites.
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def inspect_demo_database(source: Path) -> dict:
    if not source.is_file() or source.is_symlink():
        raise ValueError("source must be a local regular SQLite demo file")
    uri = f"file:{source.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"transactions", "demo_review_feedback"}.issubset(tables):
            raise ValueError("not a migrated TransactionShield demonstration database")
        transactions = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        feedback = db.execute("SELECT COUNT(*) FROM demo_review_feedback").fetchone()[0]
    return {"transaction_count": int(transactions), "review_count": int(feedback)}


def backup_demo_database(source, output, *, confirm=False, environment="development") -> dict:
    """Only a local demo backup, with no overwrite and atomic publication."""
    if environment not in {"development", "test"}:
        raise ValueError("refusing backups from production or unknown environment")
    source, output = Path(source), Path(output)
    if not source.exists() or source.is_symlink() or not source.is_file():
        raise ValueError("source must be an existing regular SQLite demo database")
    if output.exists() or output.is_symlink():
        raise FileExistsError("backup destination already exists")
    if source.resolve() == output.resolve():
        raise ValueError("backup cannot overwrite the source database")
    counts = inspect_demo_database(source)
    result = {"status": "dry_run", "scope": "fictional_local_sqlite_only", **counts,
              "encrypted": False, "production_backup": False}
    if not confirm:
        return result
    if not output.parent.is_dir():
        raise ValueError("backup output parent directory does not exist")
    # Create-exclusive temporary database in target folder. Never overwrite.
    from uuid import uuid4
    staging = output.with_name(f".{output.name}.{uuid4().hex}.tmp")
    try:
        with sqlite3.connect(f"file:{source.resolve().as_posix()}?mode=ro", uri=True) as src:
            with sqlite3.connect(str(staging)) as dst:
                src.backup(dst)
        actual = inspect_demo_database(staging)
        if actual != counts:
            raise ValueError("backup row-count verification failed")
        # This is explicitly a demo-only process, and the destination is
        # rechecked immediately before copy to reduce overwrite risk.
        if output.exists() or output.is_symlink():
            raise FileExistsError("backup destination appeared during creation")
        with staging.open("rb") as fin, output.open("xb") as fout:
            for chunk in iter(lambda: fin.read(1024 * 1024), b""):
                fout.write(chunk)
        result["status"] = "created_and_verified"
    finally:
        staging.unlink(missing_ok=True)
    return result


def main():
    from backend.app.core.config import ENVIRONMENT, DATABASE_URL
    parser = argparse.ArgumentParser(description="Dry-run/backup fictional SQLite demo only")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirm-synthetic-only", action="store_true")
    args = parser.parse_args()
    source = args.source
    if source is None:
        if not DATABASE_URL.startswith("sqlite:///") or DATABASE_URL.endswith(":memory:"):
            parser.error("explicit --source required when database is not file-backed SQLite")
        source = Path(DATABASE_URL[len("sqlite:///"):])
    result = backup_demo_database(source, args.output, confirm=args.confirm_synthetic_only,
                                  environment=ENVIRONMENT)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
