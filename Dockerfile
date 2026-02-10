FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (optional but useful)
# RUN apt-get update && apt-get install -y curl \
#     && apt-get install -y --no-install-recommends libexpat1 \
#     build-essential \
#     git \
#     && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y \
    curl \
    git \
    libexpat1 \
    ca-certificates \
    && curl -L https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.69.1_Linux-ARM64.tar.gz \
    | tar zx -C /usr/local/bin trivy \
    && chmod +x /usr/local/bin/trivy \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY scripts .
    
# Install Python dependencies
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
