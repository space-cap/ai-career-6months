# app/feedback/feedback_analyzer.py
"""
피드백 감정 분석 모듈 (한글 지원)

OpenAI GPT 기반 감정 분석으로 한글 피드백의 감정과 점수를 추출합니다.
"""
import logging
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

# LLM 초기화 (싱글톤 패턴)
_llm_instance: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """LLM 인스턴스 반환 (lazy initialization)"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # 감정 분류는 일관성이 중요
            openai_api_key=settings.OPENAI_API_KEY,
        )
    return _llm_instance


def analyze_feedback(
    feedback_text: str,
    polarity_threshold_positive: float = 0.1,
    polarity_threshold_negative: float = -0.1,
) -> Dict[str, any]:
    """
    피드백 문장에서 감정 점수와 레이블 추출 (한글 지원)

    Args:
        feedback_text: 분석할 피드백 텍스트
        polarity_threshold_positive: 긍정 판단 임계값 (기본값: 0.1)
        polarity_threshold_negative: 부정 판단 임계값 (기본값: -0.1)

    Returns:
        {
            "sentiment": "positive" | "neutral" | "negative",
            "score": float (-1.0 ~ 1.0),
            "korean_label": "긍정" | "중립" | "부정",
            "error": str (오류 발생 시에만)
        }

    Raises:
        ValueError: feedback_text가 비어있거나 None일 때
    """
    # 입력 검증
    if not feedback_text or not feedback_text.strip():
        logger.warning("빈 피드백 텍스트가 입력되었습니다.")
        raise ValueError("피드백 텍스트는 비어있을 수 없습니다.")

    try:
        llm = get_llm()

        # GPT 프롬프트: 감정 레이블 + 점수 동시 추출
        prompt = f"""다음 피드백 문장의 감정을 분석해주세요.

피드백: "{feedback_text}"

응답 형식 (JSON):
{{
  "sentiment": "긍정" 또는 "중립" 또는 "부정",
  "score": -1.0에서 1.0 사이의 숫자 (부정적일수록 음수, 긍정적일수록 양수)
}}

주의: 반드시 위 JSON 형식으로만 답변하고, 다른 설명은 추가하지 마세요."""

        response = llm.invoke([HumanMessage(content=prompt)])
        result_text = response.content.strip()

        # JSON 파싱 시도
        import json

        try:
            # JSON 블록 추출 (```json ... ``` 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(result_text)
            korean_label = parsed.get("sentiment", "중립")
            score = float(parsed.get("score", 0.0))

        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.warning(
                f"LLM 응답 파싱 실패, 폴백 처리: {result_text[:100]}... | 오류: {e}"
            )
            # 폴백: 키워드 기반 분석
            korean_label = _extract_sentiment_fallback(result_text)
            score = _estimate_score_from_label(korean_label)

        # 한글 레이블 -> 영어 레이블 변환
        sentiment_mapping = {
            "긍정": "positive",
            "부정": "negative",
            "중립": "neutral",
        }
        english_label = sentiment_mapping.get(korean_label, "neutral")

        # 점수 범위 검증 및 보정
        score = max(-1.0, min(1.0, score))

        # 임계값 기반 재분류 (선택적)
        if score > polarity_threshold_positive:
            english_label = "positive"
            korean_label = "긍정"
        elif score < polarity_threshold_negative:
            english_label = "negative"
            korean_label = "부정"
        else:
            if abs(score) <= 0.05:  # 거의 0에 가까우면 중립
                english_label = "neutral"
                korean_label = "중립"

        return {
            "sentiment": english_label,
            "score": round(score, 3),
            "korean_label": korean_label,
        }

    except Exception as e:
        logger.error(f"피드백 감정 분석 중 오류 발생: {e}", exc_info=True)
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "korean_label": "중립",
            "error": str(e),
        }


def _extract_sentiment_fallback(text: str) -> str:
    """LLM 응답 파싱 실패 시 키워드 기반 폴백"""
    text_lower = text.lower()
    if "긍정" in text or "positive" in text_lower or "좋" in text:
        return "긍정"
    elif "부정" in text or "negative" in text_lower or "나쁨" in text or "싫" in text:
        return "부정"
    else:
        return "중립"


def _estimate_score_from_label(label: str) -> float:
    """감정 레이블에서 대략적인 점수 추정"""
    if label == "긍정":
        return 0.5
    elif label == "부정":
        return -0.5
    else:
        return 0.0
