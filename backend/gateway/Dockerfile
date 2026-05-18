# syntax=docker/dockerfile:1.7
# Node.js API Gateway — P-023
#
# Build:  docker build -f gateway/Dockerfile -t crm-gateway .
# Run:    docker run -p 3000:3000 --env-file .env crm-gateway

# ── Stage 1: dependency install ────────────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

# Copy only manifest files first for layer caching
COPY gateway/package.json gateway/package-lock.json* ./

RUN npm ci --omit=dev --ignore-scripts

# ── Stage 2: production image ─────────────────────────────────────────────────
FROM node:20-alpine AS runtime

RUN addgroup -S crm && adduser -S crm -G crm

WORKDIR /app

# Copy installed node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy gateway source (everything under gateway/)
COPY gateway/ ./

# Non-root user for least-privilege
USER crm

EXPOSE 3000

ENV NODE_ENV=production \
    PORT=3000 \
    SERVICE_NAME=crm-gateway \
    SERVICE_VERSION=1.0.0

# Liveness / readiness probes hit GET /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
