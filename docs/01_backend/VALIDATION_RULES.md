Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Shared

# VALIDATION_RULES.md
> Source: backend/gateway/routes/v1-*.routes.js, backend/services/*/entities.py, backend/src/*/entities.py, backend/gateway/middleware/request-validation.js

---

## 1. Validation Architecture

Validation occurs at two layers:

| Layer | Mechanism | Where |
|---|---|---|
| Gateway (Node.js) | Manual field checks in route handlers; `requestValidationMiddleware` | backend/gateway/routes/v1-*.routes.js, middleware/request-validation.js |
| FastAPI service (Python) | Pydantic v2 schemas with field validators | backend/services/*/entities.py, backend/src/*/entities.py |

**Gateway validation pattern:** Inline in route handlers:
```javascript
if (!email || typeof email !== 'string') {
  return respondError(res, 'validation_error', 'email is required.', [{ field: 'email', reason: 'required' }], 422);
}
```

**FastAPI validation pattern:** Pydantic `BaseModel` schemas with `@field_validator` decorators. FastAPI auto-returns 422 on schema validation failures.

---

## 2. Common Field Validators

### Required field pattern (gateway)
All route handlers manually check required fields before processing:
```javascript
// Pattern from v1-leads.routes.js
if (!owner_id) {
  return respondError(res, 'validation_error', 'owner_id is required.', [{ field: 'owner_id', reason: 'required' }], 422);
}
```

### Email validation
- **Gateway:** Type check only (`typeof email === 'string'` and `email` truthy)
- **FastAPI (Pydantic):** Plain `str` type — CONFIRMED 2026-06-23: `grep -r "EmailStr" backend/src/` returns no matches. `pydantic-email-validator` is NOT used. Email uses plain `str` type (e.g. `customer_360_cdp/entities.py` line 16: `email: str`). Email format is NOT validated at the FastAPI layer.
- **Format:** Standard email format (local@domain.tld) — enforced by convention, not validator

### Phone number (E.164) validation
- **Format enforced:** E.164 — `+923xxxxxxxxx` format for Pakistan numbers
- **DB constraint:** `phone_e164 TEXT NOT NULL` with UNIQUE(tenant_id, phone_e164) in contacts table
- **Deduplication:** Phone-based dedup on `POST /contacts/import` and `POST /leads/import`
- **Pattern:** CONFIRMED ABSENT — No phone regex validator found in `backend/src/` or `backend/gateway/` (Phase 3.25 grep). Phone validation is string equality for dedup only. E.164 format is an enforced convention, not a programmatic regex check.

### PKR amount validation
- **DB constraint:** `amount NUMERIC(18,2)` with `CHECK (amount > 0)` or `CHECK (amount >= 0)` depending on entity
- **Gateway:** Numeric type check; specific amount constraints per endpoint
- **Examples:**
  - Payment amount: `CHECK (amount > 0)` (strict positive)
  - Invoice amount_due: `CHECK (amount_due >= 0)` (zero allowed)
  - Quote total: `NUMERIC(18,2)` (no explicit min check found)

### Currency validation
- **DB constraint:** `currency CHAR(3) CHECK (currency ~ '^[A-Z]{3}$')` — ISO 4217 format
- **Default:** `'PKR'` on all monetary fields where currency is stored
- **Gateway:** Most endpoints default currency to 'PKR' if not specified

### Date/time validation
- **Format:** ISO 8601 (dates as `DATE`, timestamps as `TIMESTAMPTZ`)
- **Pydantic:** `datetime` type from Python stdlib — accepts ISO 8601 strings
- **Gateway:** String format (ISO 8601 expected); no explicit format validation found in gateway handlers

### UUID validation
- **Format:** Standard UUID v4
- **Gateway:** Not validated — passed as strings to DB queries
- **FastAPI:** CONFIRMED `uuid.UUID` type in Pydantic BaseModel schemas (e.g. `Optional[uuid.UUID]` for contact_id in CreateCaseRequest). Generated with `from uuid import uuid4`. Services use `uuid4()` for new entity ID generation.

---

## 3. Pakistan-Specific Validation

### Phone number (Pakistan)
- **Expected format:** E.164 with Pakistan country code: `+92` followed by 10 digits
- **Example valid:** `+923001234567` (mobile), `+924231234567` (Lahore landline)
- **DB field name:** `phone_e164` (consistent across all contact/lead tables)
- **Normalization:** Applied by conversation service on WhatsApp inbound (`normalized_phone` field in messaging_db)
- **Regex pattern:** CONFIRMED ABSENT — No phone regex validator found anywhere in codebase (Phase 3.25). Same as main phone validation: E.164 is a convention, not enforced by regex.

### CNIC (Computerised National Identity Card)
- **Format:** `XXXXX-XXXXXXX-X` (13 digits with dashes)
- **Status:** CONFIRMED NOT A DB FIELD (Phase 3.25). grep across all 18 `backend/db/` schema files returns no matches. CNIC appears only as optional payment metadata in `backend/adapters/pakistan/payments/jazzcash.py` (`pp_CNIC` field, optional, from `metadata.get("cnic", "")`). Not stored in any entity table.

### NTN (National Tax Number)
- **Status:** CONFIRMED NOT A DB FIELD (Phase 3.25). No `ntn` field in any DB schema. Not implemented.

