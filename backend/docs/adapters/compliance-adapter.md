<!-- OWNERSHIP
PRIMARY FOR: ComplianceAdapter interface method signatures (canonical ABC definition); ConsentType enum and consent record schema; PDPA/GDPR consent type mapping for Pakistan market; list of services required to call the adapter and trigger conditions; Pakistan-specific implementation notes (adapters/pakistan/compliance/).
DEFERS TO: data-governance-layer.md (GDPR/PDPA data retention and governance rules — primary there); whatsapp-execution-model.md §7.4 (opt-out/opt-in keyword triggers that call this adapter); pakistan-adapter-architecture.md (adapter pattern context and L2 interface architecture).
DO NOT RE-DEFINE: GDPR/PDPA data retention durations → data-governance-layer.md §2.3; adapter pattern architecture → pakistan-adapter-architecture.md; opt-out keyword list → whatsapp-execution-model.md §7.4.
-->

# ComplianceAdapter Interface Spec

## Purpose

This document defines the **ComplianceAdapter** interface — the third L2 Interface in the platform architecture (alongside `MessagingAdapter` and `PaymentAdapter`). It specifies the method signatures, expected behavior per Pakistan market (PDPA / GDPR), the Pakistan-specific implementation at `adapters/pakistan/compliance/`, and which services are required to call it and when.

**Architecture context:** `pakistan-adapter-architecture.md` covers `MessagingAdapter` and `PaymentAdapter` fully. `data-governance-layer.md` defines GDPR/PDPA compliance rules. This doc defines the *interface contract* that bridges the governance rules and the running services.

---

## 1) Interface Contract

### 1.1 Protocol Definition

```python
# backend/adapters/interfaces/compliance_adapter.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ConsentType(str, Enum):
    MARKETING = "marketing"
    SERVICE_COMMUNICATION = "service_communication"
    DATA_PROCESSING = "data_processing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"


class RetentionPolicy(str, Enum):
    STANDARD_7_YEAR = "standard_7_year"     # audit logs, financial records
    CONTACT_5_YEAR = "contact_5_year"       # customer contact data
    SESSION_90_DAY = "session_90_day"       # session and access logs
    MARKETING_2_YEAR = "marketing_2_year"  # marketing consent and campaign data
    IMMEDIATE = "immediate"                 # on-demand anonymization (right to erasure)


class AccessPurpose(str, Enum):
    CUSTOMER_SERVICE = "customer_service"
    SALES_OPERATION = "sales_operation"
    BILLING = "billing"
    COMPLIANCE_AUDIT = "compliance_audit"
    SYSTEM_OPERATION = "system_operation"
    DATA_EXPORT = "data_export"


@dataclass
class ConsentRecord:
    consent_id: str
    subject_id: str                   # Contact or Lead ID
    tenant_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: Optional[datetime]
    revoked_at: Optional[datetime]
    channel: str                      # "whatsapp" | "web" | "phone" | "import"
    ip_address: Optional[str]
    evidence_ref: Optional[str]       # URL or hash of consent evidence


@dataclass
class RetentionCheckResult:
    subject_id: str
    subject_type: str                 # "contact" | "lead" | "activity" | "message"
    policy: RetentionPolicy
    retained_since: datetime
    expires_at: Optional[datetime]
    is_expired: bool
    action_required: str              # "none" | "schedule_anonymization" | "immediate_delete"


@dataclass
class AccessAuditEntry:
    audit_id: str
    accessed_by: str                  # user_id
    subject_id: str
    subject_type: str
    access_purpose: AccessPurpose
    accessed_at: datetime
    fields_accessed: list[str]
    tenant_id: str


@dataclass
class AnonymizationResult:
    subject_id: str
    subject_type: str
    fields_anonymized: list[str]
    completed_at: datetime
    audit_ref: str                    # reference to the AuditLog entry


class ComplianceAdapter(ABC):

    @abstractmethod
    def verify_consent(
        self,
        subject_id: str,
        tenant_id: str,
        consent_type: ConsentType,
        channel: str
    ) -> bool:
        """
        Check whether a subject has active (non-revoked) consent for the given type.
        Returns True if consent is granted and not revoked.
        Returns False if consent is absent, revoked, or expired.
        Must NOT raise — callers block the operation on False return.
        """
        ...

    @abstractmethod
    def record_consent(
        self,
        subject_id: str,
        tenant_id: str,
        consent_type: ConsentType,
        granted: bool,
        channel: str,
        ip_address: Optional[str] = None,
        evidence_ref: Optional[str] = None
    ) -> ConsentRecord:
        """
        Record a consent grant or revocation event.
        Creates an immutable ConsentRecord — records are append-only; revocation
        creates a new record with granted=False rather than updating the existing one.
        """
        ...

    @abstractmethod
    def anonymize_entity(
        self,
        subject_id: str,
        subject_type: str,
        tenant_id: str,
        requestor_id: str,
        reason: str
    ) -> AnonymizationResult:
        """
        Anonymize all PII fields on the entity (Right to Erasure / Right to be Forgotten).
        Fields replaced with deterministic pseudonyms (sha256 hash) — NOT deleted —
        to preserve referential integrity and audit trail completeness.
        Returns a list of fields that were anonymized and a reference to the audit event.
        Must be idempotent — calling twice on the same entity returns the same result.
        """
        ...

    @abstractmethod
    def check_retention_policy(
        self,
        subject_id: str,
        subject_type: str,
        tenant_id: str,
        created_at: datetime
    ) -> RetentionCheckResult:
        """
        Evaluate whether a given entity is within its retention period.
        Returns action_required: "none" | "schedule_anonymization" | "immediate_delete".
        Callers use this to decide whether to surface an entity or trigger cleanup.
        """
        ...

    @abstractmethod
    def audit_access(
        self,
        accessed_by: str,
        subject_id: str,
        subject_type: str,
        tenant_id: str,
        access_purpose: AccessPurpose,
        fields_accessed: list[str]
    ) -> AccessAuditEntry:
        """
        Record that a user accessed a specific entity and which fields were read.
        Called on any read of PII data (contact phone, email, CNIC number, address).
        Returns the created audit entry. Must be non-blocking — failures are logged
        but must not break the primary read operation.
        """
        ...
```

