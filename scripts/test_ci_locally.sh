#!/bin/bash
# Script to test GitLab CI/CD pipeline locally

# Don't exit on error - we want to continue and show all results
set +e

echo "=========================================="
echo "Testing GitLab CI/CD Pipeline Locally"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing uv...${NC}"
    pip install uv
fi

# Check if Node.js is installed (for frontend build)
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Warning: Node.js not found. Some tests may fail.${NC}"
fi

# Setup virtual environment
echo -e "${GREEN}Step 1: Setting up virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    uv venv || python -m venv .venv
else
    echo -e "${YELLOW}Virtual environment already exists, skipping creation...${NC}"
fi

# Activate virtual environment (Windows/Linux compatible)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo -e "${RED}Failed to find virtual environment activation script${NC}"
    exit 1
fi

# Install dependencies
echo -e "${GREEN}Step 2: Installing dependencies...${NC}"
if ! uv sync --frozen; then
    echo -e "${YELLOW}uv sync failed, trying pip install...${NC}"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo -e "${RED}requirements.txt not found. Please ensure dependencies are installed.${NC}"
        exit 1
    fi
fi

# Lint stage
echo -e "${GREEN}Step 3: Running lint checks...${NC}"
if command -v ruff &> /dev/null || uv run ruff --version &> /dev/null; then
    echo "Running ruff check..."
    uv run ruff check src/ tests/ || echo -e "${YELLOW}Ruff check completed with warnings${NC}"
    echo "Running ruff format check..."
    uv run ruff format --check src/ tests/ || echo -e "${YELLOW}Ruff format check completed with warnings${NC}"
else
    echo -e "${RED}Ruff not found. Skipping lint checks.${NC}"
fi

# Test stage (requires PostgreSQL)
echo -e "${GREEN}Step 4: Running tests...${NC}"
echo -e "${YELLOW}Note: Tests require PostgreSQL. Make sure it's running or use Docker.${NC}"

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    echo "PostgreSQL found. Running migrations..."
    cd src
    export DATABASE_URL="postgres://postgres:postgres@localhost:5432/djgramm_test"
    export SECRET_KEY="test-secret-key-for-ci"
    export DEBUG="True"
    export DJANGO_SETTINGS_MODULE="config.settings"

    uv run python manage.py migrate --noinput || echo -e "${YELLOW}Migration failed. Make sure PostgreSQL is running.${NC}"
    cd ..

    echo "Running pytest..."
    uv run pytest tests/ --cov=src/app --cov-report=term-missing -v || echo -e "${YELLOW}Tests completed with some failures${NC}"
else
    echo -e "${YELLOW}PostgreSQL not found. Skipping database tests.${NC}"
    echo "To run tests, start PostgreSQL or use Docker:"
    echo "  docker compose up -d db"
fi

# Django check
echo -e "${GREEN}Step 5: Running Django checks...${NC}"
cd src
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/djgramm_test"
export SECRET_KEY="test-secret-key-for-ci"
export DEBUG="True"
export DJANGO_SETTINGS_MODULE="config.settings"

uv run python manage.py check --deploy || echo -e "${YELLOW}Django check completed with warnings${NC}"
uv run python manage.py makemigrations --check --dry-run || echo -e "${YELLOW}Migration check completed${NC}"
cd ..

echo -e "${GREEN}=========================================="
echo "Local CI/CD test completed!"
echo "==========================================${NC}"
