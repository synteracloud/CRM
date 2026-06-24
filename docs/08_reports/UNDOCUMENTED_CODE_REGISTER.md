Status: Active
Authority Level: Medium
Last Reviewed: 2026-06-23
Owner: AI

# UNDOCUMENTED CODE REGISTER
> Code files, modules, services, routes, or test files found in the repository but NOT covered in documentation.

---

## Definition

An **undocumented code item** is a file or directory in the active source tree that:
- Is not referenced in any governance, backend authority, or inventory document
- Represents functionality, infrastructure, or test coverage not claimed in docs
- Could affect future development decisions if unknown

---

## Register

### UDC-001: ci.yml — Second CI/CD Workflow File
**Path:** `.github/workflows/ci.yml`
**Type:** CI/CD pipeline
**Description:** Full CI/CD pipeline file triggered on push to `main`, `feat/**`, `fix/**`, `chore/**` branches and version tags (`v*.*.*`). Runs stages including backend lint (ruff + black), backend tests, frontend lint, and presumably deployment gates.
**Documentation gap:** AI_OPERATING_CONTEXT.md only references `deploy-runtime.yml`. ci.yml is not mentioned in any governance or deployment doc.
**Impact:** Medium — any session starting without knowing ci.yml exists cannot reason about the full CI pipeline. The AI_OPERATING_CONTEXT.md claim "11 CI jobs passing on main" likely refers to jobs in ci.yml.
**Recommended action:** Add ci.yml reference to AI_OPERATING_CONTEXT.md deployment section and docs/05_deployment/.

---

### UDC-002: automation_journeys — No Dedicated MODULE_INVENTORY Entry
**Path:** `backend/src/automation_journeys/`
**Type:** Backend domain module
**Description:** Multi-step drip campaign automation engine. Handles sequenced message delivery over time.
**Documentation gap:** MODULE_INVENTORY.md only mentions it as a note within §12 (Marketing/Campaigns). No dedicated entry with entities, gateway route, or status.
**Impact:** Low — functionality is present and operational, but a future session reading MODULE_INVENTORY would not find a dedicated entry for this module.
**Recommended action:** Add §12.5 or similar entry for automation_journeys in MODULE_INVENTORY.md.

---

### UDC-003: custom_objects + custom_object_framework — No Gateway Route
**Path:** `backend/src/custom_objects/`, `backend/src/custom_object_framework/`
**Type:** Backend domain modules (gateway route missing)
**Description:** Custom object builder and runtime. Documented in MODULE_INVENTORY.md §23. No corresponding `v1-custom-objects.routes.js` found in gateway/routes/.
**Documentation gap:** MODULE_INVENTORY §23 notes "gateway route for custom objects not found" but BACKEND_GAP_REGISTER.md G-MED-004 classifies this as REQUIRES_OWNER_APPROVAL.
**Impact:** Medium — frontend custom object builder page exists (object-builder.html K-02) but has no live API surface.
**Status:** Already documented as G-MED-004. Owner decision required.

---

### UDC-004: backend/docs/ Sub-directories (domain/, security/, adapters/, etc.)
**Path:** `backend/docs/domain/`, `backend/docs/security/`, `backend/docs/adapters/`, `backend/docs/product/`, `backend/docs/architecture/`, `backend/docs/infrastructure/`, `backend/docs/ui/`, `backend/docs/_b9/`, `backend/docs/_qc/`, `backend/docs/adr/`
**Type:** Backend domain specification documents
**Description:** Extensive documentation tree within backend/docs/ covering domain models, security design, adapter patterns, product specs, architecture docs, and ADRs. Not surfaced in the main docs/ authority framework.
**Documentation gap:** docs/01_backend/ does not reference backend/docs/domain/ or backend/docs/architecture/ by specific file. The Backend Authority Capture documents (BACKEND_ARCHITECTURE.md etc.) are summaries; detailed domain specs live only in backend/docs/.
**Impact:** Low — backend/docs/ is a rich internal spec library. Future AI sessions reading docs/01_backend/ alone would miss detailed domain contracts in backend/docs/domain/.
**Recommended action:** Add a note in docs/01_backend/README.md pointing to backend/docs/ as the detailed domain specification library.

---

### UDC-005: backend/middleware/ Directory
**Path:** `backend/middleware/`
**Type:** Backend middleware (Python-side)
**Description:** A `middleware/` directory exists at `backend/middleware/`, separate from `backend/gateway/middleware/`. Contents not fully inventoried.
**Documentation gap:** SERVICE_CATALOG.md and BACKEND_ARCHITECTURE.md document `backend/gateway/middleware/` (Node.js layer) but may not reference `backend/middleware/` (Python layer, `execution_control.py` confirmed in MODULE_INVENTORY).
**Impact:** Low — MODULE_INVENTORY does list `middleware/execution_control.py` as an infrastructure module, but the full directory is not catalogued.

---

### UDC-006: backend/adapters/ Directory
**Path:** `backend/adapters/`
**Type:** External integration adapters (Pakistan-specific)
**Description:** Contains Pakistan-specific adapters: `adapters/pakistan/messaging/` (meta_api, gupshup, dialog360, twilio), `adapters/pakistan/payments/` (jazzcash, easypaisa). Also includes `adapters/interfaces/` (DDD protocol layer).
**Documentation gap:** INTEGRATION_CATALOG.md covers the 4 WhatsApp adapters and 2 payment adapters at a high level. The full adapter directory structure (adapters/interfaces/) is not documented in detail.
**Impact:** Low — sufficiently covered for frontend planning purposes.

---

## Summary

| ID | Item | Type | Impact | Action |
|----|------|------|--------|--------|
| UDC-001 | ci.yml | CI/CD pipeline | Medium | Add to AI_OPERATING_CONTEXT.md |
| UDC-002 | automation_journeys | Backend module | Low | Add MODULE_INVENTORY entry |
| UDC-003 | custom_objects gateway | Missing route | Medium | Owner decision (G-MED-004) |
| UDC-004 | backend/docs/ subtree | Spec library | Low | Add reference in docs/01_backend/README.md |
| UDC-005 | backend/middleware/ | Python middleware | Low | Informational |
| UDC-006 | backend/adapters/ | Integration adapters | Low | Informational |

---

*End UNDOCUMENTED_CODE_REGISTER.md*
