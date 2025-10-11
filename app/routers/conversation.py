from fastapi import APIRouter, Query
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog

router = APIRouter()


@router.get("/conversation/logs")
def get_logs(limit: int = 10, user_id: str | None = None):
    db = SessionLocal()
    query = db.query(ConversationLog)
    if user_id:
        query = query.filter(ConversationLog.user_id == user_id)
    logs = query.order_by(ConversationLog.created_at.desc()).limit(limit).all()
    db.close()
    return logs
