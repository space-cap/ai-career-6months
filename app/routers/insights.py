from fastapi import APIRouter
from sqlalchemy import func
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog

router = APIRouter()


@router.get("/insights/stats")
def get_stats():
    db = SessionLocal()
    result = (
        db.query(
            func.date(ConversationLog.created_at).label("date"),
            func.count().label("count")
        )
        .group_by(func.date(ConversationLog.created_at))
        .all()
    )
    db.close()
    return [{"date": str(r.date), "count": r.count} for r in result]
