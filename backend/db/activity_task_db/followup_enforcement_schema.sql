-- Follow-up enforcement schema (strict no-forgotten-lead controls)

CREATE TABLE IF NOT EXISTS followup_tasks (
    task_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    lead_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'overdue', 'completed')),
    due_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    completed_activity_id TEXT NULL,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('TimeBased', 'ActivityBased', 'InactivityBased')),
    escalation_level TEXT NOT NULL DEFAULT 'none'
        CHECK (escalation_level IN ('none', 'reminder', 'warning', 'escalated', 'reassigned')),
    generated_by TEXT NOT NULL CHECK (generated_by IN ('Scheduler', 'EscalationEngine', 'SystemRepair')),
    is_canonical BOOLEAN NOT NULL DEFAULT TRUE,
    manager_cancel_reason TEXT NULL,
    canceled_by_manager_id TEXT NULL,
    canceled_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_followup_tasks_lead_state_due
    ON followup_tasks (lead_id, state, due_at);

CREATE UNIQUE INDEX IF NOT EXISTS ux_followup_tasks_one_canonical_pending
    ON followup_tasks (lead_id)
    WHERE state = 'pending' AND is_canonical = TRUE;

CREATE TABLE IF NOT EXISTS followup_escalations (
    escalation_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    lead_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    escalation_level TEXT NOT NULL
        CHECK (escalation_level IN ('reminder', 'warning', 'escalated', 'reassigned')),
    owner_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS followup_violations (
    violation_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    lead_id TEXT NOT NULL,
    code TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS followup_enforcement_audit (
    audit_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    lead_id TEXT NOT NULL,
    task_id TEXT NULL,
    actor_type TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    happened_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
