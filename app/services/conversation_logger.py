"""
대화 로그 저장 서비스
"""
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog


def save_conversation(question: str, answer: str, sentiment: str, topic: str, user_id: str = "guest"):
    """
    대화 내용을 데이터베이스에 저장합니다.

    Args:
        question: 사용자 질문
        answer: AI 응답
        user_id: 사용자 ID (기본값: "guest")
    """
    db = SessionLocal()
    try:
        log = ConversationLog(
            user_id=user_id,
            question=question,
            answer=answer,
            sentiment=sentiment,
            topic=topic
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
