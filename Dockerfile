# Dockerfile (CPU)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by OpenCV, FAISS, and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install additional dependencies required by retinaface and FAISS
RUN pip install tf-keras faiss-cpu

# Copy the rest of the project
COPY . /app

# Expose port if your app serves HTTP
EXPOSE 5000

# Default command
CMD ["python", "main.py"]