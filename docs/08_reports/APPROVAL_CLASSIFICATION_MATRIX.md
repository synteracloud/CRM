Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI

# APPROVAL CLASSIFICATION MATRIX — Phase 2.9
> Full matrix of every open item reviewed in Phase 2.9: classification, status, and resolution or reason.

---

| Item ID | Description | Source | Classification | Status | Resolution / Reason |
|---------|-------------|--------|----------------|--------|---------------------|
| UC-001 | EmailStr not used in FastAPI | UNVERIFIED_CLAIMS | Documentation Correction | RESOLVED | grep confirmed absent; VALIDATION_RULES.md corrected |
| UC-002 | Phone regex pattern | UNVERIFIED_CLAIMS | Repository Determinable | OPEN | No regex found in grep; phone format enforced at DB level only |
| UC-003 | CNIC/NTN/STRN in DB | UNVERIFIED_CLAIMS | Resolved By Evidence | RESOLVED | Fields not implemented; confirmed by grep across backend/db/ and backend/src/ |
| UC-004 | Dev token in production | UNVERIFIED_CLAIMS | Resolved By Evidence | RESOLVED | JWT_SECRET confirmed in render.yaml line 37; G-MED-003 closed |
| UC-005 | SLA breach scanner | UNVERIFIED_CLAIMS | Resolved By Evidence | RESOLVED | events emitted from services/cases/service.py; G-MED-002 closed |
| UC-006 | DB pool size | UNVERIFIED_CLAIMS | Resolved By Evidence | RESOLVED | DB_POOL_MAX env var in pool.js; G-LOW-001 closed |
| UC-007 | CI job count (11) | UNVERIFIED_CLAIMS | Resolved By Evidence | RESOLVED | 11 jobs counted in ci.yml |
| UC-008 | Refresh token revocation | UNVERIFIED_CLAIMS | Resolved By Evidence (gap confirmed) | RESOLVED | Confirmed gap; G-HIGH-002 updated; OA-009 created |
| DD-001 | AI_OPERATING_CONTEXT schema count 20→18 | DOC_DRIFT | Documentation Correction | RESOLVED (Step 7) | Fixed 2026-06-23 in Step 7 |
| DD-002 | AI_OPERATING_CONTEXT Playwright count 23→25 | DOC_DRIFT | Documentation Correction | RESOLVED (Step 7) | Fixed 2026-06-23 in Step 7 |
| DD-003 | AI_OPERATING_CONTEXT Status: Draft | DOC_DRIFT | Authority Correction | RESOLVED (Step 7) | Promoted to Active |
| DD-004 | G-HIGH-005 leads.delete false alarm | DOC_DRIFT | Documentation Correction | RESOLVED (Step 7) | Closed in gap register |
| DD-005 | USER_ROLES_AND_PERMISSIONS leads.delete TBD | DOC_DRIFT | Documentation Correction | RESOLVED (Step 7) | TBD replaced with confirmation |
| DD-006 | 5 backend/docs/ files wrong location | DOC_DRIFT | Repository Hygiene | RESOLVED (Step 7) | Files moved to canonical locations |
| DD-007 | SKIP-BACKLOG.md wrong location | DOC_DRIFT | Repository Hygiene | RESOLVED (Step 7) | Moved to docs/04_testing/ |
| DD-008 | COMMERCIALISATION-PLAN.md root duplicate | DOC_DRIFT | Repository Hygiene | RESOLVED | git rm -f executed; canonical copy at docs/00_authority/ |
| DD-009 | 10 authority docs Status: Draft | DOC_DRIFT | Authority Correction | RESOLVED | All 10 promoted to Active |
| DD-010 | Service count 22→23 in 5 docs | DOC_DRIFT | Documentation Correction | RESOLVED | 5 report docs updated |
| UDC-001 | ci.yml undocumented | UNDOCUMENTED_CODE | Documentation Correction | RESOLVED | AI_OPERATING_CONTEXT.md updated |
| UDC-002 | automation_journeys no MODULE_INVENTORY entry | UNDOCUMENTED_CODE | Repository Hygiene | DEFERRED | Low priority; does not block frontend planning |
| UDC-003 | custom_objects no gateway route | UNDOCUMENTED_CODE | Product Policy Decision | OWNER DECISION | OA-005; product scope decision |
| UDC-004 | backend/docs/ subtree reference missing | UNDOCUMENTED_CODE | Repository Hygiene | DEFERRED | Low priority; add to docs/01_backend/README.md |
| UDC-005 | backend/middleware/ Python layer | UNDOCUMENTED_CODE | Resolved By Evidence | RESOLVED | Informational; MODULE_INVENTORY covers it |
| UDC-006 | backend/adapters/ directory | UNDOCUMENTED_CODE | Resolved By Evidence | RESOLVED | INTEGRATION_CATALOG sufficient for frontend |
| OA-001 | contacts.delete RBAC scope gap | OWNER_ITEMS | Security Policy Decision | OWNER DECISION | rbac-scopes.js change = TIER 2 per governance |
| OA-002 | JTI blocklist in-memory | OWNER_ITEMS | Security Policy Decision | OWNER DECISION | Auth middleware change = TIER 2 |
| OA-003 | JazzCash/Easypaisa stub mode | OWNER_ITEMS | Product Policy Decision | OWNER DECISION | Requires external vendor credentials |
| OA-004 | AI inference model | OWNER_ITEMS | Product Policy Decision | OWNER DECISION | Provider/cost business decision |
| OA-005 | contract_lifecycle_management gateway route | OWNER_ITEMS | Product Policy Decision | OWNER DECISION | C6 product scope decision |
| OA-006 | Security test artifacts disposition | OWNER_ITEMS | Security Policy Decision | OWNER DECISION | Compliance evidence policy |
| OA-007 | Load test reports disposition | OWNER_ITEMS | Deployment Decision | OWNER DECISION | Performance evidence preservation policy |
| OA-008 | Password hashing sha256 not bcrypt | OWNER_ITEMS | Security Policy Decision | OWNER DECISION | Security migration timing decision |
| OA-009 (NEW) | Refresh token not revoked on logout | PHASE 2.9 DISCOVERY | Security Policy Decision | OWNER DECISION | Auth route change = TIER 2; discovered this session |
| G-MED-002 | SLA breach scanner not confirmed | GAP_REGISTER | Resolved By Evidence | RESOLVED | Closed — events confirmed emitted |
| G-MED-003 | Dev token endpoint in prod | GAP_REGISTER | Resolved By Evidence | RESOLVED | Closed — JWT_SECRET confirmed |
| G-LOW-001 | DB pool size unknown | GAP_REGISTER | Resolved By Evidence | RESOLVED | Closed — configurable via env var |
| G-HIGH-002 | Refresh token revocation | GAP_REGISTER | Resolved By Evidence (gap confirmed) | RESOLVED | Updated with evidence; escalated as OA-009 |
| R-09 | Prompts/ → prompts/ rename | HYGIENE | Repository Hygiene (conditional) | DEFERRED | Requires grep check first; Windows NTFS cosmetic |
| R-10 | seal.ps1 move to scripts/ | HYGIENE | Repository Hygiene (conditional) | DEFERRED | Requires Makefile/CI grep check |
| RR-T3-01 to RR-T3-11 | 11 root session prompt files → docs/archive/ | HYGIENE | Repository Hygiene | NOT APPLICABLE | Root prompt files (BACKEND AUTHORITY CAPTURE.md etc.) are originals with no Prompts/Main/ copy; do not archive |

---

## Classification Summary

| Classification | Count |
|----------------|-------|
| Resolved By Evidence | 14 |
| Documentation Correction | 8 |
| Authority Correction | 4 |
| Repository Hygiene (executed) | 6 |
| Repository Hygiene (deferred, low priority) | 4 |
| Owner Decision Required | 9 |
| **Total** | **45** |

---

*End APPROVAL_CLASSIFICATION_MATRIX.md*
