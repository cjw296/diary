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
./tests_and_linting.sh

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
- `python/core/` - Core diary library
  - `src/diary/` - Source code using src layout
  - `tests/` - Test files
  - `pyproject.toml` - Package configuration with hatchling build backend
- `python/cli/` - CLI distribution
  - `src/diary_cli/` - Click-based CLI entrypoint
  - `tests/` - CLI tests
  - `pyproject.toml` - CLI package configuration (depends on core)
- `pyproject.toml` - Workspace configuration and dev dependencies

### Core Components (Python)
- **Parser**: Custom Lark-based parser for diary format
- **Key Components**:
  - `python/core/src/diary/parse.py` - Custom diary format parser using Lark grammar
  - `python/core/src/diary/objects.py` - Diary entry data models (EVENT, DID, DIDN'T, NOTE, etc.)
  - `python/core/src/diary/diary.lark` - Grammar definition for diary format
  - `python/core/src/diary/ingest.py` - Diary processing and external system sync
  - `python/core/src/diary/export.py` - Export diary entries
  - `python/core/src/diary/dump.py` - Shared utility for dumping periods to disk
  - `python/core/src/diary/zope.py` - Client for Zope blogging system integration
  - `python/core/src/diary/dates.py` - Date utility functions
  - `python/core/src/diary/config.py` - Configuration management
  - `python/cli/src/diary_cli/cli.py` - Click-based CLI entrypoint

### Custom Diary Format
The application parses a custom text-based diary format defined in `python/core/src/diary/diary.lark`. The parser transforms text entries into structured objects with types like EVENT, DID, DIDN'T, NOTE, CANCELLED, POSTPONED.

## Development Workflow

1. **Testing**: Uses pytest with testfixtures for testing parser, objects, and external integrations
2. **Type Checking**: All code must pass mypy type checking
3. **Formatting**: Use ruff for code formatting

## Code Quality Requirements

**CRITICAL: Before creating any commit, AI agents MUST run the following commands and fix all issues:**

### Type Annotations

**ALL functions and methods MUST have complete type annotations.**

- Every function parameter must have a type annotation
- Every function must have a return type annotation (use `-> None` for functions that don't return a value)
- Property methods, `__str__`, `__post_init__`, and other special methods all require type annotations
- Use `list[Any]` for Lark Transformer methods that receive children
- mypy is configured with `disallow_untyped_defs = true` and checks all of `python/` (source + tests)

**NOTE**: Test files have `disallow_untyped_defs` temporarily disabled while annotations are being added.
New test functions and fixtures MUST include proper type annotations (`-> None` for test functions,
`-> Iterator[Type]` for fixtures that yield).

```python
# CORRECT
def process_data(input: str, count: int = 0) -> list[str]:
    return input.split()

def save_file(path: Path) -> None:
    path.write_text("data")

# WRONG - missing annotations
def process_data(input, count=0):
    return input.split()

def save_file(path):
    path.write_text("data")
```

### Required Pre-commit Checks

Run the comprehensive test and linting script:
```bash
./tests_and_linting.sh
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

### Test Fixtures

**CRITICAL: A `replace` fixture is available in conftest.py for all tests. Always use it for mocking.**

- **Use the `replace` fixture for all mocking with testfixtures**:
  ```python
  # CORRECT - Use replace fixture with in_module
  def test_something(replace: Replacer) -> None:
      replace.in_module(date, mock_date(), module=diary.store)
      # ... test code ...

  # WRONG - Never use dotted string paths
  def test_something(replace: Replacer) -> None:
      replace.replace('diary.store.date', mock_date())  # NEVER DO THIS!

  # WRONG - Don't create Replacer() manually
  def test_something() -> None:
      with Replacer() as r:  # NEVER DO THIS - use the fixture!
          r.replace(...)
  ```

- **NEVER use dotted string paths with replace()**: Always use `replace.in_module(original, replacement, module=target_module)`
  - Dotted strings like `'diary.store.date'` are fragile and error-prone
  - Use `in_module()` for type safety and refactoring resilience
  - See testfixtures documentation for details on `in_module()` usage

### Test Docstrings

**DO NOT put docstrings on test functions and methods!**

Test function names should be self-documenting and descriptive enough that docstrings are unnecessary.

```python
# CORRECT - No docstring, descriptive name
def test_get_returns_none_for_nonexistent_date() -> None:
    store = MemoryStore()
    result = store.get(date(2024, 1, 15))
    compare(result, expected=None)

# WRONG - Has docstring
def test_get_nonexistent() -> None:
    """Test getting a period that doesn't exist."""
    store = MemoryStore()
    ...
```

Rationale: Docstrings in tests add noise and often just restate what the test name already says. Keep tests clean and focused.

### Assertions and Error Testing

**CRITICAL: Never use `assert` statements in tests. Always use `testfixtures.compare()` or `testfixtures.ShouldRaise()`.**

- **Use `testfixtures.compare()` for ALL equality assertions**: Provides better diff output than bare `assert` statements
  ```python
  # CORRECT - Complete object comparison, reusing variables, minimal parameters
  stuff = Stuff(type=Type.event, title="Test")  # Don't pass body=None, tags=None
  expected = Period(start=date(2024, 1, 15), stuff=[stuff], modified=date(2024, 12, 30))
  compare(result, expected=expected)

  # WRONG - Partial comparisons
  assert result is not None
  compare(result.start, expected=date(2024, 1, 15))
  compare(len(result.stuff), expected=1)

  # WRONG - Using assert
  assert result == expected_value
  assert some_condition

  # WRONG - Repeating defaults in parameters
  Stuff(type=Type.event, title="Test", body=None, tags=None)  # Verbose!
  ```

- **Always compare complete objects, not individual fields**: This catches unexpected changes in other fields
  - **Never pass parameters where the value is the default** - keeps tests minimal
  - Reuse object variables in both test setup and comparison for DRY tests
  - Use `testfixtures.Replacer()` with `test_date(delta=0)` to control `date.today()` for deterministic comparisons
  - Don't set timestamp fields on input objects - let the code under test set them
  - Only set timestamp fields in expected comparison objects
  - Never check individual attributes unless you have a specific reason

- **Use `testfixtures.ShouldRaise()` for exception testing**: More descriptive than `pytest.raises`
  ```python
  # CORRECT
  with ShouldRaise(ValueError("Specific error message")):
      function_that_should_fail()

  # WRONG
  with pytest.raises(ValueError, match="Specific error message"):
      function_that_should_fail()

  # WRONG
  try:
      function_that_should_fail()
      assert False, "Should have raised"
  except ValueError:
      pass
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
