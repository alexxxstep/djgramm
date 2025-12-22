#!/bin/bash
# Comprehensive test script for production styling
# Tests Tailwind CSS build process in production Docker environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Production Styling Test Suite"
echo "==========================================${NC}"
echo ""

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${BLUE}Testing: ${test_name}${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED: ${test_name}${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED: ${test_name}${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Check if templates exist in source
echo -e "${YELLOW}=== Test 1: Source Templates Check ===${NC}"
run_test "Source templates exist" \
    "test -d src/templates && find src/templates -name '*.html' | grep -q ."

# Test 2: Check tailwind.config.js
echo -e "${YELLOW}=== Test 2: Tailwind Config Check ===${NC}"
run_test "tailwind.config.js exists and is valid" \
    "test -f tailwind.config.js && node -e \"require('./tailwind.config.js')\""

# Test 3: Check if Dockerfile.prod has all necessary steps
echo -e "${YELLOW}=== Test 3: Dockerfile.prod Validation ===${NC}"
run_test "Dockerfile.prod copies templates" \
    "grep -q 'COPY src/templates' docker/Dockerfile.prod"
run_test "Dockerfile.prod validates CSS size" \
    "grep -q 'CSS_SIZE.*50000' docker/Dockerfile.prod"
run_test "Dockerfile.prod validates collectstatic" \
    "grep -q 'styles.css size OK' docker/Dockerfile.prod"

# Test 4: Build production image (dry-run check)
echo -e "${YELLOW}=== Test 4: Production Build Validation ===${NC}"
if command -v docker &> /dev/null; then
    echo -e "${BLUE}Checking Docker build context...${NC}"

    # Check if all required files exist
    run_test "package.json exists" "test -f package.json"
    run_test "webpack.config.js exists" "test -f webpack.config.js"
    run_test "tailwind.config.js exists" "test -f tailwind.config.js"
    run_test "postcss.config.js exists" "test -f postcss.config.js"
    run_test "frontend directory exists" "test -d frontend"
    run_test "src/templates directory exists" "test -d src/templates"

    echo ""
    echo -e "${YELLOW}=== Test 5: Local Tailwind Config Test ===${NC}"
    # Test tailwind config locally
    if command -v node &> /dev/null; then
        echo -e "${BLUE}Testing tailwind.config.js locally...${NC}"
        TEMP_DIR=$(mktemp -d)
        cp -r src/templates "$TEMP_DIR/templates" 2>/dev/null || true
        cp tailwind.config.js "$TEMP_DIR/" 2>/dev/null || true

        cd "$TEMP_DIR" || exit 1
        if node -e "
            const path = require('path');
            const fs = require('fs');
            const config = require('./tailwind.config.js');
            const contentPaths = config.content || [];
            console.log('Content paths:', contentPaths.length);
            const hasTemplates = contentPaths.some(p => p.includes('templates'));
            console.log('Has templates path:', hasTemplates);
            process.exit(hasTemplates ? 0 : 1);
        " 2>/dev/null; then
            echo -e "${GREEN}✓ PASSED: Tailwind config finds templates${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ FAILED: Tailwind config may not find templates${NC}"
            ((TESTS_FAILED++))
        fi
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
    else
        echo -e "${YELLOW}⚠ Node.js not found, skipping local config test${NC}"
    fi

    echo ""
    echo -e "${YELLOW}=== Test 6: Production Build Simulation ===${NC}"
    echo -e "${BLUE}To fully test production build, run:${NC}"
    echo -e "${GREEN}docker compose -f docker-compose.prod.yml build web --no-cache${NC}"
    echo ""
    echo -e "${BLUE}Then check logs for:${NC}"
    echo -e "  - Templates found: should show HTML files"
    echo -e "  - Tailwind build output: should show found templates"
    echo -e "  - CSS size: should be > 50KB"
    echo -e "  - styles.css size OK: should pass validation"

else
    echo -e "${YELLOW}⚠ Docker not found, skipping Docker tests${NC}"
fi

# Test 7: Check static files configuration
echo ""
echo -e "${YELLOW}=== Test 7: Django Static Files Config ===${NC}"
if [ -f "src/config/settings.py" ]; then
    run_test "STATICFILES_DIRS configured" \
        "grep -q 'STATICFILES_DIRS' src/config/settings.py"
    run_test "STATIC_ROOT configured" \
        "grep -q 'STATIC_ROOT' src/config/settings.py"
    run_test "frontend/dist path handling" \
        "grep -q 'frontend/dist' src/config/settings.py"
else
    echo -e "${RED}✗ FAILED: settings.py not found${NC}"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
echo -e "${BLUE}=========================================="
echo "Test Summary"
echo "==========================================${NC}"
echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Build production image:"
    echo "   ${GREEN}docker compose -f docker-compose.prod.yml build web --no-cache${NC}"
    echo ""
    echo "2. Check build logs for:"
    echo "   - Templates found (should list HTML files)"
    echo "   - Tailwind build output (should show found templates)"
    echo "   - CSS size OK (>50KB)"
    echo ""
    echo "3. After build, verify in container:"
    echo "   ${GREEN}docker compose -f docker-compose.prod.yml exec web ls -lh /app/staticfiles/styles.css${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please fix issues before building.${NC}"
    exit 1
fi

