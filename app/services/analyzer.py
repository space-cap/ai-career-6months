from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.config import settings


llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,  # 감정 분류는 일관성이 중요
        openai_api_key=settings.OPENAI_API_KEY
    )


def analyze_sentiment(text):
    """문장의 감정을 분석 ('긍정', '중립', '부정')"""
    prompt = f"다음 문장의 감정을 '긍정', '중립', '부정' 중 정확히 하나의 단어로만 답변해:\n{text}"
    response = llm.invoke(prompt)
    result = response.content.strip()

    # 정규화: LLM 응답을 표준 형식으로 변환
    if "긍정" in result or "positive" in result.lower():
        return "긍정"
    elif "부정" in result or "negative" in result.lower():
        return "부정"
    elif "중립" in result or "neutral" in result.lower():
        return "중립"
    else:
        return "중립"  # 기본값


def extract_topic(text: str) -> str:
    """문장의 주요 주제 키워드 추출"""
    prompt = f"다음 문장에서 가장 중심이 되는 주제를 한 단어 또는 짧은 구로 요약해줘:\n{text}"
    result = llm.invoke([HumanMessage(content=prompt)])
    return result.content.strip()