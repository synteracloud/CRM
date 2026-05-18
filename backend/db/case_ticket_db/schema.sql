-- CASE_TICKET_DB
-- Support tickets, SLA policies, escalation rules and audit.
-- Source: src/ticket_management/entities.py
--         src/support_console/entities.py
--         docs/domain-model.md (Ticket entity)
--
-- Status FSM: open → in_progress → resolved → closed
-- SLA states: healthy | at_risk | breached
-- Escalation actions: reassign | raise_priority | page_on_call | request_manager_review

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS case_ticket_db;
SET search_path TO case_ticket_db, public;

CREATE OR REPLACE FUNCTION case_ticket_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── SLA Policies ───────────────────────────────────────────────────────────────
-- Defines response and resolution time targets per priority tier.
CREATE TABLE IF NOT EXISTS sla_policies (
  policy_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  name                 TEXT NOT NULL,
  priority             TEXT NOT NULL,
  response_minutes     INTEGER NOT NULL CHECK (response_minutes > 0),
  resolution_minutes   INTEGER NOT NULL CHECK (resolution_minutes > 0),
  business_hours_only  BOOLEAN NOT NULL DEFAULT FALSE,
  active               BOOLEAN NOT NULL DEFAULT TRUE,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT sla_priority_chk CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  UNIQUE (tenant_id, priority, active)
);
CREATE TRIGGER trg_sla_policies_updated_at BEFORE UPDATE ON sla_policies
  FOR EACH ROW EXECUTE FUNCTION case_ticket_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_sla_policies_tenant ON sla_policies(tenant_id, active);

-- ── Cases (Tickets) ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cases (
  ticket_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  account_id           UUID,                       -- FK enforced by app (cross-schema)
  contact_id           UUID,                       -- FK enforced by app (cross-schema)
  owner_user_id        UUID NOT NULL,
  subject              TEXT NOT NULL,
  description          TEXT,
  priority             TEXT NOT NULL DEFAULT 'medium',
  status               TEXT NOT NULL DEFAULT 'open',
  sla_policy_id        UUID REFERENCES sla_policies(policy_id) ON DELETE SET NULL,
  queue_name           TEXT NOT NULL DEFAULT 'default',
  sla_state            TEXT NOT NULL DEFAULT 'healthy',
  response_due_at      TIMESTAMPTZ,
  resolution_due_at    TIMESTAMPTZ,
  first_responded_at   TIMESTAMPTZ,
  resolved_at          TIMESTAMPTZ,
  closed_at            TIMESTAMPTZ,
  version_no           INTEGER NOT NULL DEFAULT 1,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT case_priority_chk CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  CONSTRAINT case_status_chk   CHECK (status   IN ('open', 'in_progress', 'resolved', 'closed')),
  CONSTRAINT case_sla_state_chk CHECK (sla_state IN ('healthy', 'at_risk', 'breached'))
);
CREATE TRIGGER trg_cases_updated_at BEFORE UPDATE ON cases
  FOR EACH ROW EXECUTE FUNCTION case_ticket_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_cases_tenant_owner    ON cases(tenant_id, owner_user_id);
