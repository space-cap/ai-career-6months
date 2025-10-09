"""
자동 문서 임베딩 스크립트 (with --reset)
-----------------------------------------
docs/ 폴더 아래의 모든 .txt 파일을 읽어
Chroma VectorStore에 임베딩(embedding) 후 저장합니다.

기능:
    --reset : 기존 Chroma DB를 완전히 초기화하고 새로 임베딩합니다.

사용 예시:
    poetry run python scripts/ingest_docs.py
    poetry run python scripts/ingest_docs.py --reset
"""

import os
import sys
import shutil
from app.services.vectorstore import get_vectorstore
from app.core.config import settings

CHROMA_PATH = settings.CHROMA_PATH
DOCS_PATH = "docs"


def reset_chroma():
    """기존 Chroma DB를 삭제"""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"🧹 기존 Chroma DB 초기화 완료: {CHROMA_PATH}")
    else:
        print("ℹ️ 초기화할 Chroma DB가 없습니다. (처음 실행일 수 있습니다.)")


def ingest_docs():
    """docs 폴더의 모든 .txt 문서를 Chroma에 임베딩"""
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


def show_help():
    """도움말 출력"""
    print(
        """
🧠 사용법:
    poetry run python scripts/ingest_docs.py         # 문서 임베딩
    poetry run python scripts/ingest_docs.py --reset # 기존 DB 삭제 후 새로 임베딩

옵션:
    --reset    기존 Chroma DB를 완전히 초기화합니다.
    --help     도움말 보기
"""
    )


if __name__ == "__main__":
    if "--help" in sys.argv:
        show_help()
    elif "--reset" in sys.argv:
        reset_chroma()
        ingest_docs()
    else:
        ingest_docs()
