from fastapi import APIRouter, Query
from app.services.ingest_service import ingest_documents

router = APIRouter()


@router.post("/ingest")
async def ingest_docs(reset: bool = Query(False, description="기존 Chroma DB 초기화 여부")):
    """
    docs 폴더의 모든 .txt 문서를 Chroma에 임베딩합니다.
    reset=true 시 기존 DB를 삭제 후 새로 임베딩합니다.
    """
    result = ingest_documents(reset=reset)
    return result
