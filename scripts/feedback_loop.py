"""
feedback_loop.py
----------------------------------------
AI 피드백 루프 자동화 스크립트 (Feedback → Retrain → Report)
----------------------------------------
1. feedback_log 에서 좋아요/싫어요 통계 조회
2. 부정 피드백 비율 계산 → 임계값 초과 시 vector_retrain 실행
3. Slack 으로 "AI 성능 개선 리포트" 자동 전송
----------------------------------------
실행 예시:
    python scripts/feedback_loop.py
    python scripts/feedback_loop.py --threshold 0.4

스케줄링:
- 매일 또는 매주 cron job / Render Background Worker 사용
----------------------------------------
"""

import sys
from datetime import datetime
from sqlalchemy import text
from app.database import SessionLocal
from app.core.config import settings
from app.utils.slack_notifier import send_slack_message
from app.utils.vector_retrain import retrain_if_needed

# 대시보드 URL (환경변수 또는 기본값)
DASHBOARD_URL = "https://ai-dashboard.onrender.com"


# -----------------------------------
# Step 1️⃣: 피드백 통계 조회
# -----------------------------------
def get_feedback_stats(db):
    """feedback_log 에서 좋아요/싫어요 통계 조회"""
    try:
        result = db.execute(text("""
            SELECT
              SUM(CASE WHEN feedback='like' THEN 1 ELSE 0 END) AS likes,
              SUM(CASE WHEN feedback='dislike' THEN 1 ELSE 0 END) AS dislikes,
              COUNT(*) AS total
            FROM feedback_log
        """)).fetchone()

        likes = result[0] or 0
        dislikes = result[1] or 0
        total = result[2] or 0
        ratio = (dislikes / total) if total else 0.0

        print(f"🗳️ Feedback 통계 - 👍 {likes} / 👎 {dislikes} / 총 {total} (부정비율 {ratio:.2%})")
        return {"likes": likes, "dislikes": dislikes, "total": total, "ratio": ratio}

    except Exception as e:
        print(f"❌ 피드백 통계 조회 중 오류: {e}")
        return {"likes": 0, "dislikes": 0, "total": 0, "ratio": 0.0}


# -----------------------------------
# Step 2️⃣: 부정 피드백 감지 및 재임베딩 트리거
# -----------------------------------
def trigger_retrain_if_needed(db, ratio, threshold=0.3):
    """
    부정 피드백 비율이 threshold 초과 시 재임베딩 필요 여부 반환

    Note: 실제 재임베딩은 scripts/retrain_vectorstore.py에서 수행
    """
    needs_retrain = retrain_if_needed(db, threshold)

    if needs_retrain:
        msg = (
            f"🚨 *부정 피드백 임계값 초과*\n"
            f"• 현재 부정 비율: {ratio:.2%}\n"
            f"• 임계값: {threshold:.0%}\n"
            f"• 조치: 벡터 재임베딩 필요\n\n"
            f"💡 재학습을 실행하려면:\n"
            f"`python scripts/retrain_vectorstore.py --force`"
        )
        print(msg)
        send_slack_message(msg)
        return True
    else:
        print(f"✅ 피드백 비율 정상 ({ratio:.2%}), 재학습 불필요.")
        return False


# -----------------------------------
# Step 3️⃣: Slack 리포트 전송
# -----------------------------------
def send_feedback_report(stats, retrain_needed):
    """Slack 으로 피드백 리포트 전송"""
    likes = stats["likes"]
    dislikes = stats["dislikes"]
    total = stats["total"]
    ratio = stats["ratio"]

    if retrain_needed:
        status = "⚠️ 재학습 필요"
        emoji = "🚨"
    else:
        status = "✅ 정상 유지"
        emoji = "✅"

    message = (
        f"{emoji} *AI Feedback Loop Report*\n\n"
        f"📊 *피드백 통계*\n"
        f"• 👍 좋아요: {likes}\n"
        f"• 👎 싫어요: {dislikes}\n"
        f"• 📝 총 피드백: {total}\n"
        f"• 📉 부정 비율: {ratio:.1%}\n\n"
        f"🎯 *상태*: {status}\n"
        f"🕐 *생성 시각*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📊 <{DASHBOARD_URL}|실시간 Dashboard 보기>"
    )

    send_slack_message(message)
    print("✅ Slack 리포트 전송 완료")


# -----------------------------------
# Step 4️⃣: 전체 루프 실행
# -----------------------------------
def run_feedback_loop(threshold=0.3):
    """
    AI Feedback Loop 메인 실행 함수

    Args:
        threshold: 부정 피드백 임계값 (기본 0.3 = 30%)
    """
    print("\n" + "=" * 60)
    print("🚀 AI Feedback Loop 시작...")
    print("=" * 60 + "\n")

    db = SessionLocal()

    try:
        # 1. 피드백 통계 조회
        stats = get_feedback_stats(db)

        # 2. 재학습 필요 여부 체크
        retrain_needed = trigger_retrain_if_needed(db, stats["ratio"], threshold=threshold)

        # 3. Slack 리포트 전송
        send_feedback_report(stats, retrain_needed)

        print("\n" + "=" * 60)
        print("🎯 AI Feedback Loop 완료 ✅")
        print("=" * 60 + "\n")

    except Exception as e:
        error_msg = f"❌ Feedback Loop 실행 중 오류: {e}"
        print(error_msg)
        send_slack_message(error_msg)

    finally:
        db.close()


if __name__ == "__main__":
    # 커맨드 라인 인자 파싱
    args = sys.argv[1:]
    threshold = 0.3

    if "--threshold" in args:
        try:
            idx = args.index("--threshold")
            threshold = float(args[idx + 1])
            print(f"📌 부정 피드백 임계값: {threshold:.0%}\n")
        except (IndexError, ValueError):
            print("⚠️ --threshold 옵션 사용법: --threshold 0.3")
            sys.exit(1)

    run_feedback_loop(threshold=threshold)
