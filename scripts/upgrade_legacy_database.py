"""Opt-in, guarded schema upgrade from the original unversioned demo schema.

Only run against a backed-up original TransactionShield demonstration database.
"""
import argparse
import sys
import subprocess
from pathlib import Path
from sqlalchemy import inspect

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.db.session import engine

OLD_COLUMNS = {
    'transaction_id', 'created_at', 'amount', 'fraud_probability',
    'risk_score', 'risk_level', 'is_flagged', 'model_version', 'reasons',
}


def verify_original_schema():
    inspector = inspect(engine)
    if inspector.has_table('alembic_version'):
        raise RuntimeError('Database is already Alembic-managed; use alembic upgrade head')
    if not inspector.has_table('transactions'):
        raise RuntimeError('No legacy transactions table found; use alembic upgrade head')
    existing = {c['name'] for c in inspector.get_columns('transactions')}
    if existing != OLD_COLUMNS:
        raise RuntimeError(f'Unexpected legacy schema: {sorted(existing)}')
    if inspector.has_table('demo_review_feedback'):
        raise RuntimeError('Review feedback table already exists; inspect migration manually')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup-confirmed', action='store_true', required=True,
                        help='A restorable database backup has been verified')
    parser.parse_args()
    verify_original_schema()
    subprocess.run([sys.executable, '-m', 'alembic', 'stamp', '0001'], check=True)
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], check=True)
    print('Migration complete. Verify all rows and keep backup until acceptance tests pass.')


if __name__ == '__main__':
    main()
