@echo off
REM Скрипт для локального тестування кроків з GitHub Actions CI/CD (Windows)

echo 🧪 Тестування CI/CD кроків локально...
echo.

REM Перевірка залежностей
echo 📦 Перевірка залежностей...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python не встановлено
    exit /b 1
)
echo ✅ Python встановлено

where pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip не встановлено
    exit /b 1
)
echo ✅ pip встановлено

where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker не встановлено
    exit /b 1
)
echo ✅ Docker встановлено
echo.

REM Встановлення UV
echo 🔧 Встановлення UV...
pip install uv --quiet
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Не вдалося встановити UV
    exit /b 1
)
echo ✅ UV встановлено
echo.

REM Створення venv
echo 🐍 Створення віртуального оточення...
if not exist ".venv" (
    uv venv
    echo ✅ Venv створено
) else (
    echo ⚠️  Venv вже існує
)
echo.

REM Активування venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Встановлення залежностей
echo 📚 Встановлення залежностей...
uv sync --frozen
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Не вдалося встановити залежності
    exit /b 1
)
echo ✅ Залежності встановлено
echo.

REM Ruff check
echo 🔍 Запуск ruff check...
uv run ruff check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ruff check не пройшов
    exit /b 1
)
echo ✅ Ruff check пройшов
echo.

REM Ruff format check
echo 🎨 Запуск ruff format check...
uv run ruff format --check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ruff format check не пройшов
    echo 💡 Запустіть: uv run ruff format src/ tests/
    exit /b 1
)
echo ✅ Ruff format check пройшов
echo.

REM Перевірка Dockerfile
echo 🐳 Перевірка Dockerfile...
if not exist "docker\Dockerfile" (
    echo ❌ Dockerfile не знайдено
    exit /b 1
)
echo ✅ Dockerfile знайдено

echo 🔨 Тестування збірки Docker образу...
docker build -f docker/Dockerfile -t djgramm:test . >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build не вдався
    exit /b 1
)
echo ✅ Docker build успішний
docker rmi djgramm:test >nul 2>&1
echo.

REM Django check
echo 🔧 Перевірка Django...
docker ps | findstr postgres-test >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  PostgreSQL контейнер вже запущений
) else (
    echo 🐘 Запуск PostgreSQL для тестів...
    docker run -d --name postgres-test -e POSTGRES_DB=djgramm_test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine >nul 2>&1
    echo ⏳ Очікування готовності PostgreSQL...
    timeout /t 5 /nobreak >nul
)

set DATABASE_URL=postgres://postgres:postgres@localhost:5432/djgramm_test
set SECRET_KEY=test-secret-key-for-ci
set DEBUG=False

cd src

uv run python manage.py check --deploy
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Django check не пройшов
    cd ..
    docker stop postgres-test >nul 2>&1
    exit /b 1
)
echo ✅ Django check пройшов

uv run python manage.py makemigrations --check --dry-run
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Проблеми з міграціями
    cd ..
    docker stop postgres-test >nul 2>&1
    exit /b 1
)
echo ✅ Міграції перевірені

cd ..

REM Зупинка PostgreSQL
set /p STOP_DB="Зупинити PostgreSQL контейнер? (y/n) "
if /i "%STOP_DB%"=="y" (
    docker stop postgres-test >nul 2>&1
    docker rm postgres-test >nul 2>&1
    echo ✅ PostgreSQL контейнер зупинено
)

echo.
echo 🎉 Всі перевірки пройшли успішно!
echo.
echo 💡 Наступні кроки:
echo    1. Зробіть commit та push на GitHub
echo    2. Перевірте результат в Actions tab
echo    3. Або створіть Pull Request для автоматичного запуску

