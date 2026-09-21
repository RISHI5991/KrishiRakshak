#!/bin/bash
# Dhurandhar Setup Script
# Initializes the environment for the Flask API server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Dhurandhar Setup...${NC}"

# 1. Check Python version (requires 3.11+)
echo "Checking Python version..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$PY_VER < 3.11" | bc -l) )); then
        echo -e "${RED}Error: Python 3.11+ is required. Found $PY_VER${NC}"
        exit 1
    fi
    echo -e "${GREEN}Python $PY_VER found.${NC}"
else
    echo -e "${RED}Error: python3 not found.${NC}"
    exit 1
fi

# 2. Create virtual environment
echo "Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}Created .venv directory.${NC}"
else
    echo -e "${YELLOW}.venv already exists. Skipping creation.${NC}"
fi

source .venv/bin/activate

# 3. Install requirements
echo "Installing dependencies..."
if [ -f "services/flask-api/requirements.txt" ]; then
    pip install -r services/flask-api/requirements.txt
    echo -e "${GREEN}Dependencies installed.${NC}"
else
    echo -e "${YELLOW}Warning: services/flask-api/requirements.txt not found. Skipping pip install.${NC}"
fi

# 4. Verify model files
echo "Verifying model files..."
MODELS_DIR="models"
REQUIRED_MODELS=("AgriGuard_Model1_Final.keras" "AgriGuard_Model2_Final.keras" "m3_pest24_best.pt" "npk_vision_baseline_v1.pt" "m3_embedded_rf.joblib")

MISSING_MODELS=0
for model in "${REQUIRED_MODELS[@]}"; do
    if [ ! -f "$MODELS_DIR/$model" ]; then
        echo -e "${YELLOW}Warning: Model file $model is missing from $MODELS_DIR/${NC}"
        MISSING_MODELS=$((MISSING_MODELS + 1))
    fi
done

if [ $MISSING_MODELS -eq 0 ]; then
    echo -e "${GREEN}All required model files found.${NC}"
else
    echo -e "${YELLOW}Some model files are missing. Please download them as per models/README.md before running the server.${NC}"
fi

echo -e "\n${GREEN}Setup Complete!${NC}"
echo "To run the server, use: ./scripts/run-server.sh"
