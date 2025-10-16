"""
vector_retrain.py
--------------------------------
평가 결과 기반 벡터스토어 자동 업데이트

대화 로그를 기반으로 벡터스토어를 재학습시켜
이전 대화 패턴을 RAG에 활용할 수 있도록 합니다.

실행 방법:
  python -m app.vector_retrain
--------------------------------
"""
import os
import pandas as pd
from sqlalchemy import create_engine
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# -----------------------------------
# 환경 변수 설정
# -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set in .env file")

engine = create_engine(DATABASE_URL)


def retrain_vectorstore():
    """
    대화 로그를 벡터스토어에 재학습시킵니다.

    동작:
        1. conversation_log 테이블에서 모든 대화 조회
        2. "Q: {질문}\nA: {답변}" 형식으로 데이터 변환
        3. OpenAI 임베딩 생성
        4. Chroma 벡터스토어에 메타데이터와 함께 저장

    벡터스토어 컬렉션:
        - 이름: "conversation_retrained"
        - 경로: CHROMA_PATH (기본값: ./chroma_db)
    """
    print("📊 Starting vectorstore retraining...")

    try:
        # 1. 대화 로그 조회 (ID와 생성일자 포함)
        df = pd.read_sql(
            "SELECT id, question, answer, sentiment, topic, created_at FROM conversation_log",
            engine
        )

        if df.empty:
            print("⚠️ No conversation data found in database.")
            return

        print(f"✅ Found {len(df)} conversations to process.")

        # 2. 데이터 변환 (Q&A 형식)
        texts = [
            f"Q: {row['question']}\nA: {row['answer']}"
            for _, row in df.iterrows()
        ]

        # 3. 메타데이터 생성 (출처 추적용)
        metadatas = [
            {
                "conversation_id": str(row["id"]),
                "sentiment": row["sentiment"] if pd.notna(row["sentiment"]) else "unknown",
                "topic": row["topic"] if pd.notna(row["topic"]) else "general",
                "created_at": str(row["created_at"]),
                "source": "conversation_log"
            }
            for _, row in df.iterrows()
        ]

        # 4. OpenAI 임베딩 초기화
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )

        # 5. Chroma 벡터스토어 초기화
        vectorstore = Chroma(
            collection_name="conversation_retrained",
            embedding_function=embeddings,
            persist_directory=CHROMA_PATH
        )

        # 6. 텍스트와 메타데이터 추가
        print("🔄 Adding texts to vectorstore...")
        vectorstore.add_texts(texts=texts, metadatas=metadatas)

        print(f"✅ Vectorstore retraining complete!")
        print(f"   - Collection: conversation_retrained")
        print(f"   - Location: {CHROMA_PATH}")
        print(f"   - Documents added: {len(texts)}")

    except Exception as e:
        print(f"❌ Error during vectorstore retraining: {e}")
        raise


if __name__ == "__main__":
    retrain_vectorstore()
