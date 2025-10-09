from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vectorstore import get_vectorstore
from app.services.llm_service import get_ai_response

router = APIRouter()


@router.get("/ping")
async def ping():
    """서버 상태 확인용"""
    return {"status": "ok"}


@router.get("/vector-count")
async def vector_count():
    """Chroma DB 상태 조회"""
    store = get_vectorstore()
    count = len(store.get()["ids"])
    return {"vector_count": count}


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest):
    answer = get_ai_response(request.question)
    return {"user_input": request.question, "ai_answer": answer}