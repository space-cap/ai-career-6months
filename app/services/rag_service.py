from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.services.vectorstore import get_vectorstore
from app.core.config import settings


def format_docs(docs):
    """검색된 문서를 문자열로 포맷팅"""
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_response(user_input: str) -> str:
    """
    RAG(Retrieval-Augmented Generation) 방식으로 AI 응답 생성

    VectorStore에서 관련 문서를 검색하고, 해당 문서를 컨텍스트로 활용하여 답변을 생성합니다.

    Args:
        user_input (str): 사용자 질문

    Returns:
        str: AI 생성 답변
    """
    # VectorStore에서 retriever 생성
    store = get_vectorstore()
    retriever = store.as_retriever(search_kwargs={"k": 3})

    # 프롬프트 템플릿 정의
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 도움이 되는 AI 어시스턴트입니다. 아래 제공된 컨텍스트를 바탕으로 질문에 답변해주세요.\n\n컨텍스트: {context}"),
        ("human", "{question}")
    ])

    # LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # LCEL 체인 구성: retriever -> format_docs -> prompt -> llm -> output_parser
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 체인 실행
    response = rag_chain.invoke(user_input)
    return response
