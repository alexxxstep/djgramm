@echo off
REM Script to test GitLab CI/CD pipeline locally on Windows

echo ==========================================
echo Testing GitLab CI/CD Pipeline Locally
echo ==========================================

REM Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing uv...
    pip install uv
)

REM Setup virtual environment
echo Step 1: Setting up virtual environment...
if not exist .venv (
    uv venv || python -m venv .venv
)
call .venv\Scripts\activate.bat

REM Install dependencies
echo Step 2: Installing dependencies...
uv sync --frozen || pip install -r requirements.txt

REM Lint stage
echo Step 3: Running lint checks...
uv run ruff check src/ tests/ || echo Ruff check completed with warnings
uv run ruff format --check src/ tests/ || echo Ruff format check completed with warnings

REM Test stage
echo Step 4: Running tests...
echo Note: Tests require PostgreSQL. Make sure it's running or use Docker.

cd src
set DATABASE_URL=postgres://postgres:postgres@localhost:5432/djgramm_test
set SECRET_KEY=test-secret-key-for-ci
set DEBUG=True
set DJANGO_SETTINGS_MODULE=config.settings

uv run python manage.py migrate --noinput || echo Migration failed. Make sure PostgreSQL is running.
cd ..

uv run pytest tests/ --cov=src/app --cov-report=term-missing -v || echo Tests completed with some failures

REM Django check
echo Step 5: Running Django checks...
cd src
uv run python manage.py check --deploy || echo Django check completed with warnings
uv run python manage.py makemigrations --check --dry-run || echo Migration check completed
cd ..

echo ==========================================
echo Local CI/CD test completed!
echo ==========================================
