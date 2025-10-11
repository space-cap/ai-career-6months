from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class ConversationLog(Base):
    __tablename__ = "conversation_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
