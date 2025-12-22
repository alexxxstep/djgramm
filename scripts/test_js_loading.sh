#!/bin/bash
# Тест завантаження JavaScript файлів

set -e

echo "=========================================="
echo "JavaScript Loading Test"
echo "=========================================="
echo ""

# Кольори
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Перевірка main.js в frontend/dist
echo -e "${BLUE}=== 1. Checking frontend/dist/main.js ===${NC}"
if docker compose exec -T web test -f /app/frontend/dist/main.js; then
    SIZE=$(docker compose exec -T web stat -c%s /app/frontend/dist/main.js 2>/dev/null || echo 0)
    echo -e "${GREEN}✓ main.js found in frontend/dist ($SIZE bytes)${NC}"
else
    echo -e "${RED}✗ main.js NOT found in frontend/dist${NC}"
    exit 1
fi

# 2. Перевірка main.js в staticfiles
echo ""
echo -e "${BLUE}=== 2. Checking staticfiles/main.js ===${NC}"
if docker compose exec -T web test -f /app/staticfiles/main.js; then
    SIZE=$(docker compose exec -T web stat -c%s /app/staticfiles/main.js 2>/dev/null || echo 0)
    echo -e "${GREEN}✓ main.js found in staticfiles ($SIZE bytes)${NC}"
else
    echo -e "${YELLOW}⚠ main.js NOT in staticfiles (served from STATICFILES_DIRS)${NC}"
fi

# 3. Перевірка через Django findstatic
echo ""
echo -e "${BLUE}=== 3. Django findstatic ===${NC}"
RESULT=$(docker compose exec -T web uv run python manage.py findstatic main.js 2>&1)
if echo "$RESULT" | grep -q "Found"; then
    echo -e "${GREEN}✓ Django can find main.js${NC}"
    echo "$RESULT" | grep "Found"
else
    echo -e "${RED}✗ Django cannot find main.js${NC}"
    echo "$RESULT"
fi

# 4. HTTP перевірка
echo ""
echo -e "${BLUE}=== 4. HTTP Access Test ===${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/static/main.js || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    SIZE=$(curl -s http://localhost:9000/static/main.js | wc -c)
    echo -e "${GREEN}✓ main.js accessible via HTTP ($HTTP_CODE, $SIZE bytes)${NC}"
else
    echo -e "${RED}✗ main.js NOT accessible via HTTP ($HTTP_CODE)${NC}"
fi

# 5. Перевірка в HTML
echo ""
echo -e "${BLUE}=== 5. HTML Template Check ===${NC}"
HTML_CHECK=$(curl -s http://localhost:9000/ | grep -o 'src="[^"]*main\.js[^"]*"' || echo "")
if [ -n "$HTML_CHECK" ]; then
    echo -e "${GREEN}✓ main.js referenced in HTML${NC}"
    echo "   $HTML_CHECK"
else
    echo -e "${YELLOW}⚠ main.js not found in HTML (may be loaded dynamically)${NC}"
fi

# 6. Перевірка вмісту файлу
echo ""
echo -e "${BLUE}=== 6. File Content Check ===${NC}"
CONTENT=$(curl -s http://localhost:9000/static/main.js | head -5)
if echo "$CONTENT" | grep -qE "(function|var|const|import|export)"; then
    echo -e "${GREEN}✓ main.js contains valid JavaScript${NC}"
    echo "   First 5 lines:"
    echo "$CONTENT" | sed 's/^/   /'
else
    echo -e "${RED}✗ main.js may be empty or invalid${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Test Complete"
echo "==========================================${NC}"