---

## 2) Pakistan Implementation

### 2.1 Location

```
backend/adapters/pakistan/compliance/
├── __init__.py
├── compliance_adapter.py     — PakistanComplianceAdapter(ComplianceAdapter)
├── consent_store.py          — DB-backed consent record storage
├── anonymization.py          — PII field detection + pseudonymization logic
└── retention_rules.py        — Pakistan PDPA + GDPR retention rule table
```

### 2.2 PakistanComplianceAdapter

```python
class PakistanComplianceAdapter(ComplianceAdapter):
    """
    Pakistan-specific compliance implementation.

    Regulatory context:
    - PDPA 2023 (Pakistan Personal Data Protection Act): requires explicit consent
      for personal data processing; right of erasure; data localization preference.
    - GDPR: applied for international customer contacts or EU-resident leads.
    - Default posture: PDPA rules apply; stricter GDPR rules apply when
      Contact.country = EU member state.
    """
```

### 2.3 Consent Logic

**WhatsApp consent capture:**
- When a lead/contact sends a message to the business number, the system automatically records `consent_type = SERVICE_COMMUNICATION, granted = True, channel = whatsapp`.
- This satisfies PDPA §4(2)(b): "data processing necessary for performance of contract or provision of services the data subject requested."
- Marketing consent is NOT automatically granted — must be explicitly given via opt-in keyword (e.g. "SUBSCRIBE", "سبسکرائب").
- Opt-out keyword "STOP" / "بند کرو" immediately records `consent_type = MARKETING, granted = False`.

**Consent check points:**
- Before sending any WhatsApp template message: `verify_consent(contact_id, SERVICE_COMMUNICATION)` must return `True`.
- Before sending a marketing campaign message: `verify_consent(contact_id, MARKETING)` must return `True`.
- If `verify_consent` returns `False`: message is not sent; `consent_blocked` flag set on the outbound record.

### 2.4 PII Fields Subject to Anonymization

| Entity | PII fields |
|---|---|
| `Contact` | `full_name`, `phone_number`, `email`, `address`, `cnic_number`, `date_of_birth` |
| `Lead` | `name`, `phone_number`, `email`, `company_name` |
| `Message` | `body` (if it contains phone/email detected by regex), `from_number`, `to_number` |
| `ActivityEvent` | `actor_name`, `actor_email` (in `ActorContext`) |
| `InvoiceSummary` | `customer_name`, `customer_phone` |
| `SessionToken` | `ip_address`, `user_agent` |

**Anonymization method:** SHA-256 hash of `(tenant_id + field_value)`. This is deterministic (same input → same output) and irreversible. Original value is not stored after anonymization.

**Fields NOT anonymized:** `tenant_id`, `created_at`, `status`, foreign keys (UUIDs), financial amounts. These are required for audit trail completeness.

