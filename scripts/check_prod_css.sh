#!/bin/bash
# Production CSS verification script
# Run this on the server after deployment to verify CSS is working

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "Production CSS Verification"
echo "==========================================${NC}"
echo ""

# Check if container is running
if ! docker compose -f docker-compose.prod.yml ps web | grep -q "Up"; then
    echo -e "${RED}ERROR: Web container is not running!${NC}"
    exit 1
fi

echo -e "${BLUE}=== Checking CSS in container ===${NC}"

# Check 1: CSS file exists and size
echo -e "${YELLOW}1. CSS file check...${NC}"
if docker compose -f docker-compose.prod.yml exec -T web test -f /app/staticfiles/styles.css; then
    CSS_SIZE=$(docker compose -f docker-compose.prod.yml exec -T web stat -c%s /app/staticfiles/styles.css 2>/dev/null || echo 0)
    CSS_SIZE_KB=$(echo "scale=1; $CSS_SIZE/1024" | bc)
    echo -e "${GREEN}✓ styles.css exists${NC}"
    echo "  Size: $CSS_SIZE bytes ($CSS_SIZE_KB KB)"

    if [ "$CSS_SIZE" -gt 50000 ]; then
        echo -e "${GREEN}✓ CSS size OK (>50KB)${NC}"
    else
        echo -e "${YELLOW}⚠ CSS size is small ($CSS_SIZE_KB KB)${NC}"
    fi
else
    echo -e "${RED}✗ styles.css not found!${NC}"
    exit 1
fi

# Check 2: Count Tailwind classes
echo ""
echo -e "${YELLOW}2. Tailwind classes check...${NC}"
BG_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.bg-gray\|\.bg-white\|\.bg-primary" /app/staticfiles/styles.css || echo "0")
TEXT_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.text-gray\|\.text-white\|\.text-primary" /app/staticfiles/styles.css || echo "0")
FLEX_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.flex\|\.grid" /app/staticfiles/styles.css || echo "0")
DARK_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.dark\." /app/staticfiles/styles.css || echo "0")
HOVER_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.hover:" /app/staticfiles/styles.css || echo "0")

echo "  Background classes: $BG_COUNT"
echo "  Text classes: $TEXT_COUNT"
echo "  Flex/Grid classes: $FLEX_COUNT"
echo "  Dark mode classes: $DARK_COUNT"
echo "  Hover classes: $HOVER_COUNT"

TOTAL_CLASSES=$((BG_COUNT + TEXT_COUNT + FLEX_COUNT + DARK_COUNT + HOVER_COUNT))
echo "  Total classes: $TOTAL_CLASSES"

if [ "$TOTAL_CLASSES" -gt 100 ]; then
    echo -e "${GREEN}✓ Sufficient classes found (>100)${NC}"
elif [ "$TOTAL_CLASSES" -gt 50 ]; then
    echo -e "${YELLOW}⚠ Moderate number of classes (50-100)${NC}"
else
    echo -e "${RED}✗ Too few classes found (<50)!${NC}"
    exit 1
fi

# Check 3: Sample CSS content
echo ""
echo -e "${YELLOW}3. Sample CSS content...${NC}"
echo "First 20 lines with Tailwind classes:"
docker compose -f docker-compose.prod.yml exec -T web grep -E "\.(bg|text|flex|grid|dark)" /app/staticfiles/styles.css | head -20 || echo "No classes found"

# Check 4: Nginx serving
echo ""
echo -e "${YELLOW}4. Nginx static files serving...${NC}"
if docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
    echo "  CSS should be available at: https://your-domain.com/static/styles.css"
else
    echo -e "${YELLOW}⚠ Nginx not running (optional)${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}=========================================="
echo "Verification Summary"
echo "==========================================${NC}"

if [ "$CSS_SIZE" -gt 50000 ] && [ "$TOTAL_CLASSES" -gt 100 ]; then
    echo -e "${GREEN}✓ All checks passed! CSS is working correctly.${NC}"
    exit 0
elif [ "$TOTAL_CLASSES" -gt 50 ]; then
    echo -e "${YELLOW}⚠ CSS is functional but may be missing some classes.${NC}"
    echo "  Consider checking if all templates are being scanned."
    exit 0
else
    echo -e "${RED}✗ CSS verification failed!${NC}"
    echo "  CSS may not be working correctly."
    exit 1
fi