### STRN (Sales Tax Registration Number)
- **Status:** CONFIRMED NOT A DB FIELD (Phase 3.25). No `strn` field in any DB schema. Not implemented.

---

## 4. Business Rule Validation

### Lead validation
- `owner_id` — required (no orphan leads). 422 if missing.
- `stage` — must be in: new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified
- `status` — must be in: open/working/idle/closed
- `priority` — must be in: hot/warm/cold
- `source` — must be in: whatsapp/web/import/manual/referral/campaign

### Case validation
- `version_no` — must match current version for PATCH (optimistic concurrency). 409 if stale.
- Reopen window — cases can only be reopened within 14 calendar days of closing. 422 REOPEN_WINDOW_EXPIRED otherwise.
- ASSIGNED → IN_PROGRESS — auto-transition on first `customer_reply` comment type

### Case SLA validation
- `sla_tier` — must be in: tier_1_critical/tier_2_high/tier_3_standard/tier_4_low
- SLA deadlines computed from defaults:
  - tier_1_critical: 1h first response / 8h resolution
  - tier_2_high: 4h / 24h
  - tier_3_standard: 8h / 72h
  - tier_4_low: 24h / 168h

### Quote/CPQ validation
- `discount_pct > 10%` — auto-triggers approval workflow (requires_approval=true)
- Order is immutable post-fulfillment

### Opportunity validation
- `version_no` — optimistic concurrency on PATCH
- Stage transitions emit events: `opportunity.stage.changed.v1`, `opportunity.closed.v1` (terminal)

### Inbox validation
- Agent capacity cap: inbox claim fails if `open_conversation_count >= max_concurrent` (default 10). 409.
- Handoff permissions: non-supervisor agents can only handoff their own conversations

### Follow-up validation
- Exactly one canonical pending task per lead (DB unique constraint enforced)
- Snooze: 409 if task already completed
- `due_at`: required ISO 8601

### Payment validation
- `proof_url`: must be valid https URL on proof upload
- `verification_status`: must be `verified` or `rejected` on proof verification
- `rejected`: requires `rejection_reason`

### Workflow validation
- Publish: requires ≥1 step in workflow definition
- PATCH: 403 on is_system workflows; 409 on archived workflows
- Retry: `max_retries` enforced

### Territory validation
- `criteria_type`: must be in geographic/postal/account_segment/rep_assigned/hybrid
- Default territory: 409 if attempting to soft-delete the default territory

### Campaign validation
- PATCH: 409 if campaign status is `completed` or `cancelled`
- Activate: requires `segment_id` and `template_id`
- Urdu WhatsApp templates: require `urdu_approved_by` (P-017 blocker)

### Idempotency validation
- All write requests must include `Idempotency-Key` header. 422 if missing.
- Key reuse with different body: 409

---

## 5. Pydantic Schema Patterns

**Found in `backend/services/*/entities.py` and `backend/src/*/entities.py`:**

```python
# Pattern: frozen dataclass entities
@dataclass(frozen=True)
class FollowupTask:
    task_id: str
    lead_id: str
    tenant_id: str
    owner_id: str
    state: FollowupState   # Enum validation
    due_at: datetime
    ...

# Pattern: Pydantic BaseModel for request/response schemas
class CreateCaseRequest(BaseModel):
    subject: str
    priority: CasePriority  # Enum with allowed values
    source: str
    contact_id: Optional[uuid.UUID] = None
    
    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in VALID_SOURCES:
            raise ValueError(f"source must be one of {VALID_SOURCES}")
        return v
```

**Enum-based validation pattern (FastAPI services):**
- `CasePriority` (Enum): critical/high/medium/low
- `SLATier` (Enum): tier_1_critical/tier_2_high/tier_3_standard/tier_4_low
- `PresenceStatus` (Enum): online/away/busy/offline
- `HandoffReason` (Enum): agent_unavailable/capacity_exceeded/skill_match/manual/escalation
- `ScoreBand` (Enum): hot/warm/cold/disqualified
- `ChurnRiskBand` (Enum): high/medium/low
- `SuggestionType`, `SuggestionPriority`, `QueryIntent` (Enums — see ai/entities.py)
- `FollowupState` (Enum): pending/overdue/completed
- `EscalationLevel` (Enum): none/reminder/warning/escalated/reassigned

---

## 6. Validation Error Response Format

See ERROR_CONTRACT.md §4 for full format. Example:
```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "details": [
      { "field": "owner_id", "reason": "required" },
      { "field": "stage", "reason": "invalid_value" }
    ]
  },
  "meta": { "request_id": "uuid" }
}
```

---

## 7. Where Validation Does NOT Occur

- **Cross-schema FK consistency:** The DB does not enforce foreign keys across schemas (e.g. contact_id on leads is not FK-constrained to contacts table). Application layer must validate these.
- **Field format in DB CHECK constraints:** Most format validation is application-level. DB has CHECK constraints for enums (status/stage/priority values) but not for formats like email or phone.
- **Frontend validation:** Frontend uses DUMMY_MODE for most pages; backend-frontend validation parity is largely undefined for the 70 pages not yet wired. See VALIDATION_PARITY.md.

---

*End VALIDATION_RULES.md*
