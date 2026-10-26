from backend.app.core.config import normalize_database_url


def test_render_database_uri_normalization():
    assert normalize_database_url('postgres://u:p@db:5432/shield') == 'postgresql+psycopg://u:p@db:5432/shield'
    assert normalize_database_url('postgresql://u:p@db:5432/shield') == 'postgresql+psycopg://u:p@db:5432/shield'
    assert normalize_database_url('sqlite:///memory.db') == 'sqlite:///memory.db'
    assert normalize_database_url('postgresql+psycopg://u:p@host/db') == 'postgresql+psycopg://u:p@host/db'
