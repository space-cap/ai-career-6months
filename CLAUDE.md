# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Career 6 Months** is a 6-month career transition project for developers learning AI technologies. The project implements a production-ready FastAPI-based AI backend service using LangChain, Chroma VectorDB for RAG (Retrieval-Augmented Generation), and integrates with Slack for notifications. This is a Korean-language learning project focused on building practical AI chatbot, automation services, and analytics dashboards.

### Key Features

- **RAG-based Chat**: Personalized AI chatbot with context retrieval from vector database
- **Conversation Logging**: All user interactions logged to MySQL for analytics
- **Insights & Reports**: Sentiment analysis, topic extraction, and visual reports generation
- **Slack Integration**: Automated notifications for backups, alerts, and system events
- **Streamlit Dashboard**: Real-time analytics visualization
- **Automated Maintenance**: Scheduled cron jobs for DB backups and vectorstore retraining

## Development Setup

### Running the Application

```bash
# Install dependencies using pip
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run the FastAPI server (development mode with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run Streamlit dashboard
streamlit run dashboards/dashboard.py --server.port 8501
```

### Environment Configuration

Create a `.env` file with the following required variables:

**Core Settings:**
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM
- `DATABASE_URL`: MySQL connection string for production (Render uses this)
- `MYSQL_URL`: MySQL connection string for local development (default: `mysql://root:doolman@localhost:3306/ai_career`)
- `CHROMA_PATH`: Path to Chroma vector database directory (default: `./chroma_db`)

**Optional Settings:**
- `SLACK_WEBHOOK_URL`: Slack incoming webhook URL for notifications
- `ENV`: Environment flag (`production` or `development`)

### Code Quality Tools

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Run tests
pytest

# Run async tests
pytest -v
```

## Git Commit Guidelines

**모든 커밋 메시지는 한글로 작성합니다.**

커밋 메시지 형식:
- 제목: 변경 사항을 간결하게 설명 (한글)
- 본문: 상세한 변경 내역을 불릿 포인트로 나열 (한글)
- 푸터: Claude Code 서명 자동 추가

예시:
```
문서 임베딩 API 엔드포인트 추가

- app/routers/ingest.py: POST /api/ingest 엔드포인트 구현
- app/services/ingest_service.py: 문서 임베딩 서비스 로직 분리
- app/main.py: CORS 미들웨어 추가 및 ingest 라우터 등록

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Architecture

### Core Structure

The application follows a production-grade FastAPI modular architecture:

- **`app/main.py`**: FastAPI application entry point. Registers all routers, CORS middleware, and serves React frontend via StaticFiles.
- **`app/core/config.py`**: Centralized configuration using Pydantic settings. All environment variables loaded via `Settings` class.
- **`app/database.py`**: SQLAlchemy database engine and session management with connection pooling.
- **`app/routers/`**: API route handlers organized by domain:
  - `chat.py`: Basic chat endpoints with vector count and health checks
  - `rag_chat.py`: RAG-based personalized chat with context retrieval
  - `personal_chat.py`: User-specific personalized chat interactions
  - `ingest.py`: Document ingestion and embedding endpoints
  - `conversation.py`: Conversation history retrieval
  - `insights.py`: Analytics endpoints (sentiment analysis, topic extraction)
  - `report.py`: Report generation endpoints with matplotlib visualizations
  - `feedback.py`: User feedback collection API
  - `maintenance.py`: Maintenance mode status check
- **`app/services/`**: Business logic and external service integrations:
  - `vectorstore.py`: Chroma VectorDB initialization and management
  - `retriever.py`: RAG retrieval logic with semantic search
  - `llm_service.py`: OpenAI LLM integration and prompt management
  - `rag_service.py`: End-to-end RAG pipeline orchestration
  - `ingest_service.py`: Document processing and embedding workflow
  - `personalizer.py`: User preference learning and personalization
  - `conversation_logger.py`: Conversation logging to MySQL database
  - `analyzer.py`: Sentiment analysis and topic extraction
  - `slack_utils.py`: Slack webhook notification utilities
- **`scripts/`**: Utility and maintenance scripts:
  - `ingest_docs.py`: Batch document ingestion from `docs/` folder
  - `create_tables.py`: Database schema initialization
  - `backup_and_cleanup_db.py`: MySQL backup with log rotation and Slack notifications
  - `retrain_vectorstore.py`: Scheduled vectorstore retraining from database
- **`dashboards/`**: Streamlit analytics dashboards:
  - `dashboard.py`: Real-time conversation analytics and visualizations

### Key Architectural Patterns

1. **Configuration Management**: Uses `pydantic-settings` with `.env` file loading. All settings accessed via `app.core.config.settings` singleton. Supports both `DATABASE_URL` (production) and `MYSQL_URL` (development).

2. **VectorStore Initialization**: The `get_vectorstore()` function in `app/services/vectorstore.py:7` creates a Chroma instance with OpenAI embeddings. This is the foundation for RAG functionality.

3. **Router Registration**: Routers are registered in `app/main.py:26-33` with the `/api` prefix. Frontend SPA is served via StaticFiles mount at `/`.

4. **Database Session Management**: Uses SQLAlchemy 2.0 with `get_db()` dependency injection pattern. Connection pooling configured in `app/database.py`.

5. **Conversation Logging**: All chat interactions logged to `response_log` table via `conversation_logger.py` for analytics and personalization.

6. **Slack Notifications**: `slack_utils.py` provides `send_slack_message()` utility for sending formatted notifications to Slack channels.

### Technology Stack

