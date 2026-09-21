#!/bin/bash
# Run all tests and linters for Dhurandhar

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Running Dhurandhar Test Suite..."

# Ensure venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run Linting
echo "Running flake8 linting..."
if command -v flake8 &>/dev/null; then
    flake8 services/flask-api/ --count --select=E9,F63,F7,F82 --show-source --statistics || { echo -e "${RED}Linting failed.${NC}"; exit 1; }
    echo -e "${GREEN}Linting passed.${NC}"
else
    echo -e "${RED}flake8 not found. Skipping linting.${NC}"
fi

# Run Tests
echo "Running pytest..."
if command -v pytest &>/dev/null; then
    cd services/flask-api
    pytest || { echo -e "${RED}Tests failed.${NC}"; exit 1; }
    cd ../..
    echo -e "${GREEN}All tests passed.${NC}"
else
    echo -e "${RED}pytest not found. Skipping tests.${NC}"
fi

echo -e "\n${GREEN}Test suite completed successfully.${NC}"
