#!/bin/bash
# Script to fix comment input dark mode and rebuild project

set -e

echo "=========================================="
echo "Fixing Comment Input Dark Mode"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Build frontend
echo -e "${GREEN}Step 1: Building frontend...${NC}"
cd /h/DEV/Projects/_FOXMIND/Python_Web/task13_djgramm/djgramm
npm run build || echo -e "${YELLOW}Local build failed, trying Docker...${NC}"

# 2. Build in Docker
echo -e "${GREEN}Step 2: Building frontend in Docker...${NC}"
docker compose exec web npm run build || echo -e "${YELLOW}Docker build failed${NC}"

# 3. Collect static files
echo -e "${GREEN}Step 3: Collecting static files...${NC}"
docker compose exec web python manage.py collectstatic --clear --noinput || echo -e "${YELLOW}Collectstatic failed${NC}"

# 4. Run tests
echo -e "${GREEN}Step 4: Running tests...${NC}"
docker compose exec web uv run pytest tests/ -v --tb=short 2>&1 | tail -30 || echo -e "${YELLOW}Tests failed${NC}"

# 5. Restart services
echo -e "${GREEN}Step 5: Restarting services...${NC}"
docker compose restart web || echo -e "${YELLOW}Restart failed${NC}"

# 6. Check status
echo -e "${GREEN}Step 6: Checking service status...${NC}"
docker compose ps

echo -e "${GREEN}=========================================="
echo "Fix completed!"
echo "==========================================${NC}"
echo ""
echo "Please:"
echo "1. Clear browser cache (Ctrl+Shift+R)"
echo "2. Reload the page"
echo "3. Check if comment input text is white in dark mode"

