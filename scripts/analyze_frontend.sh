#!/bin/bash
# Frontend Analysis Script
# Analyzes current frontend codebase for optimization opportunities

set -e

echo "=========================================="
echo "Frontend Code Analysis"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. File sizes
echo "📊 File Sizes:"
echo "----------------------------------------"
echo "Source files:"
find frontend/src/js -name "*.js" -exec wc -l {} + 2>/dev/null | sort -n | tail -10
echo ""
echo "Built files:"
if [ -d "frontend/dist" ]; then
    ls -lh frontend/dist/*.js frontend/dist/*.css 2>/dev/null | awk '{print $5, $9}' || echo "No built files found"
else
    echo "⚠️  frontend/dist directory not found. Run 'npm run build' first."
fi
echo ""

# 2. Console.log count
echo "🔍 Console Statements:"
echo "----------------------------------------"
CONSOLE_COUNT=$(grep -r "console\.\(log\|warn\|error\)" frontend/src/js --include="*.js" | wc -l)
echo "Total console statements: $CONSOLE_COUNT"
if [ "$CONSOLE_COUNT" -gt 50 ]; then
    echo -e "${YELLOW}⚠️  High number of console statements. Consider removing in production.${NC}"
fi
echo ""

# 3. DOM queries
echo "🔎 DOM Queries:"
echo "----------------------------------------"
QUERY_SELECTOR=$(grep -r "querySelector" frontend/src/js --include="*.js" | wc -l)
QUERY_ALL=$(grep -r "querySelectorAll" frontend/src/js --include="*.js" | wc -l)
GET_BY_ID=$(grep -r "getElementById" frontend/src/js --include="*.js" | wc -l)
echo "querySelector: $QUERY_SELECTOR"
echo "querySelectorAll: $QUERY_ALL"
echo "getElementById: $GET_BY_ID"
TOTAL_QUERIES=$((QUERY_SELECTOR + QUERY_ALL + GET_BY_ID))
echo "Total DOM queries: $TOTAL_QUERIES"
if [ "$TOTAL_QUERIES" -gt 100 ]; then
    echo -e "${YELLOW}⚠️  High number of DOM queries. Consider caching selectors.${NC}"
fi
echo ""

# 4. Event listeners
echo "👂 Event Listeners:"
echo "----------------------------------------"
EVENT_LISTENERS=$(grep -r "addEventListener" frontend/src/js --include="*.js" | wc -l)
echo "Total addEventListener calls: $EVENT_LISTENERS"
echo ""

# 5. Duplicate code patterns
echo "🔄 Potential Duplications:"
echo "----------------------------------------"
echo "AJAX patterns:"
grep -r "fetch\|ajax" frontend/src/js --include="*.js" | wc -l
echo "Error handling patterns:"
grep -r "catch\|error" frontend/src/js --include="*.js" | wc -l
echo ""

# 6. Import/Export analysis
echo "📦 Module Dependencies:"
echo "----------------------------------------"
echo "Imports:"
grep -r "^import" frontend/src/js --include="*.js" | wc -l
echo "Exports:"
grep -r "^export" frontend/src/js --include="*.js" | wc -l
echo ""

# 7. Bundle analysis (if available)
echo "📦 Bundle Analysis:"
echo "----------------------------------------"
if [ -f "frontend/dist/main.js" ]; then
    BUNDLE_SIZE=$(du -h frontend/dist/main.js | cut -f1)
    echo "main.js size: $BUNDLE_SIZE"

    # Check if gzipped
    if command -v gzip &> /dev/null; then
        GZIP_SIZE=$(gzip -c frontend/dist/main.js | wc -c)
        GZIP_SIZE_KB=$((GZIP_SIZE / 1024))
        echo "main.js gzipped: ${GZIP_SIZE_KB}KB"

        if [ "$GZIP_SIZE_KB" -gt 200 ]; then
            echo -e "${YELLOW}⚠️  Bundle size is large. Consider code splitting.${NC}"
        else
            echo -e "${GREEN}✓ Bundle size is acceptable.${NC}"
        fi
    fi
else
    echo "⚠️  main.js not found. Run 'npm run build' first."
fi
echo ""

# 8. Recommendations
echo "💡 Recommendations:"
echo "----------------------------------------"
if [ "$CONSOLE_COUNT" -gt 50 ]; then
    echo "1. Remove console.log statements in production build"
fi
if [ "$TOTAL_QUERIES" -gt 100 ]; then
    echo "2. Cache DOM queries to improve performance"
fi
if [ -f "frontend/dist/main.js" ] && [ "$GZIP_SIZE_KB" -gt 200 ]; then
    echo "3. Implement code splitting to reduce initial bundle size"
fi
echo "4. Run 'npm run build:analyze' for detailed bundle analysis"
echo "5. Run 'npm run lint' to check code quality"
echo ""

echo "=========================================="
echo "Analysis Complete"
echo "=========================================="

