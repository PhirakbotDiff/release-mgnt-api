FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (optional but useful)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app app

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "-b", "0.0.0.0:8000"]
