#!/bin/bash
# Script to test GitLab CI/CD pipeline using Docker (simulates CI environment)

set -e

echo "=========================================="
echo "Testing GitLab CI/CD Pipeline with Docker"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Start PostgreSQL if not running
if ! docker ps | grep -q postgres; then
    echo -e "${GREEN}Starting PostgreSQL container...${NC}"
    docker run -d \
        --name djgramm-postgres-test \
        -e POSTGRES_DB=djgramm_test \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -p 5433:5432 \
        postgres:16-alpine

    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
fi

# Run lint stage
echo -e "${GREEN}Running lint stage...${NC}"
docker run --rm \
    -v "$(pwd):/app" \
    -w /app \
    python:3.12-slim \
    bash -c "
        pip install uv &&
        uv venv &&
        source .venv/bin/activate &&
        uv sync --frozen &&
        uv run ruff check src/ tests/ &&
        uv run ruff format --check src/ tests/
    " || echo -e "${YELLOW}Lint stage completed with warnings${NC}"

# Run test stage
echo -e "${GREEN}Running test stage...${NC}"
docker run --rm \
    --link djgramm-postgres-test:postgres \
    -v "$(pwd):/app" \
    -w /app \
    -e DATABASE_URL='postgres://postgres:postgres@postgres:5432/djgramm_test' \
    -e SECRET_KEY='test-secret-key-for-ci' \
    -e DEBUG='True' \
    -e DJANGO_SETTINGS_MODULE='config.settings' \
    python:3.12-slim \
    bash -c "
        pip install uv &&
        uv venv &&
        source .venv/bin/activate &&
        uv sync --frozen &&
        cd src &&
        uv run python manage.py migrate --noinput &&
        cd .. &&
        uv run pytest tests/ --cov=src/app --cov-report=term-missing -v
    " || echo -e "${YELLOW}Test stage completed with some failures${NC}"

# Cleanup
echo -e "${GREEN}Cleaning up...${NC}"
docker stop djgramm-postgres-test &> /dev/null || true
docker rm djgramm-postgres-test &> /dev/null || true

echo -e "${GREEN}=========================================="
echo "Docker CI/CD test completed!"
echo "==========================================${NC}"

