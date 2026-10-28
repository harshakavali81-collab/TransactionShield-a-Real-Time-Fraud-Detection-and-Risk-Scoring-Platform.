"""Dry-run, joint deletion and strict production refusal for the demo retention tool."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.models import ReviewFeedback, TransactionRecord
from backend.app.db.session import Base
from scripts.purge_demo_data import purge_synthetic_demo_data

NOW = datetime(2026, 10, 28, tzinfo=timezone.utc)


def insert(session, token, when, with_review):
    session.add(TransactionRecord(
        transaction_id=token, created_at=when, amount=25,
        fraud_probability=0.2, risk_score=20, risk_level="LOW", is_flagged=False,
        model_version="fictional", reasons=[], numeric_features={},
    ))
    if with_review:
        session.add(ReviewFeedback(transaction_id=token, submitted_at=when,
                                   review_label=False, reviewer_note="fictional"))
    session.commit()


@pytest.fixture
def database():
    eng = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        insert(s, "old-demo", NOW - timedelta(days=40), True)
        insert(s, "new-demo", NOW - timedelta(days=2), True)
        yield s
    eng.dispose()


def count(session, klass):
    return session.scalar(select(func.count()).select_from(klass))


def test_dry_run_leaves_transactions_and_feedback_untouched(database):
    result = purge_synthetic_demo_data(database, days=30, now=NOW, environment="test")
    assert result["status"] == "dry_run"
    assert result["eligible_transactions"] == 1
    assert result["linked_demo_reviews"] == 1
    assert "old-demo" not in repr(result)
    assert count(database, TransactionRecord) == 2
    assert count(database, ReviewFeedback) == 2


def test_confirmed_retention_deletes_only_expired_rows_and_reviews(database):
    result = purge_synthetic_demo_data(database, days=30, now=NOW, environment="test",
                                       apply=True, confirmed=True)
    assert result["status"] == "deleted"
    assert count(database, TransactionRecord) == 1
    assert count(database, ReviewFeedback) == 1
    assert database.get(TransactionRecord, "new-demo") is not None
    assert database.get(ReviewFeedback, "new-demo") is not None


def test_refuses_production_and_requires_explicit_confirmation(database):
    for environment in ("production", "unexpected"):
        with pytest.raises(ValueError, match="refuses"):
            purge_synthetic_demo_data(database, environment=environment, apply=True,
                                       confirmed=True, now=NOW)
    with pytest.raises(ValueError, match="confirm"):
        purge_synthetic_demo_data(database, environment="test", apply=True, now=NOW)
    assert count(database, TransactionRecord) == 2


def test_bounded_refusal_does_not_delete_any_records(database):
    insert(database, "another-old", NOW - timedelta(days=60), False)
    with pytest.raises(ValueError, match="exceed max_records"):
        purge_synthetic_demo_data(database, environment="test", days=30,
                                  apply=True, confirmed=True, max_records=1, now=NOW)
    assert count(database, TransactionRecord) == 3
    assert count(database, ReviewFeedback) == 2


@pytest.mark.parametrize("days,max_records", [(0, 1000), (3651, 1000), (30, 0), (30, 100001)])
def test_rejects_unsafe_parameters(database, days, max_records):
    with pytest.raises(ValueError):
        purge_synthetic_demo_data(database, environment="test", days=days,
                                  max_records=max_records, now=NOW)


def test_requires_timezone_aware_clock(database):
    with pytest.raises(ValueError, match="timezone-aware"):
        purge_synthetic_demo_data(database, environment="test", now=datetime(2026, 10, 28))
