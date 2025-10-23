# API Reference

AI Career 6 Months - FastAPI 기반 AI 챗봇 API 서버

**Base URL**: `http://localhost:8000` (개발) / `https://your-domain.com` (프로덕션)

---

## 📚 목차

1. [인증](#인증)
2. [채팅 API](#채팅-api)
3. [문서 관리 API](#문서-관리-api)
4. [피드백 API](#피드백-api)
5. [분석 API](#분석-api)
6. [리포트 API](#리포트-api)
7. [시스템 API](#시스템-api)
8. [Slack 통합 API](#slack-통합-api)
9. [에러 코드](#에러-코드)

---

## 인증

현재 버전은 **인증이 필요하지 않습니다**. 프로덕션 환경에서는 API 키 또는 JWT 인증을 추가하는 것을 권장합니다.

---

## 채팅 API

### 1. POST `/api/chat`

기본 채팅 엔드포인트 (VectorDB 없이 직접 LLM 호출)

**Request:**
```json
{
  "question": "FastAPI란 무엇인가요?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "answer": "FastAPI는 Python 3.6+ 기반의 현대적이고 빠른 웹 프레임워크입니다...",
  "conversation_id": 42
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "FastAPI란 무엇인가요?", "user_id": "user123"}'
```

**Python 예시:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "FastAPI란 무엇인가요?", "user_id": "user123"}
)
print(response.json())
```

---

### 2. POST `/api/rag-chat`

RAG (Retrieval-Augmented Generation) 기반 채팅 - VectorDB에서 관련 문서를 검색하여 컨텍스트 제공

**Request:**
```json
{
  "question": "LangChain의 주요 기능은?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "answer": "LangChain의 주요 기능은 다음과 같습니다: 1) Chains를 통한 모듈 조합...",
  "sources": [
    {
      "content": "LangChain은 LLM 애플리케이션 개발을 위한...",
      "metadata": {"source": "docs/langchain_guide.txt"}
    }
  ],
  "conversation_id": 43
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/api/rag-chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "LangChain의 주요 기능은?", "user_id": "user123"}'
```

---

### 3. POST `/api/personal-chat`

개인화된 채팅 - 사용자 선호도와 이전 대화 기록을 반영

**Request:**
```json
{
  "question": "추천해줄만한 프레임워크가 있나요?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "answer": "이전에 FastAPI에 관심을 보이셨으니, Pydantic과 함께 사용하면 좋습니다...",
  "personalized": true,
  "conversation_id": 44
}
```

---

## 문서 관리 API

### 4. POST `/api/ingest`

문서를 임베딩하여 VectorDB에 저장

**Request:**
```json
{
  "text": "LangChain은 LLM 애플리케이션 개발 프레임워크입니다. Chains, Agents, Memory 등의 구성요소를 제공합니다.",
  "metadata": {
    "source": "langchain_intro.txt",
    "author": "admin"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document ingested successfully",
  "chunks": 1,
  "vector_count": 387
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "LangChain은 LLM 애플리케이션 개발 프레임워크입니다.",
    "metadata": {"source": "langchain_intro.txt"}
  }'
```

---

### 5. GET `/api/vector-count`

VectorDB에 저장된 문서 수 조회

**Response:**
```json
{
  "count": 387
}
```

**cURL 예시:**
```bash
curl "http://localhost:8000/api/vector-count"
```

---

## 피드백 API

### 6. POST `/api/feedback`

사용자 피드백 수집 (좋아요/싫어요)

**Request:**
```json
{
  "conversation_id": 42,
  "feedback": "like",
  "reason": "정확하고 자세한 답변이었습니다"
}
```

**Parameters:**
- `conversation_id` (integer, required): 대화 ID
- `feedback` (string, required): `"like"` 또는 `"dislike"`
- `reason` (string, optional): 피드백 사유

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "feedback_id": 15
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 42,
    "feedback": "like",
    "reason": "정확하고 자세한 답변"
  }'
```

---

## 분석 API

### 7. GET `/api/insights/sentiment`

감정 분석 결과 조회

**Query Parameters:**
- `start_date` (string, optional): 시작일 (YYYY-MM-DD)
- `end_date` (string, optional): 종료일 (YYYY-MM-DD)
- `user_id` (string, optional): 특정 사용자 필터링

**Response:**
```json
{
  "total": 150,
  "sentiments": {
    "positive": 85,
    "neutral": 50,
    "negative": 15
  },
  "percentage": {
    "positive": 56.7,
    "neutral": 33.3,
    "negative": 10.0
  }
}
```

**cURL 예시:**
```bash
curl "http://localhost:8000/api/insights/sentiment?start_date=2025-01-01&end_date=2025-01-31"
```

---

### 8. GET `/api/insights/topics`

주제 추출 결과 조회

**Query Parameters:**
- `start_date` (string, optional): 시작일
- `end_date` (string, optional): 종료일
- `limit` (integer, optional): 최대 개수 (기본값: 10)

**Response:**
```json
{
  "topics": [
    {
      "topic": "FastAPI 프레임워크",
      "count": 42,
      "percentage": 28.0
    },
    {
      "topic": "LangChain 활용",
      "count": 35,
      "percentage": 23.3
    }
  ]
}
```

**cURL 예시:**
```bash
curl "http://localhost:8000/api/insights/topics?limit=5"
```

---

## 리포트 API

### 9. POST `/api/report/generate`

주간 운영 리포트 생성 (PDF)

**Request:**
```json
{
  "days": 7,
  "format": "pdf"
}
```

**Parameters:**
- `days` (integer, optional): 리포트 기간 (기본값: 7일)
- `format` (string, optional): 출력 형식 (`"pdf"`, 기본값)

**Response:**
```json
{
  "status": "success",
  "report_path": "reports/weekly_report_2025-01-23.pdf",
  "start_date": "2025-01-16",
  "end_date": "2025-01-23",
  "stats": {
    "conversations": 150,
    "sentiment": {
      "total": 150,
      "analyzed": 145
    },
    "feedback": {
      "total": 50,
      "likes": 42,
      "dislikes": 8
    }
  }
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/api/report/generate" \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

---

## 시스템 API

### 10. GET `/api/health`

시스템 헬스 체크 (DB 연결 확인 포함)

**Response:**
```json
{
  "status": "ok",
  "db_time": "2025-01-23 10:30:45.123456+00:00",
  "openai_key": true
}
```

**cURL 예시:**
```bash
curl "http://localhost:8000/api/health"
```

---

### 11. GET `/api/ping`

간단한 핑 엔드포인트

**Response:**
```json
{
  "message": "pong"
}
```

---

### 12. GET `/api/maintenance/status`

메인테넌스 모드 상태 확인

**Response:**
```json
{
  "maintenance": false
}
```

---

### 13. GET `/api/conversation/history`

대화 기록 조회

**Query Parameters:**
- `user_id` (string, optional): 사용자 ID
- `limit` (integer, optional): 최대 개수 (기본값: 50)
- `offset` (integer, optional): 오프셋 (기본값: 0)

**Response:**
```json
{
  "total": 150,
  "conversations": [
    {
      "id": 42,
      "user_id": "user123",
      "question": "FastAPI란 무엇인가요?",
      "answer": "FastAPI는 Python 3.6+ 기반의...",
      "sentiment": "positive",
      "topic": "FastAPI 프레임워크",
      "created_at": "2025-01-23T10:30:45.123456+00:00"
    }
  ]
}
```

**cURL 예시:**
```bash
curl "http://localhost:8000/api/conversation/history?user_id=user123&limit=10"
```

---

## Slack 통합 API

### 14. POST `/slack/ai-report`

Slack Slash Command 핸들러 - 주간 리포트 즉시 생성 및 업로드

**Request (Slack에서 자동 전송):**
```
token=verification_token_here
command=/ai-report
text=7
user_name=john.doe
channel_id=C05F2JH2JB0
```

**Response (Slack 메시지):**
```json
{
  "response_type": "in_channel",
  "text": "📊 AI 운영 리포트 생성 시작\n\n요청자: john.doe\n기간: 최근 7일\n\n잠시 후 채널에 업로드됩니다..."
}
```

**사용 방법:**
- Slack에서 `/ai-report` 입력 → 최근 7일 리포트
- Slack에서 `/ai-report 14` 입력 → 최근 14일 리포트
- Slack에서 `/ai-report 30` 입력 → 최근 30일 리포트

**주의사항:**
- `.env` 파일에 `SLACK_VERIFICATION_TOKEN` 설정 필요
- Slack App 설정에서 Request URL 등록 필요

---

## 에러 코드

### HTTP 상태 코드

| 코드 | 설명 | 예시 |
|------|------|------|
| `200` | 성공 | 정상 응답 |
| `400` | 잘못된 요청 | 필수 파라미터 누락 |
| `401` | 인증 실패 | 잘못된 Slack 검증 토큰 |
| `404` | 리소스 없음 | 존재하지 않는 conversation_id |
| `500` | 서버 오류 | 데이터베이스 연결 실패 |

### 에러 응답 형식

```json
{
  "detail": "Conversation not found",
  "error_code": "CONVERSATION_NOT_FOUND",
  "status_code": 404
}
```

---

## 사용 시나리오

### 시나리오 1: RAG 기반 Q&A 챗봇 구축

```python
import requests

# 1. 문서 임베딩
requests.post("http://localhost:8000/api/ingest", json={
    "text": "FastAPI는 빠르고 현대적인 Python 웹 프레임워크입니다.",
    "metadata": {"source": "fastapi_guide.txt"}
})

# 2. RAG 채팅
response = requests.post("http://localhost:8000/api/rag-chat", json={
    "question": "FastAPI의 특징은?",
    "user_id": "user123"
})

print(response.json()["answer"])

# 3. 피드백 제공
conv_id = response.json()["conversation_id"]
requests.post("http://localhost:8000/api/feedback", json={
    "conversation_id": conv_id,
    "feedback": "like"
})
```

### 시나리오 2: 주간 리포트 자동화

```python
import requests

# 1. 리포트 생성
report = requests.post("http://localhost:8000/api/report/generate", json={
    "days": 7
}).json()

print(f"리포트 생성 완료: {report['report_path']}")
print(f"총 대화: {report['stats']['conversations']}개")
print(f"만족도: {report['stats']['feedback']['likes']}/{report['stats']['feedback']['total']}")
```

### 시나리오 3: 실시간 분석 대시보드

```python
import requests

# 감정 분석
sentiment = requests.get("http://localhost:8000/api/insights/sentiment").json()
print(f"긍정: {sentiment['percentage']['positive']}%")

# 주제 분석
topics = requests.get("http://localhost:8000/api/insights/topics?limit=5").json()
for topic in topics['topics']:
    print(f"{topic['topic']}: {topic['count']}건")
```

---

## 추가 정보

- **API 문서 (Swagger UI)**: `http://localhost:8000/docs`
- **API 문서 (ReDoc)**: `http://localhost:8000/redoc`
- **시스템 아키텍처**: [system_flow.mmd](./system_flow.mmd)
- **GitHub**: https://github.com/space-cap/ai-career-6months

---

**Last Updated**: 2025-01-23
**Version**: 0.1.0
