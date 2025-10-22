"""
slack_uploader.py
----------------------------------------
PDF 파일을 지정된 Slack 채널로 업로드
----------------------------------------
"""

import logging
from pathlib import Path

from app.core.config import settings

# Slack SDK는 선택적 의존성
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False
    WebClient = None
    SlackApiError = Exception

# 로깅 설정
logger = logging.getLogger(__name__)

# Slack 파일 크기 제한 (1GB)
MAX_FILE_SIZE_MB = 1024


def validate_file(file_path: Path) -> dict:
    """
    파일 유효성 검증

    Args:
        file_path: 파일 경로

    Returns:
        dict: 검증 결과
    """
    if not file_path.exists():
        return {"valid": False, "error": f"파일이 존재하지 않습니다: {file_path}"}

    if not file_path.is_file():
        return {"valid": False, "error": f"디렉토리입니다: {file_path}"}

    # 파일 크기 확인 (MB 단위)
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return {
            "valid": False,
            "error": f"파일 크기가 너무 큽니다: {file_size_mb:.2f}MB (최대 {MAX_FILE_SIZE_MB}MB)",
        }

    return {"valid": True, "size_mb": file_size_mb}


def upload_to_slack(file_path: str, comment: str = None) -> dict:
    """
    PDF 파일을 Slack 채널에 업로드

    Args:
        file_path: 업로드할 파일 경로
        comment: 업로드 시 추가할 코멘트 (선택)

    Returns:
        dict: 업로드 결과
            - status: "success" | "error"
            - file_url: 업로드된 파일 URL (성공 시)
            - error: 에러 메시지 (실패 시)
    """
    try:
        # 0. Slack SDK 확인
        if not SLACK_SDK_AVAILABLE:
            error_msg = "slack_sdk가 설치되지 않았습니다. 'pip install slack-sdk'로 설치하세요."
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        # 1. 설정 확인
        if not settings.SLACK_BOT_TOKEN:
            error_msg = "SLACK_BOT_TOKEN이 설정되지 않았습니다."
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        if not settings.SLACK_CHANNEL:
            error_msg = "SLACK_CHANNEL이 설정되지 않았습니다."
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        # 2. 파일 검증
        file_path_obj = Path(file_path)
        validation = validate_file(file_path_obj)

        if not validation["valid"]:
            logger.error(f"파일 검증 실패: {validation['error']}")
            return {"status": "error", "error": validation["error"]}

        logger.info(
            f"파일 업로드 시작: {file_path_obj.name} ({validation['size_mb']:.2f}MB)"
        )

        # 3. Slack 클라이언트 생성
        client = WebClient(token=settings.SLACK_BOT_TOKEN)

        # 4. 파일 업로드
        default_comment = f"[AI Report] {file_path_obj.name} uploaded"
        upload_comment = comment or default_comment

        response = client.files_upload_v2(
            channel=settings.SLACK_CHANNEL,
            file=str(file_path_obj),
            initial_comment=upload_comment,
        )

        # 5. 응답 처리
        if response["ok"]:
            file_url = response.get("file", {}).get("permalink", "")
            logger.info(f"Slack 업로드 성공: {file_url}")
            print(f"[OK] Slack 업로드 성공: {file_path_obj.name}")

            return {
                "status": "success",
                "file_url": file_url,
                "file_name": file_path_obj.name,
                "size_mb": validation["size_mb"],
            }
        else:
            error_msg = response.get("error", "Unknown error")
            logger.error(f"Slack API 응답 오류: {error_msg}")
            return {"status": "error", "error": error_msg}

    except SlackApiError as e:
        error_msg = f"Slack API 오류: {e.response['error']}"
        logger.error(error_msg, exc_info=True)
        print(f"[오류] Slack 업로드 실패: {e.response['error']}")
        return {"status": "error", "error": error_msg}

    except Exception as e:
        error_msg = f"예상치 못한 오류: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"[오류] Slack 업로드 실패: {e}")
        return {"status": "error", "error": error_msg}
