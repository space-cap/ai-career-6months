from fastapi import FastAPI, Depends
from app.routers import chat, ingest, rag_chat, conversation, personal_chat, insights
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.database import get_db
from app.core.config import settings

app = FastAPI(
    title="AI Career 6 Months",
    description="LangChain + FastAPI 기반 AI 커리어 프로젝트 API 서버",
    version="0.1.0",
)

# ✅ CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(rag_chat.router, prefix="/api", tags=["rag_chat"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(conversation.router, prefix="/api", tags=["conversation"])
app.include_router(personal_chat.router, prefix="/api", tags=["personal_chat"])
app.include_router(insights.router, prefix="/api", tags=["insights"])


@app.get("/api/health")
def health_check(db=Depends(get_db)):
    result = db.execute(text("SELECT NOW()")).fetchone()
    return {"status": "ok", "db_time": str(result[0]), "openai_key": bool(settings.OPENAI_API_KEY)}


# @app.get("/")
# def root():
#    return {"message": "🚀 AI Career 6 Months API is running!"}

# ✅ Vite 빌드된 React 파일 연결 (맨 마지막에 마운트)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
