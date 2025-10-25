# Feedback Analyzer Module

피드백 감정 분석 모듈 - OpenAI GPT 기반 한글 감정 분석

## 개요

사용자 피드백 텍스트에서 감정(긍정/중립/부정)과 감정 점수(-1.0 ~ 1.0)를 추출합니다.

### 주요 특징

- ✅ **한글 완벽 지원**: OpenAI GPT-4o-mini 기반 한글 감정 분석
- ✅ **에러 핸들링**: 빈 문자열, 파싱 오류 등 예외 처리
- ✅ **폴백 메커니즘**: LLM 응답 파싱 실패 시 키워드 기반 분석
- ✅ **조정 가능한 임계값**: 긍정/부정 판단 임계값 커스터마이징
- ✅ **싱글톤 LLM**: 성능 최적화를 위한 LLM 인스턴스 재사용

## 설치

이 모듈은 다음 패키지에 의존합니다:

```bash
pip install langchain-openai langchain-core pydantic-settings
```

환경변수 설정:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## 사용법

### 기본 사용

```python
from app.feedback.feedback_analyzer import analyze_feedback

# 피드백 분석
result = analyze_feedback("정확하고 자세한 답변이었습니다!")

print(result)
# {
#     "sentiment": "positive",
#     "score": 0.9,
#     "korean_label": "긍정"
# }
```

### 임계값 조정

```python
# 더 엄격한 긍정/부정 판단 (중립 범위 확대)
result = analyze_feedback(
    "괜찮은 것 같아요.",
    polarity_threshold_positive=0.3,   # 기본값: 0.1
    polarity_threshold_negative=-0.3   # 기본값: -0.1
)

print(result)
# {
#     "sentiment": "neutral",
#     "score": 0.15,
#     "korean_label": "중립"
# }
```

### 에러 처리

```python
try:
    result = analyze_feedback("")  # 빈 문자열
except ValueError as e:
    print(f"에러: {e}")
    # 에러: 피드백 텍스트는 비어있을 수 없습니다.
```

```python
# 예외를 반환값으로 처리하는 방식
result = analyze_feedback("some text with API error")

if "error" in result:
    print(f"분석 실패: {result['error']}")
    # 분석 실패: API connection timeout
```

## API Reference

### `analyze_feedback(feedback_text, polarity_threshold_positive=0.1, polarity_threshold_negative=-0.1)`

피드백 문장에서 감정 점수와 레이블 추출 (한글 지원)

**Parameters:**
- `feedback_text` (str): 분석할 피드백 텍스트
- `polarity_threshold_positive` (float, optional): 긍정 판단 임계값 (기본값: 0.1)
- `polarity_threshold_negative` (float, optional): 부정 판단 임계값 (기본값: -0.1)

**Returns:**
```python
{
    "sentiment": "positive" | "neutral" | "negative",
    "score": float,  # -1.0 ~ 1.0
    "korean_label": "긍정" | "중립" | "부정",
    "error": str  # (오류 발생 시에만)
}
```

**Raises:**
- `ValueError`: feedback_text가 비어있거나 None일 때

## 테스트

테스트 스크립트 실행:

```bash
python scripts/test_feedback_analyzer.py
```

예상 출력:
```
================================================================================
[피드백 감정 분석 테스트]
================================================================================

[테스트 1]
피드백: '정확하고 자세한 답변이었습니다. 정말 도움이 많이 되었어요!'
결과: {'sentiment': 'positive', 'score': 0.9, 'korean_label': '긍정'}
  - 감정: positive (긍정)
  - 점수: 0.9

[테스트 2]
피드백: '답변이 너무 불친절하고 이해하기 어려웠습니다.'
결과: {'sentiment': 'negative', 'score': -0.8, 'korean_label': '부정'}
  - 감정: negative (부정)
  - 점수: -0.8

...
```

## 통합 예시

### FastAPI 라우터와 통합

```python
from fastapi import APIRouter, HTTPException
from app.feedback.feedback_analyzer import analyze_feedback

router = APIRouter()

@router.post("/api/feedback/analyze")
async def analyze_user_feedback(feedback_text: str):
    """사용자 피드백 감정 분석"""
    try:
        result = analyze_feedback(feedback_text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 데이터베이스 저장과 통합

```python
from app.feedback.feedback_analyzer import analyze_feedback
from app.database import SessionLocal
from app.models import FeedbackLog

def save_feedback_with_sentiment(conversation_id: int, feedback_text: str):
    """피드백을 감정 분석 결과와 함께 저장"""
    # 감정 분석
    analysis = analyze_feedback(feedback_text)

    # DB 저장
    db = SessionLocal()
    try:
        feedback_log = FeedbackLog(
            conversation_id=conversation_id,
            feedback=analysis["sentiment"],
            reason=feedback_text,
            sentiment_score=analysis["score"],
            korean_label=analysis["korean_label"]
        )
        db.add(feedback_log)
        db.commit()
        return feedback_log
    finally:
        db.close()
