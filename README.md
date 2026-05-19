# Pakistan CRM OS

**Execution-First Business Execution System for Pakistan's SMB market.**

> Never lose a lead. Never miss a follow-up. Always know your cash position.

---

## What this is

This is not CRM software. It is a **Business Execution System** — built for Pakistan's SMB market where leads are lost in WhatsApp, follow-ups are forgotten, and cash position is unknown until it's too late.

**Three core guarantees:**
1. Every WhatsApp message becomes a tracked contact. No prospect falls through the cracks.
2. The system auto-schedules, enforces, and escalates every follow-up commitment.
3. Invoices, payments (JazzCash/Easypaisa/cash), and collections are tracked in real time.

**Primary interaction layer:** WhatsApp — not a browser form.  
**Primary market:** Pakistan SMBs — PKR, Lakh/Crore notation, JazzCash, Easypaisa, Urdu.

---

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend  —  NexLink + Custom Pages    │  src/app/ (75 custom + 96 library)
└──────────────────┬──────────────────────┘
                   │ HTTP / REST
┌──────────────────▼──────────────────────┐
│  Gateway  —  Node.js API Gateway        │  backend/gateway/   port 3000
└──────────────────┬──────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────┐
│  Services  —  Python / FastAPI          │  backend/services/  port 5002
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  PostgreSQL 16  +  Redis                │  port 5432 / 6379
└─────────────────────────────────────────┘
```

**Six platform engines:** Follow-up · Collections · WhatsApp · Activity Control · Activation · Execution Control Plane  
**Architecture pattern:** DDD + Microservices + Adapter-based country isolation  
**Pakistan adapter:** `backend/adapters/pakistan/` — JazzCash, Easypaisa, 360dialog, Gupshup

Full architecture: [`backend/docs/architecture-overview.md`](backend/docs/architecture-overview.md)  
Architecture decisions: [`backend/docs/adr/`](backend/docs/adr/)

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- `D:\Python\python.exe` (3.12.10) for local Python work
- Node.js 20+ for gateway local work

### Run with Docker (recommended)

```bash
cd backend
cp .env.example .env        # fill in DB_PASSWORD at minimum
docker compose up
```

Services start at:
- Gateway API: `http://localhost:3000`
- Python services: `http://localhost:5002`
- OpenAPI docs: `http://localhost:5002/docs`
- PostgreSQL: `localhost:5432`

### Frontend dev server

```powershell
cd frontend
npm install
npm run serve               # http://localhost:3001
```

### Python environment (local)

```powershell
D:\CRM\backend\.venv\Scripts\Activate.ps1
pip install -r backend\services\requirements.txt
```

### Common commands

```bash
make dev        # start full stack via docker compose
make test       # run pytest + npm test
make migrate    # run database migrations
make lint       # ruff + black check
```

---

## Project Structure

```
D:\CRM\
├── frontend/               # NexLink-based frontend
│   └── src/app/            # 96 library pages + 75 custom pages (in progress)
├── backend/
│   ├── gateway/            # Node.js API gateway (port 3000)
│   ├── services/           # Python/FastAPI service layer (port 5002)
│   ├── adapters/           # Pakistan-specific adapters (JazzCash, WhatsApp)
│   ├── db/                 # PostgreSQL schemas + migrations
│   ├── docs/               # 47 domain specs + ADRs
│   └── docker-compose.yml  # Full-stack local dev
├── REBUILD-PLAN.md         # 10/10 roadmap (6 phases, ~21 weeks)
├── PENDING.md              # Task checklist — 229 tasks
├── DESIGN-SPEC.md          # 75 custom pages, 13 archetypes
└── DOC-CATALOGUE.md        # Full document index
```

---

## Documentation Index

| Document | Purpose |
|---|---|
| [`DESIGN-SPEC.md`](DESIGN-SPEC.md) | 75 custom pages, archetypes A–M, build phases |
| [`REBUILD-PLAN.md`](REBUILD-PLAN.md) | 10/10 roadmap — phases, grades, deliverables |
| [`backend/README.md`](backend/README.md) | Backend system identity and module map |
| [`backend/docs/architecture-overview.md`](backend/docs/architecture-overview.md) | Layer model, engine registry, service architecture |
| [`backend/docs/domain-model.md`](backend/docs/domain-model.md) | 58 canonical domain entities |
| [`backend/CONSTRAINTS.md`](backend/CONSTRAINTS.md) | 17 non-negotiable build constraints |
| [`backend/PENDING.md`](backend/PENDING.md) | Blocked items (P-016 credentials, P-017 Urdu) |
| [`DOC-CATALOGUE.md`](DOC-CATALOGUE.md) | Index of all 90+ project documents |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute — branch naming, commits, PRs |

---

## Key Constraints

- **C-001** — RTL from day 1. Cannot be retrofitted.
- **C-007** — All API calls via `crm-api.js` with `DUMMY_MODE: true` until backend is live.
- **C-009** — `JAZZCASH_STUB_MODE` and `EASYPAISA_STUB_MODE` must remain `true` until P-016 sandbox credentials are verified.
- **P-016** — JazzCash/Easypaisa production credentials: blocked, awaiting external onboarding.
- **P-017** — Urdu string review: blocked, awaiting Urdu speaker.

Full constraints: [`backend/CONSTRAINTS.md`](backend/CONSTRAINTS.md)

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).
