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
uv run -m pytest --cov
uv run coverage report --show-missing

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

## Code Quality Requirements

**CRITICAL: Before creating any commit, AI agents MUST run the following commands and fix all issues:**

### Required Pre-commit Checks
```bash
# Format code (MUST be run first)
uv run ruff format .

# Type checking (MUST pass with no errors)
uv run mypy .

# Run tests to ensure nothing is broken
uv run pytest
```

### Failure Handling
- If `ruff format` makes changes, those changes MUST be included in the commit
- If `mypy` reports any type errors, they MUST be fixed before committing
- If tests fail, they MUST be fixed before committing
- These checks are non-negotiable - commits should never be created with formatting or typing issues

## Key Files
- `diary.lark` - Grammar definition for diary format parsing
- `pyproject.toml` - Python dependencies and project configuration
- `frontend/package.json` - Frontend dependencies and scripts
- `tests/conftest.py` - Test fixtures with superuser and normal user setups
- `alembic/` - Database migration files

## Testing Standards

### Test Structure
- **Use pytest fixtures instead of `setup_method`**: Create reusable fixtures for common test objects
- **Leverage fixture-based mocking**: Use pytest fixtures for external dependencies (e.g., `mocked_responses` for HTTP mocking)
- **Avoid complex function mocking**: Prefer real error-generating content over monkey-patching. If mocking is unavoidable, provide detailed documentation explaining why

### Assertions and Error Testing
- **Use `testfixtures.compare()` for equality assertions**: Provides better diff output than bare `assert` statements
  ```python
  # Preferred
  compare(result, expected={'key': 'value'})
  compare(periods, expected=[Period(start=date(2023, 1, 15), ...)])
  
  # Instead of
  assert result == {'key': 'value'}
  ```

- **Use `testfixtures.ShouldRaise()` for exception testing**: More descriptive than `pytest.raises`
  ```python
  # Preferred  
  with ShouldRaise(ValueError("Specific error message")):
      function_that_should_fail()
      
  # Instead of
  with pytest.raises(ValueError, match="Specific error message"):
      function_that_should_fail()
  ```

### HTTP Testing
- **Use `responses` library via fixtures**: Mock HTTP interactions cleanly without decorators
- **Verify authentication data**: Always check that HTTP Basic Auth credentials are passed correctly
- **Test both success and error scenarios**: Include status code validation and error handling

### Coverage Goals
- **Aim for 100% code coverage** on new modules
- **Test edge cases and error paths**: Include boundary conditions and exception handling
- **Document any untestable code**: If certain code paths cannot be tested, explain why in comments

## Testing Notes
- Tests use PostgreSQL containers via testservices
- Session-scoped fixtures create superuser and normal user for API testing
- Each test runs in a transaction that's rolled back for isolation
- Use `pytest-alembic` for migration testing
