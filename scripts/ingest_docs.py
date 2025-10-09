"""
자동 문서 임베딩 스크립트
-------------------------
docs/ 폴더 아래의 모든 .txt 파일을 읽어서
Chroma VectorStore에 임베딩(embedding) 후 저장합니다.

실행 명령:
    poetry run python scripts/ingest_docs.py
"""

import os
from app.services.vectorstore import get_vectorstore
from app.core.config import settings


def ingest_docs():
    docs_path = "docs"
    store = get_vectorstore()

    # .txt 파일만 추출
    txt_files = [f for f in os.listdir(docs_path) if f.endswith(".txt")]

    if not txt_files:
        print("❌ docs 폴더에 .txt 파일이 없습니다.")
        return

    print(f"📂 {len(txt_files)}개 문서를 Chroma에 임베딩합니다...\n")

    for file_name in txt_files:
        file_path = os.path.join(docs_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"→ 임베딩 중: {file_name}")

        try:
            # 벡터스토어에 추가
            store.add_texts([text], metadatas=[{"source": file_name}])
        except Exception as e:
            print(f"⚠️ {file_name} 처리 중 오류 발생: {e}")

    # DB 저장
    store.persist()
    print("\n✅ 모든 문서 임베딩 완료!")
    print(f"📁 Chroma 경로: {settings.CHROMA_PATH}")


if __name__ == "__main__":
    ingest_docs()
