from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
import datetime

router = APIRouter()


class FeedbackRequest(BaseModel):
    """사용자 피드백 요청 모델"""
    conversation_id: str = Field(..., description="대화 ID")
    feedback: Literal['like', 'dislike'] = Field(..., description="피드백 유형")
    reason: str | None = Field(None, description="피드백 이유 (예: 'too slow', 'irrelevant')")


@router.post("/feedback")
def submit_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    """
    사용자 피드백 저장 API
    - body: { conversation_id, feedback: 'like'|'dislike', reason: 'too slow'|'irrelevant' }
    """
    try:
        db.execute(text("""
            INSERT INTO feedback_log (conversation_id, feedback, reason, created_at)
            VALUES (:cid, :feedback, :reason, :created)
        """), {
            "cid": data.conversation_id,
            "feedback": data.feedback,
            "reason": data.reason,
            "created": datetime.datetime.now(datetime.UTC)
        })
        db.commit()
        return {"status": "ok", "message": "Feedback recorded."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
