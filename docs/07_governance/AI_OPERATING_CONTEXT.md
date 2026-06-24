Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI

---

# AI OPERATING CONTEXT — Pakistan CRM OS

## Purpose

This document is the primary context document for any AI agent (Claude or other) starting work on this repository. Read this document FIRST before reading any source code. Every critical fact about the system is stated here with a file reference for verification.

---

## CURRENT_PHASE

**Phase:** C6 — Commercial Launch
**Status:** Active — in progress
**Date confirmed:** 2026-06-21 (U10 Final Status)

**What is complete:**
- 75/75 custom HTML pages built and browser-approved
- 34 FastAPI Python backend modules built
- 44 gateway route groups (228 API endpoints) built
- 18 database schemas + 12 Alembic migrations applied (local and production)
- 3 application services + 2 managed data services live on Render.com (gateway + services + frontend + managed PostgreSQL + managed Redis = 5 Render entities total)
- 79 backend pytest test files, 25 Playwright E2E test files, 8 API contract test files
- CI/CD: GitHub Actions 11 jobs passing on main (`.github/workflows/ci.yml` — backend-lint, backend-test, security-scan, arch-guard, gateway-lint, api-contracts, build-gateway, build-services, deploy-staging, smoke-staging, deploy-prod; separate `deploy-runtime.yml` for Render.com production deploys)
- C0 environment seal active (all tool caches on D:)

**What is in progress:**
- Full live-API re-verification pass (Phase 6 Component 3) — all 75 pages pending
- 5 pages confirmed wired to live API; remainder use DUMMY_MODE graceful fallback
- Governance Implementation Phase 1 (this document set)

**DUMMY_MODE status:**
- crm-api.js DUMMY_MODE: false (set in C1)
- Pages that confirmed wired to live API: integrations.html (G-05), report-builder.html (H-07), data-governance.html (J-03), engagement-dashboard.html (A-08), billing-settings.html (G-04 wired but content blocked by P-016)
- All other 70 pages: have live API calls with graceful dummy fallback from crm-dummy.js

**Source:** COMMERCIALISATION-PLAN.md (RESUME POINT table), CURRENT_PROJECT_STATUS.md, AUTHORITY_RECONSTRUCTION_REPORT.md §12

---

## FROZEN_DECISIONS

These decisions are made and must not be changed without explicit human sign-off. Every item has code evidence.

