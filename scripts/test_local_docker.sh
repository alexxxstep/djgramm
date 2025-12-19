#!/bin/bash
# Скрипт для тестування локального Docker проекту

set -e

echo "=========================================="
echo "Local Docker Testing"
echo "=========================================="
echo ""

# Кольори
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Перевірка статусу контейнерів
echo -e "${BLUE}=== 1. Container Status ===${NC}"
docker compose ps

echo ""
echo -e "${BLUE}=== 2. Health Check ===${NC}"
HEALTH=$(curl -s http://localhost:9000/health/ || echo "FAILED")
if [ "$HEALTH" = "OK" ]; then
    echo -e "${GREEN}✓ Health check: OK${NC}"
else
    echo -e "${RED}✗ Health check: FAILED${NC}"
fi

echo ""
echo -e "${BLUE}=== 3. Django Check ===${NC}"
docker compose exec -T web uv run python manage.py check 2>&1 | grep -E "(System check|issues|ERROR)" || echo "Check completed"

echo ""
echo -e "${BLUE}=== 4. Frontend Files ===${NC}"
echo "Checking frontend/dist files:"
docker compose exec -T web ls -lh /app/frontend/dist/*.js /app/frontend/dist/*.css 2>/dev/null | head -10 || echo "Frontend files not found"

echo ""
echo -e "${BLUE}=== 5. Static Files ===${NC}"
echo "Checking staticfiles:"
docker compose exec -T web ls -lh /app/staticfiles/ 2>/dev/null | head -10 || echo "Staticfiles directory not found"

echo ""
echo -e "${BLUE}=== 6. Web Server Response ===${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/ || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Web server: OK (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Web server: FAILED (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}=== 7. Recent Logs ===${NC}"
docker compose logs web --tail=20 | grep -E "(Starting|Listening|ERROR|WARNING)" || echo "No errors found"

echo ""
echo -e "${GREEN}=========================================="
echo "Testing Complete"
echo "==========================================${NC}"

