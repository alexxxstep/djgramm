#!/bin/bash
# Script to check if favicon is properly configured and accessible

echo "=========================================="
echo "Checking Favicon Configuration"
echo "=========================================="
echo ""

# Check if icon.png exists in source
if [ -f "src/static/icon.png" ]; then
    echo "✓ icon.png found in src/static/"
    ls -lh src/static/icon.png
else
    echo "✗ ERROR: icon.png not found in src/static/"
    exit 1
fi

echo ""
echo "Checking Django static files configuration..."
echo ""

# Check if static directory is in STATICFILES_DIRS
if grep -q "static_dir = BASE_DIR / \"static\"" src/config/settings.py; then
    echo "✓ static directory configured in settings.py"
else
    echo "✗ WARNING: static directory may not be configured"
fi

# Check if icon.png is referenced in base.html
if grep -q "icon.png" src/templates/base.html; then
    echo "✓ icon.png referenced in base.html"
else
    echo "✗ ERROR: icon.png not found in base.html"
    exit 1
fi

echo ""
echo "Checking Nginx configuration..."
echo ""

# Check if favicon location is configured in nginx
if grep -q "location = /static/icon.png" docker/nginx.conf; then
    echo "✓ Favicon location configured in nginx.conf"
else
    echo "✗ WARNING: Favicon location not specifically configured in nginx"
fi

# Check if static files location is configured
if grep -q "location /static/" docker/nginx.conf; then
    echo "✓ Static files location configured in nginx.conf"
else
    echo "✗ ERROR: Static files location not configured in nginx"
    exit 1
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "To verify favicon on server:"
echo "1. Check if icon.png is collected:"
echo "   docker compose -f docker-compose.prod.yml exec web ls -lh /app/staticfiles/icon.png"
echo ""
echo "2. Check if favicon is accessible:"
echo "   curl -I http://localhost/static/icon.png"
echo "   (or https://your-domain.com/static/icon.png)"
echo ""
echo "3. Check browser DevTools → Network tab for /static/icon.png"
echo "   Status should be 200 OK"
echo ""

