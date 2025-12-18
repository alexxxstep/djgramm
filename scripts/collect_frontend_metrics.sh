#!/bin/bash
# Collect frontend metrics for optimization tracking

set -e

echo "=========================================="
echo "Frontend Metrics Collection"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Bundle sizes
echo "📦 Bundle Sizes:"
echo "----------------------------------------"
if [ -d "frontend/dist" ]; then
    echo "Production build files:"
    ls -lh frontend/dist/*.js frontend/dist/*.css 2>/dev/null | awk '{print $5, $9}' || echo "No built files found"

    # Calculate total size
    TOTAL_SIZE=$(du -sh frontend/dist 2>/dev/null | cut -f1)
    echo "Total dist size: $TOTAL_SIZE"

    # Gzip sizes if available
    if command -v gzip &> /dev/null; then
        echo ""
        echo "Gzipped sizes:"
        for file in frontend/dist/*.js frontend/dist/*.css 2>/dev/null; do
            if [ -f "$file" ]; then
                GZIP_SIZE=$(gzip -c "$file" | wc -c)
                GZIP_SIZE_KB=$((GZIP_SIZE / 1024))
                echo "  $(basename $file): ${GZIP_SIZE_KB}KB"
            fi
        done
    fi
else
    echo -e "${YELLOW}⚠️  frontend/dist not found. Run 'npm run build' first.${NC}"
fi
echo ""

# 2. Source code metrics
echo "📊 Source Code Metrics:"
echo "----------------------------------------"
echo "JavaScript files:"
find frontend/src/js -name "*.js" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print "Total lines:", $1}'
echo ""

echo "File count:"
JS_COUNT=$(find frontend/src/js -name "*.js" | wc -l)
echo "  JavaScript files: $JS_COUNT"
CSS_COUNT=$(find frontend/src/css -name "*.css" 2>/dev/null | wc -l)
echo "  CSS files: $CSS_COUNT"
echo ""

# 3. Test coverage
echo "🧪 Test Coverage:"
echo "----------------------------------------"
if [ -d "frontend/tests" ]; then
    TEST_COUNT=$(find frontend/tests -name "*.test.js" 2>/dev/null | wc -l)
    echo "Test files: $TEST_COUNT"

    if [ "$TEST_COUNT" -gt 0 ]; then
        echo "Test files:"
        find frontend/tests -name "*.test.js" 2>/dev/null | while read test; do
            echo "  - $(basename $test)"
        done
    fi
else
    echo "No tests directory found"
fi
echo ""

# 4. Code quality metrics
echo "🔍 Code Quality:"
echo "----------------------------------------"
CONSOLE_COUNT=$(grep -r "console\.\(log\|warn\|error\)" frontend/src/js --include="*.js" 2>/dev/null | wc -l)
echo "Console statements: $CONSOLE_COUNT"

DOM_QUERIES=$(grep -r "querySelector\|getElementById" frontend/src/js --include="*.js" 2>/dev/null | wc -l)
echo "DOM queries: $DOM_QUERIES"

IMPORTS=$(grep -r "^import" frontend/src/js --include="*.js" 2>/dev/null | wc -l)
echo "Import statements: $IMPORTS"

EXPORTS=$(grep -r "^export" frontend/src/js --include="*.js" 2>/dev/null | wc -l)
echo "Export statements: $EXPORTS"
echo ""

# 5. Module structure
echo "📁 Module Structure:"
echo "----------------------------------------"
echo "Modules:"
find frontend/src/js/modules -type d 2>/dev/null | sed 's|frontend/src/js/||' | while read dir; do
    echo "  - $dir"
done || echo "  No modules directory"

echo ""
echo "Utils:"
find frontend/src/js/utils -name "*.js" 2>/dev/null | sed 's|frontend/src/js/||' | while read file; do
    echo "  - $file"
done || echo "  No utils directory"
echo ""

# 6. Recommendations
echo "💡 Recommendations:"
echo "----------------------------------------"
if [ "$CONSOLE_COUNT" -gt 50 ]; then
    echo "⚠️  High number of console statements. Consider removing in production."
fi

if [ -d "frontend/dist" ]; then
    MAIN_JS_SIZE=$(stat -f%z frontend/dist/main.js 2>/dev/null || stat -c%s frontend/dist/main.js 2>/dev/null || echo "0")
    if [ "$MAIN_JS_SIZE" -gt 200000 ]; then
        echo "⚠️  main.js is large. Consider further code splitting."
    else
        echo -e "${GREEN}✓ main.js size is acceptable${NC}"
    fi
fi

if [ "$TEST_COUNT" -lt 5 ]; then
    echo "⚠️  Low test coverage. Consider adding more tests."
fi

echo ""
echo "=========================================="
echo "Metrics Collection Complete"
echo "=========================================="

