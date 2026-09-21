#!/bin/bash
# Dhurandhar Server Runner Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
PRODUCTION=false
if [ "$1" == "--production" ]; then
    PRODUCTION=true
fi

echo -e "${BLUE}Starting Dhurandhar Flask API Server...${NC}"

# Ensure venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f ".venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    else
        echo -e "${RED}Error: Virtual environment not found. Please run ./scripts/setup.sh first.${NC}"
        exit 1
    fi
fi

# Change to the api directory
cd services/flask-api || { echo -e "${RED}Error: services/flask-api directory not found.${NC}"; exit 1; }

if [ "$PRODUCTION" = true ]; then
    echo -e "${GREEN}Running in PRODUCTION mode with gunicorn...${NC}"
    # Assuming app object is named 'app' in app.py
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    echo -e "${GREEN}Running in DEVELOPMENT mode...${NC}"
    export FLASK_APP=app.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python app.py
fi
