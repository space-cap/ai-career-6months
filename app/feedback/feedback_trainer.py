# app/feedback/feedback_trainer.py
from app.feedback.feedback_analyzer import analyze_feedback
from app.db import get_session
from app.models import FeedbackLog


def retrain_from_feedback():
    """
    저장된 피드백 데이터를 기반으로 AI 응답 품질 개선
    """
    session = get_session()
    feedbacks = session.query(FeedbackLog).all()
    
    total, pos, neg = 0, 0, 0
    for fb in feedbacks:
        result = analyze_feedback(fb.comment)
        if result["sentiment"] == "positive":
            pos += 1
        elif result["sentiment"] == "negative":
            neg += 1
        total += 1

    print(f"[Retrain Loop] Total: {total}, Positive: {pos}, Negative: {neg}")
    # TODO: 모델 업데이트 로직 추가 (예: 프롬프트 튜닝 or 데이터 보강)
    session.close()
