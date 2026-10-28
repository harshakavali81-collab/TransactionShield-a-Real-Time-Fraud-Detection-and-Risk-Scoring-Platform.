"""Do not ever point integration smoke at an operational or non-ephemeral DB."""
import pytest
from scripts.smoke_postgres import validate_target


VALID = {
    "ENVIRONMENT": "test", "API_KEY": "synthetic-test-only-secret",
    "DATABASE_URL": "postgresql+psycopg://ci_user:dummy@localhost:5432/transactionshield_ci",
}


def test_only_ephemeral_test_postgresql_is_allowed():
    parsed = validate_target(VALID)
    assert parsed.database == "transactionshield_ci"


@pytest.mark.parametrize("change", [
    {"ENVIRONMENT": "production"},
    {"ENVIRONMENT": "staging"},
    {"DATABASE_URL": "postgresql+psycopg://ci_user:dummy@localhost/transactionshield"},
    {"DATABASE_URL": "sqlite:////tmp/transactionshield_ci"},
    {"DATABASE_URL": "postgresql+psycopg://ci_user:dummy@localhost/postgres"},
    {"DATABASE_URL": "bogus"},
    {"API_KEY": ""},
])
def test_invalid_targets_rejected(change):
    with pytest.raises(RuntimeError):
        validate_target({**VALID, **change})
