# Pakistan CRM OS — Makefile
# Run from D:\CRM root.
# Requires: Docker, Python 3.12 (D:\Python), Node.js 20+

.PHONY: dev dev-frontend dev-backend test test-backend test-frontend \
        migrate migrate-create lint lint-py lint-js build push clean help

# ── Config ─────────────────────────────────────────────────────────────────────
PYTHON      := D:/Python/python.exe
VENV        := backend/.venv/Scripts
PIP         := $(VENV)/pip.exe
PYTEST      := $(VENV)/pytest.exe
ALEMBIC     := $(VENV)/alembic.exe
RUFF        := $(VENV)/ruff.exe
BLACK       := $(VENV)/black.exe
COMPOSE     := docker compose -f backend/docker-compose.yml

# ── Development ────────────────────────────────────────────────────────────────

dev: ## Start full stack (Docker): gateway + services + postgres + redis
	$(COMPOSE) up

dev-frontend: ## Start frontend dev server on port 3001
	cd frontend && npm run serve

dev-backend: ## Start Python services locally (no Docker)
	$(VENV)/activate.bat && uvicorn services.app:app --reload --port 5002 --app-dir backend

# ── Database ───────────────────────────────────────────────────────────────────

migrate: ## Run all pending Alembic migrations
	cd backend && $(ALEMBIC) upgrade head

migrate-create: ## Create a new migration: make migrate-create MSG="describe change"
	cd backend && $(ALEMBIC) revision --autogenerate -m "$(MSG)"

migrate-down: ## Roll back one migration
	cd backend && $(ALEMBIC) downgrade -1

migrate-status: ## Show current migration status
	cd backend && $(ALEMBIC) current

# ── Testing ────────────────────────────────────────────────────────────────────

test: test-backend test-frontend ## Run all tests

test-backend: ## Run Python tests with coverage
	cd backend && $(PYTEST) tests/ -v --tb=short --cov=services --cov-report=term-missing

test-frontend: ## Run frontend tests
	cd frontend && npm test

# ── Linting ────────────────────────────────────────────────────────────────────

lint: lint-py lint-js ## Run all linters

lint-py: ## Run ruff + black check on Python code
	$(RUFF) check backend/
	$(BLACK) --check backend/

lint-py-fix: ## Auto-fix Python lint issues
	$(RUFF) check --fix backend/
	$(BLACK) backend/

lint-js: ## Run ESLint on frontend
	cd frontend && npm run lint

# ── Build & Deploy ─────────────────────────────────────────────────────────────

build: ## Build Docker images
	$(COMPOSE) build

push: ## Push Docker images to registry
	$(COMPOSE) push

# ── Utilities ──────────────────────────────────────────────────────────────────

install: ## Install Python + Node dependencies
	$(PIP) install -r backend/services/requirements.txt
	cd frontend && npm install

clean: ## Stop containers and remove volumes
	$(COMPOSE) down -v

logs: ## Tail docker compose logs
	$(COMPOSE) logs -f

health: ## Check all service health endpoints
	curl -s http://localhost:3000/health | python -m json.tool
	curl -s http://localhost:5002/health | python -m json.tool

pages-check: ## Verify all 96 library pages return HTTP 200
	@echo "Checking all 96 library pages..."
	cd frontend && node -e " \
	  const http = require('http'); \
	  const fs = require('fs'); \
	  const files = fs.readdirSync('src/app').filter(f => f.endsWith('.html')); \
	  let pass = 0, fail = 0; \
	  files.forEach(f => { \
	    http.get('http://localhost:3001/app/' + f, r => { \
	      if (r.statusCode === 200) pass++; \
	      else { fail++; console.log('FAIL:', f, r.statusCode); } \
	      if (pass + fail === files.length) console.log(pass + ' PASS / ' + fail + ' FAIL'); \
	    }); \
	  }); \
	"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
