import pytest
from ml.data.generate import create_synthetic
from ml.training.rolling_validation import rolling_origin_report


def test_rolling_folds_use_strictly_chronological_windows():
    report = rolling_origin_report(create_synthetic(n=2500, seed=42),
                                   min_train=1000, validation_size=350,
                                   test_size=350, step=350, max_folds=3)
    assert report["fold_count"] >= 2
    for fold in report["folds"]:
        assert fold["train_through"] < fold["validation_from"]
        assert fold["validation_through"] < fold["test_from"]
        assert fold["train_rows"] + fold["validation_rows"] + fold["test_rows"] <= 2500
        assert fold["threshold"] >= .03
        assert fold["positive_cases"] > 0
        assert fold["pr_auc"] >= 0


def test_rolling_folds_reject_invalid_windows_and_duplicates():
    data = create_synthetic(n=350, seed=17)
    with pytest.raises(ValueError, match="Invalid rolling"):
        rolling_origin_report(data, min_train=1)
    with pytest.raises(ValueError, match="No valid folds"):
        rolling_origin_report(data, min_train=200, validation_size=100, test_size=100)
    duplicate = data.copy()
    duplicate.loc[1, "event_time"] = duplicate.loc[0, "event_time"]
    with pytest.raises(ValueError, match="unique"):
        rolling_origin_report(duplicate, min_train=200, validation_size=100, test_size=100)


def test_diagnostic_is_independent_of_serving_model():
    report = rolling_origin_report(create_synthetic(n=2300, seed=99),
                                   min_train=900, validation_size=300,
                                   test_size=300, step=300, max_folds=3)
    assert report["fold_count"] >= 2
    assert report["model"].startswith("logistic_regression")
    assert [f["fold"] for f in report["folds"]] == sorted(f["fold"] for f in report["folds"])
