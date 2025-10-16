"""
deploy_check.py
-----------------
Render 배포 전 필수 점검 스크립트.
✅ DB 연결 / OpenAI Key / Chroma 경로 / 환경 설정 등을 자동 검증합니다.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

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
CHROMA_PATH = os.getenv("CHROMA_PATH")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY 누락됨")
else:
    print("✅ OPENAI_API_KEY 존재함")

if not DATABASE_URL:
    print("❌ DATABASE_URL 누락됨")
    sys.exit(1)
else:
    print("✅ DATABASE_URL 확인됨")

# -------------------------------
# 3️⃣ DB 연결 테스트 (Neon PostgreSQL)
# -------------------------------
print("\n🔗 PostgreSQL 연결 테스트 중...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    now = cur.fetchone()[0]
    print(f"✅ DB 연결 성공 (서버 시간: {now})")
    cur.close()
    conn.close()
except Exception as e:
    print("❌ DB 연결 실패:")
    print(e)
    sys.exit(1)

# -------------------------------
# 4️⃣ OpenAI Key 테스트
# -------------------------------
print("\n🤖 OpenAI Key 테스트 중...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.models.list()
    model_count = len(response.data)
    print(f"✅ OpenAI Key 유효함 (모델 {model_count}개 확인)")
except Exception as e:
    print("❌ OpenAI API 테스트 실패:")
    print(e)
    sys.exit(1)

# -------------------------------
# 5️⃣ Chroma 경로 점검
# -------------------------------
print("\n🧠 Chroma 벡터스토어 경로 점검 중...")
if CHROMA_PATH:
    path = Path(CHROMA_PATH)
    if not path.exists():
        print(f"⚠️ Chroma 폴더가 존재하지 않아 새로 생성함: {path}")
        path.mkdir(parents=True, exist_ok=True)
    else:
        print(f"✅ Chroma 폴더 존재: {path.resolve()}")
else:
    print("⚠️ CHROMA_PATH 설정 없음 (환경파일 확인 필요)")

print("\n🎯 모든 점검 완료 — Ready for Deploy 🚀")
