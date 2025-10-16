"""
slack_notifier.py
----------------------------------
Slack 메시지 및 파일 업로드 공통 유틸리티

Slack BOT Token 및 Channel 환경변수를 기반으로
텍스트 메시지와 파일을 Slack으로 전송합니다.

모든 모듈에서 import하여 재사용 가능합니다.

사용 예시:
    from app.utils.slack_notifier import send_slack_message

    # 텍스트 메시지 전송
    send_slack_message("Hello Slack!")

    # 파일 전송
    send_slack_message("Report attached", file_path="./report.csv")

환경 변수:
    - SLACK_BOT_TOKEN: Slack Bot User OAuth Token (필수)
    - SLACK_CHANNEL: 메시지를 보낼 채널 (기본값: ai-reports)
----------------------------------
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# Slack 설정
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "ai-reports")


def send_slack_message(text: str, file_path: str | None = None) -> dict:
    """
    Slack으로 메시지 또는 파일을 전송합니다.

    Args:
        text (str): 전송할 메시지 내용
        file_path (str | None, optional): 업로드할 파일 경로.
            파일이 지정되면 files.upload API를 사용하고,
            없으면 chat.postMessage API를 사용합니다.
            기본값: None

    Returns:
        dict: Slack API 응답
            - ok (bool): 성공 여부
            - error (str): 에러 메시지 (실패 시)

    Examples:
        >>> send_slack_message("Hello!")
        {'ok': True, 'message': {...}}

        >>> send_slack_message("Report", file_path="./data.csv")
        {'ok': True, 'file': {...}}

    Raises:
        requests.RequestException: HTTP 요청 실패 시
    """
    if not SLACK_BOT_TOKEN:
        print("⚠️ SLACK_BOT_TOKEN not set. Skipping Slack message.")
        print("💡 Tip: .env 파일에 SLACK_BOT_TOKEN을 설정하세요.")
        return {"ok": False, "error": "missing_token"}

    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

    try:
        # 파일이 있으면 파일 업로드
        if file_path and os.path.exists(file_path):
            data = {"channels": SLACK_CHANNEL, "initial_comment": text}

            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://slack.com/api/files.upload",
                    headers=headers,
                    data=data,
                    files={"file": f},
                    timeout=30  # 타임아웃 설정
                )

            print(f"📎 Uploading file: {os.path.basename(file_path)}")

        else:
            # 텍스트 메시지 전송
            if file_path:
                print(f"⚠️ File not found: {file_path}. Sending text only.")

            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json={"channel": SLACK_CHANNEL, "text": text},
                timeout=10
            )

        # 응답 처리
        response.raise_for_status()  # HTTP 에러 체크
        result = response.json()

        if result.get("ok"):
            print(f"✅ Slack 전송 완료 → #{SLACK_CHANNEL}")
        else:
            error_msg = result.get("error", "unknown_error")
            print(f"❌ Slack API 오류: {error_msg}")

            # 권한 관련 에러 힌트 제공
            if error_msg == "missing_scope":
                print(f"💡 Hint: Bot Token에 필요한 권한이 없습니다.")
                print(f"   필요한 scope: {result.get('needed', 'N/A')}")
            elif error_msg == "channel_not_found":
                print(f"💡 Hint: 채널 '{SLACK_CHANNEL}'을 찾을 수 없습니다.")
                print(f"   채널 이름을 확인하거나 Bot을 채널에 초대하세요.")

        return result

    except requests.RequestException as e:
        print(f"❌ HTTP 요청 오류: {e}")
        return {"ok": False, "error": f"request_failed: {str(e)}"}

    except Exception as e:
        print(f"❌ Slack 전송 중 예외 발생: {e}")
        return {"ok": False, "error": str(e)}
