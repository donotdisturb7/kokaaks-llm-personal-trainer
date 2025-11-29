# ============================================================================
# Stage 1: Builder - Compile dependencies
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to separate location
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (libpq for psycopg2 + postgresql-client for startup script)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code (excluding tests, docs via .dockerignore)
COPY --chown=appuser:appuser . .

# Make startup script executable
RUN chmod +x startup.sh

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Production command
CMD ["./startup.sh"]

