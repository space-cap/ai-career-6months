![AI Career 6 Months Banner](docs/banner_1.png)

# 🚀 AI Career 6 Months
> 나의 커리어를 AI로 다시 세운 6개월의 기록

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://www.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791.svg)](https://neon.tech/)

---

## 🧠 Overview

**AI Career 6 Months**는 개발자가 6개월 동안
AI 기술을 실무 수준으로 익히고 **AI 챗봇 / 자동화 / RAG 기반 서비스 개발자**로 전환하기 위한
자기주도형 커리어 전환 프로젝트입니다.

이 프로젝트는 학습, 실습, 배포, 포트폴리오까지 이어지는
**완전한 6개월 로드맵**으로 구성되어 있습니다.

### ✨ 주요 기능

- 🤖 **RAG 기반 AI 챗봇**: ChromaDB VectorStore를 활용한 검색 증강 생성
- 📊 **실시간 분석**: 감정 분석, 주제 추출, 대화 통계
- 📄 **자동 리포트**: PDF 주간 운영 리포트 자동 생성
- 💬 **Slack 통합**: Slash Command (`/ai-report`)로 즉시 리포트 생성
- 📈 **관리자 대시보드**: Streamlit 기반 실시간 모니터링 및 시각화
- 🔄 **자동화**: DB 백업, 시스템 모니터링, 피드백 루프 스케줄링
- 🎯 **개인화**: 사용자 선호도 학습 및 맞춤형 응답 제공
- 👍 **피드백 시스템**: 좋아요/싫어요 수집 및 분석

---

## 📅 Roadmap Summary

| 단계 | 기간 | 목표 | 주요 기술 |
|------|------|------|------------|
| 1단계 | 1~4주 | FastAPI + LangChain 기초 학습 | Python, FastAPI, LangChain |
| 2단계 | 5~10주 | AI 서비스 실무 프로젝트 제작 | OpenAI API, Chroma, PostgreSQL |
| 3단계 | 11~16주 | 서비스 배포 + 포트폴리오 구축 | Render, Docker, Slack |
| 4단계 | 17~24주 | 수익화 + 커리어 확장 | GitHub, Notion, 크몽/위시켓 |

---

## 🧩 Tech Stack

| Category | Tools / Frameworks |
|-----------|-------------------|
| **Language** | Python 3.11+, JavaScript (ES6+) |
| **Backend** | FastAPI 0.115+, LangChain 0.3+, LangGraph 0.1+ |
| **Database** | PostgreSQL (Neon DB), ChromaDB (VectorStore) |
| **Frontend** | React 18+, Vite 5+ |
| **AI/LLM** | OpenAI GPT-4, OpenAI Embeddings |
| **Analytics** | Streamlit 1.50+, pandas 2.3+, matplotlib 3.10+ |
| **Integration** | Slack SDK, Slack Webhooks |
| **Infra** | Render.com, Docker |
| **Dev Tools** | Poetry, Black, isort, flake8, pytest |

---

## 📂 Project Structure

```text
ai-career-6months/
│
├── app/                       # FastAPI 애플리케이션
│   ├── main.py                  # 엔트리포인트
│   ├── core/
│   │   └── config.py            # 환경 설정
│   ├── routers/                 # API 라우터
│   │   ├── chat.py              # 기본 채팅
│   │   ├── rag_chat.py          # RAG 채팅
│   │   ├── personal_chat.py     # 개인화 채팅
│   │   ├── ingest.py            # 문서 임베딩
│   │   ├── feedback.py          # 피드백 수집
│   │   ├── insights.py          # 분석 API
│   │   ├── report.py            # 리포트 생성
│   │   ├── conversation.py      # 대화 기록
│   │   └── maintenance.py       # 메인테넌스
│   ├── services/                # 비즈니스 로직
│   │   ├── vectorstore.py       # VectorDB 관리
│   │   ├── llm_service.py       # LLM 서비스
│   │   ├── rag_service.py       # RAG 파이프라인
│   │   ├── analyzer.py          # 감정/주제 분석
│   │   └── personalizer.py      # 개인화 엔진
│   ├── utils/                   # 유틸리티
│   │   ├── report_generator.py  # PDF 리포트 생성
│   │   ├── slack_uploader.py    # Slack 파일 업로드
│   │   ├── slack_command_handler.py # Slack Slash Command
│   │   ├── backup_manager.py    # DB 백업
│   │   └── monitor.py           # 시스템 모니터링
│   ├── models/                  # SQLAlchemy 모델
│   │   ├── conversation_log.py
│   │   └── feedback_log.py
│   └── database.py              # DB 연결
│
├── frontend/                  # React + Vite 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
│
├── dashboards/                # Streamlit 대시보드
│   ├── dashboard.py             # 메인 대시보드
│   └── admin_dashboard.py       # 관리자 대시보드
│
├── scripts/                   # 자동화 스크립트
│   ├── ingest_docs.py           # 문서 일괄 임베딩
│   ├── create_tables.py         # DB 테이블 생성
│   ├── backup_and_cleanup_db.py # DB 백업 및 정리
│   └── retrain_vectorstore.py   # VectorStore 재학습
│
├── docs/                      # 문서 및 다이어그램
│   ├── api_reference.md         # API 레퍼런스
│   ├── system_flow.mmd          # 시스템 아키텍처 (Mermaid)
│   └── task_schedule/           # 주차별 학습 자료
│
├── notebooks/                 # Jupyter 실험 노트북
├── chroma_db/                 # ChromaDB 데이터
├── reports/                   # 생성된 PDF 리포트
├── logs/                      # 로그 파일
├── .env                       # 환경변수 (git ignored)
├── pyproject.toml             # Poetry 의존성
├── render.yaml                # Render 배포 설정
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL (또는 Neon DB 계정)
- OpenAI API Key
- (선택) Slack Workspace

### 2. Installation

```bash
# 저장소 클론
git clone https://github.com/space-cap/ai-career-6months.git
cd ai-career-6months

