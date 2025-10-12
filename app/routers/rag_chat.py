from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import get_rag_response
from app.services.conversation_logger import save_conversation

router = APIRouter()


class RAGRequest(BaseModel):
    question: str


@router.post("/rag-chat")
async def rag_chat(request: RAGRequest):
    response = get_rag_response(request.question)
    save_conversation(question=request.question, answer=response)
    return {"question": request.question, "answer": response}
