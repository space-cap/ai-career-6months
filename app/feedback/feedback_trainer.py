# app/feedback/feedback_trainer.py
"""
피드백 기반 학습 및 개선 제안 모듈

부정 피드백을 분석하여 AI 응답 품질 개선을 위한 인사이트 제공
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter

from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.database import get_db
from app.models.feedback_log import FeedbackLog
from app.models.conversation_log import ConversationLog
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_feedback_statistics(
    db: Session, days: int = 30
) -> Dict[str, any]:
    """
    최근 N일간 피드백 통계 조회

    Args:
        db: 데이터베이스 세션
        days: 조회 기간 (일)

    Returns:
        {
            "total": 전체 피드백 수,
            "likes": 긍정 피드백 수,
            "dislikes": 부정 피드백 수,
            "satisfaction_rate": 만족도 (0.0 ~ 1.0),
            "period": "최근 N일"
        }
    """
    try:
        since = datetime.utcnow() - timedelta(days=days)

        total = db.query(FeedbackLog).filter(
            FeedbackLog.created_at >= since
        ).count()

        likes = db.query(FeedbackLog).filter(
            FeedbackLog.created_at >= since,
            FeedbackLog.feedback == "like"
        ).count()

        dislikes = total - likes

        return {
            "total": total,
            "likes": likes,
            "dislikes": dislikes,
            "satisfaction_rate": round(likes / total, 3) if total > 0 else 0.0,
            "period": f"최근 {days}일",
            "period_start": since.strftime("%Y-%m-%d"),
            "period_end": datetime.utcnow().strftime("%Y-%m-%d"),
        }

    except Exception as e:
        logger.error(f"피드백 통계 조회 실패: {e}", exc_info=True)
        return {
            "total": 0,
            "likes": 0,
            "dislikes": 0,
            "satisfaction_rate": 0.0,
            "error": str(e),
        }


def analyze_negative_feedback_patterns(
    db: Session, limit: int = 50
) -> Dict[str, any]:
    """
    부정 피드백 패턴 분석

    Args:
        db: 데이터베이스 세션
        limit: 분석할 부정 피드백 최대 개수

    Returns:
        {
            "negative_feedbacks": 부정 피드백 리스트,
            "common_issues": 공통 이슈 키워드,
            "sample_qa_pairs": 문제가 있는 Q&A 샘플
        }
    """
    try:
        # 부정 피드백 조회 (최신순)
        negative_feedbacks = (
            db.query(FeedbackLog)
            .filter(FeedbackLog.feedback == "dislike")
            .order_by(FeedbackLog.created_at.desc())
            .limit(limit)
            .all()
        )

        if not negative_feedbacks:
            logger.info("부정 피드백이 없습니다.")
            return {
                "negative_feedbacks": [],
                "common_issues": [],
                "sample_qa_pairs": [],
                "message": "분석할 부정 피드백이 없습니다.",
            }

        # 부정 피드백 사유 수집
        reasons = []
        qa_pairs = []

        for fb in negative_feedbacks:
            if fb.reason:
                reasons.append(fb.reason)

            # 해당 대화 내용 조회
            conversation = (
                db.query(ConversationLog)
                .filter(ConversationLog.id == fb.conversation_id)
                .first()
            )

            if conversation:
                qa_pairs.append({
                    "question": conversation.question,
                    "answer": conversation.answer,
                    "feedback_reason": fb.reason or "(사유 없음)",
                    "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                })

        # 공통 이슈 키워드 추출 (간단한 키워드 빈도)
        common_keywords = _extract_common_keywords(reasons)

        return {
            "total_negative": len(negative_feedbacks),
            "negative_feedbacks": [
                {
                    "id": fb.id,
                    "conversation_id": fb.conversation_id,
                    "reason": fb.reason or "(사유 없음)",
                    "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for fb in negative_feedbacks[:10]  # 최대 10개만 반환
            ],
            "common_issues": common_keywords[:10],  # 상위 10개 키워드
            "sample_qa_pairs": qa_pairs[:5],  # 샘플 5개
        }

    except Exception as e:
        logger.error(f"부정 피드백 패턴 분석 실패: {e}", exc_info=True)
        return {
            "negative_feedbacks": [],
            "common_issues": [],
            "sample_qa_pairs": [],
            "error": str(e),
        }


def _extract_common_keywords(texts: List[str]) -> List[Dict[str, any]]:
    """
    텍스트에서 공통 키워드 추출 (빈도 기반)

    Args:
        texts: 분석할 텍스트 리스트

    Returns:
        [{"keyword": "키워드", "count": 빈도}, ...]
    """
    if not texts:
        return []

    # 간단한 키워드 추출 (공백 기준 split)
    words = []
    stopwords = {"이", "그", "저", "것", "수", "등", "및", "또는", "하지만", "그리고"}

    for text in texts:
        if not text:
            continue
        # 단순 공백 분리 (실제로는 형태소 분석기 사용 권장)
        words.extend([
            word.strip() for word in text.split()
            if len(word.strip()) > 1 and word.strip() not in stopwords
        ])

    # 빈도 계산
    word_counts = Counter(words)

    return [
        {"keyword": word, "count": count}
        for word, count in word_counts.most_common(20)
    ]


def generate_improvement_suggestions(
    db: Session, limit: int = 50
) -> Dict[str, any]:
    """
    부정 피드백을 분석하여 AI 프롬프트 개선 제안 생성 (GPT 기반)

    Args:
        db: 데이터베이스 세션
        limit: 분석할 부정 피드백 최대 개수

    Returns:
        {
            "statistics": 피드백 통계,
            "analysis": 부정 피드백 분석 결과,
            "suggestions": GPT 기반 개선 제안 리스트
        }
    """
    try:
        # 1. 통계 조회
        stats = get_feedback_statistics(db, days=30)

        # 2. 부정 피드백 패턴 분석
        analysis = analyze_negative_feedback_patterns(db, limit=limit)

        if analysis.get("total_negative", 0) == 0:
            return {
                "statistics": stats,
                "analysis": analysis,
                "suggestions": [],
                "message": "부정 피드백이 없어 개선 제안을 생성할 수 없습니다.",
            }

        # 3. GPT를 사용하여 개선 제안 생성
        suggestions = _generate_suggestions_with_gpt(analysis)

        return {
            "statistics": stats,
            "analysis": analysis,
            "suggestions": suggestions,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        logger.error(f"개선 제안 생성 실패: {e}", exc_info=True)
        return {
            "statistics": {},
            "analysis": {},
            "suggestions": [],
            "error": str(e),
        }


def _generate_suggestions_with_gpt(
    analysis: Dict[str, any]
) -> List[Dict[str, str]]:
    """
    GPT를 사용하여 구체적인 개선 제안 생성

    Args:
        analysis: 부정 피드백 분석 결과

    Returns:
        [{"category": "카테고리", "suggestion": "제안 내용"}, ...]
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        # 분석 결과 요약
        sample_qa = analysis.get("sample_qa_pairs", [])
        common_issues = analysis.get("common_issues", [])

        if not sample_qa and not common_issues:
            return []

        # GPT 프롬프트 생성
        prompt = f"""당신은 AI 챗봇 품질 개선 전문가입니다.

다음은 사용자들이 부정적인 피드백을 남긴 대화 샘플과 공통 이슈입니다:

**공통 이슈 키워드:**
{chr(10).join([f"- {issue['keyword']} ({issue['count']}회)" for issue in common_issues[:10]])}

**문제가 있는 Q&A 샘플:**
{chr(10).join([
    f"Q: {qa['question'][:100]}...\\nA: {qa['answer'][:100]}...\\n피드백: {qa['feedback_reason']}\\n"
    for qa in sample_qa[:3]
])}

위 데이터를 분석하여 AI 챗봇의 응답 품질을 개선하기 위한 구체적인 제안 3가지를 작성해주세요.

각 제안은 다음 형식의 JSON 배열로 작성해주세요:
[
  {{
    "category": "개선 카테고리 (예: 프롬프트 튜닝, 응답 길이, 정확도 등)",
    "suggestion": "구체적인 개선 방안 (1-2문장)"
  }}
]

주의: 반드시 JSON 배열 형식으로만 답변하고, 다른 설명은 추가하지 마세요."""

        response = llm.invoke([HumanMessage(content=prompt)])
        result_text = response.content.strip()

        # JSON 파싱
        import json

        try:
            # JSON 블록 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            suggestions = json.loads(result_text)

            if not isinstance(suggestions, list):
                suggestions = [suggestions]

            return suggestions

        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.warning(f"GPT 응답 파싱 실패: {result_text[:200]}... | 오류: {e}")
            # 폴백: 기본 제안 반환
            return [
                {
                    "category": "일반",
                    "suggestion": "부정 피드백을 참고하여 프롬프트를 수동으로 개선하세요.",
                }
            ]

    except Exception as e:
        logger.error(f"GPT 기반 제안 생성 실패: {e}", exc_info=True)
        return [
            {
                "category": "오류",
                "suggestion": f"제안 생성 중 오류 발생: {str(e)}",
            }
        ]


def retrain_from_feedback(days: int = 30, limit: int = 50) -> Dict[str, any]:
    """
    피드백 기반 학습 루프 실행 (메인 함수)

    Args:
        days: 통계 조회 기간 (일)
        limit: 분석할 부정 피드백 최대 개수

    Returns:
        {
            "statistics": 피드백 통계,
            "analysis": 부정 피드백 분석,
            "suggestions": 개선 제안 리스트
        }
    """
    db = next(get_db())
    try:
        logger.info(f"피드백 기반 학습 시작 (최근 {days}일)")

        result = generate_improvement_suggestions(db, limit=limit)

        logger.info(
            f"피드백 학습 완료 - 만족도: {result.get('statistics', {}).get('satisfaction_rate', 0):.1%}"
        )

        return result

    except Exception as e:
        logger.error(f"피드백 학습 실패: {e}", exc_info=True)
        return {
            "statistics": {},
            "analysis": {},
            "suggestions": [],
            "error": str(e),
        }
    finally:
        db.close()
