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

# Build frontend assets
RUN npm run build

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
