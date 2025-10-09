# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Career 6 Months** is a 6-month career transition project for developers learning AI technologies. The project implements a FastAPI-based AI backend service using LangChain and Chroma VectorDB for RAG (Retrieval-Augmented Generation) capabilities. This is a Korean-language learning project focused on building practical AI chatbot and automation services.

## Development Setup

### Running the Application

```bash
# Install dependencies using pip
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run the FastAPI server (development mode with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Configuration

Create a `.env` file with the following required variables:
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM
- `MYSQL_URL`: MySQL connection string (default: `mysql://root:doolman@localhost:3306/ai_career`)
- `CHROMA_PATH`: Path to Chroma vector database directory (default: `./chroma_db`)

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

## Architecture

### Core Structure

The application follows a standard FastAPI modular architecture:

- **`app/main.py`**: FastAPI application entry point. Registers routers and defines the root endpoint.
- **`app/core/config.py`**: Centralized configuration using Pydantic settings. All environment variables are loaded here via `Settings` class.
- **`app/routers/`**: API route handlers organized by domain (currently `chat.py`).
- **`app/services/`**: Business logic and external service integrations:
  - `vectorstore.py`: Chroma VectorDB initialization and management
  - `retriever.py`: RAG retrieval logic (minimal implementation)

### Key Architectural Patterns

1. **Configuration Management**: Uses `pydantic-settings` with `.env` file loading. All settings accessed via `app.core.config.settings` singleton.

2. **VectorStore Initialization**: The `get_vectorstore()` function in `app/services/vectorstore.py:7` creates a Chroma instance with OpenAI embeddings. This is the foundation for RAG functionality.

3. **Router Registration**: Routers are registered in `app/main.py:11` with the `/api` prefix. All chat-related endpoints are under `/api/chat`.

### Technology Stack

- **Backend**: FastAPI 0.115+, Uvicorn with standard extras
- **AI/LLM**: LangChain 0.3+, LangGraph 0.1+, OpenAI 1.40+
- **VectorDB**: ChromaDB 0.5+ with OpenAI embeddings
- **Database**: MySQL via mysqlclient and SQLAlchemy 2.0+
- **Code Quality**: Black (line length 88), isort, flake8
- **Testing**: pytest with pytest-asyncio

### Current Implementation Status

The project is in early development:
- FastAPI server skeleton is complete
- Chroma VectorDB integration is functional
- Basic health check endpoints exist (`/api/ping`, `/api/vector-count`)
- RAG retrieval service exists but is not fully implemented
- No actual chat or LLM chain endpoints yet

## Python Version

Requires Python 3.11+ (specified in `pyproject.toml:10`). Black is configured to target Python 3.13 syntax.

## Database Notes

- MySQL is configured but not yet integrated into the application logic
- Chroma VectorDB stores embeddings in the local `./chroma_db` directory (or path specified in `.env`)
- The vector collection is named `"ai_career_docs"` (see `app/services/vectorstore.py:12`)
