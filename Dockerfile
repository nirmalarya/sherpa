# SHERPA V1 - Backend Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Base image with Python dependencies
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Stage 2: Development/Build stage
FROM base as builder

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 3: Production stage
FROM base as production

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY sherpa/ /app/sherpa/
COPY setup.py /app/
COPY README.md /app/

# Create necessary directories
RUN mkdir -p /app/sherpa/data \
    /app/sherpa/logs \
    /app/sherpa/snippets.local

# Create a non-root user for security
RUN useradd -m -u 1000 sherpa && \
    chown -R sherpa:sherpa /app

# Switch to non-root user
USER sherpa

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Set default environment
ENV SHERPA_ENV=production \
    SHERPA_HOST=0.0.0.0 \
    SHERPA_PORT=8000

# Default command - run the API server
CMD ["python", "-m", "uvicorn", "sherpa.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
