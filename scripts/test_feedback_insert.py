"""
test_feedback_insert.py
----------------------------------------
feedback_log 테이블이 정상적으로 생성되었는지 테스트용으로
샘플 데이터를 삽입해보는 간단한 스크립트입니다.

실행:
    python scripts/test_feedback_insert.py
----------------------------------------
"""

import sys
import datetime
from app.database import SessionLocal
from app.models.feedback_log import FeedbackLog


def insert_sample_feedback():
    """샘플 피드백 데이터 삽입 (ORM 방식)"""
    print("🧪 Inserting sample feedback records...\n")

    db = SessionLocal()

    try:
        # 샘플 피드백 데이터 생성
        samples = [
            FeedbackLog(
                conversation_id=1,
                feedback="like",
                reason="정확한 답변"
            ),
            FeedbackLog(
                conversation_id=2,
                feedback="dislike",
                reason="너무 느림"
            ),
            FeedbackLog(
                conversation_id=3,
                feedback="like",
                reason="친절한 응대"
            ),
        ]

        # DB에 추가
        for idx, feedback in enumerate(samples, 1):
            db.add(feedback)
            print(f"[{idx}/{len(samples)}] 피드백 추가: conversation_id={feedback.conversation_id}, feedback={feedback.feedback}")

        db.commit()
        print("\n✅ Sample feedback inserted successfully!")

        # 삽입된 데이터 확인
        print("\n📋 삽입된 피드백 데이터:")
        all_feedback = db.query(FeedbackLog).all()
        for f in all_feedback:
            print(f"  • ID: {f.id}, Conversation: {f.conversation_id}, Feedback: {f.feedback}, Reason: {f.reason}, Created: {f.created_at}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 피드백 삽입 중 오류 발생: {e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    insert_sample_feedback()
