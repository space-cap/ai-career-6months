#!/usr/bin/env python3
"""
로깅 유틸리티 테스트 스크립트

Usage:
    python scripts/test_logger.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.logger import get_logger, set_log_level, get_active_loggers


def test_basic_logging():
    """기본 로깅 테스트"""
    print("=" * 80)
    print("[기본 로깅 테스트]")
    print("=" * 80)

    logger = get_logger(__name__)

    print("\n[다양한 로그 레벨 테스트]")
    logger.debug("DEBUG 레벨 메시지 (개발 환경에서만 출력)")
    logger.info("INFO 레벨 메시지 (일반 정보)")
    logger.warning("WARNING 레벨 메시지 (경고)")
    logger.error("ERROR 레벨 메시지 (오류)")
    logger.critical("CRITICAL 레벨 메시지 (치명적 오류)")


def test_multiple_loggers():
    """여러 로거 생성 테스트 (싱글톤)"""
    print("\n" + "=" * 80)
    print("[여러 로거 생성 테스트]")
    print("=" * 80)

    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    logger3 = get_logger("module1")  # 재사용 (싱글톤)

    print(f"\nlogger1 ID: {id(logger1)}")
    print(f"logger2 ID: {id(logger2)}")
    print(f"logger3 ID: {id(logger3)} (logger1과 동일해야 함)")

    assert logger1 is logger3, "싱글톤 패턴 실패!"
    print("\n[성공] 싱글톤 패턴 정상 작동")

    logger1.info("module1에서 로그 출력")
    logger2.info("module2에서 로그 출력")


def test_exception_logging():
    """예외 로깅 테스트 (스택 트레이스)"""
    print("\n" + "=" * 80)
    print("[예외 로깅 테스트]")
    print("=" * 80)

    logger = get_logger(__name__)

    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("0으로 나누기 오류 발생", exc_info=True)
        print("\n[성공] 스택 트레이스 포함 로그 출력")


def test_dynamic_log_level():
    """동적 로그 레벨 변경 테스트"""
    print("\n" + "=" * 80)
    print("[동적 로그 레벨 변경 테스트]")
    print("=" * 80)

    logger = get_logger("test_dynamic", level="INFO")

    print("\n[1단계] INFO 레벨 설정")
    logger.debug("DEBUG 메시지 (출력 안 됨)")
    logger.info("INFO 메시지 (출력됨)")

    print("\n[2단계] DEBUG 레벨로 변경")
    set_log_level("test_dynamic", "DEBUG")
    logger.debug("DEBUG 메시지 (이제 출력됨)")
    logger.info("INFO 메시지 (출력됨)")

    print("\n[3단계] ERROR 레벨로 변경")
    set_log_level("test_dynamic", "ERROR")
    logger.info("INFO 메시지 (출력 안 됨)")
    logger.error("ERROR 메시지 (출력됨)")


def test_active_loggers():
    """활성 로거 목록 조회 테스트"""
    print("\n" + "=" * 80)
    print("[활성 로거 목록 조회 테스트]")
    print("=" * 80)

    # 여러 로거 생성
    get_logger("app.routers.chat")
    get_logger("app.services.llm_service")
    get_logger("app.database")

    active_loggers = get_active_loggers()
    print(f"\n[활성 로거 목록] ({len(active_loggers)}개)")
    for logger_name in sorted(active_loggers):
        print(f"  - {logger_name}")


def test_custom_logger_name():
    """커스텀 로거 이름 테스트"""
    print("\n" + "=" * 80)
    print("[커스텀 로거 이름 테스트]")
    print("=" * 80)

    logger_custom = get_logger("my_custom_module")
    logger_auto = get_logger(__name__)

    print(f"\n커스텀 로거 이름: {logger_custom.name}")
    print(f"자동 로거 이름: {logger_auto.name}")

    logger_custom.info("커스텀 이름 로거에서 출력")
    logger_auto.info("자동 이름 로거에서 출력")


def test_performance():
    """로깅 성능 테스트"""
    print("\n" + "=" * 80)
    print("[로깅 성능 테스트]")
    print("=" * 80)

    import time

    logger = get_logger(__name__)

    # 1000개 로그 출력 시간 측정
    start = time.time()
    for i in range(1000):
        logger.info(f"성능 테스트 로그 {i}")
    elapsed = time.time() - start

    print(f"\n[결과] 1000개 로그 출력 시간: {elapsed:.3f}초")
    print(f"평균 로그 출력 시간: {elapsed / 1000 * 1000:.3f}ms")


def test_log_formats():
    """로그 포맷 테스트"""
    print("\n" + "=" * 80)
    print("[로그 포맷 테스트]")
    print("=" * 80)

    logger = get_logger(__name__)

    print("\n[기본 메시지]")
    logger.info("간단한 메시지")

    print("\n[변수 포함]")
    user_id = "user123"
    action = "로그인"
    logger.info(f"사용자 작업 - ID: {user_id}, 작업: {action}")

    print("\n[긴 메시지]")
    long_message = "이것은 매우 긴 메시지입니다. " * 10
    logger.info(long_message)


def main():
    """메인 테스트 실행"""
    print("\n")
    print("###############################################################################")
    print("#                                                                             #")
    print("#                      Logger Utility Test Suite                             #")
    print("#                                                                             #")
    print("###############################################################################")
    print("\n")

    try:
        # 1. 기본 로깅 테스트
        test_basic_logging()

        # 2. 여러 로거 생성 테스트
        test_multiple_loggers()

        # 3. 예외 로깅 테스트
        test_exception_logging()

        # 4. 동적 로그 레벨 변경 테스트
        test_dynamic_log_level()

        # 5. 활성 로거 목록 조회 테스트
        test_active_loggers()

        # 6. 커스텀 로거 이름 테스트
        test_custom_logger_name()

        # 7. 로그 포맷 테스트
        test_log_formats()

        # 8. 성능 테스트
        test_performance()

        print("\n" + "=" * 80)
        print("[테스트 완료]")
        print("=" * 80)

        print("\n[확인 사항]")
        print("1. logs/app.log 파일이 생성되었는지 확인")
        print("2. 로그가 콘솔과 파일에 모두 출력되었는지 확인")
        print("3. 로그 포맷이 올바른지 확인")
        print("4. 싱글톤 패턴이 정상 작동했는지 확인")
        print("\n")

    except Exception as e:
        print(f"\n[에러] 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
