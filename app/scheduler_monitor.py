"""
scheduler_monitor.py
----------------------------------------
모든 모니터링 + 백업 작업을 일정 주기로 실행
----------------------------------------
"""

import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule

from app.core.config import settings
from app.utils.monitor import check_server_status, setup_logging as setup_monitor_logging
from app.utils.backup_manager import create_backup

# 로깅 설정
LOG_DIR = Path("logs")
LOG_PATH = LOG_DIR / "scheduler.log"

logger = logging.getLogger(__name__)

# graceful shutdown을 위한 플래그
shutdown_flag = False


def setup_logging():
    """스케줄러 로깅 설정"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러도 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def safe_monitor_check():
    """
    서버 모니터링 작업을 안전하게 실행 (에러 핸들링 포함)
    """
    try:
        logger.info("서버 상태 체크 시작")
        result = check_server_status()
        logger.info(f"서버 상태 체크 완료: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"서버 모니터링 중 오류 발생: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def safe_backup():
    """
    백업 작업을 안전하게 실행 (에러 핸들링 포함)
    """
    try:
        logger.info("백업 작업 시작")
        result = create_backup(retention_days=settings.BACKUP_RETENTION_DAYS)
        logger.info(f"백업 작업 완료: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"백업 작업 중 오류 발생: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def signal_handler(signum, frame):
    """
    시그널 핸들러 (graceful shutdown)
    """
    global shutdown_flag
    signal_name = signal.Signals(signum).name
    logger.info(f"종료 시그널 수신: {signal_name}")
    print(f"\n[INFO] 종료 시그널 수신: {signal_name}")
    print("[INFO] 스케줄러를 안전하게 종료합니다...")
    shutdown_flag = True


def print_schedule_info():
    """
    현재 스케줄 정보 출력
    """
    jobs = schedule.get_jobs()
    if not jobs:
        logger.warning("등록된 스케줄 작업이 없습니다.")
        return

    print("\n" + "=" * 60)
    print("등록된 스케줄 작업")
    print("=" * 60)

    for job in jobs:
        next_run = job.next_run
        if next_run:
            next_run_str = next_run.strftime("%Y-%m-%d %H:%M:%S")
        else:
            next_run_str = "알 수 없음"

        print(f"  - 작업: {job.job_func.__name__}")
        print(f"    주기: {job}")
        print(f"    다음 실행: {next_run_str}")
        print()

    logger.info(f"총 {len(jobs)}개의 스케줄 작업이 등록되었습니다.")


def run_schedule():
    """
    스케줄러 메인 루프 실행
    """
    global shutdown_flag

    # 로깅 설정
    setup_logging()
    setup_monitor_logging()

    logger.info("=" * 60)
    logger.info("시스템 모니터링 스케줄러 시작")
    logger.info("=" * 60)

    # 시그널 핸들러 등록 (graceful shutdown)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill

    # 스케줄 등록
    logger.info(f"서버 모니터링 주기: {settings.MONITOR_INTERVAL_MINUTES}분")
    schedule.every(settings.MONITOR_INTERVAL_MINUTES).minutes.do(safe_monitor_check)

    logger.info(f"백업 실행 시간: 매일 {settings.BACKUP_TIME}")
    schedule.every().day.at(settings.BACKUP_TIME).do(safe_backup)

    logger.info(f"백업 보관 기간: {settings.BACKUP_RETENTION_DAYS}일")

    # 스케줄 정보 출력
    print_schedule_info()

    print("\n[INFO] 스케줄러 실행 중... (Ctrl+C로 종료)")
    logger.info("스케줄러 루프 시작")

    # 메인 루프
    try:
        while not shutdown_flag:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt 수신")
        print("\n[INFO] 키보드 인터럽트로 종료합니다...")
    except Exception as e:
        logger.error(f"스케줄러 실행 중 예상치 못한 오류: {e}", exc_info=True)
        print(f"\n[오류] 스케줄러 오류: {e}")
    finally:
        logger.info("=" * 60)
        logger.info("시스템 모니터링 스케줄러 종료")
        logger.info("=" * 60)
        print("\n[INFO] 스케줄러가 안전하게 종료되었습니다.")


if __name__ == "__main__":
    run_schedule()
