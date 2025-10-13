from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import get_rag_response
from app.services.conversation_logger import save_conversation
from app.services.analyzer import analyze_sentiment, extract_topic

router = APIRouter()


class RAGRequest(BaseModel):
    question: str


@router.post("/rag-chat")
async def rag_chat(request: RAGRequest):
    response = get_rag_response(request.question)

    # ✅ 감정 / 주제 분석 추가
    sentiment = analyze_sentiment(response)
    topic = extract_topic(response)

    save_conversation(question=request.question, 
                      answer=response,
                      sentiment=sentiment,
                      topic=topic)
    return {"question": request.question, "answer": response}
