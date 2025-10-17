from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class FeedbackLog(Base):
    __tablename__ = "feedback_log"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation_log.id"))
    feedback = Column(String(10))  # 'like' or 'dislike'
    reason = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
