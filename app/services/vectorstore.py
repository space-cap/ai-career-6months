from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
import os
from functools import lru_cache
from enum import Enum


class EmbeddingModel(str, Enum):
    """OpenAI 임베딩 모델 선택"""
    ADA_002 = "text-embedding-ada-002"  # 가성비 좋음 ($0.10/1M tokens)
    SMALL = "text-embedding-3-small"    # 가장 저렴 ($0.02/1M tokens)
    LARGE = "text-embedding-3-large"    # 최고 성능 ($0.13/1M tokens)


@lru_cache(maxsize=1)
def get_vectorstore(embedding_model: EmbeddingModel = EmbeddingModel.SMALL):
    """
    Chroma VectorStore 초기화 (싱글톤 패턴)

    첫 호출 시에만 인스턴스를 생성하고, 이후 호출에서는 캐시된 인스턴스를 재사용합니다.

    Args:
        embedding_model (EmbeddingModel): 사용할 OpenAI 임베딩 모델. 기본값은 SMALL.
    """
    os.makedirs(settings.CHROMA_PATH, exist_ok=True)
    embeddings = OpenAIEmbeddings(
        model=embedding_model.value,
        openai_api_key=settings.OPENAI_API_KEY
    )
    vectorstore = Chroma(
        collection_name="ai_career_docs",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH,
    )
    return vectorstore


def add_document(text: str, metadata: dict = None):
    """
    VectorStore에 텍스트 문서를 추가합니다.

    Args:
        text (str): 추가할 텍스트 문서
        metadata (dict, optional): 문서와 함께 저장할 메타데이터 (예: {"source": "README.md"})
    """
    store = get_vectorstore()
    store.add_texts([text], metadatas=[metadata or {}])
    store.persist()


def search_document(query: str, k: int = 3):
    """
    유사도 기반으로 VectorStore에서 관련 문서를 검색합니다.

    Args:
        query (str): 검색할 질문 또는 키워드
        k (int, optional): 반환할 문서 개수. 기본값은 3개.

    Returns:
        List[Document]: 유사도가 높은 문서 리스트 (LangChain Document 객체)
    """
    store = get_vectorstore()
    results = store.similarity_search(query, k=k)
    return results

