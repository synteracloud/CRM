# syntax=docker/dockerfile:1.7
# Python Service Layer — P-023
#
# Build:  docker build -f services/Dockerfile -t crm-services .
# Run:    docker run -p 5002:5002 --env-file .env crm-services

# ── Stage 1: dependency install ────────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /build

COPY services/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN addgroup --system crm && adduser --system --ingroup crm crm

WORKDIR /app

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy the full repository so cross-service imports (src/, services/, adapters/) resolve
COPY . .

USER crm

EXPOSE 5002

ENV NODE_ENV=production \
    SERVICE_NAME=crm-python-services \
    LOG_LEVEL=INFO \
    PORT=5002

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5002/health')" || exit 1

CMD ["uvicorn", "services.app:app", "--host", "0.0.0.0", "--port", "5002", "--workers", "2"]
