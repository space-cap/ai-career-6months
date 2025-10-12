from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings


def summarize_context(logs):
    summaries = [f"Q: {log.question} / A: {log.answer}" for log in logs]
    return "\n".join(summaries)


def generate_personal_answer(question, logs):
    context = summarize_context(logs)
    messages = [
        SystemMessage(content="너는 사용자의 과거 대화를 이해하고 개인화된 답변을 주는 어시스턴트야."),
        HumanMessage(content=f"이전 대화 내용:\n{context}\n\n새로운 질문: {question}")
    ]
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )
    response = llm.invoke(messages)
    return response.content
