from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings


def get_ai_response(user_input: str) -> str:
    prompt = PromptTemplate(
        input_variables=["question"],
        template="당신은 AI 멘토입니다. 다음 질문에 간결히 답해주세요:\n\n질문: {question}",
    )

    llm = OpenAI(openai_api_key=settings.OPENAI_API_KEY, temperature=0.5)
    chain = LLMChain(prompt=prompt, llm=llm)
    response = chain.run(user_input)
    return response
