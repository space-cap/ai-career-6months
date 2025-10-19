"""
init_db.py
------------------------------------------
AI Career 6 Months 프로젝트용 DB 초기화 스크립트

✅ 기능:
  - DATABASE_URL(.env 또는 Render 환경변수) 자동 로드
  - SQLAlchemy Base 모델 기반 테이블 자동 생성
  - 로컬(SQLite) 또는 Render/Neon(PostgreSQL) 모두 지원
  - 현재 연결된 DB URL과 테이블 목록 출력

실행:
  poetry run python -m app.init_db
------------------------------------------
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base

# ✅ 모델을 명시적으로 import해야 SQLAlchemy가 테이블 구조를 인식합니다
from app.models.conversation_log import ConversationLog  # noqa: F401
from app.models.feedback_log import FeedbackLog  # noqa: F401

# ------------------------------------------
# 1️⃣ 환경 변수 로드 (.env.local 또는 .env.prod)
# ------------------------------------------
from dotenv import load_dotenv

# 우선순위: .env.prod → .env.local
if os.path.exists(".env.prod"):
    load_dotenv(".env.prod")
elif os.path.exists(".env.local"):
    load_dotenv(".env.local")

# ------------------------------------------
# 2️⃣ DATABASE_URL 가져오기
# ------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL이 설정되어 있지 않습니다.")
    print("👉 .env.local 또는 .env.prod 파일을 확인하세요.")
    sys.exit(1)

print(f"🔗 Connecting to database: {DATABASE_URL}")

# ------------------------------------------
# 3️⃣ DB 엔진 생성
# ------------------------------------------
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"❌ 데이터베이스 엔진 생성 실패: {e}")
    sys.exit(1)

# ------------------------------------------
# 4️⃣ 테이블 생성
# ------------------------------------------
try:
    Base.metadata.create_all(bind=engine)
    print("✅ 모든 테이블이 성공적으로 생성되었습니다.")
except SQLAlchemyError as e:
    print(f"❌ 테이블 생성 중 오류 발생: {e}")
    sys.exit(1)

# ------------------------------------------
# 5️⃣ 생성된 테이블 목록 출력
# ------------------------------------------
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if tables:
        print("📋 생성된 테이블 목록:")
        for t in tables:
            print(f"   • {t}")
    else:
        print("⚠️ 생성된 테이블이 없습니다.")
except Exception as e:
    print(f"⚠️ 테이블 확인 중 오류: {e}")

print("🎉 DB 초기화가 완료되었습니다.")
