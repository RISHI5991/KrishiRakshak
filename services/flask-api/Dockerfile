# ---------- build stage ----------
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.11-slim

LABEL maintainer="Dhurandhar Team"
LABEL description="Dhurandhar Flask AI Gateway"

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create log directory
RUN mkdir -p logs

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5003/api/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5003", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "app:app"]
