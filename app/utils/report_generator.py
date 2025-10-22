"""
report_generator.py
----------------------------------------
AI 운영 주간 리포트를 자동 생성하여 PDF로 저장.
matplotlib을 사용한 차트 생성 및 한글 폰트 지원.
----------------------------------------
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sqlalchemy import text

from app.core.config import settings
from app.database import engine

# matplotlib 백엔드 설정 (GUI 없는 환경)
matplotlib.use("Agg")

# 한글 폰트 설정 (Windows/Linux 호환)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# 로깅 설정
logger = logging.getLogger(__name__)

# 리포트 디렉토리 설정
REPORT_DIR = Path("reports")


def get_feedback_stats(conn, start_date: str, end_date: str) -> dict:
    """
    피드백 통계 조회

    Args:
        conn: DB 연결 객체
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        dict: 피드백 통계 딕셔너리
    """
    try:
        result = conn.execute(
            text("""
            SELECT
              SUM(CASE WHEN feedback='like' THEN 1 ELSE 0 END) AS likes,
              SUM(CASE WHEN feedback='dislike' THEN 1 ELSE 0 END) AS dislikes,
              COUNT(*) AS total
            FROM feedback_log
            WHERE created_at BETWEEN :start AND :end
        """),
            {"start": start_date, "end": end_date},
        ).fetchone()

        if result:
            return {
                "likes": int(result.likes or 0),
                "dislikes": int(result.dislikes or 0),
                "total": int(result.total or 0),
            }
        return {"likes": 0, "dislikes": 0, "total": 0}
    except Exception as e:
        logger.error(f"피드백 통계 조회 실패: {e}")
        return {"likes": 0, "dislikes": 0, "total": 0}


def get_conversation_count(conn, start_date: str, end_date: str) -> int:
    """
    대화 수 조회

    Args:
        conn: DB 연결 객체
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        int: 대화 개수
    """
    try:
        result = conn.execute(
            text("""
            SELECT COUNT(*) FROM conversation_log
            WHERE created_at BETWEEN :start AND :end
        """),
            {"start": start_date, "end": end_date},
        ).scalar()
        return int(result or 0)
    except Exception as e:
        logger.error(f"대화 수 조회 실패: {e}")
        return 0


def get_sentiment_stats(conn, start_date: str, end_date: str) -> dict:
    """
    감정 분석 통계 조회

    Args:
        conn: DB 연결 객체
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        dict: 감정 통계 딕셔너리
    """
    try:
        result = conn.execute(
            text("""
            SELECT
              COUNT(*) as total,
              SUM(CASE WHEN sentiment IS NOT NULL THEN 1 ELSE 0 END) as analyzed
            FROM conversation_log
            WHERE created_at BETWEEN :start AND :end
        """),
            {"start": start_date, "end": end_date},
        ).fetchone()

        if result:
            return {
                "total": int(result.total or 0),
                "analyzed": int(result.analyzed or 0),
            }
        return {"total": 0, "analyzed": 0}
    except Exception as e:
        logger.error(f"감정 통계 조회 실패: {e}")
        return {"total": 0, "analyzed": 0}


def create_feedback_chart(feedback_stats: dict) -> BytesIO:
    """
    피드백 통계 차트 생성

    Args:
        feedback_stats: 피드백 통계 딕셔너리

    Returns:
        BytesIO: 차트 이미지 버퍼
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["Likes", "Dislikes"]
    values = [feedback_stats["likes"], feedback_stats["dislikes"]]
    colors = ["#4CAF50", "#F44336"]

    ax.bar(labels, values, color=colors, alpha=0.7, edgecolor="black")
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Feedback Statistics", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # y축을 정수로 표시
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_weekly_report(days: int = 7) -> dict:
    """
    주간 리포트 생성

    Args:
        days: 리포트 기간 (일)

    Returns:
        dict: 리포트 생성 결과
    """
    try:
        # 리포트 디렉토리 생성
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        # 날짜 계산
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=days)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")

        report_filename = f"weekly_report_{end_date}.pdf"
        report_path = REPORT_DIR / report_filename

        logger.info(f"리포트 생성 시작: {start_date} ~ {end_date}")

        # 데이터 수집
        with engine.begin() as conn:
            feedback_stats = get_feedback_stats(conn, start_date, end_date)
            conv_count = get_conversation_count(conn, start_date, end_date)
            sentiment_stats = get_sentiment_stats(conn, start_date, end_date)

        # PDF 생성
        with PdfPages(str(report_path)) as pdf:
            # 페이지 1: 요약 정보
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 크기
            ax.axis("off")

            # 타이틀
            title_text = "AI Weekly Operation Report"
            ax.text(
                0.5,
                0.95,
                title_text,
                ha="center",
                va="top",
                fontsize=20,
                fontweight="bold",
            )

            # 기간
            period_text = f"Period: {start_date} ~ {end_date}"
            ax.text(0.5, 0.90, period_text, ha="center", va="top", fontsize=12)

            # 통계 정보
            y_pos = 0.80
            line_height = 0.05

            stats_data = [
                ("Total Conversations", conv_count),
                ("Sentiment Analyzed", f"{sentiment_stats['analyzed']}/{sentiment_stats['total']}"),
                ("Total Feedback", feedback_stats["total"]),
                ("Likes", feedback_stats["likes"]),
                ("Dislikes", feedback_stats["dislikes"]),
            ]

            for label, value in stats_data:
                ax.text(0.2, y_pos, f"{label}:", fontsize=12, fontweight="bold")
                ax.text(0.6, y_pos, str(value), fontsize=12)
                y_pos -= line_height

            # 생성 일시
            gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ax.text(
                0.5,
                0.05,
                f"Generated: {gen_time}",
                ha="center",
                va="bottom",
                fontsize=10,
                style="italic",
            )

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            # 페이지 2: 피드백 차트
            if feedback_stats["total"] > 0:
                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis("off")

                # 차트 타이틀
                ax.text(
                    0.5,
                    0.95,
                    "Feedback Statistics",
                    ha="center",
                    va="top",
                    fontsize=16,
                    fontweight="bold",
                )

                # 차트 삽입
                chart_buf = create_feedback_chart(feedback_stats)
                chart_img = plt.imread(chart_buf, format="png")
                ax_img = fig.add_axes([0.1, 0.3, 0.8, 0.6])
                ax_img.imshow(chart_img)
                ax_img.axis("off")

                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

        logger.info(f"리포트 생성 완료: {report_path}")
        print(f"[OK] 주간 리포트 생성 완료: {report_path}")

        return {
            "status": "success",
            "report_path": str(report_path),
            "start_date": start_date,
            "end_date": end_date,
            "stats": {
                "conversations": conv_count,
                "sentiment": sentiment_stats,
                "feedback": feedback_stats,
            },
        }

    except Exception as e:
        logger.error(f"리포트 생성 중 오류 발생: {e}", exc_info=True)
        print(f"[오류] 리포트 생성 실패: {e}")
        return {"status": "error", "error": str(e)}
