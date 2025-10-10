import os
import shutil
from app.services.vectorstore import get_vectorstore
from app.core.config import settings

CHROMA_PATH = settings.CHROMA_PATH
DOCS_PATH = "docs"


def reset_chroma():
    """기존 Chroma DB 삭제"""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        return f"🧹 기존 Chroma DB 초기화 완료: {CHROMA_PATH}"
    return "ℹ️ 초기화할 Chroma DB가 없습니다."


def ingest_documents(reset: bool = False):
    """문서 임베딩 + 상태 리턴"""
    log_messages = []

    if reset:
        msg = reset_chroma()
        log_messages.append(msg)

    if not os.path.exists(DOCS_PATH):
        return {"status": "error", "message": f"{DOCS_PATH}/ 폴더가 없습니다."}

    txt_files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".txt")]
    if not txt_files:
        return {"status": "warning", "message": f"{DOCS_PATH}/ 폴더에 .txt 파일이 없습니다."}

    store = get_vectorstore()
    log_messages.append(f"📂 총 {len(txt_files)}개 문서를 임베딩 중...")

    for idx, file_name in enumerate(txt_files, 1):
        file_path = os.path.join(DOCS_PATH, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        try:
            store.add_texts([text], metadatas=[{"source": file_name}])
            log_messages.append(f"[{idx}] ✅ {file_name} 임베딩 완료")
        except Exception as e:
            log_messages.append(f"[{idx}] ⚠️ {file_name} 처리 중 오류: {e}")

    log_messages.append(f"📁 저장 완료: {CHROMA_PATH}")

    # 임베딩 후 벡터 개수 리턴
    try:
        count = len(store.get()["ids"])
    except Exception:
        count = "알 수 없음"

    return {
        "status": "success",
        "message": "문서 임베딩 완료",
        "vector_count": count,
        "log": log_messages,
    }
