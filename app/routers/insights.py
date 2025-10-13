from fastapi import APIRouter
from sqlalchemy import func, case
from app.database import SessionLocal
from app.models.conversation_log import ConversationLog

router = APIRouter()


@router.get("/insights/stats")
def get_stats():
    db = SessionLocal()
    result = (
        db.query(
            func.date(ConversationLog.created_at).label("date"),
            func.count().label("count")
        )
        .group_by(func.date(ConversationLog.created_at))
        .all()
    )
    db.close()
    return [{"date": str(r.date), "count": r.count} for r in result]


@router.get("/insights/topics")
def get_topics():
    db = SessionLocal()
    results = (
        db.query(ConversationLog.topic, func.count().label("count"))
        .filter(ConversationLog.topic.isnot(None))  # NULL 제외
        .group_by(ConversationLog.topic)
        .order_by(func.count().desc())
        .limit(10)
        .all()
    )
    db.close()
    return [{"topic": r.topic, "count": r.count} for r in results]


@router.get("/insights/sentiment-trend")
def get_sentiment_trend():
    """
    날짜별 감정 분포를 반환합니다.
    예: [{date: '2025-10-10', positive: 3, neutral: 2, negative: 1}, ...]
    """
    db = SessionLocal()

    sentiment_case = {
        "positive": func.sum(case((ConversationLog.sentiment == "긍정", 1), else_=0)),
        "neutral": func.sum(case((ConversationLog.sentiment == "중립", 1), else_=0)),
        "negative": func.sum(case((ConversationLog.sentiment == "부정", 1), else_=0)),
    }

    results = (
        db.query(
            func.date(ConversationLog.created_at).label("date"),
            sentiment_case["positive"].label("positive"),
            sentiment_case["neutral"].label("neutral"),
            sentiment_case["negative"].label("negative"),
        )
        .group_by(func.date(ConversationLog.created_at))
        .order_by(func.date(ConversationLog.created_at))
        .all()
    )
    db.close()

    return [
        {
            "date": str(r.date),
            "positive": r.positive,
            "neutral": r.neutral,
            "negative": r.negative,
        }
        for r in results
    ]