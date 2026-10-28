"""Never confuse illustrative scenarios with real fraud-loss optimization."""
import pytest
from scripts.decision_costs import cost_scenarios, make_svg


def test_review_cost_math_uses_fixed_confusion_matrix():
    rows = cost_scenarios([[660, 119], [18, 3]], missed_costs=(2, 10))
    assert rows == [
        {"missed_case_penalty_units": 2, "review_units": 122,
         "missed_case_units": 36, "total_hypothetical_units": 158},
        {"missed_case_penalty_units": 10, "review_units": 122,
         "missed_case_units": 180, "total_hypothetical_units": 302},
    ]
    svg = make_svg(rows, positive_count=21)
    assert "synthetic holdout" in svg and "No real banking data" in svg
    assert "<svg" in svg and "</svg>" in svg


def test_invalid_cost_input_and_matrix_rejected():
    with pytest.raises(ValueError):
        cost_scenarios([[1, 2, 3], [1, 2]])
    with pytest.raises(ValueError):
        cost_scenarios([[1, -1], [3, 4]])
    with pytest.raises(ValueError):
        cost_scenarios([[1, 2], [3, 4]], missed_costs=(0,))
