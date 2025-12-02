#!/bin/bash
# Скрипт для локального тестування кроків з GitHub Actions CI/CD

set -e  # Зупинитися при помилці

echo "🧪 Тестування CI/CD кроків локально..."
echo ""

# Кольори для виводу
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функція для перевірки команди
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1 встановлено${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 не встановлено${NC}"
        return 1
    fi
}

# Перевірка залежностей
echo "📦 Перевірка залежностей..."
check_command "python3" || exit 1
check_command "pip" || exit 1
check_command "docker" || exit 1
echo ""

# 1. Перевірка YAML синтаксису
echo "📝 Перевірка YAML синтаксису..."
if command -v yamllint &> /dev/null; then
    yamllint .github/workflows/ci.yml && echo -e "${GREEN}✅ YAML синтаксис валідний${NC}" || echo -e "${RED}❌ Помилки в YAML${NC}"
else
    echo -e "${YELLOW}⚠️  yamllint не встановлено, пропускаємо перевірку${NC}"
fi
echo ""

# 2. Встановлення UV
echo "🔧 Встановлення UV..."
pip install uv --quiet
echo -e "${GREEN}✅ UV встановлено${NC}"
echo ""

# 3. Створення venv
echo "🐍 Створення віртуального оточення..."
if [ ! -d ".venv" ]; then
    uv venv
    echo -e "${GREEN}✅ Venv створено${NC}"
else
    echo -e "${YELLOW}⚠️  Venv вже існує${NC}"
fi

# Активування venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi
echo ""

# 4. Встановлення залежностей
echo "📚 Встановлення залежностей..."
uv sync --frozen
echo -e "${GREEN}✅ Залежності встановлено${NC}"
echo ""

# 5. Ruff check
echo "🔍 Запуск ruff check..."
if uv run ruff check src/ tests/; then
    echo -e "${GREEN}✅ Ruff check пройшов${NC}"
else
    echo -e "${RED}❌ Ruff check не пройшов${NC}"
    exit 1
fi
echo ""

# 6. Ruff format check
echo "🎨 Запуск ruff format check..."
if uv run ruff format --check src/ tests/; then
    echo -e "${GREEN}✅ Ruff format check пройшов${NC}"
else
    echo -e "${RED}❌ Ruff format check не пройшов${NC}"
    echo -e "${YELLOW}💡 Запустіть: uv run ruff format src/ tests/${NC}"
    exit 1
fi
echo ""

# 7. Перевірка Dockerfile
echo "🐳 Перевірка Dockerfile..."
if [ -f "docker/Dockerfile" ]; then
    echo -e "${GREEN}✅ Dockerfile знайдено${NC}"
    echo "🔨 Тестування збірки Docker образу..."
    if docker build -f docker/Dockerfile -t djgramm:test . --quiet; then
        echo -e "${GREEN}✅ Docker build успішний${NC}"
        docker rmi djgramm:test --quiet 2>/dev/null || true
    else
        echo -e "${RED}❌ Docker build не вдався${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Dockerfile не знайдено${NC}"
    exit 1
fi
echo ""

# 8. Django check (потребує БД)
echo "🔧 Перевірка Django..."
if docker ps | grep -q postgres-test || docker ps -a | grep -q postgres-test; then
    echo -e "${YELLOW}⚠️  PostgreSQL контейнер вже запущений${NC}"
else
    echo "🐘 Запуск PostgreSQL для тестів..."
    docker run -d \
        --name postgres-test \
        -e POSTGRES_DB=djgramm_test \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -p 5432:5432 \
        postgres:16-alpine \
        > /dev/null 2>&1

    echo "⏳ Очікування готовності PostgreSQL..."
    sleep 5
fi

export DATABASE_URL=postgres://postgres:postgres@localhost:5432/djgramm_test
export SECRET_KEY=test-secret-key-for-ci
export DEBUG=False

cd src

if uv run python manage.py check --deploy; then
    echo -e "${GREEN}✅ Django check пройшов${NC}"
else
    echo -e "${RED}❌ Django check не пройшов${NC}"
    cd ..
    docker stop postgres-test > /dev/null 2>&1 || true
    exit 1
fi

if uv run python manage.py makemigrations --check --dry-run; then
    echo -e "${GREEN}✅ Міграції перевірені${NC}"
else
    echo -e "${RED}❌ Проблеми з міграціями${NC}"
    cd ..
    docker stop postgres-test > /dev/null 2>&1 || true
    exit 1
fi

cd ..

# Зупинка PostgreSQL (опціонально)
read -p "Зупинити PostgreSQL контейнер? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker stop postgres-test > /dev/null 2>&1 || true
    docker rm postgres-test > /dev/null 2>&1 || true
    echo -e "${GREEN}✅ PostgreSQL контейнер зупинено${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Всі перевірки пройшли успішно!${NC}"
echo ""
echo "💡 Наступні кроки:"
echo "   1. Зробіть commit та push на GitHub"
echo "   2. Перевірте результат в Actions tab"
echo "   3. Або створіть Pull Request для автоматичного запуску"

