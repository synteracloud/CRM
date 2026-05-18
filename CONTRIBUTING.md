# Contributing to Pakistan CRM OS

---

## Branch Naming

```
<type>/<short-description>
```

| Type | Use for |
|---|---|
| `feat/` | New feature or page |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `refactor/` | Code restructure, no behaviour change |
| `test/` | Tests only |
| `chore/` | Tooling, dependencies, config |
| `phase/` | Rebuild phase work (e.g. `phase/1-foundation`) |

**Examples:**
```
feat/followup-engine-endpoints
fix/collections-overdue-sort
docs/adr-whatsapp-first
phase/2-followup-engine
```

---

## Commit Format

```
<type>(<scope>): <short summary>

[optional body — why, not what]

Co-Authored-By: ...
```

**Types:** `feat` · `fix` · `docs` · `refactor` · `test` · `chore`  
**Scope:** `gateway` · `services` · `frontend` · `docs` · `db` · `adapters` · `ci`

**Examples:**
```
feat(services): add followup enforcement timer logic

Implements T+0/+2h/+24h/+48h escalation ladder per followup-enforcement-model.md.
Rule precedence: inactivity > time > activity.
```

```
docs(adr): add ADR-002 adapter pattern decision
```

```
fix(frontend): correct PKR formatting on collections queue
```

---

## Pull Request Process

1. **Branch from `main`** — never commit directly to main.
2. **One concern per PR** — a PR that builds a page should not also refactor the gateway.
3. **Title** — follow commit format: `feat(services): followup engine endpoints`
4. **Description must include:**
   - What changed and why
   - Which spec docs were anchored to (e.g. `followup-enforcement-model.md`)
   - Test evidence (pytest output or HTTP response screenshots)
   - Confirmation: `All 96 library pages still HTTP 200 ✓`
5. **No merge without:** passing CI (lint + test) + at least one review.

---

## Non-Negotiables

These apply to every contribution, no exceptions:

| Rule | Source |
|---|---|
| RTL must be wired at build time — not retrofitted | `CONSTRAINTS.md C-001` |
| All API calls via `crm-api.js` with `DUMMY_MODE` flag | `CONSTRAINTS.md C-007` |
| `JAZZCASH_STUB_MODE=true` until P-016 credentials verified | `CONSTRAINTS.md C-009` |
| No country-specific logic in `core/` | `architecture-overview.md` |
| `core/*` must never import `adapters/pakistan/*` | `architecture-overview.md` |
| Never commit `.env` — use `.env.example` | `.gitignore` |
| All 96 existing library pages must stay at HTTP 200 | `REBUILD-PLAN.md` |

---

## Local Dev Setup

```bash
# Full stack (Docker)
cd backend && cp .env.example .env
docker compose up

# Frontend only
cd frontend && npm run serve   # http://localhost:3001

# Python only
D:\CRM\backend\.venv\Scripts\Activate.ps1
uvicorn services.app:app --reload --port 5002
```

See `README.md` for full setup instructions.

---

## Code Standards

**Python:** ruff (linting) + black (formatting). Enforced by pre-commit hooks and CI.  
**JavaScript:** ESLint config in `frontend/`. No inline styles.  
**SQL:** snake_case table and column names. All migrations in `backend/alembic/versions/`.

Run checks manually:
```bash
make lint    # ruff check + black --check
make test    # pytest + frontend tests
```
