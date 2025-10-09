from fastapi import FastAPI
from app.routers import chat

app = FastAPI(
    title="AI Career 6 Months",
    description="LangChain + FastAPI 기반 AI 커리어 프로젝트 API 서버",
    version="0.1.0",
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
def root():
    return {"message": "🚀 AI Career 6 Months API is running!"}
