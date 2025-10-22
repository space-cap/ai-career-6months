"""
generate_weekly_report.py
----------------------------------------
주간 AI 운영 리포트를 생성하고 Slack에 자동 업로드
----------------------------------------
"""

import sys
import logging
from datetime import datetime

from app.utils.report_generator import generate_weekly_report
from app.utils.slack_uploader import upload_to_slack

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    """
    주간 리포트 생성 및 Slack 업로드 메인 함수
    """
    logger.info("=" * 60)
    logger.info("주간 AI 운영 리포트 생성 및 업로드 시작")
    logger.info("=" * 60)

    try:
        # 1. 리포트 생성
        logger.info("1단계: PDF 리포트 생성 중...")
        report_result = generate_weekly_report(days=7)

        if report_result["status"] != "success":
            error_msg = report_result.get("error", "Unknown error")
            logger.error(f"리포트 생성 실패: {error_msg}")
            print(f"[오류] 리포트 생성 실패: {error_msg}")
            return 1

        # 리포트 정보 추출
        report_path = report_result["report_path"]
        start_date = report_result["start_date"]
        end_date = report_result["end_date"]
        stats = report_result["stats"]

        logger.info(f"리포트 생성 성공: {report_path}")
        logger.info(f"기간: {start_date} ~ {end_date}")
        logger.info(f"통계: 대화 {stats['conversations']}개, 피드백 {stats['feedback']['total']}개")

        # 2. Slack 업로드
        logger.info("2단계: Slack 업로드 중...")

        # Slack 메시지 작성
        slack_comment = f"""📊 *AI 주간 운영 리포트*

📅 기간: {start_date} ~ {end_date}

📈 주요 지표:
  • 총 대화: {stats['conversations']}개
  • 감정 분석: {stats['sentiment']['analyzed']}/{stats['sentiment']['total']}
  • 피드백: 👍 {stats['feedback']['likes']} / 👎 {stats['feedback']['dislikes']}

생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        upload_result = upload_to_slack(
            file_path=report_path, comment=slack_comment
        )

        if upload_result["status"] != "success":
            error_msg = upload_result.get("error", "Unknown error")
            logger.error(f"Slack 업로드 실패: {error_msg}")
            print(f"[오류] Slack 업로드 실패: {error_msg}")
            print(f"[정보] 리포트는 로컬에 저장됨: {report_path}")
            return 1

        # 3. 성공
        file_url = upload_result.get("file_url", "")
        logger.info(f"Slack 업로드 성공: {file_url}")

        logger.info("=" * 60)
        logger.info("주간 리포트 생성 및 업로드 완료")
        logger.info("=" * 60)

        print("\n[OK] 주간 리포트 생성 및 업로드 완료!")
        print(f"  - 로컬 파일: {report_path}")
        print(f"  - Slack URL: {file_url}")

        return 0

    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
        print(f"\n[오류] 예상치 못한 오류: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
