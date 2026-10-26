"""No real banking data: assertions use independently sampled synthetic test fixtures."""
import numpy as np
import pytest
from ml.data.generate import create_synthetic
from ml.data.partner_contract import validate_approved_feed
from ml.training.independent_validation import audit, bootstrap_intervals
from ml.config import MODEL


def fixture_data(n=220):
    df = create_synthetic(n=n, seed=84)
    df['transaction_id'] = [f'EXT-{i:06d}' for i in range(n)]
    # Guarantee both classes to make the test deterministic on a tiny fixture.
    df.loc[:11, 'is_fraud'] = 1
    return df


def test_feed_valid_and_sorted():
    df = fixture_data()
    df = df.iloc[::-1].copy()
    valid = validate_approved_feed(df, labeled=True)
    assert len(valid) == len(df)
    assert valid.event_time.is_monotonic_increasing


def test_feed_rejects_identifiers_and_unknown_columns():
    df = fixture_data()
    df['card_number'] = '4111111111111111'
    with pytest.raises(ValueError, match='Restricted'):
        validate_approved_feed(df, labeled=True)
    df = fixture_data()
    df['other'] = 'suspicious'
    with pytest.raises(ValueError, match='schema mismatch'):
        validate_approved_feed(df, labeled=True)


def test_feed_rejects_duplicates_time_and_invalid_categories():
    df = fixture_data()
    df.loc[1, 'transaction_id'] = df.loc[0, 'transaction_id']
    with pytest.raises(ValueError, match='Duplicate'):
        validate_approved_feed(df, labeled=True)
    df = fixture_data()
    df.loc[0, 'event_time'] = 'not a time'
    with pytest.raises(ValueError, match='event_time'):
        validate_approved_feed(df, labeled=True)
    df = fixture_data()
    df.loc[0, 'merchant_category'] = '<invalid>'
    with pytest.raises(ValueError, match='categories'):
        validate_approved_feed(df, labeled=True)


def test_holdout_does_not_tune_or_export_raw_rows(tmp_path):
    df = fixture_data()
    path = tmp_path / 'holdout.csv'
    df.to_csv(path, index=False)
    result = audit(path, model_path=MODEL, provenance='Approved synthetic test fixture with toy labels',
                   approved=True, draws=30)
    assert result['no_retraining_or_threshold_tuning'] is True
    assert 'transaction_id' not in str(result)
    assert 'card_number' not in str(result)
    assert result['population']['rows'] == len(df)
    assert 0 <= result['metrics']['pr_auc'] <= 1
    assert len(result['confidence_intervals']['pr_auc']) == 2
    with pytest.raises(ValueError, match='Explicit data approval'):
        audit(path, provenance='Approved synthetic test fixture', approved=False)


def test_holdout_rejects_original_demo_rows(tmp_path):
    path = tmp_path / 'demo.csv'
    create_synthetic(n=220).to_csv(path, index=False)
    with pytest.raises(ValueError, match='synthetic demo IDs'):
        audit(path, provenance='Synthetic demo row fixtures', approved=True)


def test_bootstrap_rejects_insufficient_support():
    assert bootstrap_intervals(np.array([0, 0, 1]), np.array([.01, .05, .7]), .5)['status'] == 'insufficient_positive_or_negative_cases'
