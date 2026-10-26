from datetime import datetime,timezone
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,DateTime,Float,Integer,Boolean,JSON
from backend.app.db.session import Base

def utcnow():return datetime.now(timezone.utc)
class TransactionRecord(Base):
    __tablename__="transactions"
    transaction_id:Mapped[str]=mapped_column(String(80),primary_key=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,index=True)
    amount:Mapped[float]=mapped_column(Float)
    fraud_probability:Mapped[float]=mapped_column(Float)
    risk_score:Mapped[int]=mapped_column(Integer)
    risk_level:Mapped[str]=mapped_column(String(10))
    is_flagged:Mapped[bool]=mapped_column(Boolean)
    model_version:Mapped[str]=mapped_column(String(100))
    reasons:Mapped[list]=mapped_column(JSON)
