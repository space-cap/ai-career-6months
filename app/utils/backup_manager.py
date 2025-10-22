"""
backup_manager.py
----------------------------------------
PostgreSQL DB 및 로그 파일을 백업하여 보관.
pg_dump를 사용한 PostgreSQL 백업 및 오래된 백업 자동 정리.
----------------------------------------
"""

import os
import subprocess
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings
from app.utils.slack_notifier import send_slack_message

# 설정
BACKUP_DIR = Path("backups")
LOG_DIR = Path("logs")
DEFAULT_RETENTION_DAYS = 7

# 로깅 설정
logger = logging.getLogger(__name__)


def parse_database_url(database_url: str) -> dict:
    """
    DATABASE_URL 파싱하여 연결 정보 추출

    Args:
        database_url: PostgreSQL 연결 URL
            (예: postgresql://user:password@host:port/dbname)

    Returns:
        dict: 연결 정보 딕셔너리
    """
    try:
        parsed = urlparse(database_url)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/"),
        }
    except Exception as e:
        logger.error(f"DATABASE_URL 파싱 실패: {e}")
        raise


def backup_postgresql(output_file: Path) -> bool:
    """
    PostgreSQL 데이터베이스를 pg_dump로 백업

    Args:
        output_file: 백업 파일 경로

    Returns:
        bool: 성공 여부
    """
    try:
        db_config = parse_database_url(settings.DATABASE_URL)

        # pg_dump 명령어 구성
        env = os.environ.copy()
        env["PGPASSWORD"] = db_config["password"]

        cmd = [
            "pg_dump",
            "-h",
            db_config["host"],
            "-p",
            str(db_config["port"]),
            "-U",
            db_config["user"],
            "-d",
            db_config["database"],
            "-F",
            "c",  # Custom format (압축됨)
            "-f",
            str(output_file),
        ]

        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=300
        )

        if result.returncode == 0:
            logger.info(f"PostgreSQL 백업 성공: {output_file}")
            return True
        else:
            logger.error(f"pg_dump 실패: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("pg_dump 실행 시간 초과 (5분)")
        return False
    except FileNotFoundError:
        logger.error("pg_dump 명령어를 찾을 수 없습니다. PostgreSQL 클라이언트가 설치되어 있는지 확인하세요.")
        return False
    except Exception as e:
        logger.error(f"PostgreSQL 백업 중 오류 발생: {e}")
        return False


def backup_logs(zipf: zipfile.ZipFile) -> int:
    """
    로그 파일들을 zip에 추가

    Args:
        zipf: ZipFile 객체

    Returns:
        int: 백업된 로그 파일 개수
    """
    count = 0
    if not LOG_DIR.exists():
        logger.warning(f"로그 디렉토리가 존재하지 않습니다: {LOG_DIR}")
        return count

    try:
        for log_file in LOG_DIR.glob("*.log*"):
            if log_file.is_file():
                zipf.write(log_file, arcname=f"logs/{log_file.name}")
                count += 1
        logger.info(f"{count}개의 로그 파일 백업 완료")
    except Exception as e:
        logger.error(f"로그 백업 중 오류: {e}")

    return count


def cleanup_old_backups(retention_days: int = DEFAULT_RETENTION_DAYS) -> int:
    """
    오래된 백업 파일 삭제

    Args:
        retention_days: 보관 기간 (일)

    Returns:
        int: 삭제된 파일 개수
    """
    if not BACKUP_DIR.exists():
        return 0

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0

    try:
        for backup_file in BACKUP_DIR.glob("backup_*.zip"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"오래된 백업 파일 삭제: {backup_file.name}")

        if deleted_count > 0:
            logger.info(f"{deleted_count}개의 오래된 백업 파일 삭제 완료")
    except Exception as e:
        logger.error(f"백업 파일 정리 중 오류: {e}")

    return deleted_count


def create_backup(retention_days: int = DEFAULT_RETENTION_DAYS) -> dict:
    """
    PostgreSQL DB 및 로그 파일을 백업하고 오래된 백업 정리

    Args:
        retention_days: 백업 보관 기간 (일)

    Returns:
        dict: 백업 결과 정보
    """
    try:
        # 백업 디렉토리 생성
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        db_backup_file = BACKUP_DIR / f"db_backup_{timestamp}.dump"
        zip_backup_file = BACKUP_DIR / f"backup_{timestamp}.zip"

        result = {
            "status": "success",
            "timestamp": timestamp,
            "db_backup": None,
            "log_count": 0,
            "zip_file": None,
            "cleaned_count": 0,
        }

        # 1. PostgreSQL 백업
        logger.info("PostgreSQL 백업 시작...")
        db_success = backup_postgresql(db_backup_file)

        if not db_success:
            result["status"] = "partial_failure"
            result["error"] = "PostgreSQL 백업 실패"

        # 2. 로그 및 DB 덤프를 zip으로 압축
        logger.info("파일 압축 시작...")
        with zipfile.ZipFile(zip_backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            # DB 덤프 파일 추가
            if db_success and db_backup_file.exists():
                zipf.write(db_backup_file, arcname=db_backup_file.name)
                result["db_backup"] = str(db_backup_file)

            # 로그 파일 추가
            result["log_count"] = backup_logs(zipf)

        result["zip_file"] = str(zip_backup_file)

        # 3. 임시 DB 덤프 파일 삭제 (zip에 포함되었으므로)
        if db_backup_file.exists():
            db_backup_file.unlink()

        # 4. 오래된 백업 정리
        logger.info(f"{retention_days}일 이상 된 백업 파일 정리 중...")
        result["cleaned_count"] = cleanup_old_backups(retention_days)

        # 5. Slack 알림
        try:
            zip_size_mb = zip_backup_file.stat().st_size / (1024 * 1024)
            msg = (
                f"[백업 완료]\n"
                f"- 파일: {zip_backup_file.name}\n"
                f"- 크기: {zip_size_mb:.2f} MB\n"
                f"- 로그: {result['log_count']}개\n"
                f"- 정리: {result['cleaned_count']}개 삭제\n"
                f"- 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            send_slack_message(msg)
        except Exception as e:
            logger.warning(f"Slack 알림 전송 실패: {e}")

        logger.info(f"백업 완료: {zip_backup_file}")
        print(f"[OK] 백업 완료: {zip_backup_file.name} ({zip_size_mb:.2f} MB)")

        return result

    except Exception as e:
        logger.error(f"백업 프로세스 중 오류 발생: {e}")
        print(f"[오류] 백업 실패: {e}")
        return {"status": "error", "error": str(e)}