# 의존성 설치
pip install -e .

# 개발 의존성 설치 (선택)
pip install -e ".[dev]"
```

### 3. Environment Setup

`.env` 파일 생성:

```env
# 필수 환경변수
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:password@host:5432/dbname
CHROMA_PATH=./chroma_db

# Slack 통합 (선택)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=C05F2JH2JB0
SLACK_VERIFICATION_TOKEN=...

# 스케줄러 설정 (선택)
MONITOR_INTERVAL_MINUTES=30
BACKUP_TIME=00:00
BACKUP_RETENTION_DAYS=7
LOG_RETENTION_DAYS=30
```

### 4. Database Initialization

```bash
# 테이블 생성
python scripts/create_tables.py

# 샘플 문서 임베딩
python scripts/ingest_docs.py
```

### 5. Run Services

**FastAPI 백엔드:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 헬스 체크: http://localhost:8000/api/health

**Streamlit 대시보드:**
```bash
streamlit run dashboards/admin_dashboard.py --server.port 8501
```

- 대시보드: http://localhost:8501

**React 프론트엔드 (개발 모드):**
```bash
cd frontend
npm install
npm run dev
```

- 웹 UI: http://localhost:5173

---

## 📡 API Endpoints

전체 14개 엔드포인트 제공:

### 채팅 API
- `POST /api/chat` - 기본 채팅
- `POST /api/rag-chat` - RAG 기반 채팅
- `POST /api/personal-chat` - 개인화 채팅

### 문서 관리
- `POST /api/ingest` - 문서 임베딩
- `GET /api/vector-count` - VectorDB 문서 수

### 피드백
- `POST /api/feedback` - 좋아요/싫어요 수집

### 분석
- `GET /api/insights/sentiment` - 감정 분석 결과
- `GET /api/insights/topics` - 주제 추출 결과

### 리포트
- `POST /api/report/generate` - PDF 리포트 생성

### 시스템
- `GET /api/health` - 헬스 체크
- `GET /api/ping` - 핑
- `GET /api/maintenance/status` - 메인테넌스 상태
- `GET /api/conversation/history` - 대화 기록

### Slack 통합
- `POST /slack/ai-report` - Slack Slash Command

자세한 내용은 [API Reference](docs/api_reference.md) 참조

---

## 🏗️ System Architecture

전체 시스템 아키텍처는 [system_flow.mmd](docs/system_flow.mmd)에서 확인하세요.

**주요 컴포넌트:**
- FastAPI Backend (8개 라우터, 7개 핵심 서비스)
- PostgreSQL (Neon DB) - 대화 기록, 피드백
- ChromaDB - 문서 임베딩 VectorStore
- OpenAI API - GPT-4 & Embeddings
- Slack - 알림 & Slash Command
- Streamlit - 실시간 대시보드

---

## 💬 Slack Integration

### Slash Command 설정

1. Slack App 생성 및 Slash Command 추가
2. Command: `/ai-report`
3. Request URL: `https://your-domain.com/slack/ai-report`
4. `.env`에 `SLACK_VERIFICATION_TOKEN` 추가

### 사용 방법

```
/ai-report          → 최근 7일 리포트 생성
/ai-report 14       → 최근 14일 리포트 생성
/ai-report 30       → 최근 30일 리포트 생성
```

리포트는 백그라운드에서 생성되어 Slack 채널에 자동 업로드됩니다.

---

## 🔄 Automation & Monitoring

### 자동화 작업

**스케줄러 실행:**
```bash
python app/scheduler_monitor.py
```

**자동 실행 작업:**
- 매일 자정: PostgreSQL 백업 및 로그 정리
- 30분마다: 시스템 리소스 모니터링
- 주 1회: VectorStore 재학습 (선택)

### 백업 관리

**수동 백업:**
```bash
python scripts/backup_and_cleanup_db.py
```

