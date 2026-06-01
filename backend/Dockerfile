# syntax=docker/dockerfile:1.7
# Pakistan CRM — Python Services Layer
#
# Build:  docker build -f backend/Dockerfile -t crm-services .
# Run:    docker run -p 5002:5002 --env-file .env crm-services

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY services/ ./services/
COPY adapters/ ./adapters/
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Non-root user
RUN addgroup --system crm && adduser --system --ingroup crm crm
USER crm

EXPOSE 5002

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5002 \
    SERVICE_NAME=crm-services

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5002/health')" || exit 1

CMD ["uvicorn", "services.app:app", "--host", "0.0.0.0", "--port", "5002", "--workers", "1"]