```

## 기술적 세부사항

### 아키텍처

1. **LLM 싱글톤 패턴**: `get_llm()` 함수가 ChatOpenAI 인스턴스를 재사용하여 성능 최적화
2. **Structured Output**: GPT에게 JSON 형식 응답 요청으로 파싱 안정성 확보
3. **폴백 메커니즘**: JSON 파싱 실패 시 키워드 기반 분석으로 대체
4. **임계값 재분류**: LLM 점수와 임계값을 비교하여 최종 감정 결정

### 성능 고려사항

- **API 호출 비용**: 각 분석마다 OpenAI API 호출 (gpt-4o-mini)
- **응답 시간**: 평균 1-3초 (네트워크 상태에 따라 변동)
- **캐싱 권장**: 동일 피드백 반복 분석 시 결과 캐싱 고려

### TextBlob에서 마이그레이션

이전 버전에서 TextBlob을 사용했다면 다음과 같이 마이그레이션:

**Before (TextBlob - 영어 전용):**
```python
from textblob import TextBlob

analysis = TextBlob(feedback_text)
polarity = analysis.sentiment.polarity
sentiment = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
```

**After (GPT - 한글 지원):**
```python
from app.feedback.feedback_analyzer import analyze_feedback

result = analyze_feedback(feedback_text)
sentiment = result["sentiment"]
polarity = result["score"]
```

## 피드백 기반 학습 루프 (Feedback Trainer)

### 개요

`feedback_trainer.py` 모듈은 부정 피드백을 분석하여 AI 챗봇 응답 품질 개선을 위한 인사이트를 제공합니다.

### 주요 기능

1. **피드백 통계 조회**: 최근 N일간 긍정/부정 피드백 통계
2. **부정 피드백 패턴 분석**: 부정 피드백의 공통 이슈 키워드 추출
3. **GPT 기반 개선 제안**: AI가 자동으로 프롬프트 개선 방안 제안

### 사용법

#### 1. 전체 피드백 루프 실행

```python
from app.feedback.feedback_trainer import retrain_from_feedback

# 최근 30일 피드백 분석 및 개선 제안 생성
result = retrain_from_feedback(days=30, limit=50)

print(result["statistics"])     # 피드백 통계
print(result["analysis"])        # 부정 피드백 분석
print(result["suggestions"])     # AI 개선 제안
```

**예상 출력:**
```python
{
  "statistics": {
    "total": 150,
    "likes": 120,
    "dislikes": 30,
    "satisfaction_rate": 0.8,
    "period": "최근 30일"
  },
  "analysis": {
    "total_negative": 30,
    "common_issues": [
      {"keyword": "불친절", "count": 5},
      {"keyword": "이해하기", "count": 3}
    ],
    "sample_qa_pairs": [...]
  },
  "suggestions": [
    {
      "category": "프롬프트 튜닝",
      "suggestion": "답변 어조를 더 친절하고 공감적으로 변경하세요."
    },
    {
      "category": "응답 구조",
      "suggestion": "복잡한 개념은 단계별로 나누어 설명하세요."
    }
  ]
}
```

#### 2. 개별 함수 사용

**통계 조회:**
```python
from app.feedback.feedback_trainer import get_feedback_statistics
from app.database import get_db

db = next(get_db())
stats = get_feedback_statistics(db, days=7)
print(f"만족도: {stats['satisfaction_rate']:.1%}")
```

**부정 피드백 분석:**
```python
from app.feedback.feedback_trainer import analyze_negative_feedback_patterns
from app.database import get_db

db = next(get_db())
analysis = analyze_negative_feedback_patterns(db, limit=20)

for issue in analysis["common_issues"][:5]:
    print(f"{issue['keyword']}: {issue['count']}회")
```

### 테스트

```bash
python scripts/test_feedback_trainer.py
```

### API 엔드포인트 통합 예시

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.feedback.feedback_trainer import (
    get_feedback_statistics,
    generate_improvement_suggestions,
)

router = APIRouter()

@router.get("/api/feedback/stats")
async def get_stats(days: int = 30, db: Session = Depends(get_db)):
    """피드백 통계 조회"""
    return get_feedback_statistics(db, days=days)

@router.post("/api/feedback/improve")
async def get_improvement_suggestions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """AI 기반 개선 제안 생성"""
    return generate_improvement_suggestions(db, limit=limit)
```

### Slack 알림 통합 예시

```python
from app.feedback.feedback_trainer import retrain_from_feedback
from app.utils.slack_utils import send_slack_message

# 주간 피드백 리포트 자동 생성 및 Slack 전송
result = retrain_from_feedback(days=7, limit=30)

stats = result["statistics"]
suggestions = result["suggestions"]

message = f"""
📊 *주간 피드백 리포트*

만족도: {stats['satisfaction_rate']:.1%}
긍정: {stats['likes']}개 | 부정: {stats['dislikes']}개

💡 *AI 개선 제안:*
{chr(10).join([f"- [{s['category']}] {s['suggestion']}" for s in suggestions[:3]])}
"""

send_slack_message(message)
```

## 향후 개선 계획

**feedback_analyzer.py:**
- [ ] 배치 분석 API 추가 (여러 피드백 동시 처리)
- [ ] 결과 캐싱 레이어 (Redis)
- [ ] 감정 외 추가 메타데이터 추출 (주제, 키워드 등)
- [ ] 사용자 정의 감정 카테고리 지원 (5단계 등)

**feedback_trainer.py:**
- [ ] 한국어 형태소 분석기 적용 (KoNLPy)
- [ ] 시계열 트렌드 분석 (만족도 추이)
- [ ] 자동 프롬프트 A/B 테스트 기능
- [ ] 개선 제안 이력 추적 및 효과 측정

## 라이선스

MIT License

---

**관련 문서:**
- [API Reference](../../docs/api_reference.md)
- [프로젝트 README](../../README.md)
