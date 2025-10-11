from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import get_rag_response
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog

router = APIRouter()


class RAGRequest(BaseModel):
    question: str


@router.post("/rag-chat")
async def rag_chat(request: RAGRequest):
    response = get_rag_response(request.question)
    db = SessionLocal()
    log = ConversationLog(user_id="guest", question=request.question, answer=response)
    db.add(log)
    db.commit()
    db.close()
    return {"question": request.question, "answer": response}
