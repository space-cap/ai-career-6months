from fastapi import APIRouter
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog
from app.services.personalizer import generate_personal_answer

router = APIRouter()


class PersonalChatRequest(BaseModel):
    question: str
    user_id: str = "guest"


@router.post("/personal-chat")
async def personal_chat(request: PersonalChatRequest):
    question = request.question
    user_id = request.user_id

    db = SessionLocal()
    recent_logs = (
        db.query(ConversationLog)
        .filter(ConversationLog.user_id == user_id)
        .order_by(ConversationLog.created_at.desc())
        .limit(10)
        .all()
    )
    db.close()

    response = generate_personal_answer(question, recent_logs)
    return {"question": question, "answer": response}