CREATE INDEX IF NOT EXISTS idx_cases_tenant_status   ON cases(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_cases_tenant_priority ON cases(tenant_id, priority);
CREATE INDEX IF NOT EXISTS idx_cases_tenant_sla      ON cases(tenant_id, sla_state, resolution_due_at);
CREATE INDEX IF NOT EXISTS idx_cases_contact         ON cases(tenant_id, contact_id);
CREATE INDEX IF NOT EXISTS idx_cases_account         ON cases(tenant_id, account_id);

-- ── Case Assignments ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_assignments (
  assignment_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id      UUID NOT NULL REFERENCES cases(ticket_id) ON DELETE CASCADE,
  tenant_id      UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  owner_user_id  UUID NOT NULL,
  assigned_by    UUID,                           -- NULL = system/rule assignment
  reason         TEXT,
  assigned_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_case_assignments_ticket ON case_assignments(ticket_id, assigned_at DESC);
CREATE INDEX IF NOT EXISTS idx_case_assignments_owner  ON case_assignments(tenant_id, owner_user_id);

-- ── Case History (immutable field-change audit trail) ──────────────────────────
CREATE TABLE IF NOT EXISTS case_history (
  history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id    UUID NOT NULL REFERENCES cases(ticket_id) ON DELETE CASCADE,
  tenant_id    UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  changed_by   UUID,
  field_name   TEXT NOT NULL,
  old_value    TEXT,
  new_value    TEXT,
  changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_case_history_ticket ON case_history(ticket_id, changed_at DESC);

-- ── SLA Events ────────────────────────────────────────────────────────────────
-- Records SLA state transitions and breach events.
CREATE TABLE IF NOT EXISTS sla_events (
  event_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id     UUID NOT NULL REFERENCES cases(ticket_id) ON DELETE CASCADE,
  tenant_id     UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  event_type    TEXT NOT NULL,   -- response_due | resolution_due | state_change | breached
  old_sla_state TEXT,
  new_sla_state TEXT,
  occurred_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sla_events_ticket ON sla_events(ticket_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_sla_events_tenant_breach ON sla_events(tenant_id, event_type, occurred_at DESC);

-- ── Escalation Rules ───────────────────────────────────────────────────────────
-- Configurable rules that trigger escalation actions.
-- Source: src/ticket_management/entities.py EscalationRule
CREATE TABLE IF NOT EXISTS escalation_rules (
  rule_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  level              INTEGER NOT NULL DEFAULT 1,
  name               TEXT NOT NULL,
  route_to           TEXT NOT NULL,     -- user_id | team_id | role name
  trigger            TEXT NOT NULL,     -- sla_breach | idle_too_long | manual
  threshold_minutes  INTEGER NOT NULL DEFAULT 60 CHECK (threshold_minutes > 0),
  condition_field    TEXT,              -- optional: e.g. "priority"
  condition_op       TEXT,              -- eq | ne | gt | lt | in
  condition_value    TEXT,              -- value to compare against
  action             TEXT NOT NULL DEFAULT 'reassign',
  active             BOOLEAN NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT escalation_action_chk CHECK (
    action IN ('reassign', 'raise_priority', 'page_on_call', 'request_manager_review')
  )
);
CREATE TRIGGER trg_escalation_rules_updated_at BEFORE UPDATE ON escalation_rules
  FOR EACH ROW EXECUTE FUNCTION case_ticket_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_escalation_rules_tenant ON escalation_rules(tenant_id, active, level);

-- ── Escalation Actions (per-ticket escalation records) ─────────────────────────
-- Source: src/ticket_management/entities.py EscalationAction
CREATE TABLE IF NOT EXISTS escalation_actions (
  action_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id        UUID NOT NULL REFERENCES cases(ticket_id) ON DELETE CASCADE,
  tenant_id        UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  rule_id          UUID REFERENCES escalation_rules(rule_id) ON DELETE SET NULL,
  level            INTEGER NOT NULL,
  route_to         TEXT NOT NULL,
  escalation_state TEXT NOT NULL DEFAULT 'open',
  reason           TEXT,
  escalated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at      TIMESTAMPTZ,
  CONSTRAINT escalation_state_chk CHECK (escalation_state IN ('open', 'acknowledged', 'resolved'))
);
CREATE INDEX IF NOT EXISTS idx_escalation_actions_ticket ON escalation_actions(ticket_id, escalated_at DESC);
CREATE INDEX IF NOT EXISTS idx_escalation_actions_tenant ON escalation_actions(tenant_id, escalation_state);

-- ── Escalation Audit ───────────────────────────────────────────────────────────
-- Source: src/ticket_management/entities.py EscalationAuditRecord
CREATE TABLE IF NOT EXISTS escalation_audit (
  audit_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id   UUID NOT NULL REFERENCES cases(ticket_id) ON DELETE CASCADE,
  tenant_id   UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  event_type  TEXT NOT NULL,
  details     JSONB NOT NULL DEFAULT '{}',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_escalation_audit_ticket ON escalation_audit(ticket_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_escalation_audit_tenant ON escalation_audit(tenant_id, event_type, created_at DESC);