- **Backend**: FastAPI 0.115+, Uvicorn with standard extras
- **Frontend**: React + Vite (served via FastAPI StaticFiles)
- **AI/LLM**: LangChain 0.3+, LangGraph 0.1+, OpenAI 1.40+
- **VectorDB**: ChromaDB 0.5+ with OpenAI embeddings
- **Database**: MySQL via mysqlclient and SQLAlchemy 2.0+, PostgreSQL support via psycopg2
- **Analytics**: pandas 2.3+, matplotlib 3.10+
- **Dashboard**: Streamlit 1.50+
- **Integrations**: Slack SDK, schedule library for cron jobs
- **Code Quality**: Black (line length 88), isort, flake8
- **Testing**: pytest with pytest-asyncio
- **Deployment**: Render.com (web services + cron jobs)

### Current Implementation Status

The project is in production deployment:
- ✅ FastAPI server with full CRUD operations
- ✅ Chroma VectorDB integration with document ingestion pipeline
- ✅ RAG-based chat with personalization
- ✅ MySQL database with conversation logging
- ✅ Sentiment analysis and topic extraction
- ✅ Report generation with matplotlib charts
- ✅ Slack notification system
- ✅ Streamlit analytics dashboard
- ✅ Automated DB backups with log rotation
- ✅ Scheduled vectorstore retraining
- ✅ React frontend integration
- ✅ Render.com deployment configuration

## Database Schema

### Primary Tables

- **`response_log`**: Stores all chat interactions
  - Fields: `id`, `user_query`, `bot_response`, `response_time`, `created_at`, `user_id`, `metadata`

- **`feedback_log`**: Stores user feedback
  - Fields: `id`, `conversation_id`, `feedback` (like/dislike), `reason`, `created_at`

- **`user_preferences`**: Stores personalization data
  - Fields: `user_id`, `preference_key`, `preference_value`, `updated_at`

### VectorDB Collections

- **`ai_career_docs`**: Main collection for document embeddings (see `app/services/vectorstore.py:12`)

## Deployment

### Render.com Configuration

The project is deployed on Render.com with the following services:

**Web Services:**
1. **Main API Server** (`ai-career-6months`)
   - Runtime: Python
   - Build: Install npm dependencies, build React frontend, install Python dependencies
   - Start: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables: `DATABASE_URL`, `OPENAI_API_KEY`, `CHROMA_PATH`, `SLACK_WEBHOOK_URL`

2. **Streamlit Dashboard** (`ai-dashboard`)
   - Runtime: Python
   - Start: `poetry run streamlit run dashboards/dashboard.py --server.port 10001 --server.address 0.0.0.0`

**Cron Jobs:**
- Daily DB backups (see `scripts/backup_and_cleanup_db.py`)
- Vectorstore retraining (see `scripts/retrain_vectorstore.py`)

### Pre-deployment Checks

Run the following scripts before deploying:

```bash
# Basic environment check
python deploy_check.py

# Production pre-flight check (comprehensive)
python deploy_preflight_check_pro.py
```

These scripts verify:
- Environment variables configuration
- Database connectivity
- OpenAI API connectivity
- VectorDB initialization
- Critical dependencies

## Python Version

Requires Python 3.11+ (specified in `pyproject.toml:10`). Black is configured to target Python 3.13 syntax.

## Maintenance & Operations

### Manual Tasks

**Ingest new documents:**
```bash
# Place .txt files in docs/ folder, then run:
poetry run python scripts/ingest_docs.py
```

**Create database tables:**
```bash
poetry run python scripts/create_tables.py
```

**Manual backup:**
```bash
poetry run python scripts/backup_and_cleanup_db.py
```

**Retrain vectorstore:**
```bash
poetry run python scripts/retrain_vectorstore.py
```

### Monitoring

- Check `/api/health` endpoint for system health status
- Check `/api/maintenance/status` for maintenance mode status
- View Streamlit dashboard for real-time analytics
- Slack notifications for critical events and backups

## API Endpoints Reference

### Core Endpoints
- `GET /api/health` - Health check with DB connectivity test
- `GET /api/ping` - Simple ping endpoint
- `GET /api/vector-count` - Get vectorstore document count

### Chat Endpoints
- `POST /api/chat` - Basic chat interaction
- `POST /api/rag-chat` - RAG-based chat with context retrieval
- `POST /api/personal-chat` - Personalized chat with user preferences

### Data Management
- `POST /api/ingest` - Ingest and embed documents
- `GET /api/conversation/history` - Retrieve conversation history
- `POST /api/feedback` - Submit user feedback

### Analytics
- `GET /api/insights/sentiment` - Get sentiment analysis
- `GET /api/insights/topics` - Get topic extraction
- `POST /api/report/generate` - Generate visual reports

### Maintenance
- `GET /api/maintenance/status` - Check maintenance mode status

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify `DATABASE_URL` or `MYSQL_URL` in `.env`
   - Check MySQL server is running
   - Run `scripts/create_tables.py` to initialize schema

2. **VectorDB Initialization Failures**:
   - Ensure `CHROMA_PATH` directory exists and has write permissions
   - Verify OpenAI API key is valid
   - Run `scripts/ingest_docs.py` to populate vectorstore

3. **Slack Notifications Not Working**:
   - Verify `SLACK_WEBHOOK_URL` is configured
   - Test with `app/services/slack_utils.py:send_slack_message()`

4. **Frontend Not Loading**:
   - Ensure `frontend/dist` directory exists
   - Run `cd frontend && npm install && npm run build`

## Learning Resources

The `docs/` folder contains week-by-week learning materials in Korean, covering:
- LangChain fundamentals
- RAG implementation
- FastAPI backend development
- Database integration
- Slack automation
- Deployment strategies
- Monitoring and maintenance
