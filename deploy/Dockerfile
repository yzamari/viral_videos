# 🚀 AI Video Generator - Production Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Runtime dependencies
    ffmpeg \
    curl \
    wget \
    # Audio/Video processing
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    # Image processing
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    # System utilities
    procps \
    htop \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get autoclean

# Create application user
RUN groupadd -r viralai && useradd -r -g viralai viralai

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=viralai:viralai . .

# Create necessary directories
RUN mkdir -p outputs logs cache config && \
    chown -R viralai:viralai /app

# Set proper permissions
RUN chmod +x /app/main.py /app/modern_ui.py && \
    chmod 750 /app && \
    chmod 755 /app/outputs /app/logs /app/cache

# Create health check script
RUN echo '#!/bin/bash\n\
curl -f http://localhost:7860/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Switch to application user
USER viralai

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Add labels for better container management
LABEL maintainer="AI Video Generator Team" \
      version="2.2.0" \
      description="Enterprise-grade AI Video Generator with VEO2 integration" \
      org.opencontainers.image.title="AI Video Generator" \
      org.opencontainers.image.description="Production-ready AI video generation platform" \
      org.opencontainers.image.version="2.2.0" \
      org.opencontainers.image.vendor="AI Video Generator" \
      org.opencontainers.image.licenses="MIT"

# Default command
CMD ["python", "modern_ui.py"] 