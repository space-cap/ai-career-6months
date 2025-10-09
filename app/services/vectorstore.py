from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
import os


def get_vectorstore():
    """Chroma VectorStore 초기화"""
    os.makedirs(settings.CHROMA_PATH, exist_ok=True)
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    vectorstore = Chroma(
        collection_name="ai_career_docs",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH,
    )
    return vectorstore


def add_document(text: str, metadata: dict = None):
    store = get_vectorstore()
    store.add_texts([text], metadatas=[metadata or {}])
    store.persist()


def search_document(query: str, k: int = 3):
    store = get_vectorstore()
    results = store.similarity_search(query, k=k)
    return results

