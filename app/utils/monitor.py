"""
monitor.py
----------------------------------------
CPU, Memory, Disk, API 응답 상태를 모니터링하고
이상 발생 시 Slack으로 알림을 보냄
----------------------------------------
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

import psutil

from app.utils.slack_notifier import send_slack_message

# 로그 디렉토리 및 파일 경로 설정
LOG_DIR = Path("logs")
LOG_PATH = LOG_DIR / "system_monitor.log"

# 로깅 설정
logger = logging.getLogger(__name__)


def setup_logging():
    """로깅 설정 초기화 (로테이션 포함)"""
    # 로그 디렉토리 생성
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # RotatingFileHandler 설정 (최대 10MB, 백업 5개)
    handler = RotatingFileHandler(
        LOG_PATH, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def get_disk_path():
    """OS별 디스크 경로 반환 (Windows/Linux 호환)"""
    if sys.platform == "win32":
        # Windows: 현재 작업 디렉토리의 드라이브 (예: C:\)
        return os.path.abspath(os.sep)
    else:
        # Linux/Unix: 루트 파일시스템
        return "/"


def log_status(cpu, mem, disk):
    """상태 로그 기록"""
    logger.info(f"CPU:{cpu:.1f}% | MEM:{mem:.1f}% | DISK:{disk:.1f}%")


def check_server_status(
    threshold_cpu=85, threshold_mem=90, threshold_disk=90, send_slack=True
):
    """
    서버 리소스 상태 체크 및 알림

    Args:
        threshold_cpu (int): CPU 사용률 임계값 (%)
        threshold_mem (int): 메모리 사용률 임계값 (%)
        threshold_disk (int): 디스크 사용률 임계값 (%)
        send_slack (bool): Slack 알림 전송 여부

    Returns:
        dict: 상태 정보 딕셔너리
    """
    try:
        # 리소스 사용률 수집
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk_path = get_disk_path()
        disk = psutil.disk_usage(disk_path).percent

        # 로그 기록
        log_status(cpu, mem, disk)

        # 임계값 체크
        alerts = []
        if cpu > threshold_cpu:
            alerts.append(f"CPU: {cpu:.1f}% (임계값: {threshold_cpu}%)")
        if mem > threshold_mem:
            alerts.append(f"Memory: {mem:.1f}% (임계값: {threshold_mem}%)")
        if disk > threshold_disk:
            alerts.append(f"Disk: {disk:.1f}% (임계값: {threshold_disk}%)")

        # 경고 발생 시 처리
        if alerts:
            alert_msg = "\n".join([f"  - {a}" for a in alerts])
            msg = (
                f"🚨 *서버 자원 경고*\n"
                f"{alert_msg}\n"
                f"- 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            logger.warning(f"리소스 임계값 초과:\n{alert_msg}")
            print(f"[경고] 리소스 임계값 초과\n{alert_msg}")

            # Slack 알림 전송 (옵션)
            if send_slack:
                try:
                    send_slack_message(msg)
                    logger.info("Slack 알림 전송 완료")
                except Exception as e:
                    logger.error(f"Slack 알림 전송 실패: {e}")
                    print(f"[오류] Slack 알림 전송 실패: {e}")

            return {
                "status": "warning",
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "alerts": alerts,
            }
        else:
            print(f"[OK] 정상 상태 - CPU {cpu:.1f}%, MEM {mem:.1f}%, DISK {disk:.1f}%")
            return {
                "status": "ok",
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "alerts": [],
            }

    except Exception as e:
        logger.error(f"모니터링 실행 중 오류 발생: {e}")
        print(f"[오류] 모니터링 오류: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    setup_logging()
    result = check_server_status()
    print(f"\n모니터링 결과: {result}")
