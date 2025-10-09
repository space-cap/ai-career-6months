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
