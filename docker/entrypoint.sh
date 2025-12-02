#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U postgres; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running migrations..."
uv run python manage.py migrate --noinput

# Collect static files (only in production)
if [ "$DEBUG" != "True" ]; then
    echo "Collecting static files..."
    uv run python manage.py collectstatic --noinput
fi

# Execute the main command
exec "$@"
