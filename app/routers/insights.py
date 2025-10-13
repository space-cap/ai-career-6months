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


@router.get("/insights/topics")
def get_topics():
    db = SessionLocal()
    results = (
        db.query(ConversationLog.topic, func.count().label("count"))
        .group_by(ConversationLog.topic)
        .order_by(func.count().desc())
        .limit(10)
        .all()
    )
    db.close()
    return [{"topic": r.topic, "count": r.count} for r in results]
