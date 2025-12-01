#!/bin/bash
set -e  # Exit immediately if any command fails

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running pre-CI checks${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 1. Formatting check
echo -e "${BLUE}[1/3] Checking code formatting...${NC}"
# Run ruff format and capture if any files were changed
uv run ruff format . > /tmp/ruff_output.txt 2>&1
if grep -q "reformatted" /tmp/ruff_output.txt; then
    echo -e "${RED}✗ Formatting check failed - files were reformatted${NC}"
    echo "Please review the changes and commit them."
    cat /tmp/ruff_output.txt
    rm /tmp/ruff_output.txt
    exit 1
fi
rm /tmp/ruff_output.txt
echo -e "${GREEN}✓ Formatting check passed${NC}"
echo

# 2. Type checking
echo -e "${BLUE}[2/3] Running type checks...${NC}"
uv run --all-groups mypy .
echo -e "${GREEN}✓ Type checking passed${NC}"
echo

# 3. Tests with coverage
echo -e "${BLUE}[3/3] Running tests with coverage...${NC}"
uv run -m pytest --cov --cov-fail-under=100 --cov-report term-missing
echo -e "${GREEN}✓ Tests passed with 100% coverage${NC}"
echo

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All checks passed! ✓${NC}"
echo -e "${GREEN}========================================${NC}"