### 2.5 Retention Rules (Pakistan)

| Data type | Retention policy | Trigger for cleanup |
|---|---|---|
| Financial records (invoices, payments) | 7 years | Annual cleanup job |
| Audit logs (AuditLog entity) | 7 years | Annual cleanup job |
| Contact PII | 5 years after last activity | Triggered by retention scanner |
| Lead PII | 2 years after last activity | Triggered by retention scanner |
| Marketing consent records | 2 years | Triggered by retention scanner |
| Session tokens | 90 days | Hourly cleanup job |
| WhatsApp messages (body) | 2 years | Triggered by retention scanner |
| Activity event metadata | 5 years | Annual cleanup job |

**Right to Erasure (RTbF):** When a customer explicitly requests data deletion via WhatsApp keyword "ERASE MY DATA" / "میرا ڈیٹا مٹا دو" or via the web form, `anonymize_entity()` is called immediately for all PII entities linked to that contact, regardless of retention schedule.

---

## 3) Call Sites — Which Services Must Call the Adapter

### 3.1 Mandatory Call Sites

| Service | Operation | Adapter method called |
|---|---|---|
| WhatsApp Engine | Before sending any outbound template | `verify_consent(SERVICE_COMMUNICATION)` |
| WhatsApp Engine | On inbound message from new contact | `record_consent(SERVICE_COMMUNICATION, granted=True, channel="whatsapp")` |
| WhatsApp Engine | On "STOP" keyword received | `record_consent(MARKETING, granted=False)` |
| Campaign Service | Before sending any campaign message | `verify_consent(MARKETING)` |
| Contact API | On `GET /api/v1/contacts/{id}` returning PII fields | `audit_access(purpose=CUSTOMER_SERVICE)` |
| Lead API | On `GET /api/v1/leads/{id}` returning contact info | `audit_access(purpose=SALES_OPERATION)` |
| Data Export API | On bulk export of contact/lead data | `audit_access(purpose=DATA_EXPORT, fields_accessed=["all"])` |
| Compliance Settings | On RTbF request submission | `anonymize_entity()` |
| Retention Scanner | On finding entity past retention window | `check_retention_policy()` + `anonymize_entity()` |

### 3.2 Non-Call Sites (Explicit Exclusions)

The following operations do NOT call the ComplianceAdapter (they are internal system operations not involving PII display):

- Internal service-to-service reads (audit log reads, pipeline status checks, task scheduling).
- Dashboard aggregate/count queries (no individual PII fields returned).
- `GET /api/v1/activities/chain-integrity` (returns hashes only).
- All `GET` endpoints that return anonymized or aggregate data.

---

## 4) Adapter Registration

The ComplianceAdapter is registered in the `app.py` lifespan alongside the Messaging and Payment adapters:

```python
# backend/services/app.py (lifespan section)
from adapters.pakistan.compliance.compliance_adapter import PakistanComplianceAdapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.compliance_adapter = PakistanComplianceAdapter(db=get_db_session())
    # ... other adapter registrations
    yield
    # cleanup
```

All services access the adapter via `request.app.state.compliance_adapter`.

---

## 5) PENDING.md Reference

- **L-03:** Wire `ComplianceAdapter` into service lifecycle — this file defines what to wire. See PENDING.md Phase 4 Sprint 5 for the code task.

---

## 6) Implementation Acceptance Checklist

- [ ] `backend/adapters/interfaces/compliance_adapter.py` created with `ComplianceAdapter(ABC)` protocol.
- [ ] `backend/adapters/pakistan/compliance/compliance_adapter.py` created with `PakistanComplianceAdapter`.
- [ ] `verify_consent()` returns False (not raises) for absent/revoked consent.
- [ ] `record_consent()` is append-only (no update — new record on revocation).
- [ ] `anonymize_entity()` is idempotent; uses SHA-256 pseudonymization; does not delete FK columns.
- [ ] `check_retention_policy()` returns correct `action_required` based on `retention_rules.py` table.
- [ ] `audit_access()` is non-blocking — failure logs but does not break the primary read.
- [ ] WhatsApp Engine calls `verify_consent` before every outbound template send.
- [ ] WhatsApp Engine calls `record_consent(SERVICE_COMMUNICATION)` on every new inbound message.
- [ ] "STOP" keyword handling calls `record_consent(MARKETING, granted=False)`.
- [ ] Adapter registered in `app.py` lifespan under `app.state.compliance_adapter`.
- [ ] Contact and Lead API endpoints call `audit_access` on PII field reads.
