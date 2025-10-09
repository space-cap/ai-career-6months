from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings


def get_ai_response(user_input: str) -> str:
    """LangChain LCEL(LangChain Expression Language) 방식으로 AI 응답 생성"""

    # 프롬프트 템플릿 정의 (시스템 메시지와 사용자 메시지 분리)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 AI 멘토입니다. 다음 질문에 간결히 답해주세요."),
        ("human", "{question}")
    ])

    # ChatOpenAI 모델 초기화 (gpt-4o-mini 사용)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # LCEL 체인 구성: prompt | llm | output_parser
    chain = prompt | llm | StrOutputParser()

    # 체인 실행 (.invoke() 메서드 사용)
    response = chain.invoke({"question": user_input})
    return response
