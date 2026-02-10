FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    && ARCH="$(uname -m)" \
    && case "$ARCH" in \
      x86_64)  TRIVY_ARCH="64bit" ;; \
      aarch64) TRIVY_ARCH="ARM64" ;; \
      *) echo "Unsupported architecture: $ARCH" && exit 1 ;; \
    esac \
    && curl -L "https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.69.1_Linux-${TRIVY_ARCH}.tar.gz" \
        | tar zx -C /usr/local/bin trivy \
    && chmod +x /usr/local/bin/trivy \
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
