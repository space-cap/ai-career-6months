from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import get_rag_response

router = APIRouter()


class RAGRequest(BaseModel):
    question: str


@router.post("/rag-chat")
async def rag_chat(request: RAGRequest):
    answer = get_rag_response(request.question)
    return {"question": request.question, "answer": answer}
