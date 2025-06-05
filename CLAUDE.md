# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal diary/journal web application with a FastAPI backend and React frontend. It features a custom text-based diary format with sophisticated parsing capabilities and external system integration.

## Development Commands

### Backend Development
```bash
# Install dependencies
uv sync

# Run backend development server
uv run fastapi dev api/

# Database migrations
uv run alembic upgrade head

# User management CLI
uv run manage.py --help

# Diary ingestion script
uv run ingest.py --help

# Run tests
uv run pytest
uv run pytest tests/test_specific.py  # Run specific test file
uv run pytest -k "test_name"         # Run specific test

# Check code coverage
uv run -m pytest --cov --cov-fail-under=100 --cov-report term-missing

# Code formatting
uv run black .
```

### Frontend Development
```bash
# Setup (first time)
cd frontend
nvm install && nvm use
npm install

# Run frontend development server
cd frontend
nvm use
npm run dev

# Build frontend
npm run build

# Lint and format
npm run lint

# Generate API client (after backend changes)
./frontend/generate-client.sh
```

## Architecture

### Backend (Python)
- **Framework**: FastAPI with SQLModel/SQLAlchemy ORM
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT tokens with OAuth2 password flow
- **Key Components**:
  - `api/` - FastAPI routes and dependencies
  - `models/` - SQLModel data models
  - `parse.py` - Custom diary format parser using Lark grammar
  - `objects.py` - Diary entry data models (EVENT, DID, DIDN'T, NOTE, etc.)
  - `ingest.py` - Diary processing and external system sync

### Frontend (TypeScript/React)
- **Framework**: React 18 with TypeScript
- **Routing**: TanStack Router (file-based routing in `src/routes/`)
- **UI**: Chakra UI with Emotion styling
- **State Management**: TanStack Query for server state
- **Build Tool**: Vite
- **API Client**: Auto-generated from OpenAPI spec

### Custom Diary Format
The application parses a custom text-based diary format defined in `diary.lark`. The parser transforms text entries into structured objects with types like EVENT, DID, DIDN'T, NOTE, CANCELLED, POSTPONED.

## Development Workflow

1. **API Changes**: After modifying FastAPI routes, run `./frontend/generate-client.sh` to update the frontend client
2. **Database Changes**: Create migrations with `uv run alembic revision --autogenerate -m "description"`
3. **Testing**: Uses pytest with PostgreSQL containers and comprehensive fixtures for different user types
4. **Frontend**: File-based routing - add new pages in `frontend/src/routes/`

## Key Files
- `diary.lark` - Grammar definition for diary format parsing
- `pyproject.toml` - Python dependencies and project configuration
- `frontend/package.json` - Frontend dependencies and scripts
- `tests/conftest.py` - Test fixtures with superuser and normal user setups
- `alembic/` - Database migration files

## Testing Notes
- Tests use PostgreSQL containers via testservices
- Session-scoped fixtures create superuser and normal user for API testing
- Each test runs in a transaction that's rolled back for isolation
- Use `pytest-alembic` for migration testing
