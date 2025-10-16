from sqlalchemy.orm import Session
from sqlalchemy import text


def retrain_if_needed(db: Session, threshold: float = 0.3) -> bool:
    """
    피드백 데이터 기반 자동 재학습 트리거
    - 부정(feedback='dislike') 비율이 threshold 초과 시 True 반환

    Args:
        db: Database session (get_db()로부터 주입)
        threshold: 부정 피드백 임계값 (기본 0.3 = 30%)

    Returns:
        bool: 재학습이 필요하면 True, 아니면 False

    Example:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            if retrain_if_needed(db, threshold=0.3):
                # 실제 재임베딩 로직 실행
                perform_retraining()
        finally:
            db.close()
    """
    try:
        result = db.execute(text("""
            SELECT
                SUM(CASE WHEN feedback='dislike' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS dislike_ratio
            FROM feedback_log
        """)).fetchone()

        dislike_ratio = result[0] if result and result[0] else 0.0
        print(f"🧠 부정 피드백 비율: {dislike_ratio:.2%}")

        if dislike_ratio > threshold:
            print(f"🚀 부정 피드백이 {threshold:.0%} 초과 — 벡터 재임베딩 필요!")
            return True
        else:
            print(f"✅ 피드백 비율 정상 ({dislike_ratio:.2%}), 재학습 불필요.")
            return False

    except Exception as e:
        print(f"❌ 재학습 체크 중 오류: {e}")
        return False
