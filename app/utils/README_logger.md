# Logging Utility Documentation

중앙 로깅 유틸리티 - 프로젝트 전체 로그 관리

## 개요

`app/utils/logger.py`는 프로젝트 전체에서 사용하는 통합 로거를 제공합니다.

### 주요 특징

- ✅ **환경별 자동 설정**: development = DEBUG, production = INFO
- ✅ **파일 회전**: 10MB 크기, 5개 백업 파일 자동 관리
- ✅ **콘솔 + 파일 동시 출력**: 개발 시 편리한 디버깅
- ✅ **싱글톤 패턴**: 동일 이름 로거 재사용으로 성능 최적화
- ✅ **에러 핸들링**: 로그 디렉토리 권한 오류 시 콘솔 전용 모드
- ✅ **타입 힌트**: 완전한 타입 안전성
- ✅ **외부 라이브러리 로그 억제**: SQLAlchemy, urllib3 등 noisy 로그 자동 필터링

## 설치 및 설정

### 1. 환경변수 설정 (.env)

```bash
# 환경 구분
ENV=development  # development | production

# 로그 설정
LOG_LEVEL=INFO   # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_DIR=./logs   # 로그 디렉토리 (상대/절대 경로)
LOG_RETENTION_DAYS=30
```

### 2. 로그 디렉토리

- 기본값: `./logs` (프로젝트 루트)
- 자동 생성: 디렉토리가 없으면 자동 생성
- 권한 오류: 생성 실패 시 콘솔 로그만 사용 (경고 메시지 출력)

## 사용법

### 기본 사용

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("치명적 오류")
```

### 모듈별 로거 생성

```python
# app/routers/chat.py
from app.utils.logger import get_logger

logger = get_logger(__name__)  # 로거 이름: "app.routers.chat"

@router.post("/api/chat")
async def chat(question: str):
    logger.info(f"채팅 요청: {question}")
    # ...
```

### 예외 로깅 (스택 트레이스 포함)

```python
logger = get_logger(__name__)

try:
    result = some_function()
except Exception as e:
    logger.error("함수 실행 실패", exc_info=True)  # 스택 트레이스 포함
    # 또는
    logger.exception("함수 실행 실패")  # exc_info=True와 동일
```

### 커스텀 로그 레벨 지정

```python
from app.utils.logger import get_logger

# 특정 모듈만 DEBUG 레벨로 설정
logger = get_logger(__name__, level="DEBUG")

logger.debug("상세 디버그 정보")
```

### 동적 로그 레벨 변경

```python
from app.utils.logger import get_logger, set_log_level

logger = get_logger("my_module")

# 런타임에 로그 레벨 변경
set_log_level("my_module", "DEBUG")
logger.debug("이제 디버그 로그가 출력됩니다")

set_log_level("my_module", "ERROR")
logger.info("이 메시지는 출력되지 않습니다")
```

### 활성화된 로거 목록 조회

```python
from app.utils.logger import get_active_loggers

