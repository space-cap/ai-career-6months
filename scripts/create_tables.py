"""
데이터베이스 테이블 생성 스크립트
실행: poetry run python scripts/create_tables.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine
from app.models.conversation_log import ConversationLog  # noqa: F401

if __name__ == "__main__":
    print("🔨 데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료!")
    print(f"✅ 생성된 테이블: {list(Base.metadata.tables.keys())}")
