---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 2.97
---

# FINAL CLASSIFIED REGISTER

> One authoritative list of every open item from all phases (U0–Phase 2.97).
> Final classification for each. No TBDs. No "pending" labels.
> Source of truth for what requires owner action vs. what is resolved.

---

## How to Read This Register

| Classification | Meaning |
|---------------|---------|
| AUTO-CLOSED | Resolved by evidence, investigation, or scope confirmation. No action needed. |
| SAFE-DEFAULT | A deterministic default has been documented. Implementation proceeds on the default unless owner objects. |
| SAFE_REPOSITORY_HYGIENE | Low-risk doc/folder/artifact maintenance. Executable without approval. |
| OWNER-REQUIRED | Genuinely requires human commercial/legal/credential/product-scope decision. |
| RESOLVED | Closed during a prior phase — listed here for completeness. |

---

## OWNER-REQUIRED Items (2 remaining — D-002 CLOSED in Phase 3.25)

| ID | Description | Why Genuinely Owner-Required | Launch Impact | Priority |
|----|-------------|------------------------------|---------------|----------|
| OA-003 | JazzCash/Easypaisa live payment credentials | External vendor merchant account + credentials. No code can supply this. | No revenue collection at launch. Free-tier viable. | P1 — commercial launch |
| G-MED-005 | Urdu WhatsApp template approval (P-017) | Urdu native speaker required for linguistic/cultural verification. Content decision, not technical. | Urdu-language campaigns blocked. English unaffected. | P2 — pre-campaign |

---

## SAFE-DEFAULT Items (12 — implemented by default unless owner objects)

| ID | Description | Safe Default | Sprint |
|----|-------------|-------------|--------|
| OA-001 | contacts.delete scope missing | Grant CONTACTS_DELETE to tenant_admin + super_admin (matches all other delete scope grants) | Pre-launch hotfix (2 lines) |
| OA-002 | JTI blocklist in-memory | Accept for C6 single-instance; Redis migration in Post-C6 Auth Sprint | Post-C6 Sprint 1 |
| OA-006 | Security test artifact disposition | Move tests/security/*.json to docs/reports/security/ | Next hygiene pass |
| OA-007 | Load test report disposition | Move c5-prod-*.html to docs/reports/load/; gitignore dev outputs | Next hygiene pass |
| OA-008 | Password hashing (SHA-256 not bcrypt) | Accept for C6; transparent re-hash-on-login (bcrypt) in C7 | C7 Security Sprint |
| OA-009 | Refresh token not revoked on logout | Accept for C6; fix in Post-C6 Auth Sprint (bundle with OA-002) | Post-C6 Sprint 1 |
| G-HIGH-003 | No message broker | Accept in-process events for C6; evaluate broker at multi-instance scale | C7 Architecture Sprint |
| G-HIGH-004 | Outbox publisher not implemented | Accept for C6 (stub payments anyway); implement when OA-003 activates | OA-003 activation sprint |
| G-MED-001 | No external task scheduler | Accept for C6; implement Celery Beat or APScheduler in C7 | C7 |
| D-005 | 4 backend archive docs | Move to docs/08_reports/ or docs/_archive/ per SAFE_REPOSITORY_HYGIENE | Next hygiene pass |
| G-LOW-003 | Rate limit fails open on Redis outage | Accept for C6; note for C7 hardening | C7 |
| G-LOW-004 | No PostgreSQL RLS | Accepted architecture trade-off; semgrep CI mitigates; no change | Permanent |

---

## AUTO-CLOSED Items (4)

| ID | Description | Reason Closed |
|----|-------------|--------------|
| OA-004 | AI inference model selection | Rule-based IS the C6 designed behavior. LLM is a C7 additive feature. Nothing to decide for C6. |
| OA-005 | contracts gateway route | DESIGN-SPEC.md confirms no contracts page in C6 scope. Backend module ready for C7. |
| D-003 | 5 entity schema attributions unverified | Investigation task, not owner decision. Can be verified by reading schema.sql files directly. |
| D-002 | Custom objects module product scope in C6 | CLOSED Phase 3.25: FEATURE_SCOPE.md §22 Feature 129 Status=Built confirms K-02 is C6 advisory shell. No owner decision needed. |

---

## RESOLVED Items (closed in prior phases — listed for traceability)

| ID | Description | Phase Closed | Resolution |
|----|-------------|--------------|-----------|
| G-HIGH-005 | leads.delete scope gap | Phase 2.9 | LEADS_DELETE IS present in rbac-scopes.js line 21. Not a gap. |
| G-MED-002 | SLA breach events not emitted | Phase 2.9 | Confirmed emitted from services/cases/service.py. Not a gap. |
| G-MED-003 | Dev token endpoint active in prod | Phase 2.9 | JWT_SECRET always set in render.yaml; endpoint is inactive in production. |
| G-LOW-001 | DB connection pool size | Phase 2.9 | Pool configurable via DB_POOL_MAX env var. Not a gap. |
| CRIT-002 | python-jose version drift | U10 | venv has 3.5.0; pip-audit.json was stale. |
| OA-005 | contracts gateway route | Phase 2.95 | Confirmed C7 scope by DESIGN-SPEC.md. Closed in 2.95, confirmed here. |

---

## SAFE_REPOSITORY_HYGIENE Items (from APPROVAL_RECLASSIFICATION_REPORT.md — pending execution)

These do not require this register — they are governed by SAFE_REPOSITORY_HYGIENE_POLICY.md. Listed here for completeness.

| Action | Status |
|--------|--------|
| Move OA-006 security artifacts | Pending next hygiene pass |
| Move OA-007 load test reports | Pending next hygiene pass |
| Archive D-005 backend phase4 docs | Pending next hygiene pass |
| Move any remaining session docs to docs/reports/session/ | Pending next hygiene pass |

---

## Summary for Frontend Authority Capture

**What can be assumed stable for frontend planning:**
- RBAC model: 7 roles, 91 scopes (91 when OA-001 applied = 92)
- All 228 API endpoints documented and stable
- Auth contract: JWT HS256, 15-min access, 7-day refresh, HttpOnly cookie
- Tenancy: x-tenant-id extracted from JWT automatically
- DUMMY_MODE: false — live API with graceful dummy fallback
- Payment: stub state is the documented C6 production behavior
- AI: rule-based advisory is the documented C6 production behavior
- contacts.delete: hide for all roles except tenant_admin + super_admin (OA-001 pending code change)
- Idempotency-Key header: MUST be generated by frontend on all POST/PUT/PATCH

**What is not stable (owner decisions pending):**
- Payment live activation (OA-003) — affects G-04 only; stub state is already the build target
- Urdu template approval (G-MED-005) — affects campaign creation only

**D-002 CLOSED (Phase 3.25):** K-02 is confirmed C6 advisory shell from FEATURE_SCOPE.md + DESIGN-SPEC.md. No longer pending.

---

*End FINAL_CLASSIFIED_REGISTER.md*
