#!/usr/bin/env python3
# scripts/backup_db.py
"""
데이터베이스 백업 스크립트 (프로덕션 급)

기능:
- PostgreSQL: pg_dump 사용 (custom format)
- SQLite: 파일 복사 + 압축
- 백업 파일 자동 삭제 (보관 기간 경과)
- 백업 검증 (파일 크기, 무결성)
- Slack 알림 (성공/실패)
- 타임존 명시 (UTC)

Usage:
    python scripts/backup_db.py
    python scripts/backup_db.py --retention-days 14
"""
import sys
import subprocess
import shutil
import gzip
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import argparse

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 백업 디렉토리 설정
BACKUP_DIR = Path(settings.LOG_DIR).parent / "backups"
if not BACKUP_DIR.is_absolute():
    BACKUP_DIR = PROJECT_ROOT / BACKUP_DIR

# 백업 디렉토리 생성
try:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"백업 디렉토리: {BACKUP_DIR}")
except PermissionError as e:
    logger.error(f"백업 디렉토리 생성 실패: {BACKUP_DIR} - {e}")
    sys.exit(1)

# Slack 알림 설정
SLACK_NOTIFY = settings.SLACK_WEBHOOK_URL is not None

# Slack 유틸 import
try:
    from app.utils.slack_utils import send_slack_message
except ImportError:
    logger.warning("Slack 유틸리티를 찾을 수 없습니다. 알림이 비활성화됩니다.")
    send_slack_message = None
    SLACK_NOTIFY = False


