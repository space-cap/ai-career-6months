from langchain_openai import ChatOpenAI
from app.core.config import settings


def analyze_sentiment(text):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,  # 감정 분류는 일관성이 중요
        openai_api_key=settings.OPENAI_API_KEY
    )
    prompt = f"다음 문장의 감정을 '긍정', '중립', '부정' 중 하나로 분류해줘:\n{text}"
    response = llm.invoke(prompt)
    return response.content.strip()
