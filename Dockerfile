# Pokemon Discord Stock Bot - Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash pokemon-bot
USER pokemon-bot

# Copy application code
COPY --chown=pokemon-bot:pokemon-bot . .

# Create necessary directories
RUN mkdir -p data logs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python check_setup.py || exit 1

# Default command
CMD ["python", "main.py"]