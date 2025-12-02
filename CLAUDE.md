# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a command-line toolkit for managing a personal diary/journal. It features a custom text-based diary format with sophisticated parsing capabilities and external system integration for syncing with Zope-based blogging systems.

## Development Commands

```bash
# Install dependencies
uv sync

# Diary commands
uv run diary ingest --help
uv run diary export --help

# Run all pre-commit checks (formatting, type checking, tests)
./scripts/tests_and_linting.sh

# Run tests
cd python/core && uv run pytest
uv run pytest python/core/tests/test_specific.py  # Run specific test file
uv run pytest -k "test_name"                      # Run specific test

# Check code coverage
cd python/core && uv run -m pytest --cov --cov-fail-under=100 --cov-report term-missing

# Code formatting
uv run ruff format .

# Type checking
uv run --all-groups mypy python/core/src
```

## Architecture

### Project Structure
This project uses a uv workspace layout:
- `python/core/` - Main diary package
  - `src/diary/` - Source code using src layout
  - `tests/` - Test files
  - `pyproject.toml` - Package configuration with hatchling build backend
- `scripts/` - Utility scripts (tests_and_linting.sh)
- `pyproject.toml` - Workspace configuration and dev dependencies

### Core Components (Python)
- **Parser**: Custom Lark-based parser for diary format
- **Key Components**:
  - `python/core/src/diary/parse.py` - Custom diary format parser using Lark grammar
  - `python/core/src/diary/objects.py` - Diary entry data models (EVENT, DID, DIDN'T, NOTE, etc.)
  - `python/core/src/diary/diary.lark` - Grammar definition for diary format
  - `python/core/src/diary/cli.py` - Click-based CLI entrypoint
  - `python/core/src/diary/ingest.py` - Diary processing and external system sync
  - `python/core/src/diary/export.py` - Export diary entries
  - `python/core/src/diary/dump.py` - Shared utility for dumping periods to disk
  - `python/core/src/diary/zope.py` - Client for Zope blogging system integration
  - `python/core/src/diary/dates.py` - Date utility functions
  - `python/core/src/diary/config.py` - Configuration management

### Custom Diary Format
The application parses a custom text-based diary format defined in `python/core/src/diary/diary.lark`. The parser transforms text entries into structured objects with types like EVENT, DID, DIDN'T, NOTE, CANCELLED, POSTPONED.

## Development Workflow

1. **Testing**: Uses pytest with testfixtures for testing parser, objects, and external integrations
2. **Type Checking**: All code must pass mypy type checking
3. **Formatting**: Use ruff for code formatting

## Code Quality Requirements

**CRITICAL: Before creating any commit, AI agents MUST run the following commands and fix all issues:**

### Required Pre-commit Checks

Run the comprehensive test and linting script:
```bash
./scripts/tests_and_linting.sh
```

Or run individual checks:
```bash
# Format code (MUST be run first)
uv run ruff format .

# Type checking (MUST pass with no errors)
uv run --all-groups mypy python/core/src

# Run tests to ensure nothing is broken
cd python/core && uv run pytest
```

### Failure Handling
- If `ruff format` makes changes, those changes MUST be included in the commit
- If `mypy` reports any type errors, they MUST be fixed before committing
- If Python tests fail, they MUST be fixed before committing
- These checks are non-negotiable - commits should never be created with formatting, typing, or test issues

## Key Files
- `python/core/src/diary/diary.lark` - Grammar definition for diary format parsing
- `pyproject.toml` - Workspace configuration and dev dependencies
- `python/core/pyproject.toml` - Package configuration with hatchling build backend
- `python/core/tests/` - Test files
- `scripts/` - Command-line scripts

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
- Each test runs independently with no shared state
- Use testfixtures for better test assertions and error messages
- Mock external HTTP calls using the responses library
