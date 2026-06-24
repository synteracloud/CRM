---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human
Phase: 2.95
---

# PRODUCT DECISION REGISTER

> All product-scope decisions identified during Phase 2.9–2.95.
> Source of truth for what is decided, deferred, and pending owner input.

---

## Decision Table

| ID | Description | Recommendation | Classification | Frontend Impact | Backend Impact | Priority | Status |
|----|-------------|----------------|----------------|-----------------|----------------|----------|--------|
| OA-001 | contacts.delete RBAC scope missing — returns 403 for all roles | Grant to tenant_admin + super_admin (Option A) | OWNER_CONFIRMATION_ONLY | Hide delete button for viewer/field_agent/support_agent/tenant_owner | 2 lines in rbac-scopes.js | CRITICAL — commercial launch blocker | Pending approval |
| OA-002 | JTI blocklist in-memory — cleared on restart, unsafe on multi-instance | Accept for C6 launch; Redis migration in auth hardening sprint post-C6 | OWNER_CONFIRMATION_ONLY | None | ~10 lines in auth hardening sprint | HIGH — pre-scale security | Deferred to post-C6 sprint |
| OA-003 | JazzCash/Easypaisa in STUB mode — no real payments | Obtain merchant credentials before launch (Option A), or defer to C7 (Option D) | TRUE_OWNER_DECISION | Minimal — G-04 built for stub state | Set env vars in render.yaml; zero code changes | CRITICAL — commercial launch blocker | Owner decision required |
| OA-004 | AI inference model unselected — rule-based only | Keep rule-based for C6; defer LLM to C7 (Option C) | OWNER_CONFIRMATION_ONLY | None — M-01, M-02 functional with rule-based | None at launch | MEDIUM — C7 feature | Deferred to C7 |
| OA-005 | contract_lifecycle_management — no gateway route | Defer to C7 — no contracts page in C6 scope | RESOLVED | None — no contracts screen in DESIGN-SPEC.md | None at launch; v1-contracts.routes.js in C7 | LOW — C7 feature | Resolved — defer to C7 |
| OA-006 | Security test JSON artifacts — compliance evidence or CI output? | Move to docs/reports/security/ as compliance evidence | OWNER_CONFIRMATION_ONLY | None | None | LOW — hygiene | Pending confirmation |
| OA-007 | C5 load test HTML reports — preserve or gitignore? | Move c5-prod-*.html to docs/reports/load/; gitignore dev reports | OWNER_CONFIRMATION_ONLY | None | None | LOW — hygiene | Pending confirmation |
| OA-008 | Password hashing SHA-256 (not bcrypt) | Accept for C6; transparent bcrypt migration in C7 | OWNER_CONFIRMATION_ONLY | None | C7: add re-hash-on-login logic | MEDIUM — C7 security sprint | Deferred to C7 |
| OA-009 | Refresh token not revoked on logout | Bundle with OA-002 in post-C6 auth hardening sprint | OWNER_CONFIRMATION_ONLY | None | 3–5 lines in v1-auth.routes.js | HIGH — pre-scale security | Deferred to post-C6 sprint |

---

## Decision Count by Classification

| Classification | Count | Items |
|----------------|-------|-------|
| RESOLVED | 1 | OA-005 |
| OWNER_CONFIRMATION_ONLY | 7 | OA-001, OA-002, OA-004, OA-006, OA-007, OA-008, OA-009 |
| TRUE_OWNER_DECISION | 1 | OA-003 |

---

## Commercial Launch Gate

Two items must be resolved before commercial launch:

1. **OA-001** — contacts.delete scope (2-line code fix; owner confirms which roles)
2. **OA-003** — payment credentials (vendor relationship; owner obtains credentials)

All other items are either deferred to C7 or post-C6 sprints.

---

## Sprint Planning View

### Pre-launch (before C6 go-live)
| Action | Item | Effort |
|--------|------|--------|
| Confirm contacts.delete role grant | OA-001 | 2 lines |
| Obtain JazzCash + Easypaisa credentials | OA-003 | Business action |

### Post-C6 Sprint 1 — Auth Hardening
| Action | Item | Effort |
|--------|------|--------|
| Migrate JTI blocklist to Redis | OA-002 | ~10 lines |
| Fix logout to revoke refresh token | OA-009 | 3–5 lines |

### Post-C6 Sprint 2 — Security Upgrade
| Action | Item | Effort |
|--------|------|--------|
| Add transparent bcrypt re-hash on login | OA-008 | ~20 lines |

### C7 Features
| Action | Item |
|--------|------|
| LLM inference model integration | OA-004 |
| Contract lifecycle gateway route | OA-005 |

---

*End PRODUCT_DECISION_REGISTER.md*
