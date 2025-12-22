# Development/Production Dockerfile for DJGramm

FROM python:3.12-slim

# Install system dependencies (including Node.js for frontend build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy Node.js dependency files
COPY package.json package-lock.json* ./

# Install Node.js dependencies
RUN npm ci || npm install

# Copy frontend source and config files
COPY frontend/ ./frontend/
COPY webpack.config.js tailwind.config.js postcss.config.js ./

# Copy templates for Tailwind CSS to scan (needed for content paths)
# Templates are copied temporarily just for the build
COPY src/templates/ ./templates/

# Verify templates are copied (same as production)
RUN echo "=== Templates found ===" && \
    find ./templates -name "*.html" | head -10 || (echo "ERROR: No templates found!" && exit 1)

# Build frontend assets
RUN npm run build

# Verify CSS was generated correctly
RUN if [ -f "frontend/dist/styles.css" ]; then \
      CSS_SIZE=$(stat -f%z frontend/dist/styles.css 2>/dev/null || stat -c%s frontend/dist/styles.css 2>/dev/null || echo 0) && \
      echo "CSS size: $CSS_SIZE bytes" && \
      if [ "$CSS_SIZE" -lt 50000 ]; then \
        echo "WARNING: CSS too small (<50KB)"; \
      fi; \
    fi

# Remove templates after build (they'll be copied again with src/)
RUN rm -rf ./templates

# Copy entrypoint and fix line endings (CRLF -> LF) for Windows compatibility
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Copy source code
COPY src/ .

# Create directories
RUN mkdir -p staticfiles media

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
