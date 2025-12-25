#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U postgres; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready!"

# Install dev dependencies if in DEBUG mode (before migrations)
if [ "$DEBUG" = "True" ]; then
    echo "Installing dev dependencies..."
    cd /app || cd /app/src || true
    uv sync --group dev --frozen 2>/dev/null || uv sync --group dev 2>/dev/null || true
fi

# Build frontend assets (if Node.js is available and package.json exists)
if [ -f "/app/package.json" ] || [ -f "/app/src/../package.json" ]; then
    echo "Building frontend assets..."
    cd /app || cd /app/src/.. || true
    npm run build 2>/dev/null || echo "Frontend build skipped (Node.js not available or already built)"
fi

# Run migrations
echo "Running migrations..."
cd /app || cd /app/src || true
uv run python manage.py migrate --noinput

# Collect static files (only in production)
if [ "$DEBUG" != "True" ]; then
    echo "Collecting static files..."
    # Remove Cloudinary static files to avoid permission errors
    # Cloudinary files are served via CDN and don't need to be in staticfiles
    if [ -d "/app/staticfiles/cloudinary" ]; then
        echo "Removing Cloudinary static files..."
        rm -rf /app/staticfiles/cloudinary || true
    fi
    # Fix permissions for staticfiles directory
    if [ -d "/app/staticfiles" ]; then
        chmod -R u+w /app/staticfiles 2>/dev/null || true
    fi
    uv run python manage.py collectstatic --noinput
fi

# Execute the main command
exec "$@"
