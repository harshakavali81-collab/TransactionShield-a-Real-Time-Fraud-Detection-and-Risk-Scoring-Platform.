"""Use a separate, disposable database when testing API routes."""
import os
import tempfile
os.environ["DATABASE_URL"]=f"sqlite:///{tempfile.gettempdir()}/transactionshield-pytest-{os.getpid()}.sqlite3"
