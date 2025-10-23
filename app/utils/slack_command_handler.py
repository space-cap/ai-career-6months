"""
slack_command_handler.py
----------------------------------------
Slack 명령(/ai-report)으로 리포트 생성 및 업로드 트리거
----------------------------------------
Slack Slash Command로 주간 AI 운영 리포트를 즉시 생성하고 업로드
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.utils.report_generator import generate_weekly_report
from app.utils.slack_uploader import upload_to_slack

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()


async def generate_and_upload_report(user: str, days: int = 7):
    """
    백그라운드에서 리포트 생성 및 업로드 실행

    Args:
        user: Slack 사용자명
        days: 리포트 기간 (일 단위)
    """
    try:
        logger.info(f"[Slack Command] {user} 님이 {days}일 리포트 생성 요청")

        # 1. 리포트 생성
        logger.info("1단계: PDF 리포트 생성 중...")
        report_result = generate_weekly_report(days=days)

        if report_result["status"] != "success":
            error_msg = report_result.get("error", "Unknown error")
            logger.error(f"리포트 생성 실패: {error_msg}")
            return

        # 리포트 정보 추출
        report_path = report_result["report_path"]
        start_date = report_result["start_date"]
        end_date = report_result["end_date"]
        stats = report_result["stats"]

        logger.info(f"리포트 생성 성공: {report_path}")
        logger.info(f"기간: {start_date} ~ {end_date}")

        # 2. Slack 업로드
        logger.info("2단계: Slack 업로드 중...")

        slack_comment = f"""📊 *AI 주간 운영 리포트* (요청자: {user})

📅 기간: {start_date} ~ {end_date}

📈 주요 지표:
  • 총 대화: {stats['conversations']}개
  • 감정 분석: {stats['sentiment']['analyzed']}/{stats['sentiment']['total']}
  • 피드백: 👍 {stats['feedback']['likes']} / 👎 {stats['feedback']['dislikes']}

생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        upload_result = upload_to_slack(
            file_path=report_path,
            comment=slack_comment
        )

        if upload_result["status"] != "success":
            error_msg = upload_result.get("error", "Unknown error")
            logger.error(f"Slack 업로드 실패: {error_msg}")
            return

        # 3. 성공
        file_url = upload_result.get("file_url", "")
        logger.info(f"Slack 업로드 성공: {file_url}")
        logger.info(f"[Slack Command] {user} 님의 리포트 생성 완료")

    except Exception as e:
        logger.error(f"리포트 생성 중 예상치 못한 오류: {e}", exc_info=True)


@router.post("/slack/ai-report")
async def handle_slack_command(request: Request, background_tasks: BackgroundTasks):
    """
    Slack Slash Command 핸들러: /ai-report

    리포트 생성을 백그라운드에서 실행하고 즉시 응답 반환
    (Slack은 3초 내 응답 필요)
    """
    try:
        # 1. 요청 파싱
        form = await request.form()
        token = form.get("token")
        user = form.get("user_name", "unknown")
        command = form.get("command", "")
        text = form.get("text", "").strip()

        logger.info(f"[Slack Command] 수신: user={user}, command={command}, text={text}")

        # 2. 보안 검증
        if not settings.SLACK_VERIFICATION_TOKEN:
            logger.warning("SLACK_VERIFICATION_TOKEN이 설정되지 않았습니다")
            return JSONResponse(
                content={"text": "[오류] 서버 설정 오류: 검증 토큰이 없습니다"},
                status_code=500
            )

        if token != settings.SLACK_VERIFICATION_TOKEN:
            logger.warning(f"[Slack Command] 인증 실패: 잘못된 토큰 (user={user})")
            return JSONResponse(
                content={"text": "[오류] 인증 실패: 잘못된 요청입니다"},
                status_code=401
            )

        # 3. 파라미터 파싱 (옵션: 일수 지정 가능)
        days = 7  # 기본값
        if text and text.isdigit():
            days = int(text)
            if days < 1 or days > 90:
                return JSONResponse(
                    content={
                        "response_type": "ephemeral",
                        "text": "[오류] 일수는 1-90 사이로 지정해주세요. 예: /ai-report 7"
                    }
                )

        # 4. 백그라운드에서 리포트 생성 실행
        background_tasks.add_task(generate_and_upload_report, user, days)

        # 5. 즉시 응답 반환 (Slack 3초 제한 대응)
        logger.info(f"[Slack Command] 백그라운드 작업 시작: {days}일 리포트 생성")

        return JSONResponse(content={
            "response_type": "in_channel",
            "text": f"📊 AI 운영 리포트 생성 시작\n\n요청자: {user}\n기간: 최근 {days}일\n\n잠시 후 채널에 업로드됩니다..."
        })

    except Exception as e:
        logger.error(f"[Slack Command] 처리 중 오류: {e}", exc_info=True)
        return JSONResponse(
            content={
                "response_type": "ephemeral",
                "text": f"[오류] 리포트 생성 실패: {str(e)}"
            },
            status_code=500
        )