| Decision | What Is Frozen | Code Evidence |
|---|---|---|
| PKR currency | PKR is the only currency. No multi-currency. Lakh/Crore number formatting. | crm-components.js pkr() formatter; Invoice.currency default "PKR" |
| WhatsApp primary channel | WhatsApp is the primary interaction layer, not an integration. Inbound messages auto-create Contacts and Leads. | ADR-003; adapters/pakistan/messaging/; v1-whatsapp-webhooks.routes.js |
| FastAPI (Python) backend | All domain service modules use FastAPI (Python 3.12). | backend/src/ modules; requirements.txt; Dockerfiles |
| Express.js API gateway | Node.js Express gateway proxies all frontend↔backend traffic. 44 route groups. | backend/gateway/app.js; package.json |
| PostgreSQL 14 database | 18 domain schemas. All schemas in db/*/schema.sql. 12 Alembic migrations. | render.yaml crm-postgres; backend/db/; backend/alembic/ |
| Redis (cache + rate limiting) | JWT JTI blocklist; rate-limit middleware; OTP TTL; FeatureFlag cache (C3). | render.yaml crm-redis; gateway/middleware/jti-blocklist.js; gateway/middleware/rate-limit-hook.js |
| NexLink CSS framework | 96 library pages + 75 custom pages built on NexLink. Cannot switch frameworks. | FRAMEWORK.md; frontend/src/app/*.html |
| JWT HS256 authentication | 15-min access tokens, 7-day refresh tokens, single-use rotation, JTI revocation. | gateway/routes/v1-auth.routes.js; gateway/middleware/auth-rbac.js |
| Multi-tenant application-level isolation | x-tenant-id header on every request; every SQL binds tenant_id; semgrep CI enforces. | gateway/middleware/auth-rbac.js; .semgrep/tenant-isolation.yaml |
| Render.com deployment | 3 services (gateway, services, frontend) + managed PostgreSQL + Redis. Free tier → scale. | render.yaml |
| DDD + L1/L2/L3 adapter pattern | core/* → adapters/interfaces/* only. core/* → adapters/pakistan/* FORBIDDEN. Ruff CI enforces. | ADR-001; ADR-002; backend/docs/architecture/ |
| Default-deny RBAC, 91 scopes, 7 roles | Every route has requireScopes([]); no implicit access; scope list frozen in rbac-scopes.js. | gateway/config/rbac-scopes.js; gateway/middleware/auth-rbac.js |
| JAZZCASH_STUB_MODE=true | JazzCash adapter in stub mode. Real payments blocked until P-016 credentials verified. | render.yaml; adapters/pakistan/payments/jazzcash.py |
| EASYPAISA_STUB_MODE=true | Easypaisa adapter in stub mode. Same as JazzCash. | render.yaml; adapters/pakistan/payments/easypaisa.py |

---

## KNOWN_CONSTRAINTS

Verified constraints from U0–U10 findings. These are not design choices — they are external limitations.

| Constraint ID | Constraint | Impact | Unblocking Condition |
|---|---|---|---|
| P-016 | JazzCash/Easypaisa live payment integration blocked | billing-settings.html (G-04) is static stub; POST /payments is stub; WF-002 WhatsApp reminders work but payment confirmation is stub | Real sandbox credentials received + full E2E sandbox test passes |
| P-017 | Urdu customer-facing strings pending native speaker review | notifications.html (G-06) has EN strings only; RTL CSS and locale infrastructure is built; Urdu strings exist with <!-- UR_TODO: --> markers | Native Urdu speaker reviews and approves all _STRINGS['ur'] values |
| MR-001 | Facebook/Instagram lead capture blocked | Not rendered in UI; hidden div with data-unblock="MR-001" | Meta Business Manager account setup + API approval |
| MR-003 | Voice note transcription blocked | Microphone icon is disabled in UI | Transcription provider selected + credentials |
| MR-007 | Kuickpay adapter blocked | Not rendered in UI | Kuickpay API credentials |
| AI-001 | AI inference model not selected | ai-copilot.html (M-01) is advisory-only shell; all AI is rule-based (no OpenAI/Anthropic/Google SDK in requirements.txt) | Human decision on AI inference provider; SDK added to requirements.txt |
| D-001 | contract_lifecycle_management module has no gateway route | 12 API endpoints defined in Python backend but no v1-contract*.routes.js in gateway | Human architectural decision: expose via gateway or archive |
| D-002 | custom_objects module routing mechanism unresolved | custom_object_framework/ and custom_objects/ confirmed in backend; no v1-custom-objects.routes.js found in gateway route list | Human decision on routing mechanism or gateway file location |
| D-003 | 5 entities lack confirmed DB schema attribution | Entity fields inferred from gateway code; schema.sql not directly read for all entities | Code verification pass on specific schema files |
| starlette CVEs | 3 known CVEs in starlette transitive dependency | Accepted risk; FastAPI 0.115 compatibility constraint limits upgrade | FastAPI upstream fix or version bump |
| PTA compliance | Pakistan Telecommunications Authority regulations apply to WhatsApp message content. Compliance adapter hooks are built in adapters/pakistan/ but details are pending legal review. | WhatsApp message content may need PTA-compliant disclaimers; affects WhatsApp broadcast campaigns. | Legal review of compliance-adapter.md + human sign-off |
| FBR compliance | Federal Board of Revenue requirements for invoice formatting (Pakistan tax authority). Invoice formatting requirements not yet verified. | Invoices generated via /invoice-summaries may need FBR-specific fields (NTN, STRN). | Human legal review + FBR API integration if required |

---

## ACTIVE_AUTHORITY_DOCS

These are the documents that govern current behavior. Read these before making any change.

| Document | Path | Authority Level | What It Governs |
|---|---|---|---|
| PROJECT_CHARTER.md | docs/00_authority/PROJECT_CHARTER.md | Critical | Project scope, frozen decisions, stakeholders |
| FEATURE_SCOPE.md | docs/00_authority/FEATURE_SCOPE.md | Critical | Full feature list, phase gates, freeze status |
| DOMAIN_MODEL.md | docs/00_authority/DOMAIN_MODEL.md | Critical | All entities, relationships, business rules |
| PRODUCT_WORKFLOWS.md | docs/00_authority/PRODUCT_WORKFLOWS.md | Critical | 5 primary workflows, 5 system workflows, events |
| FULLSTACK_STITCHING_CONTRACT.md | docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md | Critical | Feature → entity → API → page → permission traceability |
| AI_OPERATING_CONTEXT.md | docs/07_governance/AI_OPERATING_CONTEXT.md | Critical | This document — AI session context |
| REVISED_DECISION_ESCALATION_MATRIX.md | docs/07_governance/REVISED_DECISION_ESCALATION_MATRIX.md | High | What AI can do vs what requires human — 4-tier model (supersedes DECISION_ESCALATION_MATRIX.md) |
| SAFE_REPOSITORY_HYGIENE_POLICY.md | docs/07_governance/SAFE_REPOSITORY_HYGIENE_POLICY.md | High | Definition, qualifying criteria, and action list for Tier 1 SAFE_REPOSITORY_HYGIENE |
| APPROVAL_RECLASSIFICATION_REPORT.md | docs/07_governance/APPROVAL_RECLASSIFICATION_REPORT.md | Medium | Full reclassification of all open repository restructuring items |
| REPOSITORY_HYGIENE_EXECUTION_GUIDELINES.md | docs/07_governance/REPOSITORY_HYGIENE_EXECUTION_GUIDELINES.md | Medium | Practical execution guide for Tier 1 hygiene tasks |
| ADR-001_PROJECT_FOUNDATION.md | docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md | High | Architecture decisions and rationale |
| COMMERCIALISATION-PLAN.md | COMMERCIALISATION-PLAN.md | Critical | C0–C6 phases; current phase gate; non-negotiable rules |
| CLAUDE.md | CLAUDE.md | Critical | Page build rules; scope gate; recurring bug checklist |
| DESIGN-SPEC.md | DESIGN-SPEC.md | Critical | 75 pages, 13 archetypes, 8 build phases |
| FRAMEWORK.md | FRAMEWORK.md | Critical | CSS stack, JS stack, shell rules, QC tiers T1–T4 |
| backend/CONSTRAINTS.md | backend/CONSTRAINTS.md | Critical | 17 build constraints — never violate |
| rbac-scopes.js | backend/gateway/config/rbac-scopes.js | Critical | 7 roles, 91 scopes — source of truth for RBAC |
| AUTHORITY_RECONSTRUCTION_REPORT.md | docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md | High | Full U1 system summary |
| CURRENT_PROJECT_STATUS.md | docs/reports/u-series/CURRENT_PROJECT_STATUS.md | High | Phase-by-phase build status |

---

## PROTECTED_AREAS

These areas must not be modified without explicit human approval. They are security-critical or data-integrity-critical.

| Area | Files | Why Protected |
|---|---|---|
| Authentication / JWT logic | gateway/routes/v1-auth.routes.js, gateway/middleware/auth-rbac.js | Token issuance, scope enforcement, JTI revocation — any bug here compromises all tenants |
| Tenant isolation middleware | gateway/middleware/auth-rbac.js, .semgrep/tenant-isolation.yaml | Cross-tenant data leakage is a critical security failure |
| Payment webhook handlers | gateway/routes/v1-payment-webhooks.routes.js, adapters/pakistan/payments/ | Financial integrity; stub mode must remain until P-016 cleared |
| Database migrations (Alembic) | backend/alembic/versions/ | Schema changes are irreversible in production without a down-migration |
| CI/CD pipeline configuration | .github/workflows/ci.yml | Breaking CI breaks the deploy gate |
| RBAC scope definitions | gateway/config/rbac-scopes.js | Adding/removing scopes changes access control for all tenants |
| AuditLog write path | gateway/routes/v1-audit.routes.js, db/audit_compliance_db/ | Audit log is immutable by design; any modification undermines compliance |

---

## DO_NOT_MODIFY_AREAS

These are completely frozen — no modifications under any circumstances without explicit human decision and documentation.

| Area | Reason |
|---|---|
| Production database data | No tool should write to production DB outside migrations |
| AuditLog records (db rows) | Immutable by design; hash-chain integrity would be broken |
| Tenant isolation layer | Removing or weakening isolation would expose customer data across tenants |
| C: drive (Windows) | C0 seal in force — all tools must write to D:; see COMMERCIALISATION-PLAN.md §C0 |
| render.yaml payment stub flags | JAZZCASH_STUB_MODE and EASYPAISA_STUB_MODE must remain true until P-016 approved |

---

## REQUIRED_VALIDATIONS

Before any code change is considered complete, validate all of the following:

| Validation | Command / Check | Threshold |
|---|---|---|
| Backend test suite | `pytest --cov=. --cov-fail-under=80` from backend/ | 80% coverage; 0 failures |
| Playwright E2E | `pytest tests/e2e/playwright/ -v` | All 25 test files pass |
| API contract tests | `pytest tests/api/ -v` | 0 contract failures |
| No C: drive leakage | After any tool run: `(Get-PSDrive C).Free` — compare to c-seal/baseline.txt | Delta < 2MB |
| DUMMY_MODE status | Confirm crm-api.js DUMMY_MODE: false (not per-page override back to true) | false everywhere |
| Tenant isolation | `semgrep --config=.semgrep/tenant-isolation.yaml backend/` | 0 violations |
| Security scans | pip-audit (0 Critical CVEs); npm audit --prefix frontend (0 Critical CVEs) | 0 Critical |
| Page structure | Any modified app/*.html must have crm-custom.css link + no hardcoded footer | Per CLAUDE.md §Build Checklist |

---

## OPEN_ARCHITECTURAL_QUESTIONS

Compressed in Phase 2.97 (2026-06-23). 5 original items → 1 remaining genuine owner decision.

| ID | Question | Impact | Status |
|---|---|---|---|
| D-001 | Should contract_lifecycle_management module be exposed via a gateway route? | Backend module complete (12 endpoints). No C6 frontend page exists per DESIGN-SPEC.md. | AUTO-CLOSED — OUT-OF-SCOPE for C6. Defer to C7 when contracts page is built. |
| D-002 | Is custom_objects module (K-02 object-builder.html) active in C6 product scope or a demo shell? | If active: gateway route needed. If demo: build K-02 as advisory shell with crm-dummy.js. | OWNER-REQUIRED — product scope decision. Frontend builds K-02 as advisory shell pending decision. |
| D-003 | 5 entity DB schema attributions inferred from gateway code. | Low impact — entities function correctly; documentation accuracy only. | AUTO-CLOSED — investigation task, not owner decision. Backend team to verify schema.sql files directly. |
| D-004 | Which AI inference provider should be selected? | M-01 (ai-copilot.html) and M-02 (ai-insights.html) launch with rule-based scoring. LLM upgrade is additive. | AUTO-CLOSED — current rule-based implementation IS the C6 production model. LLM integration is C7 scope. |
| D-005 | 4 backend docs may be historical artifacts (backend/docs/phase4-gap-register.md + 3 others). | Low impact — organizational only. | SAFE-DEFAULT — archive as historical artifacts via SAFE_REPOSITORY_HYGIENE. No owner decision required. |

**Remaining open (1):** D-002 — custom objects C6 product scope. Frontend authority capture documents K-02 as advisory shell pending owner decision. No C6 launch blocker.

---

## DOCUMENTATION_FRESHNESS_POLICY

**Rule:** Any AI agent that modifies code affecting a documented claim must update the relevant governance document in the same session before closing.

**Scope of updates required:**
- API endpoint added/changed → update FULLSTACK_STITCHING_CONTRACT.md + API_INVENTORY.md
- Entity field added/changed → update DOMAIN_MODEL.md + ENTITY_INVENTORY.md
- Role or scope added/changed → update ROLE_PERMISSION_INVENTORY.md + DOMAIN_MODEL.md
- Workflow step added/changed → update PRODUCT_WORKFLOWS.md + WORKFLOW_INVENTORY.md
- New module created → update MODULE_INVENTORY.md + FEATURE_SCOPE.md
- Page wired to live API → update CURRENT_PROJECT_STATUS.md + FULLSTACK_STITCHING_CONTRACT.md
- Architecture decision made → create new ADR in docs/06_decisions/

**Exception:** Test additions and bug fixes that do not change documented behavior do not require governance doc updates.

---

## CONTRACT_COMPATIBILITY_POLICY

**Rule:** The FULLSTACK_STITCHING_CONTRACT.md is the single source of truth for feature-level traceability. Any change to an API endpoint, entity, or frontend page must be reflected in the corresponding stitch contract entry before the change is merged.

**How to update:** Edit the relevant feature section (1–10) in FULLSTACK_STITCHING_CONTRACT.md. Add the new endpoint to the API Endpoints table; update DUMMY_MODE status if the page is newly wired; update Test Coverage if a new test was added.

**TBD items:** Any section marked "TBD – REQUIRES VERIFICATION" must be resolved before that feature is considered fully documented.

---

*End AI_OPERATING_CONTEXT.md*
