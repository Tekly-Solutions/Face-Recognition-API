# ==============================================================================
# Dockerfile for Face Recognition FastAPI Server - BACKEND ONLY
# Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
# 
# Production-Ready Docker image with:
# - FastAPI + Uvicorn (Backend API only)
# - InsightFace + FAISS
# - Firebase Storage Integration
# - GPU Support (optional)
# - Health Checks
# - Non-root user for security
#
# NOTE: This Dockerfile contains ONLY backend code.
# Frontend is not included (separate project/deployment).
# ==============================================================================
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Tekly IT Solutions"
LABEL description="Face Recognition API with FastAPI, InsightFace, FAISS, and Firebase"
LABEL version="2.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with minimal size
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV dependencies
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    # Additional utilities
    curl \
    wget \
    git \
    # Build essentials for package compilation
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    firebase-admin>=6.0.0 \
    pydantic>=2.0.0

# Copy only backend application code (no frontend)
COPY .. ./Backend/

RUN mkdir -p dataset models logs temp config && \
    chmod -R 755 /app && \
    chmod -R 777 dataset models logs temp

# Add non-root user for security (optional but recommended)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check with timeout and retry logic
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

# Run FastAPI server with Uvicorn
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# Build Instructions:
# docker build -t face-recognition-api:latest .
#
# Run Instructions (with volumes):
# docker run -it --rm -p 8000:8000 \
#   -v $(pwd)/dataset:/app/dataset \
#   -v $(pwd)/models:/app/models \
#   face-recognition-api:latest
#
# Run with docker-compose:
# docker-compose up
# ==============================================================================
