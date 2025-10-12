<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 플래시 카드 생성

방금 작성한 SQLAlchemy 테이블 스키마 변경 가이드 내용을 바탕으로 플래시 카드를 생성하겠습니다.[^1][^2][^3]

***

## 플래시 카드 세트: SQLAlchemy \& Alembic 마이그레이션

### 카드 1

**Q:** SQLAlchemy에서 모델 클래스를 수정하면 데이터베이스 테이블이 자동으로 변경되나요?

**A:** 아니요. `Base.metadata.create_all()`은 존재하지 않는 테이블만 생성하며, 이미 존재하는 테이블은 수정하지 않습니다. 스키마 변경은 Alembic 같은 마이그레이션 도구가 필요합니다.[^2][^4]

***

### 카드 2

**Q:** Alembic을 프로젝트에 설치하고 초기화하는 명령어는?

**A:**

```bash
# 설치
pip install alembic
# 또는
poetry add alembic

# 초기화
alembic init alembic
```


***

### 카드 3

**Q:** `alembic.ini` 파일에서 MySQL 데이터베이스 연결을 설정하는 방법은?

**A:**

```ini
sqlalchemy.url = mysql+pymysql://사용자명:비밀번호@호스트:포트/DB명
```

예시: `mysql+pymysql://root:password@localhost:3306/mydb`[^5][^2]

***

### 카드 4

**Q:** `alembic/env.py`에서 모델 메타데이터를 연결하려면 어떻게 해야 하나요?

**A:**

```python
from app.database import Base
from app.models import ConversationLog  # 모든 모델 import

target_metadata = Base.metadata
```

모든 모델을 명시적으로 import해야 autogenerate가 인식합니다.[^6][^7]

***

### 카드 5

**Q:** 모델 변경사항을 자동으로 감지하여 마이그레이션 파일을 생성하는 명령어는?

**A:**

```bash
alembic revision --autogenerate -m "변경 설명"
```

예시: `alembic revision --autogenerate -m "Add sentiment column"`[^7][^1]

***

### 카드 6

**Q:** 생성된 마이그레이션을 데이터베이스에 적용하는 명령어는?

**A:**

```bash
alembic upgrade head
```

`head`는 최신 버전까지 업그레이드한다는 의미입니다.[^2][^1]

***

### 카드 7

**Q:** 마이그레이션 파일의 `upgrade()`와 `downgrade()` 함수의 역할은?

**A:**

- `upgrade()`: 스키마를 최신 버전으로 업그레이드할 때 실행되는 SQL 명령
- `downgrade()`: 이전 버전으로 롤백할 때 실행되는 SQL 명령[^1]

***

### 카드 8

**Q:** 현재 데이터베이스의 마이그레이션 버전을 확인하는 명령어는?

**A:**

```bash
alembic current
```


***

### 카드 9

**Q:** 모든 마이그레이션 이력을 확인하는 명령어는?

**A:**

```bash
alembic history
```


***

### 카드 10

**Q:** 마이그레이션을 한 단계 롤백하는 명령어는?

**A:**

```bash
alembic downgrade -1
```

모든 마이그레이션 취소: `alembic downgrade base`[^1]

***

### 카드 11

**Q:** Alembic autogenerate가 변경사항을 감지하지 못하는 주요 원인은?

**A:**

1. `alembic/env.py`에서 모델을 import하지 않음
2. `target_metadata` 설정이 잘못됨
3. 자동 감지가 지원하지 않는 변경 유형 (테이블명 변경 등)[^6][^7]

***

### 카드 12

**Q:** 프로덕션 환경에서 마이그레이션 적용 전 반드시 해야 할 작업은?

**A:**

1. 데이터베이스 백업
2. 개발/테스트 환경에서 먼저 테스트
3. 생성된 마이그레이션 파일 검토
4. 팀원과 마이그레이션 파일 공유 (Git)[^2][^1]

***

### 카드 13

**Q:** SQLAlchemy 컬럼 추가 예시 코드는?

**A:**

```python
from sqlalchemy import Column, String

class ConversationLog(Base):
    __tablename__ = "conversation_log"
    
    # 기존 컬럼...
    sentiment = Column(String(20), nullable=True)  # 새 컬럼
    topic = Column(String(100), nullable=True)     # 새 컬럼
```


***

### 카드 14

**Q:** `alembic init alembic` 명령어 실행 시 생성되는 주요 파일/폴더는?

**A:**

- `alembic/versions/`: 마이그레이션 파일 저장 폴더
- `alembic/env.py`: Alembic 환경 설정
- `alembic.ini`: Alembic 메인 설정 파일[^4][^1]

***

### 카드 15

**Q:** pyproject.toml 환경에서 Alembic과 pymysql을 Poetry로 설치하는 명령어는?

**A:**

```bash
poetry add alembic pymysql
```


***

이 플래시 카드들을 Anki나 Quizlet 같은 플래시 카드 앱에 입력하여 학습할 수 있습니다.[^3][^2][^1]
<span style="display:none">[^8]</span>

<div align="center">⁂</div>

[^1]: https://thinhdanggroup.github.io/alembic-python/

[^2]: https://dev.to/surajbhattarai/mastering-sqlalchemy-migrations-a-comprehensive-guide-2fo0

[^3]: https://testdriven.io/blog/alembic-database-migrations/

[^4]: https://www.kubeblogs.com/build-databases-with-sqlalchemy-and-alembic/

[^5]: https://develop-davi-kr.tistory.com/entry/파이썬-각종-db-연결sqlalchemy-pymysql

[^6]: https://stackoverflow.com/questions/16076480/alembic-env-py-target-metadata-metadata-no-module-name-al-test-models

[^7]: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

[^8]: https://adex.ltd/database-migrations-with-alembic-and-fastapi-a-comprehensive-guide-using-poetry