loggers = get_active_loggers()
print(f"활성 로거: {loggers}")
# 출력: ['ai_career_app', 'app.routers.chat', 'app.services.llm_service']
```

## 로그 포맷

### Development 환경 (ENV=development)

```
2025-01-23 14:30:45 [    INFO] app.routers.chat - chat.py:42 - handle_chat() - 채팅 요청 처리 시작
```

**포함 정보:**
- 타임스탬프
- 로그 레벨 (8자리 정렬)
- 로거 이름
- 파일명:라인번호
- 함수명
- 메시지

### Production 환경 (ENV=production)

```
2025-01-23 14:30:45 [    INFO] app.routers.chat - 채팅 요청 처리 시작
```

**포함 정보:**
- 타임스탬프
- 로그 레벨
- 로거 이름
- 메시지

## 로그 파일 관리

### 파일 위치

```
프로젝트루트/
├── logs/
│   ├── app.log          # 현재 로그 파일
│   ├── app.log.1        # 백업 1 (가장 최근)
│   ├── app.log.2        # 백업 2
│   ├── app.log.3        # 백업 3
│   ├── app.log.4        # 백업 4
│   └── app.log.5        # 백업 5 (가장 오래됨)
```

### 회전 정책

- **크기 기준**: 파일이 10MB에 도달하면 자동 회전
- **백업 개수**: 최대 5개 백업 파일 유지
- **인코딩**: UTF-8 (한글 완벽 지원)

### 로그 파일 삭제

로그 파일은 자동 회전되므로 수동 삭제 불필요. 필요시:

```bash
# 모든 로그 파일 삭제
rm -rf logs/*.log*

# 30일 이상 된 로그만 삭제 (Linux/macOS)
find logs -name "*.log*" -mtime +30 -delete
```

## 환경별 설정

### Development 환경

```bash
# .env
ENV=development
LOG_LEVEL=DEBUG
LOG_DIR=./logs
```

**특징:**
- 로그 레벨: DEBUG (모든 로그 출력)
- 상세 포맷: 파일명, 함수명, 라인 번호 포함
- 콘솔 + 파일 동시 출력

### Production 환경

```bash
# .env
ENV=production
LOG_LEVEL=INFO
LOG_DIR=/var/log/ai-career-6months
```

**특징:**
- 로그 레벨: INFO (중요 정보만 출력)
- 간결 포맷: 타임스탬프, 레벨, 메시지만 출력
- 파일 중심 로깅

## 외부 라이브러리 로그 필터링

다음 라이브러리의 로그는 자동으로 WARNING 레벨로 조정됩니다:

- `sqlalchemy.engine` (SQL 쿼리 로그)
- `urllib3` (HTTP 요청 로그)
- `httpx` (HTTP 클라이언트 로그)
- `openai` (OpenAI API 로그)
- `chromadb` (Chroma VectorDB 로그)

### 추가 필터링

```python
import logging

# 특정 라이브러리 로그 완전 억제
logging.getLogger("noisy_library").setLevel(logging.CRITICAL)
```

## 고급 사용법

### 1. 컨텍스트 정보 추가 (LoggerAdapter)

```python
import logging
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 사용자 정보를 모든 로그에 자동 추가
logger_with_context = logging.LoggerAdapter(
    logger,
    {'user_id': 'user123', 'session_id': 'abc456'}
)

logger_with_context.info("사용자 요청 처리")
# 출력: ... - 사용자 요청 처리 {'user_id': 'user123', 'session_id': 'abc456'}
```

### 2. 성능 측정 로깅

```python
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

def slow_function():
    start = time.time()
    logger.debug("함수 실행 시작")

    # ... 작업 수행 ...

    elapsed = time.time() - start
    logger.info(f"함수 실행 완료 (소요 시간: {elapsed:.2f}초)")
```

### 3. 조건부 로깅 (디버그 모드)

```python
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

if settings.ENV == "development":
    logger.debug(f"디버그 정보: {complex_data}")
```

## 통합 예시

### FastAPI 라우터에서 사용

```python
from fastapi import APIRouter, HTTPException
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/api/chat")
async def chat(question: str, user_id: str):
    logger.info(f"채팅 요청 - 사용자: {user_id}, 질문: {question[:50]}...")

    try:
        answer = await generate_answer(question)
        logger.info(f"응답 생성 완료 - 길이: {len(answer)}자")
        return {"answer": answer}

    except Exception as e:
        logger.error(f"채팅 처리 실패 - 사용자: {user_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 오류")
```

### 데이터베이스 작업 로깅

```python
from sqlalchemy.orm import Session
from app.utils.logger import get_logger

logger = get_logger(__name__)

def save_conversation(db: Session, question: str, answer: str):
    logger.debug(f"대화 저장 시작 - 질문 길이: {len(question)}")

    try:
        conversation = ConversationLog(question=question, answer=answer)
        db.add(conversation)
        db.commit()

        logger.info(f"대화 저장 완료 - ID: {conversation.id}")
        return conversation

    except Exception as e:
        logger.error("대화 저장 실패", exc_info=True)
        db.rollback()
        raise
```

### 백그라운드 작업 로깅

```python
import schedule
from app.utils.logger import get_logger

logger = get_logger(__name__)

def backup_database():
    logger.info("데이터베이스 백업 시작")

    try:
        # 백업 로직
        result = perform_backup()
        logger.info(f"백업 완료 - 파일: {result['path']}, 크기: {result['size']}MB")

    except Exception as e:
        logger.critical("백업 실패", exc_info=True)
        # Slack 알림 등

schedule.every().day.at("02:00").do(backup_database)
```

## 트러블슈팅

### 문제 1: 로그가 출력되지 않음

**원인**: 로그 레벨이 너무 높게 설정됨

**해결**:
```bash
# .env에서 LOG_LEVEL 확인
LOG_LEVEL=DEBUG
```

### 문제 2: 로그 파일이 생성되지 않음

**원인**: 디렉토리 권한 없음

**해결**:
```bash
# 로그 디렉토리 권한 확인
ls -la logs/

# 권한 부여
chmod 755 logs/
```

### 문제 3: 중복 로그 출력

**원인**: 로거가 여러 번 초기화됨

**해결**: 싱글톤 패턴이 적용되어 있으므로 정상적으로 사용하면 중복 없음. 만약 중복 발생 시:
```python
# logger 재사용
logger = get_logger(__name__)  # 캐시된 로거 반환
```

### 문제 4: 외부 라이브러리 로그가 너무 많음

**원인**: 기본 필터링 외 추가 라이브러리

**해결**:
```python
import logging

# 특정 라이브러리 로그 억제
logging.getLogger("noisy_library").setLevel(logging.ERROR)
```

## API Reference

### `get_logger(name, level)`

중앙 로거 반환

**Parameters:**
- `name` (Optional[str]): 로거 이름 (기본값: "ai_career_app")
- `level` (Optional[str]): 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

**Returns:**
- `logging.Logger`: 설정된 로거 인스턴스

### `set_log_level(logger_name, level)`

로거의 로그 레벨 동적 변경

**Parameters:**
- `logger_name` (str): 로거 이름
- `level` (str): 새 로그 레벨

**Raises:**
- `ValueError`: 로거가 존재하지 않거나 유효하지 않은 레벨

### `get_active_loggers()`

활성화된 로거 목록 반환

**Returns:**
- `list[str]`: 로거 이름 리스트

## 모범 사례

### 1. 로거 이름은 `__name__` 사용

```python
# 권장
logger = get_logger(__name__)

# 비권장
logger = get_logger("my_custom_name")
```

### 2. 민감 정보 로깅 금지

```python
# 위험
logger.info(f"사용자 비밀번호: {password}")

# 안전
logger.info(f"사용자 인증 성공 - ID: {user_id}")
```

### 3. 적절한 로그 레벨 사용

- **DEBUG**: 개발 중 상세 정보
- **INFO**: 정상 작동 정보 (사용자 요청, 응답 등)
- **WARNING**: 잠재적 문제 (deprecated 기능 사용 등)
- **ERROR**: 복구 가능한 오류
- **CRITICAL**: 시스템 중단 수준의 치명적 오류

### 4. 예외는 항상 `exc_info=True`와 함께

```python
try:
    risky_operation()
except Exception as e:
    logger.error("작업 실패", exc_info=True)  # 스택 트레이스 포함
```

## 참고 자료

- [Python logging 공식 문서](https://docs.python.org/3/library/logging.html)
- [로깅 모범 사례](https://docs.python-guide.org/writing/logging/)
- [프로젝트 README](../../README.md)
