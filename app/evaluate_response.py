"""
evaluate_response.py
--------------------------------
사용자 응답 품질 평가 모듈
AI 응답의 자연스러움 / 도움 정도 / 감정 일치도 등 점수화

실행 방법:
  python -m app.evaluate_response
--------------------------------
"""
import os
import json
import pandas as pd
from sqlalchemy import create_engine
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# -----------------------------------
# 환경 변수 및 클라이언트 초기화
# -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set in .env file")

client = OpenAI(api_key=OPENAI_API_KEY)
engine = create_engine(DATABASE_URL)


def evaluate_response(answer: str, question: str) -> dict:
    """
    OpenAI API를 사용하여 AI 응답의 품질을 평가합니다.

    Args:
        answer (str): AI가 생성한 답변
        question (str): 사용자의 질문

    Returns:
        dict: 평가 결과
            - relevance (int): 질문 관련성 (0~10)
            - clarity (int): 명확성 및 도움 정도 (0~10)
            - emotion (int): 감정 톤 일치도 (0~10)
            - comment (str): 평가 코멘트
    """
    # OpenAI API 호출용 프롬프트 작성
    prompt = f"""
    Evaluate the AI's answer quality based on these 3 aspects:
    1. Relevance to the user's question (0~10)
    2. Helpfulness and clarity (0~10)
    3. Emotional tone alignment (0~10)

    Question: {question}
    Answer: {answer}

    Return the evaluation in JSON format:
    {{
        "relevance": <score 0-10>,
        "clarity": <score 0-10>,
        "emotion": <score 0-10>,
        "comment": "<brief evaluation comment>"
    }}
    """

    try:
        # ✅ 최신 OpenAI API 문법 (chat.completions.create)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI response quality evaluator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # 일관된 평가를 위해 낮은 temperature
        )

        # 응답에서 텍스트 추출
        result_text = response.choices[0].message.content.strip()

        # JSON 파싱 시도
        try:
            # JSON 코드 블록 제거 (```json ... ``` 형식)
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()

            scores = json.loads(result_text)

            # 기본값 설정 (키가 없을 경우 대비)
            return {
                "relevance": scores.get("relevance", 0),
                "clarity": scores.get("clarity", 0),
                "emotion": scores.get("emotion", 0),
                "comment": scores.get("comment", "No comment")[:200]  # 최대 200자
            }

        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본값 반환
            print(f"⚠️ JSON parsing failed. Raw response: {result_text[:100]}")
            return {
                "relevance": 0,
                "clarity": 0,
                "emotion": 0,
                "comment": result_text[:200]
            }

    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return {
            "relevance": 0,
            "clarity": 0,
            "emotion": 0,
            "comment": f"Error: {str(e)[:100]}"
        }


def run_evaluation():
    """
    최근 대화 로그를 조회하여 AI 응답 품질을 평가하고 결과를 DB에 저장합니다.

    동작:
        1. conversation_log 테이블에서 최근 10개의 대화 로그 조회
        2. 각 대화에 대해 evaluate_response() 함수 호출
        3. 평가 결과를 conversation_evaluation 테이블에 저장
    """
    print("📊 Starting evaluation process...")

    # 1. 최근 10개의 대화 로그 조회 (필요한 컬럼만 선택)
    df = pd.read_sql(
        """
        SELECT id, user_id, question, answer, sentiment, topic, created_at
        FROM conversation_log
        ORDER BY created_at DESC
        LIMIT 10
        """,
        engine
    )

    if df.empty:
        print("⚠️ No conversation data found in the database.")
        return

    print(f"✅ Found {len(df)} conversations to evaluate.")

    # 2. 각 대화에 대해 평가 실행
    evaluations = []
    for idx, row in df.iterrows():
        print(f"   Evaluating conversation {idx + 1}/{len(df)}...")
        eval_result = evaluate_response(row["answer"], row["question"])
        evaluations.append(eval_result)

    # 3. 평가 결과를 새 데이터프레임 생성 (원본 데이터 + 평가 결과)
    evaluation_df = pd.DataFrame({
        "conversation_id": df["id"],  # 원본 대화 ID 참조
        "user_id": df["user_id"],
        "question": df["question"],
        "answer": df["answer"],
        "sentiment": df["sentiment"],
        "topic": df["topic"],
        "created_at": df["created_at"],
        # 평가 결과 추가
        "relevance": [e["relevance"] for e in evaluations],
        "clarity": [e["clarity"] for e in evaluations],
        "emotion": [e["emotion"] for e in evaluations],
        "comment": [e["comment"] for e in evaluations]
    })

    # 4. 결과를 conversation_evaluation 테이블에 저장 (기존 테이블 덮어쓰기)
    evaluation_df.to_sql("conversation_evaluation", engine, if_exists="replace", index=False)

    print("✅ Evaluation results saved to 'conversation_evaluation' table.")
    print(f"   Average scores - Relevance: {evaluation_df['relevance'].mean():.1f}, "
          f"Clarity: {evaluation_df['clarity'].mean():.1f}, Emotion: {evaluation_df['emotion'].mean():.1f}")


if __name__ == "__main__":
    run_evaluation()