백업 파일은 `backups/` 디렉토리에 저장되며, 7일 후 자동 삭제됩니다.

---

## 📊 Analytics Dashboard

Streamlit 대시보드 기능:

**4개 주요 탭:**
1. **대화 추이** - 일별 대화 수 및 사용자 수 라인 차트
2. **감정 분석** - 감정별 분포 및 비율 분석
3. **피드백 통계** - 좋아요/싫어요 추이 및 만족도
4. **주제 분석** - 주제별 분포 상위 20개

**KPI 메트릭:**
- 총 대화 수
- 고유 사용자 수
- 감정 분석 완료율

---

## 🚢 Deployment

### Render.com 배포

1. GitHub 저장소 연결
2. `render.yaml` 설정 확인
3. 환경변수 설정
4. 자동 배포

**배포된 서비스:**
- Web Service: FastAPI 백엔드
- Cron Jobs: DB 백업, 모니터링
- PostgreSQL: Neon DB (외부)

### 배포 전 체크리스트

```bash
# 환경 변수 확인
python deploy_check.py

# 프로덕션 사전 점검
python deploy_preflight_check_pro.py
```

---

## 🎯 Goals & Roadmap

### 완료된 기능 ✅

* [x] FastAPI & LangChain 기반 AI 서버 구축
* [x] RAG (Retrieval-Augmented Generation) 구조 구현
* [x] PostgreSQL + ChromaDB VectorStore 통합
* [x] 감정 분석 & 주제 추출 자동화
* [x] PDF 리포트 자동 생성 시스템
* [x] Slack 통합 (Webhook, Slash Command)
* [x] Streamlit 실시간 대시보드
* [x] DB 백업 & 시스템 모니터링 자동화
* [x] 피드백 수집 및 분석 시스템
* [x] React 프론트엔드 통합
* [x] Render.com 프로덕션 배포

### 진행 중 🚧

* [ ] 사용자 인증 시스템 (JWT)
* [ ] 다국어 지원 (i18n)
* [ ] API Rate Limiting
* [ ] 캐싱 레이어 (Redis)

### 계획 중 📋

* [ ] 첫 수익 또는 프로젝트 제안 확보
* [ ] AI 기술 블로그/강의 콘텐츠 제작
* [ ] 모바일 앱 (React Native)

---

## 📖 Documentation

- [API Reference](docs/api_reference.md) - 전체 API 엔드포인트 문서
- [System Architecture](docs/system_flow.mmd) - 시스템 아키텍처 다이어그램
- [Learning Materials](docs/task_schedule/) - 주차별 학습 자료 (5-16주차)

---

## 🧪 Testing

```bash
# 단위 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/

# 비동기 테스트
pytest -v
```

---

## 🔧 Development

### Code Quality

```bash
# 코드 포맷팅
black .

# Import 정렬
isort .

# 린트 체크
flake8 .
```

### Git Commit

모든 커밋 메시지는 **한글**로 작성합니다.

```
문서 임베딩 API 엔드포인트 추가

- app/routers/ingest.py: POST /api/ingest 엔드포인트 구현
- app/services/ingest_service.py: 문서 임베딩 서비스 로직 분리

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 🛠️ Troubleshooting

### 자주 발생하는 문제

**1. Database Connection Error**
```bash
# DATABASE_URL 확인
# PostgreSQL 서버 실행 확인
python scripts/create_tables.py
```

**2. VectorDB Initialization Failed**
```bash
# CHROMA_PATH 디렉토리 생성
mkdir -p chroma_db

# OpenAI API Key 확인
echo $OPENAI_API_KEY

# 문서 재임베딩
python scripts/ingest_docs.py
```

**3. Slack Notifications Not Working**
```bash
# SLACK_WEBHOOK_URL 확인
# Slack 채널 ID 확인 (C05F2JH2JB0)
```

---

## 🧭 Links

* 📗 **Notion Roadmap**: [AI 커리어 전환 6개월 로드맵](#)
* 💻 **Live Demo**: (추가 예정)
* 📊 **Dashboard**: (추가 예정)
* 🐙 **GitHub**: https://github.com/space-cap/ai-career-6months
* 📬 **Contact**: (email 또는 LinkedIn)

---

## 🤝 Contributing

이 프로젝트는 개인 학습 프로젝트이지만, 기여는 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (한글 커밋 메시지)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Feel free to fork, learn, and build your own 6-month journey.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적이고 빠른 Python 웹 프레임워크
- [LangChain](https://www.langchain.com/) - LLM 애플리케이션 개발 프레임워크
- [OpenAI](https://openai.com/) - GPT-4 & Embeddings API
- [Neon](https://neon.tech/) - Serverless PostgreSQL
- [Render](https://render.com/) - 클라우드 플랫폼

---

⭐ **AI Career 6 Months**

> "배움에는 늦음이 없다.
> 나이 대신, 다음을 선택하자."

---

**Last Updated**: 2025-01-23
**Version**: 0.1.0
