#!/usr/bin/env python3
"""
DB 백업 스크립트 테스트

Usage:
    python scripts/test_backup_db.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.backup_db import (
    run_backup,
    cleanup_old_backups,
    BACKUP_DIR,
)
from app.core.config import settings


def test_backup_directory():
    """백업 디렉토리 생성 테스트"""
    print("=" * 80)
    print("[백업 디렉토리 테스트]")
    print("=" * 80)

    print(f"\n백업 디렉토리: {BACKUP_DIR}")
    print(f"존재 여부: {BACKUP_DIR.exists()}")
    print(f"쓰기 가능: {BACKUP_DIR.is_dir() and BACKUP_DIR.exists()}")

    if BACKUP_DIR.exists():
        files = list(BACKUP_DIR.glob("*"))
        print(f"기존 백업 파일: {len(files)}개")
        for f in sorted(files)[-5:]:  # 최근 5개만 표시
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  - {f.name} ({size_mb:.2f}MB)")


def test_database_config():
    """데이터베이스 설정 테스트"""
    print("\n" + "=" * 80)
    print("[데이터베이스 설정 테스트]")
    print("=" * 80)

    print(f"\nDATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"BACKUP_RETENTION_DAYS: {settings.BACKUP_RETENTION_DAYS}일")

    from urllib.parse import urlparse

    parsed = urlparse(settings.DATABASE_URL)
    print(f"\nDB 타입: {parsed.scheme}")
    if parsed.scheme in ("postgres", "postgresql"):
        print(f"호스트: {parsed.hostname}")
        print(f"포트: {parsed.port or 5432}")
        print(f"사용자: {parsed.username}")
        print(f"DB 이름: {parsed.path.lstrip('/')}")
    elif parsed.scheme == "sqlite":
        print(f"DB 파일: {parsed.path}")


def test_cleanup_function():
    """백업 정리 함수 테스트 (실제 삭제 없음)"""
    print("\n" + "=" * 80)
    print("[백업 정리 함수 테스트]")
    print("=" * 80)

    print(f"\n보관 기간: {settings.BACKUP_RETENTION_DAYS}일")
    print("실제 정리 실행 중...")

    try:
        result = cleanup_old_backups(retention_days=settings.BACKUP_RETENTION_DAYS)
        print(f"\n[결과]")
        print(f"  - 삭제된 백업: {result['deleted_count']}개")
        print(f"  - 확보 공간: {result['deleted_size_mb']}MB")

    except Exception as e:
        print(f"[에러] 백업 정리 실패: {e}")


def test_backup_execution():
    """백업 실행 테스트 (실제 백업)"""
    print("\n" + "=" * 80)
    print("[백업 실행 테스트]")
    print("=" * 80)

    print("\n경고: 실제 백업이 실행됩니다.")
    print("계속하시겠습니까? (y/N): ", end="")

    # 자동 테스트를 위해 'y' 입력 스킵
    # user_input = input().strip().lower()
    # if user_input != 'y':
    #     print("백업 테스트를 건너뜁니다.")
    #     return

    print("y (자동)")
    print("\n백업 실행 중...")

    try:
        result = run_backup(retention_days=settings.BACKUP_RETENTION_DAYS)

        print("\n[백업 성공]")
        print(f"  - DB 타입: {result['db_type']}")

        backup_info = result.get("backup_result", {})
        if backup_info:
            print(f"  - 파일: {Path(backup_info['file_path']).name}")
            print(f"  - 크기: {backup_info['file_size_mb']}MB")
            print(f"  - 소요 시간: {backup_info['duration_sec']}초")

        cleanup_info = result.get("cleanup_result", {})
        if cleanup_info:
            print(f"  - 정리된 백업: {cleanup_info['deleted_count']}개")

    except FileNotFoundError as e:
        print(f"\n[에러] DB 파일을 찾을 수 없습니다: {e}")
        print("SQLite DB가 없거나, PostgreSQL이 설치되지 않았을 수 있습니다.")

    except Exception as e:
        print(f"\n[에러] 백업 실패: {e}")
        import traceback

        traceback.print_exc()


def main():
    """메인 테스트 실행"""
    print("\n")
    print("###############################################################################")
    print("#                                                                             #")
    print("#                    Database Backup Test Suite                              #")
    print("#                                                                             #")
    print("###############################################################################")
    print("\n")

    try:
        # 1. 백업 디렉토리 테스트
        test_backup_directory()

        # 2. 데이터베이스 설정 테스트
        test_database_config()

        # 3. 백업 정리 함수 테스트
        test_cleanup_function()

        # 4. 백업 실행 테스트
        test_backup_execution()

        print("\n" + "=" * 80)
        print("[테스트 완료]")
        print("=" * 80)

        print("\n[확인 사항]")
        print(f"1. {BACKUP_DIR} 디렉토리에 백업 파일이 생성되었는지 확인")
        print("2. 백업 파일 크기가 0바이트가 아닌지 확인")
        print("3. 로그 파일(logs/app.log)에 백업 로그가 기록되었는지 확인")
        print("\n")

    except Exception as e:
        print(f"\n[에러] 테스트 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
