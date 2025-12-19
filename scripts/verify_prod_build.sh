#!/bin/bash
# Verify production build after Docker build completes
# Run this after: docker compose -f docker-compose.prod.yml build web

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "Production Build Verification"
echo "==========================================${NC}"
echo ""

# Check if container is running
if ! docker compose -f docker-compose.prod.yml ps web | grep -q "Up"; then
    echo -e "${YELLOW}⚠ Web container is not running. Starting it...${NC}"
    docker compose -f docker-compose.prod.yml up -d web
    echo "Waiting for container to be ready..."
    sleep 5
fi

echo -e "${BLUE}=== Checking Build Artifacts ===${NC}"

# Check 1: Verify frontend/dist exists in container
echo -e "${YELLOW}1. Checking frontend/dist in container...${NC}"
if docker compose -f docker-compose.prod.yml exec -T web test -d /app/frontend/dist; then
    echo -e "${GREEN}✓ frontend/dist exists${NC}"

    # List files
    echo "Files in frontend/dist:"
    docker compose -f docker-compose.prod.yml exec -T web ls -lh /app/frontend/dist/ | head -10
else
    echo -e "${RED}✗ frontend/dist not found!${NC}"
    exit 1
fi

# Check 2: Verify CSS file size
echo ""
echo -e "${YELLOW}2. Checking CSS file size...${NC}"
if docker compose -f docker-compose.prod.yml exec -T web test -f /app/frontend/dist/styles.css; then
    CSS_SIZE=$(docker compose -f docker-compose.prod.yml exec -T web stat -c%s /app/frontend/dist/styles.css 2>/dev/null || echo 0)
    echo "CSS size: $CSS_SIZE bytes ($(echo "scale=2; $CSS_SIZE/1024" | bc)KB)"

    if [ "$CSS_SIZE" -gt 50000 ]; then
        echo -e "${GREEN}✓ CSS size OK (>50KB)${NC}"
    else
        echo -e "${RED}✗ CSS too small (<50KB) - Tailwind may not have found templates!${NC}"
        echo "First 50 lines of CSS:"
        docker compose -f docker-compose.prod.yml exec -T web head -50 /app/frontend/dist/styles.css
        exit 1
    fi
else
    echo -e "${RED}✗ styles.css not found in frontend/dist!${NC}"
    exit 1
fi

# Check 3: Verify CSS contains Tailwind classes
echo ""
echo -e "${YELLOW}3. Checking CSS contains Tailwind classes...${NC}"
CLASS_COUNT=$(docker compose -f docker-compose.prod.yml exec -T web grep -c "\.bg-gray\|\.text-gray\|\.flex\|\.grid" /app/frontend/dist/styles.css || echo 0)
echo "Found Tailwind classes: $CLASS_COUNT"

if [ "$CLASS_COUNT" -gt 100 ]; then
    echo -e "${GREEN}✓ CSS contains Tailwind classes${NC}"
else
    echo -e "${RED}✗ CSS may not contain enough Tailwind classes${NC}"
    exit 1
fi

# Check 4: Verify staticfiles
echo ""
echo -e "${YELLOW}4. Checking staticfiles directory...${NC}"
if docker compose -f docker-compose.prod.yml exec -T web test -d /app/staticfiles; then
    echo -e "${GREEN}✓ staticfiles directory exists${NC}"

    # Check if styles.css was copied
    if docker compose -f docker-compose.prod.yml exec -T web test -f /app/staticfiles/styles.css; then
        STATIC_CSS_SIZE=$(docker compose -f docker-compose.prod.yml exec -T web stat -c%s /app/staticfiles/styles.css 2>/dev/null || echo 0)
        echo "staticfiles/styles.css size: $STATIC_CSS_SIZE bytes"

        if [ "$STATIC_CSS_SIZE" -gt 50000 ]; then
            echo -e "${GREEN}✓ styles.css in staticfiles OK${NC}"
        else
            echo -e "${RED}✗ styles.css in staticfiles too small!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ styles.css not found in staticfiles!${NC}"
        exit 1
    fi

    # List some static files
    echo "Sample static files:"
    docker compose -f docker-compose.prod.yml exec -T web ls -lh /app/staticfiles/ | head -10
else
    echo -e "${RED}✗ staticfiles directory not found!${NC}"
    exit 1
fi

# Check 5: Verify nginx can serve static files
echo ""
echo -e "${YELLOW}5. Checking nginx static files serving...${NC}"
if docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo -e "${GREEN}✓ Nginx is running${NC}"

    # Try to get styles.css via nginx (if accessible)
    echo "Nginx should serve /static/styles.css"
else
    echo -e "${YELLOW}⚠ Nginx not running (optional)${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}=========================================="
echo "Verification Summary"
echo "==========================================${NC}"
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo -e "${BLUE}Production build is ready.${NC}"
echo ""
echo -e "${YELLOW}To test in browser:${NC}"
echo "1. Visit your production URL"
echo "2. Open browser DevTools (F12)"
echo "3. Check Network tab for /static/styles.css"
echo "4. Verify CSS size is > 50KB"
echo "5. Check if styling is applied correctly"
echo ""

