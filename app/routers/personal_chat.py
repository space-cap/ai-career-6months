from fastapi import APIRouter
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog
from app.services.personalizer import generate_personal_answer

router = APIRouter()


@router.post("/personal-chat")
async def personal_chat(req: dict):
    question = req.get("question")
    db = SessionLocal()
    recent_logs = (
        db.query(ConversationLog)
        .filter(ConversationLog.user_id == "guest")
        .order_by(ConversationLog.created_at.desc())
        .limit(10)
        .all()
    )
    db.close()

    response = generate_personal_answer(question, recent_logs)
    return {"answer": response}
