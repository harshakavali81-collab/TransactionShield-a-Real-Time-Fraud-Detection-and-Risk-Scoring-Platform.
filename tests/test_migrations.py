"""Migration regression test on a clean throwaway sqlite database."""
import os
import subprocess
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[1]


def test_upgrade_to_latest_schema(tmp_path):
    url = f'sqlite:///{tmp_path / "migrated.sqlite3"}'
    env = {**os.environ, 'DATABASE_URL': url}
    result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    engine = create_engine(url)
    inspector = inspect(engine)
    assert 'transactions' in inspector.get_table_names()
    assert 'demo_review_feedback' in inspector.get_table_names()
    assert 'numeric_features' in {c['name'] for c in inspector.get_columns('transactions')}
    engine.dispose()
