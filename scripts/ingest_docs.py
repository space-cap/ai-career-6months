"""
문서 자동 임베딩 & 관리 CLI 유틸 (RAG용)
-----------------------------------------
docs/ 폴더의 텍스트 문서를 읽어 Chroma DB에 임베딩하거나,
DB를 초기화(--reset), 개수 확인(--count)할 수 있습니다.

실행 예시:
    poetry run python scripts/ingest_docs.py
    poetry run python scripts/ingest_docs.py --reset
    poetry run python scripts/ingest_docs.py --count
"""

import os
import sys
import shutil
import requests
from app.services.vectorstore import get_vectorstore
from app.core.config import settings

CHROMA_PATH = settings.CHROMA_PATH
DOCS_PATH = "docs"
API_URL = "http://127.0.0.1:8000/api/vector-count"


def reset_chroma():
    """기존 Chroma DB 삭제"""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"🧹 기존 Chroma DB 초기화 완료: {CHROMA_PATH}")
    else:
        print("ℹ️ 초기화할 Chroma DB가 없습니다. (처음 실행일 수 있습니다.)")


def ingest_docs():
    """docs 폴더 내 모든 .txt 파일을 Chroma에 임베딩"""
    if not os.path.exists(DOCS_PATH):
        print(f"❌ {DOCS_PATH}/ 폴더가 없습니다. 먼저 생성해주세요.")
        return

    txt_files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".txt")]
    if not txt_files:
        print(f"⚠️ {DOCS_PATH}/ 폴더에 .txt 문서가 없습니다.")
        return

    store = get_vectorstore()
    print(f"\n📂 총 {len(txt_files)}개 문서를 Chroma에 임베딩합니다...\n")

    for idx, file_name in enumerate(txt_files, 1):
        file_path = os.path.join(DOCS_PATH, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"[{idx}/{len(txt_files)}] → 임베딩 중: {file_name}")
        try:
            store.add_texts([text], metadatas=[{"source": file_name}])
        except Exception as e:
            print(f"⚠️ {file_name} 처리 중 오류 발생: {e}")

    print("\n✅ 모든 문서 임베딩 완료!")
    print(f"📁 Chroma 경로: {CHROMA_PATH}")


def verify_vector_count():
    """FastAPI 서버의 /api/vector-count 엔드포인트 호출"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get("vector_count", "알 수 없음")
            print(f"\n🧩 현재 Chroma DB 벡터 개수: {count}")
        else:
            print(f"⚠️ 요청 실패: 상태코드 {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("\n⚠️ FastAPI 서버가 실행 중인지 확인해주세요.")
        print("   서버 실행 명령: poetry run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"⚠️ 검증 중 오류 발생: {e}")


def show_help():
    """도움말 출력"""
    print(
        """
🧠 사용법:
    poetry run python scripts/ingest_docs.py         # 문서 임베딩
    poetry run python scripts/ingest_docs.py --reset # 기존 DB 삭제 후 새로 임베딩
    poetry run python scripts/ingest_docs.py --count # 벡터 개수만 확인

옵션:
    --reset    기존 Chroma DB를 완전히 초기화합니다.
    --count    DB를 건드리지 않고 벡터 개수만 출력합니다.
    --help     도움말 보기

📘 참고:
    FastAPI 서버가 실행 중이어야 /api/vector-count 검증이 가능합니다.
"""
    )


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        ingest_docs()
        verify_vector_count()
    elif "--help" in args:
        show_help()
    elif "--reset" in args:
        reset_chroma()
        ingest_docs()
        verify_vector_count()
    elif "--count" in args:
        verify_vector_count()
    else:
        print(f"⚠️ 알 수 없는 옵션: {' '.join(args)}")
        show_help()
