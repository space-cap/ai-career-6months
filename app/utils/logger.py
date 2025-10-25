# app/utils/logger.py
"""
중앙 로깅 유틸리티

프로젝트 전체에서 사용하는 통합 로거 설정 및 관리
- 환경별 로그 레벨 자동 설정 (개발/프로덕션)
- 파일 회전 (RotatingFileHandler)
- 콘솔 + 파일 동시 출력
- 멀티프로세스 안전 (싱글톤 패턴)
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings

# 프로젝트 루트 디렉토리 (app/utils/logger.py -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 로그 디렉토리 설정
LOG_DIR = Path(settings.LOG_DIR)
if not LOG_DIR.is_absolute():
    LOG_DIR = PROJECT_ROOT / LOG_DIR

# 로그 디렉토리 생성 (권한 에러 처리)
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError as e:
    print(f"[WARNING] 로그 디렉토리 생성 실패: {LOG_DIR} - {e}", file=sys.stderr)
    print("[WARNING] 콘솔 로그만 사용합니다.", file=sys.stderr)
    LOG_DIR = None

# 로그 레벨 매핑
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 싱글톤 로거 저장소
_loggers: dict[str, logging.Logger] = {}
_configured = False


def _configure_root_logger():
    """
    루트 로거 및 외부 라이브러리 로거 설정 (모듈 로드 시 1회만 실행)
    """
    global _configured
    if _configured:
        return

    # 외부 라이브러리 로그 레벨 조정 (noisy 라이브러리)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    _configured = True


def get_logger(
    name: Optional[str] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    중앙 로거 반환 (싱글톤 패턴)

    Args:
        name: 로거 이름 (기본값: "ai_career_app")
        level: 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
               None이면 settings.LOG_LEVEL 또는 ENV에 따라 자동 설정

    Returns:
        logging.Logger: 설정된 로거 인스턴스

    Features:
        - 파일: logs/app.log (회전: 10MB, 백업 5개)
        - 콘솔: StreamHandler (색상 포함 가능)
        - 환경별 자동 로그 레벨:
          * development: DEBUG
          * production: INFO

    Example:
        >>> from app.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("서버 시작")
        >>> logger.error("오류 발생", exc_info=True)
    """
    # 루트 로거 설정 (1회만)
    _configure_root_logger()

    # 로거 이름 결정
    logger_name = name or "ai_career_app"

    # 이미 생성된 로거가 있으면 재사용 (싱글톤)
    if logger_name in _loggers:
        return _loggers[logger_name]

    # 새 로거 생성
    logger = logging.getLogger(logger_name)

    # 로그 레벨 결정
    if level is None:
        # 환경변수 우선, 없으면 ENV에 따라 자동 설정
        level_str = settings.LOG_LEVEL.upper()
        if level_str not in LOG_LEVEL_MAP:
            # ENV 기반 폴백
            level_str = "DEBUG" if settings.ENV == "development" else "INFO"
    else:
        level_str = level.upper()

    log_level = LOG_LEVEL_MAP.get(level_str, logging.INFO)
    logger.setLevel(log_level)

    # 이미 핸들러가 있으면 추가하지 않음 (중복 방지)
    if logger.handlers:
        _loggers[logger_name] = logger
        return logger

    # 포맷터 설정
    formatter = _create_formatter(settings.ENV)

    # 1. 파일 핸들러 추가 (로그 디렉토리 생성 성공 시)
    if LOG_DIR is not None:
        try:
            file_handler = _create_file_handler(LOG_DIR, log_level, formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(
                f"[WARNING] 파일 핸들러 생성 실패: {e}",
                file=sys.stderr,
            )

    # 2. 콘솔 핸들러 추가
    console_handler = _create_console_handler(log_level, formatter)
    logger.addHandler(console_handler)

    # 로거 캐싱
    _loggers[logger_name] = logger

    return logger


def _create_formatter(env: str) -> logging.Formatter:
    """
    환경에 따른 로그 포맷터 생성

    Args:
        env: 환경 ("development" | "production")

    Returns:
        logging.Formatter: 포맷터 인스턴스
    """
    if env == "development":
        # 개발 환경: 상세 정보 (파일명, 함수명, 라인 번호)
        fmt = (
            "%(asctime)s [%(levelname)8s] %(name)s - "
            "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
        )
    else:
        # 프로덕션: 간결한 포맷
        fmt = "%(asctime)s [%(levelname)8s] %(name)s - %(message)s"

    return logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")


def _create_file_handler(
    log_dir: Path,
    level: int,
    formatter: logging.Formatter,
) -> RotatingFileHandler:
    """
    파일 핸들러 생성 (로그 회전 포함)

    Args:
        log_dir: 로그 디렉토리 경로
        level: 로그 레벨
        formatter: 포맷터

    Returns:
        RotatingFileHandler: 파일 핸들러
    """
    log_file = log_dir / "app.log"

    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    return file_handler


def _create_console_handler(
    level: int,
    formatter: logging.Formatter,
) -> logging.StreamHandler:
    """
    콘솔 핸들러 생성

    Args:
        level: 로그 레벨
        formatter: 포맷터

    Returns:
        logging.StreamHandler: 콘솔 핸들러
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    return console_handler


def set_log_level(logger_name: str, level: str):
    """
    특정 로거의 로그 레벨 동적 변경

    Args:
        logger_name: 로거 이름
        level: 새 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    Example:
        >>> set_log_level("ai_career_app", "DEBUG")
    """
    if logger_name not in _loggers:
        raise ValueError(f"로거 '{logger_name}'가 존재하지 않습니다.")

    level_int = LOG_LEVEL_MAP.get(level.upper())
    if level_int is None:
        raise ValueError(
            f"유효하지 않은 로그 레벨: {level}. "
            f"사용 가능: {', '.join(LOG_LEVEL_MAP.keys())}"
        )

    logger = _loggers[logger_name]
    logger.setLevel(level_int)

    # 모든 핸들러 레벨도 변경
    for handler in logger.handlers:
        handler.setLevel(level_int)


def get_active_loggers() -> list[str]:
    """
    현재 활성화된 로거 이름 목록 반환

    Returns:
        list[str]: 로거 이름 리스트

    Example:
        >>> get_active_loggers()
        ['ai_career_app', 'app.routers.chat', 'app.services.llm_service']
    """
    return list(_loggers.keys())
