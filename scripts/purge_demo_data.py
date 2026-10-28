"""Deliberate, bounded retention maintenance for SYNTHETIC DEMO databases only.

No production support; no scheduled deletion or access to personal financial data.
Dry-run is the default and exports only counts (not transaction identifiers).
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.core import config
from backend.app.db.models import ReviewFeedback, TransactionRecord
from backend.app.db.session import engine


def purge_synthetic_demo_data(
    session: Session, *, days: int = 30, apply: bool = False,
    confirmed: bool = False, max_records: int = 1000,
    environment: str | None = None, now: datetime | None = None,
) -> dict:
    """Preview or delete *both* scored demo rows and associated review examples.

    Fail closed if a request attempts to delete more than the permitted cap;
    the entire operation is one database transaction. The caller must ensure
    the database itself contains only fictional records.
    """
    environment = config.ENVIRONMENT if environment is None else environment
    if environment not in {"development", "test"}:
        raise ValueError("Retention tool refuses production or unknown environments")
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 3650:
        raise ValueError("days must be between 1 and 3650")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or not 1 <= max_records <= 100000:
        raise ValueError("max_records must be between 1 and 100000")
    if apply and not confirmed:
        raise ValueError("--apply requires --confirm-synthetic-only")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    cutoff = now.astimezone(timezone.utc) - timedelta(days=days)

    try:
        ids = session.scalars(
            select(TransactionRecord.transaction_id)
            .where(TransactionRecord.created_at < cutoff)
            .order_by(TransactionRecord.created_at, TransactionRecord.transaction_id)
            .limit(max_records + 1)
        ).all()
        if len(ids) > max_records:
            raise ValueError("Eligible rows exceed max_records; no data was deleted")
        feedback = 0
        if ids:
            feedback = len(session.scalars(
                select(ReviewFeedback.transaction_id)
                .where(ReviewFeedback.transaction_id.in_(ids))
            ).all())
        result = {
            "status": "deleted" if apply else "dry_run",
            "scope": "fictional_local_development_data_only",
            "older_than_days": days,
            "eligible_transactions": len(ids),
            "linked_demo_reviews": feedback,
            "production_permitted": False,
        }
        if apply and ids:
            session.execute(delete(ReviewFeedback).where(ReviewFeedback.transaction_id.in_(ids)))
            session.execute(delete(TransactionRecord).where(TransactionRecord.transaction_id.in_(ids)))
            session.commit()
        else:
            # A read-only preview should not leave a transaction open.
            session.rollback()
        return result
    except Exception:
        session.rollback()
        raise


def main():
    parser = argparse.ArgumentParser(description="Preview/purge synthetic demo rows only; never for production")
    parser.add_argument("--days", type=int, default=30, help="Delete rows strictly older than this (default 30)")
    parser.add_argument("--max-records", type=int, default=1000, help="Refuse bulk deletes beyond this bound")
    parser.add_argument("--apply", action="store_true", help="Actually delete eligible rows (default previews only)")
    parser.add_argument("--confirm-synthetic-only", action="store_true", help="Attest that this DB contains only fictional records")
    args = parser.parse_args()
    with Session(engine) as session:
        result = purge_synthetic_demo_data(session, days=args.days, max_records=args.max_records,
                                           apply=args.apply, confirmed=args.confirm_synthetic_only)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
