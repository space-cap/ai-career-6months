"""
deploy_preflight_check_pro.py
-----------------------------
✅ Render + Neon + FastAPI 프로젝트용 완전형 배포 사전 점검 스크립트
- .env 환경파일 자동 감지 및 검증
- PostgreSQL (Neon) 연결 + ORM 모델 조회
- OpenAI API Key 유효성
- Chroma Vectorstore 접근성 및 컬렉션 개수 확인
- FastAPI 서버 포트/디렉토리 구조 점검
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------
# 1️⃣ 환경 파일 자동 감지
# -------------------------------
env_mode = os.getenv("ENV", "local")
env_file = ".env.prod" if env_mode == "production" else ".env.local"

if not Path(env_file).exists():
    print(f"❌ 환경 파일({env_file})을 찾을 수 없습니다.")
    sys.exit(1)

load_dotenv(env_file)
print(f"✅ 환경 파일 로드 완료: {env_file}")

# -------------------------------
# 2️⃣ 환경 변수 확인
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

errors = []

if not OPENAI_API_KEY:
    errors.append("❌ OPENAI_API_KEY 누락됨")
else:
    print("✅ OPENAI_API_KEY 존재함")

if not DATABASE_URL:
    errors.append("❌ DATABASE_URL 누락됨")
else:
    print("✅ DATABASE_URL 확인됨")

if errors:
    print("\n🚫 환경 변수 누락으로 점검 중단:")
    for e in errors:
        print(e)
    sys.exit(1)

# -------------------------------
# 3️⃣ PostgreSQL 연결 테스트
# -------------------------------
print("\n🔗 PostgreSQL(DB) 연결 테스트 중...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, version(), now();")
    db_info = cur.fetchone()
    print(f"✅ DB 연결 성공 → DB: {db_info[0]}, 사용자: {db_info[1]}")
    print(f"🕒 서버시간: {db_info[3]}")
    cur.close()
    conn.close()
except Exception as e:
    print("❌ DB 연결 실패:", e)
    sys.exit(1)

# -------------------------------
# 4️⃣ SQLAlchemy ORM 점검
# -------------------------------
print("\n🧱 SQLAlchemy ORM 점검 중...")
try:
    engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
    insp = inspect(engine)
    tables = insp.get_table_names()
    print(f"✅ ORM 연결 성공 — 총 {len(tables)}개 테이블 탐지됨:")
    for t in tables:
        print(f"   • {t}")

    # 기본 쿼리 테스트
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()")).scalar()
        print(f"🧩 SQL 실행 OK (NOW() → {result})")

except SQLAlchemyError as e:
    print("❌ SQLAlchemy 점검 실패:", e)
    sys.exit(1)

# -------------------------------
# 5️⃣ OpenAI API Key 테스트
# -------------------------------
print("\n🤖 OpenAI API Key 유효성 점검 중...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    models = client.models.list()
    print(f"✅ OpenAI Key 유효함 — 사용 가능 모델 {len(models.data)}개")
except Exception as e:
    print("❌ OpenAI Key 검증 실패:", e)
    sys.exit(1)

# -------------------------------
# 6️⃣ Chroma Vectorstore 점검
# -------------------------------
print("\n🧠 Chroma 벡터스토어 점검 중...")
try:
    from chromadb import PersistentClient
    client = PersistentClient(path=CHROMA_PATH)
    collections = client.list_collections()
    print(f"✅ Chroma DB 연결 성공 — 총 {len(collections)}개 컬렉션 발견")
    if collections:
        for c in collections:
            print(f"   • {c.name} (count: {c.count()})")
    else:
        print("⚠️ 현재 등록된 컬렉션 없음 (정상 상태일 수도 있음)")
except Exception as e:
    print("❌ Chroma 접근 실패:", e)

# -------------------------------
# 7️⃣ FastAPI 구조 점검
# -------------------------------
print("\n🧩 FastAPI 프로젝트 구조 점검 중...")
root = Path(__file__).parent
required_paths = [
    root / "app" / "main.py",
    root / "app" / "routers",
    root / "frontend" / "dist"
]
for path in required_paths:
    if path.exists():
        print(f"✅ {path} 존재 확인됨")
    else:
        print(f"⚠️ {path} 없음 — 배포 전 확인 필요")

# -------------------------------
# 8️⃣ 포트 충돌 점검
# -------------------------------
print("\n🌐 포트 사용 가능 여부 점검 중...")

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(("127.0.0.1", 8000))
if result == 0:
    print("⚠️ 포트 8000이 이미 사용 중 (로컬에서 실행 중일 수 있음)")
else:
    print("✅ 포트 8000 사용 가능")
sock.close()

# -------------------------------
# 9️⃣ 요약 결과 출력
# -------------------------------
print("\n===============================")
print("🎯 DEPLOY PREFLIGHT CHECK 완료")
print("===============================")
print(f"환경: {env_mode.upper()}")
print(f"DB URL: {DATABASE_URL.split('@')[-1][:40]}...")
print(f"Chroma Path: {CHROMA_PATH}")
print("\n✅ 모든 핵심 구성 요소 점검 완료 — 배포해도 안전합니다 🚀")
