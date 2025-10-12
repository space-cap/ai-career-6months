from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


def summarize_context(logs):
    summaries = [f"Q: {l.question} / A: {l.answer}" for l in logs]
    return "\n".join(summaries)


def generate_personal_answer(question, logs):
    context = summarize_context(logs)
    messages = [
        SystemMessage(content="너는 사용자의 과거 대화를 이해하고 개인화된 답변을 주는 어시스턴트야."),
        HumanMessage(content=f"이전 대화 내용:\n{context}\n\n새로운 질문: {question}")
    ]
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm(messages)
    return response.content
