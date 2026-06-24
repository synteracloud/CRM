Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Shared

# DATA_SHAPE_REGISTRY.md
> Source: backend/db/*/schema.sql (all 18 schemas), backend/services/*/entities.py, backend/src/*/entities.py, backend/gateway/routes/v1-*.routes.js (response shapes)

---

## 1. Standard Response Envelope

All API responses (gateway) use the standard envelope format:

### Success response
```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "page": 1,
    "per_page": 25,
    "total": 1234
  }
}
```

### Error response
```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable message",
    "details": [{ "field": "fieldname", "reason": "reason" }]
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

---

## 2. Core Entity Shapes

### Lead (lead_management_db.leads)
```typescript
{
  id: UUID;                          // gen_random_uuid()
  tenant_id: UUID;
  owner_id: UUID;                    // required — no orphan leads
  contact_id: UUID | null;           // optional link to contacts schema
  stage: 'new' | 'qualifying' | 'nurturing' | 'proposal' | 'negotiation' | 'won' | 'lost' | 'disqualified';
  status: 'open' | 'working' | 'idle' | 'closed';
  priority: 'hot' | 'warm' | 'cold';
  source: 'whatsapp' | 'web' | 'import' | 'manual' | 'referral' | 'campaign';
  first_name: string;
  last_name: string;
  phone_e164: string;               // E.164 format e.g. +923001234567
  email: string | null;
  company_name: string | null;
  estimated_value: Numeric(18,2);
  currency: 'PKR' | string;         // CHAR(3) ISO 4217
  territory_id: UUID | null;
  campaign_id: UUID | null;
  version_no: integer;              // optimistic concurrency
  last_contacted_at: TIMESTAMPTZ | null;
  score: integer | null;            // 0–100 from AI scoring
  custom_fields: JSONB;
  is_deleted: boolean;              // soft delete
  deleted_at: TIMESTAMPTZ | null;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Contact (contact_account_db.contacts)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  first_name: string;
  last_name: string;
  phone_e164: string;              // UNIQUE(tenant_id, phone_e164)
  email: string | null;
  account_id: UUID | null;
  title: string | null;
  department: string | null;
  source: 'whatsapp' | 'import' | 'manual' | 'web' | string;
  territory_id: UUID | null;
  version_no: integer;
  last_contacted_at: TIMESTAMPTZ | null;
  custom_fields: JSONB;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Account (contact_account_db.accounts)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  name: string;
  industry: string | null;
  size_band: 'micro' | 'small' | 'medium' | 'enterprise' | null;
  annual_revenue: Numeric(18,2) | null;
  currency: string;                // CHAR(3)
  parent_account_id: UUID | null;  // self-referential hierarchy
  owner_id: UUID | null;
  territory_id: UUID | null;
  website: string | null;
  city: string | null;
  region: string | null;           // Province (Punjab, Sindh, KPK, Balochistan...)
  country: string;                 // default 'PK'
  version_no: integer;
  custom_fields: JSONB;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Opportunity (opportunity_db.opportunities)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  name: string;
  account_id: UUID;
  owner_id: UUID;
  stage: 'prospecting' | 'discovery' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: integer;            // 0–100
  amount: Numeric(18,2);
  currency: string;
  close_date: DATE;
  territory_id: UUID | null;
  campaign_id: UUID | null;
  is_recurring: boolean;
  version_no: integer;
  closed_at: TIMESTAMPTZ | null;
  custom_fields: JSONB;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Quote (quote_order_db.quotes)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  quote_number: string;            // QUO-NNNNN format
  opportunity_id: UUID;
  owner_id: UUID;
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired';
  valid_until: DATE;
  currency: string;
  subtotal: Numeric(18,2);         // GENERATED from line items
  discount_pct: Numeric(5,2);
  tax_pct: Numeric(5,2);
  total_amount: Numeric(18,2);    // GENERATED: subtotal * (1 - discount) * (1 + tax)
  requires_approval: boolean;
  approved_by: UUID | null;
  approved_at: TIMESTAMPTZ | null;
  version_no: integer;
  notes: text | null;
  custom_fields: JSONB;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Case (case_ticket_db.cases)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  case_number: string;             // CAS-NNNNN format
  contact_id: UUID | null;
  account_id: UUID | null;
  subject: string;
  description: text | null;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'critical' | 'high' | 'medium' | 'low';
  sla_tier: 'tier_1_critical' | 'tier_2_high' | 'tier_3_standard' | 'tier_4_low';
  sla_state: 'healthy' | 'at_risk' | 'breached';
  first_response_due_at: TIMESTAMPTZ | null;
  resolution_due_at: TIMESTAMPTZ | null;
  first_responded_at: TIMESTAMPTZ | null;
  resolved_at: TIMESTAMPTZ | null;
  owner_id: UUID | null;
  source: 'whatsapp' | 'email' | 'phone' | 'web' | 'manual';
  type: 'complaint' | 'billing' | 'technical' | 'general' | 'collections';
  version_no: integer;
  closed_at: TIMESTAMPTZ | null;
  custom_fields: JSONB;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

### Conversation/Message (messaging_db)
```typescript
// Note: messaging_db uses TEXT PKs (provider IDs), NOT UUID
{
  // conversations table
  id: string;                      // TEXT PK (not UUID)
  tenant_id: UUID;
  channel: 'whatsapp' | 'email' | 'sms';
  contact_phone: string;           // E.164
  status: 'active' | 'resolved' | 'closed';
  provider: 'meta' | 'twilio' | '360dialog' | 'gupshup';
  assigned_to: UUID | null;
  context: string;                 // conversation context bucket
  last_message_at: TIMESTAMPTZ | null;
  unread_count: integer;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}

{
  // messages table
  id: string;                      // TEXT PK
  tenant_id: UUID;
  conversation_id: string;         // FK to conversations.id (TEXT)
  provider_message_id: string;     // UNIQUE(tenant_id, provider, provider_message_id)
  direction: 'inbound' | 'outbound';
  content_type: 'text' | 'image' | 'document' | 'audio' | 'template';
  body: text;
  media_url: string | null;
  template_name: string | null;
  status: 'sent' | 'delivered' | 'read' | 'failed';
  sent_at: TIMESTAMPTZ | null;
  delivered_at: TIMESTAMPTZ | null;
  read_at: TIMESTAMPTZ | null;
  created_at: TIMESTAMPTZ;
}
```

### Activity (activity_task_db.activity)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  entity_type: 'lead' | 'contact' | 'account' | 'opportunity' | 'case' | 'message_thread';
  entity_id: UUID;
  actor_id: UUID;
  activity_type: string;           // e.g. 'call', 'email', 'note', 'status_change'
  summary: text;
  occurred_at: TIMESTAMPTZ;
  metadata: JSONB;
  // IMMUTABLE — no updated_at column
  created_at: TIMESTAMPTZ;
}
```

### Invoice (transaction_db.invoice_summary)
```typescript
{
  id: UUID;
  tenant_id: UUID;
  subscription_id: UUID | null;
  invoice_number: string;
  billing_period_start: DATE;
  billing_period_end: DATE;
  amount_due: Numeric(18,2);       // CHECK (amount_due >= 0)
  amount_paid: Numeric(18,2);
  currency: string;
  status: 'draft' | 'issued' | 'paid' | 'partially_paid' | 'overdue' | 'cancelled' | 'uncollectible';
  issued_at: TIMESTAMPTZ | null;
  due_at: TIMESTAMPTZ | null;
  paid_at: TIMESTAMPTZ | null;
  payment_method: 'jazzcash' | 'easypaisa' | 'bank_transfer' | null;
  created_at: TIMESTAMPTZ;
  updated_at: TIMESTAMPTZ;
}
```

---

## 3. JWT Payload Shape

See AUTH_AND_TENANCY_CONTRACT.md §1 for the full JWT claim set.

---

## 4. Pagination Shape

```json
{
  "data": [ ...items... ],
  "meta": {
    "request_id": "uuid",
    "page": 1,
    "per_page": 25,
    "total": 847,
    "total_pages": 34
  }
}
```

Default page size: 25. Controlled by `?page=N&per_page=N` query parameters.

---

## 5. Follow-up Task Shape (Python dataclass)

```python
@dataclass(frozen=True)
class FollowupTask:
    task_id: str
    lead_id: str
    tenant_id: str
    owner_id: str
    state: FollowupState          # pending | overdue | completed
    due_at: datetime
    snoozed_until: Optional[datetime]
    completed_at: Optional[datetime]
    priority: int                 # 1 (highest) to 5 (lowest)
    context_tags: List[str]
```

---

## 6. AI Score Shape

```json
{
  "entity_id": "lead-uuid",
  "tenant_id": "tenant-uuid",
  "score": 78,
  "band": "warm",
  "model_id": "lead_score_v1",
  "feature_weights": {
    "deal_stage": 0.28,
    "follow_up_count": 0.18,
    "estimated_value": 0.14,
    "days_since_last_contact": 0.12,
    "email_open_rate": 0.08,
    "activity_recency": 0.08,
    "whatsapp_engagement": 0.12
  },
  "scored_at": "2026-06-22T08:00:00Z"
}
```

---

## 7. Next Action Suggestion Shape

```python
@dataclass(frozen=True)
class NextActionSuggestion:
    suggested_action: str     # 'call' | 'send_whatsapp' | 'send_reminder' | 'escalate' | 'close'
    reason: str
    priority: int
    due_by: Optional[datetime]
```

---

## 8. Churn Risk Shape

```json
{
  "account_id": "account-uuid",
  "churn_probability": 0.72,
  "risk_band": "high",          // "high" >= 0.65, "medium" 0.35-0.64, "low" < 0.35
  "model_id": "churn_predict_v1",
  "computed_at": "2026-06-22T08:00:00Z"
}
```

---

## 9. Webhook Payload Shapes (Inbound)

### Meta WhatsApp inbound
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "phone-number-id",
    "changes": [{
      "value": {
        "messages": [{
          "id": "provider-message-id",
          "from": "+923001234567",
          "type": "text",
          "text": { "body": "message content" },
          "timestamp": "1700000000"
        }],
        "statuses": [...]
      }
    }]
  }]
}
```

### JazzCash payment callback
```json
{
  "pp_TxnRefNo": "provider-txn-id",
  "pp_Amount": "100000",
  "pp_ResponseCode": "000",
  "pp_SecureHash": "hmac-sha256-hash"
}
```

---

*End DATA_SHAPE_REGISTRY.md*
