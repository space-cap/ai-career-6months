"""
db_cleanup.py
----------------------------------------
오래된 로그 백업 및 정리 스크립트

conversation_log 테이블에서 일정 기간 지난 데이터를 백업하고 삭제합니다.

기능:
  - 지정된 기간(기본 30일) 이상 지난 로그를 CSV로 백업
  - 백업 후 원본 DB에서 삭제
  - 로컬 backups 폴더에 저장

실행 방법:
  python -m app.utils.db_cleanup

환경 변수:
  - LOG_RETENTION_DAYS: 보관 기간 (기본값: 30일)
  - DATABASE_URL: 데이터베이스 연결 문자열
----------------------------------------
"""

import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# -----------------------------------
# 1️⃣ 환경 변수 및 설정
# -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

# DB 엔진 생성
engine = create_engine(DATABASE_URL)

# 백업 폴더 생성 (프로젝트 루트/backups)
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_and_cleanup_logs() -> None:
    """
    오래된 대화 로그를 백업하고 DB에서 삭제합니다.

    동작:
        1. RETENTION_DAYS 이상 지난 로그 조회
        2. CSV 파일로 백업 (backups 폴더)
        3. DB에서 해당 로그 삭제

    환경 변수:
        - LOG_RETENTION_DAYS: 보관 기간 (기본값: 30일)

    Raises:
        SQLAlchemyError: DB 작업 중 오류 발생 시
        IOError: 파일 쓰기 중 오류 발생 시
    """
    try:
        # ✅ Python 3.12+ 호환: datetime.now(timezone.utc) 사용
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        print("📊 Starting backup and cleanup process...")
        print(f"🗓️  Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"🔧 Retention period: {RETENTION_DAYS} days")

        # -----------------------------------
        # 2️⃣ 오래된 로그 조회
        # -----------------------------------
        query = text("""
            SELECT * FROM conversation_log
            WHERE created_at < :cutoff
        """)

        df = pd.read_sql(query, engine, params={"cutoff": cutoff_date})

        if df.empty:
            print("✅ No old logs found to backup.")
            return

        print(f"📋 Found {len(df)} logs to backup.")

        # -----------------------------------
        # 3️⃣ CSV 파일로 백업
        # -----------------------------------
        backup_filename = f"conversation_log_backup_{cutoff_date.strftime('%Y%m%d_%H%M%S')}.csv"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        try:
            df.to_csv(backup_path, index=False, encoding="utf-8-sig")
            print(f"💾 Backup saved: {backup_path}")
            print(f"   - Rows backed up: {len(df)}")
            print(f"   - File size: {os.path.getsize(backup_path) / 1024:.2f} KB")
        except IOError as e:
            print(f"❌ Failed to save backup file: {e}")
            raise

        # -----------------------------------
        # 4️⃣ DB에서 삭제
        # -----------------------------------
        delete_query = text("""
            DELETE FROM conversation_log
            WHERE created_at < :cutoff
        """)

        try:
            with engine.begin() as conn:
                result = conn.execute(delete_query, {"cutoff": cutoff_date})
                deleted_count = result.rowcount

            print("🧹 Cleanup complete!")
            print(f"   - Rows deleted: {deleted_count}")
            print("✅ Backup and cleanup process finished successfully.")

        except SQLAlchemyError as e:
            print(f"❌ Failed to delete logs from database: {e}")
            print(f"⚠️  Note: Backup file was created at {backup_path}")
            raise

    except Exception as e:
        print(f"❌ Error during backup and cleanup: {e}")
        raise


if __name__ == "__main__":
    backup_and_cleanup_logs()