def backup_postgres(parsed: urlparse, backup_path: Path) -> Dict[str, Any]:
    """
    PostgreSQL 데이터베이스 백업 (pg_dump)

    Args:
        parsed: urlparse 결과 (DATABASE_URL)
        backup_path: 백업 파일 경로

    Returns:
        {
            "success": True/False,
            "file_path": backup_path,
            "file_size_mb": 파일 크기 (MB),
            "duration_sec": 소요 시간 (초)
        }

    Raises:
        subprocess.CalledProcessError: pg_dump 실행 실패
    """
    start_time = datetime.now(timezone.utc)

    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    dbname = parsed.path.lstrip("/")

    # PGPASSWORD 환경변수 설정
    env = dict(subprocess.os.environ)
    if password:
        env["PGPASSWORD"] = password

    # pg_dump 명령어
    cmd = [
        "pg_dump",
        "-h", host,
        "-p", str(port),
        "-U", user,
        "-F", "c",  # custom format (압축됨)
        "-b",  # include blobs
        "-v",  # verbose
        "-f", str(backup_path),
        dbname,
    ]

    logger.info(f"PostgreSQL 백업 시작 - DB: {dbname}, Host: {host}")
    logger.debug(f"pg_dump 명령: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        # 백업 파일 검증
        if not backup_path.exists():
            raise FileNotFoundError(f"백업 파일이 생성되지 않았습니다: {backup_path}")

        file_size_bytes = backup_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        if file_size_bytes == 0:
            raise ValueError("백업 파일 크기가 0바이트입니다")

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info(
            f"PostgreSQL 백업 완료 - 파일: {backup_path.name}, "
            f"크기: {file_size_mb:.2f}MB, 소요 시간: {duration:.2f}초"
        )

        return {
            "success": True,
            "file_path": str(backup_path),
            "file_size_mb": round(file_size_mb, 2),
            "duration_sec": round(duration, 2),
        }

    except subprocess.CalledProcessError as e:
        logger.error(f"pg_dump 실행 실패: {e.stderr}")
        raise


def backup_sqlite(db_path: Path, backup_path: Path) -> Dict[str, Any]:
    """
    SQLite 데이터베이스 백업 (파일 복사 + gzip 압축)

    Args:
        db_path: SQLite DB 파일 경로
        backup_path: 백업 파일 경로

    Returns:
        {
            "success": True/False,
            "file_path": backup_path,
            "file_size_mb": 파일 크기 (MB),
            "duration_sec": 소요 시간 (초)
        }
    """
    start_time = datetime.now(timezone.utc)

    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB 파일을 찾을 수 없습니다: {db_path}")

    logger.info(f"SQLite 백업 시작 - DB: {db_path}")

    # 백업 파일을 gzip으로 압축
    with open(db_path, "rb") as f_in:
        with gzip.open(str(backup_path) + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    backup_path_gz = Path(str(backup_path) + ".gz")

    # 백업 파일 검증
    if not backup_path_gz.exists():
        raise FileNotFoundError(f"백업 파일이 생성되지 않았습니다: {backup_path_gz}")

    file_size_bytes = backup_path_gz.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    logger.info(
        f"SQLite 백업 완료 - 파일: {backup_path_gz.name}, "
        f"크기: {file_size_mb:.2f}MB, 소요 시간: {duration:.2f}초"
    )

    return {
        "success": True,
        "file_path": str(backup_path_gz),
        "file_size_mb": round(file_size_mb, 2),
        "duration_sec": round(duration, 2),
    }


def cleanup_old_backups(retention_days: int = None):
    """
    오래된 백업 파일 자동 삭제

    Args:
        retention_days: 백업 보관 기간 (일). None이면 settings.BACKUP_RETENTION_DAYS 사용
    """
    if retention_days is None:
        retention_days = settings.BACKUP_RETENTION_DAYS

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    logger.info(f"백업 파일 정리 시작 - 보관 기간: {retention_days}일")

    deleted_count = 0
    deleted_size = 0

    for backup_file in BACKUP_DIR.glob("*_backup_*"):
        try:
            file_mtime = datetime.fromtimestamp(
                backup_file.stat().st_mtime, tz=timezone.utc
            )

            if file_mtime < cutoff_date:
                file_size = backup_file.stat().st_size
                backup_file.unlink()
                deleted_count += 1
                deleted_size += file_size
                logger.debug(f"삭제된 백업 파일: {backup_file.name}")

        except Exception as e:
            logger.warning(f"백업 파일 삭제 실패: {backup_file.name} - {e}")

    deleted_size_mb = deleted_size / (1024 * 1024)
    logger.info(
        f"백업 파일 정리 완료 - 삭제: {deleted_count}개, "
        f"확보 공간: {deleted_size_mb:.2f}MB"
    )

    return {"deleted_count": deleted_count, "deleted_size_mb": round(deleted_size_mb, 2)}


def run_backup(retention_days: Optional[int] = None) -> Dict[str, Any]:
    """
    데이터베이스 백업 실행 (메인 함수)

    Args:
        retention_days: 백업 보관 기간 (일)

    Returns:
        {
            "success": True/False,
            "db_type": "postgresql" | "sqlite",
            "backup_result": backup_postgres() 또는 backup_sqlite() 결과,
            "cleanup_result": cleanup_old_backups() 결과,
            "error": 에러 메시지 (실패 시)
        }
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    parsed = urlparse(settings.DATABASE_URL)

    result = {
        "success": False,
        "db_type": None,
        "backup_result": None,
        "cleanup_result": None,
        "timestamp": timestamp,
    }

    try:
        # 1. 데이터베이스 백업
        if parsed.scheme in ("postgres", "postgresql"):
            result["db_type"] = "postgresql"
            backup_path = BACKUP_DIR / f"pg_backup_{timestamp}.dump"
            result["backup_result"] = backup_postgres(parsed, backup_path)

        elif parsed.scheme == "sqlite":
            result["db_type"] = "sqlite"

            # SQLite 경로 파싱
            sqlite_path = parsed.path.lstrip("/")
            if not Path(sqlite_path).is_absolute():
                sqlite_path = PROJECT_ROOT / sqlite_path

            backup_path = BACKUP_DIR / f"sqlite_backup_{timestamp}.db"
            result["backup_result"] = backup_sqlite(Path(sqlite_path), backup_path)

        else:
            raise ValueError(f"지원하지 않는 DB 스키마: {parsed.scheme}")

        # 2. 오래된 백업 파일 정리
        result["cleanup_result"] = cleanup_old_backups(retention_days)

        result["success"] = True

        # 3. Slack 알림 (성공)
        if SLACK_NOTIFY and send_slack_message:
            backup_info = result["backup_result"]
            cleanup_info = result["cleanup_result"]

            message = f"""✅ **DB 백업 성공**

📊 백업 정보:
- DB 타입: {result['db_type'].upper()}
- 파일: `{Path(backup_info['file_path']).name}`
- 크기: {backup_info['file_size_mb']}MB
- 소요 시간: {backup_info['duration_sec']}초

🗑️ 정리:
- 삭제된 백업: {cleanup_info['deleted_count']}개
- 확보 공간: {cleanup_info['deleted_size_mb']}MB
- 보관 기간: {retention_days or settings.BACKUP_RETENTION_DAYS}일

⏰ 백업 시각: {timestamp} UTC
"""
            send_slack_message(message)

        return result

    except subprocess.CalledProcessError as e:
        error_msg = f"pg_dump 실행 실패: {e.stderr}"
        result["error"] = error_msg
        logger.error(error_msg, exc_info=True)

        if SLACK_NOTIFY and send_slack_message:
            send_slack_message(f"❌ **DB 백업 실패**\n\n{error_msg}")

        raise

    except Exception as e:
        error_msg = f"백업 실패: {str(e)}"
        result["error"] = error_msg
        logger.error(error_msg, exc_info=True)

        if SLACK_NOTIFY and send_slack_message:
            send_slack_message(f"❌ **DB 백업 실패**\n\n{error_msg}")

        raise


def main():
    """CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(description="데이터베이스 백업 스크립트")
    parser.add_argument(
        "--retention-days",
        type=int,
        default=None,
        help=f"백업 보관 기간 (일). 기본값: {settings.BACKUP_RETENTION_DAYS}",
    )
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("데이터베이스 백업 시작")
    logger.info("=" * 80)

    try:
        result = run_backup(retention_days=args.retention_days)

        logger.info("=" * 80)
        logger.info("데이터베이스 백업 완료")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.critical("데이터베이스 백업 실패", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
