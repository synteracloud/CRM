Status: Draft
Authority Level: Medium
Last Reviewed: 2026-06-22
Owner: Human

# CONTRACT_VERSION_REGISTRY.md
> Source: backend/gateway/routes/v1-*.routes.js (API version prefix), backend/services/ai/entities.py (model versioning), backend/db/*/schema.sql (Alembic migration versions), backend/db/alembic/versions/ (migration history)

---

## 1. API Version

The backend API is versioned at the URL prefix level:

| Tier | Version prefix | Example |
|---|---|---|
| Gateway (Node.js) | `/api/v1/` | `GET /api/v1/leads` |
| FastAPI internal | `/internal/` | `POST /internal/leads/:id/register` |
| FastAPI public | `/api/v1/` | `GET /api/v1/cases` |

**Current API version:** v1

**Version strategy:**
- Single URL prefix for all routes — no per-route versioning
- No v2 routes exist
- Breaking changes require a new prefix (v2) — NOT currently implemented
- Individual route deprecation: NOT IMPLEMENTED — no deprecation headers in any gateway route file. Will be defined when v2 routes are planned (C7+).

---

## 2. AI Model Versions

Models are versioned with explicit version strings in the SCORING_MODELS constant:

| Model ID | Version | Type | Status |
|---|---|---|---|
| `lead_score_v1` | v1 | rule_based | ACTIVE |
| `churn_predict_v1` | v1 | rule_based | ACTIVE |
| `clv_estimate_v1` | v1 | rule_based | ACTIVE |

**Versioning contract:** New model versions (v2) will be registered in `intelligence_db.scoring_models` with a new `model_key` string. The `lead_scores` table stores `model_id` for each score, enabling score history to reference the generating model version.

---

## 3. Database Migration Versions (Alembic)

12 confirmed migrations as of 2026-06-22:

| Migration ID | Name | Status |
|---|---|---|
| 0001 | followup_schema | Applied |
| 0002 | followup_scheduler | Applied |
| 0003 | followup_metrics | Applied |
| 0004 | collections_schema | Applied |
| 0005 | payments_schema | Applied |
| 0006 | activity_schema | Applied |
| 0007 | notifications_schema | Applied |
| 0008 | conversations_schema | Applied |
| 0009 | inbox_schema | Applied |
| 0010 | cases_schema | Applied |
| 0011 | ai_scoring_schema | Applied |
| 0012 | lead_management_c1_columns | Applied |

**Migration trigger:** POST /internal/migrate — runs `alembic upgrade head`. Called manually or as part of deployment.

---

## 4. Contract Version Registry (Document Versions)

This registry tracks the version of each fullstack contract document:

| Document | Version | Date | Change Summary |
|---|---|---|---|
| AUTH_AND_TENANCY_CONTRACT.md | 0.1-draft | 2026-06-22 | Initial extraction from implementation |
| USER_ROLES_AND_PERMISSIONS.md | 0.1-draft | 2026-06-22 | Initial extraction — 7 roles, 91 scopes |
| DATA_SHAPE_REGISTRY.md | 0.1-draft | 2026-06-22 | Initial shape extraction from 18 DB schemas |
| VALIDATION_PARITY.md | 0.1-draft | 2026-06-22 | Initial gap register — V-001 to V-005 |
| CONTRACT_VERSION_REGISTRY.md | 0.1-draft | 2026-06-22 | Registry created |
| BACKEND_ARCHITECTURE.md | 0.1-draft | 2026-06-22 | Initial extraction |
| DATABASE_SCHEMA.md | 0.1-draft | 2026-06-22 | Initial extraction — 18 schemas |
| API_CONTRACT.md | 0.1-draft | 2026-06-22 | Initial extraction — 228 endpoints |
| ERROR_CONTRACT.md | 0.1-draft | 2026-06-22 | Initial extraction — 9 canonical codes |
| SERVICE_CATALOG.md | 0.1-draft | 2026-06-22 | Initial extraction — 10 services |
| INTEGRATION_CATALOG.md | 0.1-draft | 2026-06-22 | Initial extraction — 8 integrations |
| VALIDATION_RULES.md | 0.1-draft | 2026-06-22 | Initial extraction |
| EVENT_AND_QUEUE_ARCHITECTURE.md | 0.1-draft | 2026-06-22 | Initial extraction |

**Versioning scheme:**
- `0.x-draft` — initial extraction, not human-reviewed
- `1.0` — human-reviewed and approved
- `1.x` — minor updates to existing content
- `2.0` — structural change or major update

---

## 5. Known Breaking Changes History

No breaking API changes to document — the API has been v1 from initial implementation.

---

## 6. Event Schema Versions

Events referenced in workflow trigger_events use `.v1` suffix convention.

**Source:** `backend/docs/infrastructure/event-catalog.md` (canonical event schema document — all payload schemas defined here)

| Event | Version | Payload Schema (key fields) |
|---|---|---|
| `opportunity.stage.changed.v1` | v1 | `{ event_id, occurred_at, opportunity_id, tenant_id, previous_stage, stage, forecast_category, amount, close_date, is_closed, is_won, updated_at }` |
| `opportunity.closed.v1` | v1 | `{ event_id, occurred_at, opportunity_id, tenant_id, stage, is_won, is_closed, amount, close_date, updated_at }` |
| `lead.idle.v1` | v1 | Registered in EVENT_NAME_SET. Payload: `{ event_id, occurred_at, lead_id, tenant_id }` (trigger_events DSL in workflow catalog) |
| `lead.created.v1` | v1 | `{ event_id, occurred_at, lead_id, tenant_id, owner_user_id, source, status, score, email, phone, company_name, created_at }` |
| `invoice.overdue.v1` | v1 | Registered in EVENT_NAME_SET. Trigger event for collections_reminder workflow. Payload: `{ event_id, occurred_at, invoice_id, tenant_id }` |
| `case.sla.breached.v1` | v1 | `{ event_id, occurred_at, case_id, tenant_id, owner_user_id, priority, status, sla_due_at }` |

**Note:** All events use `.v1` suffix indicating first-version contracts. Full payload schemas are in `backend/docs/infrastructure/event-catalog.md`. Future breaking changes to event payload shapes must increment to `.v2` and register a new event name in `catalog_events.py`.

**Route deprecation strategy:** Not implemented. Single v1 API prefix in use. No per-route deprecation headers exist. Deprecation strategy will be defined when v2 routes are planned (C7+).

---

*End CONTRACT_VERSION_REGISTRY.md*
