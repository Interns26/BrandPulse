FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ cmake libpq-dev && rm -rf /var/lib/apt/lists/*

# CRITICAL OPTIMIZATION: Install CPU-only PyTorch first to utilize Docker caching
# This uses the official PyTorch CPU wheel index which downloads much faster
RUN pip install --no-cache-dir torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install the rest of your packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code (Placed at the bottom so code changes don't break pip cache)
COPY . .
RUN mkdir -p /app/models_storage

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]