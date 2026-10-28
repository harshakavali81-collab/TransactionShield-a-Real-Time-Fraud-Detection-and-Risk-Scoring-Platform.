"""Backup consistency and fail-safe tests for fictional local databases."""
import sqlite3
from pathlib import Path

import pytest

from scripts.backup_demo_sqlite import backup_demo_database, inspect_demo_database


def make_database(tmp_path):
    db_path = tmp_path / "demo.sqlite3"
    with sqlite3.connect(db_path) as connection:
        connection.executescript("""
            CREATE TABLE transactions (transaction_id TEXT PRIMARY KEY);
            CREATE TABLE demo_review_feedback (transaction_id TEXT PRIMARY KEY);
            INSERT INTO transactions VALUES ('fictional-demo-001');
            INSERT INTO demo_review_feedback VALUES ('fictional-demo-001');
        """)
    return db_path


def test_backup_dry_run_does_not_write(tmp_path):
    src = make_database(tmp_path)
    dest = tmp_path / "recovery.sqlite3"
    result = backup_demo_database(src, dest, environment="test")
    assert result["status"] == "dry_run"
    assert result["transaction_count"] == 1
    assert result["review_count"] == 1
    assert not dest.exists()


def test_verified_snapshot_and_no_overwrite(tmp_path):
    src = make_database(tmp_path)
    dest = tmp_path / "recovery.sqlite3"
    result = backup_demo_database(src, dest, confirm=True, environment="development")
    assert result["status"] == "created_and_verified"
    assert inspect_demo_database(dest) == {"transaction_count": 1, "review_count": 1}
    with sqlite3.connect(src) as connection:
        connection.execute("INSERT INTO transactions VALUES ('fictional-later')")
    assert inspect_demo_database(src)["transaction_count"] == 2
    assert inspect_demo_database(dest)["transaction_count"] == 1
    with pytest.raises(FileExistsError):
        backup_demo_database(src, dest, confirm=True)
    assert inspect_demo_database(dest)["transaction_count"] == 1


def test_refuse_production_or_unknown_environment(tmp_path):
    src = make_database(tmp_path)
    dest = tmp_path / "new.sqlite3"
    for name in ("production", "unknown", "staging"):
        with pytest.raises(ValueError, match="production or unknown"):
            backup_demo_database(src, dest, environment=name, confirm=True)
    assert not dest.exists()


def test_refuse_missing_or_invalid_source(tmp_path):
    dest = tmp_path / "snapshot.sqlite3"
    with pytest.raises(ValueError, match="existing regular"):
        backup_demo_database(tmp_path / "missing.sqlite3", dest, confirm=True)
    junk = tmp_path / "other.sqlite3"
    with sqlite3.connect(junk) as db:
        db.execute("CREATE TABLE unrelated (id INTEGER)")
    with pytest.raises(ValueError, match="not a migrated"):
        backup_demo_database(junk, dest, confirm=True)
    assert not dest.exists()


def test_refuse_symlink_source_and_target(tmp_path):
    src = make_database(tmp_path)
    link = tmp_path / "alias.sqlite3"
    link.symlink_to(src)
    dest = tmp_path / "backup.sqlite3"
    with pytest.raises(ValueError, match="regular"):
        backup_demo_database(link, dest, confirm=True)
    dest.symlink_to(src)
    with pytest.raises(FileExistsError):
        backup_demo_database(src, dest, confirm=True)


def test_e2e_smoke_is_ephemeral_and_real_api_verified(tmp_path):
    import json
    import os
    import subprocess
    import sys

    project = Path(__file__).resolve().parents[1]
    report = tmp_path / "e2e.json"
    # subprocess prevents the smoke command from changing the test process
    # configuration, SQLAlchemy engine and model caches.
    completed = subprocess.run(
        [sys.executable, str(project / "scripts/smoke_e2e.py"), "--report", str(report)],
        cwd=project, env=os.environ.copy(), capture_output=True, text=True, timeout=40,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "passed"
    assert result["check_count"] == len(result["checks"]) == 14
    assert result["records_persisted_after_run"] == 0
    assert result["production_approved"] is False
