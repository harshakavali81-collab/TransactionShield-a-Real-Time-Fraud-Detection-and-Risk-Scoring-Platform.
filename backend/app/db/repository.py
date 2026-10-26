from sqlalchemy import select,func
from backend.app.db.models import TransactionRecord

def recent(db,limit=50):
    return db.scalars(select(TransactionRecord).order_by(TransactionRecord.created_at.desc()).limit(limit)).all()

def stats(db):
    n=db.scalar(select(func.count(TransactionRecord.transaction_id))) or 0
    flagged=db.scalar(select(func.count(TransactionRecord.transaction_id)).where(TransactionRecord.is_flagged.is_(True))) or 0
    high=db.scalar(select(func.count(TransactionRecord.transaction_id)).where(TransactionRecord.risk_level=="HIGH")) or 0
    avg=db.scalar(select(func.avg(TransactionRecord.risk_score))) or 0
    return {"total_transactions":n,"flagged_transactions":flagged,"high_risk_transactions":high,
        "flag_rate":round(flagged/n,4) if n else 0,"average_risk_score":round(float(avg),2)}
