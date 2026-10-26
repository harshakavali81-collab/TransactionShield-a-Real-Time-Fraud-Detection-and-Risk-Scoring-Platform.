import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ROOT=Path(__file__).resolve().parents[3]
DATABASE_URL=os.getenv("DATABASE_URL",f"sqlite:///{ROOT / 'transactionshield.sqlite3'}")
MODEL_PATH=Path(os.getenv("MODEL_PATH",str(ROOT/"artifacts/models/fraud_model.joblib")))
METRICS_PATH=Path(os.getenv("METRICS_PATH",str(ROOT/"artifacts/models/metrics.json")))
CORS_ORIGINS=[s.strip() for s in os.getenv("CORS_ORIGINS","http://localhost:5173,http://localhost:3000").split(",") if s.strip()]
API_KEY=os.getenv("API_KEY")
