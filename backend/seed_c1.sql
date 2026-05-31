-- C1 Seed Data for smoke testing
-- Dev tenant UUID: 00000000-0000-0000-0000-000000000001
-- Dev user UUID:   00000000-0000-0000-0000-000000000002

DO $$
BEGIN

-- ─── org_tenant_db.tenants ────────────────────────────────────────────────────
INSERT INTO org_tenant_db.tenants (tenant_id, name, slug, status, plan, region, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Dev Tenant',
  'dev-tenant',
  'active',
  'enterprise',
  'pk-south',
  NOW(), NOW()
) ON CONFLICT (tenant_id) DO NOTHING;

-- ─── identity_auth_db.users ──────────────────────────────────────────────────
INSERT INTO identity_auth_db.users (user_id, tenant_id, email, full_name, status, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000001',
  'dev@crm.pk',
  'Dev Admin',
  'active',
  NOW(), NOW()
) ON CONFLICT (user_id) DO NOTHING;

-- ─── identity_auth_db.roles ──────────────────────────────────────────────────
INSERT INTO identity_auth_db.roles (role_id, tenant_id, name, description, is_system, created_at)
VALUES (
  '00000000-0000-0000-0000-000000000010',
  '00000000-0000-0000-0000-000000000001',
  'Tenant Admin',
  'Full tenant admin role',
  false,
  NOW()
) ON CONFLICT (role_id) DO NOTHING;

-- ─── contact_account_db.accounts ─────────────────────────────────────────────
INSERT INTO contact_account_db.accounts (account_id, tenant_id, name, industry, size_band, owner_id, version_no, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000001', 'City Pharma Ltd',      'pharma',  'mid',   '00000000-0000-0000-0000-000000000002', 1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000001', 'NexTech Solutions',    'tech',    'small', '00000000-0000-0000-0000-000000000002', 1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000001', 'Pak Steel HR Module',  'steel',   'large', '00000000-0000-0000-0000-000000000002', 1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000001', 'Al-Khidmat Foundation','ngo',     'small', '00000000-0000-0000-0000-000000000002', 1, NOW(), NOW())
ON CONFLICT (account_id) DO NOTHING;

-- ─── contact_account_db.contacts ─────────────────────────────────────────────
INSERT INTO contact_account_db.contacts (contact_id, tenant_id, first_name, last_name, email, phone_e164, account_id, owner_id, status, lifecycle, tags, version_no, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000001', 'Tariq',  'Mehmood', 'tariq@citypharma.pk', '+923001234567', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000002', 'active', 'customer', '["VIP","Hot"]',  1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000001', 'Sana',   'Sheikh',  'sana@nextech.pk',     '+923119876543', '00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000002', 'active', 'prospect', '["Warm"]',       1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000001', 'Bilal',  'Malik',   'bilal@paksteel.pk',   '+923451122334', '00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000002', 'active', 'customer', '["VIP"]',        1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000033', '00000000-0000-0000-0000-000000000001', 'Fatima', 'Zahra',   'fatima@alkhidmat.pk', '+923336677889', '00000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000002', 'active', 'lead',     '["Cold"]',       1, NOW(), NOW())
ON CONFLICT (tenant_id, phone_e164) DO NOTHING;

-- ─── lead_management_db.leads ────────────────────────────────────────────────
INSERT INTO lead_management_db.leads (lead_id, tenant_id, owner_id, contact_id, title, stage, status, priority, source, contact_name, contact_phone_e164, contact_email, estimated_value, currency, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000040', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000030', 'City Pharma Renewal',        'new',         'open',    'hot',  'manual',   'Tariq Mehmood', '+923001234567', 'tariq@citypharma.pk', 450000, 'PKR', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000041', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000031', 'NexTech SaaS Upsell',        'qualifying',  'open',    'warm', 'web',      'Sana Sheikh',   '+923119876543', 'sana@nextech.pk',     250000, 'PKR', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000042', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000032', 'Pak Steel Module Expansion', 'proposal',    'working', 'hot',  'referral', 'Bilal Malik',   '+923451122334', 'bilal@paksteel.pk',   780000, 'PKR', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000043', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000033', 'Al-Khidmat NGO Lead',        'nurturing',   'open',    'cold', 'campaign', 'Fatima Zahra',  '+923336677889', 'fatima@alkhidmat.pk', 120000, 'PKR', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000044', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000030', 'Q3 Renewals Batch',          'negotiation', 'working', 'hot',  'whatsapp', 'Tariq Mehmood', '+923001234567', 'tariq@citypharma.pk', 900000, 'PKR', NOW(), NOW())
ON CONFLICT (lead_id) DO NOTHING;

-- ─── opportunity_db.opportunities ────────────────────────────────────────────
INSERT INTO opportunity_db.opportunities (opportunity_id, tenant_id, account_id, contact_id, owner_id, name, stage, amount, currency, close_date, probability, forecast_category, version_no, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000050', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000002', 'City Pharma Enterprise Deal', 'qualification', 450000, 'PKR', '2026-09-30', 30, 'pipeline', 1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000051', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000002', 'NexTech Annual License',      'proposal',      250000, 'PKR', '2026-08-15', 60, 'best_case', 1, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000052', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000002', 'Pak Steel HR Expansion',      'negotiation',   780000, 'PKR', '2026-07-31', 80, 'commit',    1, NOW(), NOW())
ON CONFLICT (opportunity_id) DO NOTHING;

-- ─── transaction_db.subscription ─────────────────────────────────────────────
INSERT INTO transaction_db.subscription (subscription_id, tenant_id, account_id, plan_code, status, start_date, renewal_date, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000020', 'enterprise-annual', 'active',   '2026-01-01', '2027-01-01', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000061', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000021', 'starter-monthly',   'active',   '2026-04-01', '2026-07-01', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000062', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000022', 'pro-annual',        'past_due', '2025-06-01', '2026-06-01', NOW(), NOW())
ON CONFLICT (subscription_id) DO NOTHING;

-- ─── transaction_db.invoice_summary ──────────────────────────────────────────
INSERT INTO transaction_db.invoice_summary (invoice_summary_id, tenant_id, subscription_id, invoice_number, amount_due, amount_paid, currency, status, due_date, issued_at, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000070', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000060', 'INV-2026-001', 450000, 450000, 'PKR', 'paid', '2026-01-31', NOW(), NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000071', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000061', 'INV-2026-002', 45000,  45000,  'PKR', 'paid', '2026-04-30', NOW(), NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000072', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000062', 'INV-2026-003', 360000, 0,      'PKR', 'open', '2026-06-01', NOW(), NOW(), NOW())
ON CONFLICT (invoice_summary_id) DO NOTHING;

-- ─── transaction_db.payment ──────────────────────────────────────────────────
INSERT INTO transaction_db.payment (payment_id, tenant_id, subscription_id, invoice_summary_id, payment_method_type, amount, currency, status, initiated_at, captured_at, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000080', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000070', 'bank_transfer', 450000, 'PKR', 'captured',  NOW() - INTERVAL '30 days', NOW() - INTERVAL '29 days', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000081', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000061', '00000000-0000-0000-0000-000000000071', 'wallet',        45000,  'PKR', 'captured',  NOW() - INTERVAL '10 days', NOW() - INTERVAL '9 days',  NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000082', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000062', '00000000-0000-0000-0000-000000000072', 'wallet',        180000, 'PKR', 'initiated', NOW() - INTERVAL '5 days',  NULL,                          NOW(), NOW())
ON CONFLICT (payment_id) DO NOTHING;

-- ─── activity_task_db.task ───────────────────────────────────────────────────
INSERT INTO activity_task_db.task (task_id, tenant_id, entity_type, entity_id, title, status, priority, created_by_user_id, assignment_method, starts_at, due_at, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000090', '00000000-0000-0000-0000-000000000001', 'lead', '00000000-0000-0000-0000-000000000040', 'Call City Pharma',    'open',        'high',   '00000000-0000-0000-0000-000000000002', 'explicit', NOW(), NOW() + INTERVAL '1 day',  NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000091', '00000000-0000-0000-0000-000000000001', 'lead', '00000000-0000-0000-0000-000000000041', 'Demo NexTech CRM',    'open',        'normal', '00000000-0000-0000-0000-000000000002', 'explicit', NOW(), NOW() + INTERVAL '3 days', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000092', '00000000-0000-0000-0000-000000000001', 'lead', '00000000-0000-0000-0000-000000000042', 'Follow up Pak Steel', 'in_progress', 'urgent', '00000000-0000-0000-0000-000000000002', 'explicit', NOW(), NOW() + INTERVAL '1 day',  NOW(), NOW())
ON CONFLICT (task_id) DO NOTHING;

-- ─── activity_task_db.activity ───────────────────────────────────────────────
INSERT INTO activity_task_db.activity (activity_id, tenant_id, actor_user_id, entity_type, entity_id, event_type, event_time, payload_json, source_service, created_at)
VALUES
  ('00000000-0000-0000-0000-0000000000a0', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'lead', '00000000-0000-0000-0000-000000000040', 'lead.created',  NOW() - INTERVAL '5 days',  '{"note":"Initial contact"}', 'gateway', NOW()),
  ('00000000-0000-0000-0000-0000000000a1', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'lead', '00000000-0000-0000-0000-000000000041', 'lead.contacted', NOW() - INTERVAL '3 days', '{"channel":"whatsapp"}',     'gateway', NOW()),
  ('00000000-0000-0000-0000-0000000000a2', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'lead', '00000000-0000-0000-0000-000000000042', 'lead.qualified', NOW() - INTERVAL '1 day',  '{"score":85}',               'gateway', NOW())
ON CONFLICT (activity_id) DO NOTHING;

-- ─── public.leads (needed for followup_tasks FK) ────────────────────────────
INSERT INTO public.leads (lead_id, tenant_id, contact_id, owner_id, stage, status, priority, source)
VALUES
  ('00000000-0000-0000-0000-000000000040', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000002', 'new',         'open',    'hot',  'manual'),
  ('00000000-0000-0000-0000-000000000041', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000002', 'qualifying',  'open',    'warm', 'web'),
  ('00000000-0000-0000-0000-000000000042', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000002', 'proposal',    'working', 'hot',  'referral')
ON CONFLICT (lead_id) DO NOTHING;

-- ─── public.followup_tasks ───────────────────────────────────────────────────
-- followups use tenant_id as text (public schema, created by Alembic)
INSERT INTO public.followup_tasks (task_id, tenant_id, lead_id, owner_id, state, due_at, rule_type, escalation_level, generated_by, is_canonical)
VALUES
  ('ft-001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000040', '00000000-0000-0000-0000-000000000002', 'pending',   NOW() + INTERVAL '1 day',  'TimeBased',       'none',     'Scheduler', true),
  ('ft-002', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000041', '00000000-0000-0000-0000-000000000002', 'overdue',   NOW() - INTERVAL '2 days', 'TimeBased',       'reminder', 'Scheduler', true),
  ('ft-003', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000042', '00000000-0000-0000-0000-000000000002', 'pending',   NOW() + INTERVAL '3 days', 'ActivityBased',   'none',     'Scheduler', true)
ON CONFLICT (task_id) DO NOTHING;

-- ─── feature_flag_db.feature_flags ───────────────────────────────────────────
INSERT INTO feature_flag_db.feature_flags (flag_id, key, name, description, default_value, status, created_by, created_at, updated_at)
SELECT '00000000-0000-0000-0000-0000000000f0', 'ai_scoring',    'AI Lead Scoring', 'Enable AI lead scoring', true, 'active', '00000000-0000-0000-0000-000000000002', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM feature_flag_db.feature_flags WHERE key = 'ai_scoring');

INSERT INTO feature_flag_db.feature_flags (flag_id, key, name, description, default_value, status, created_by, created_at, updated_at)
SELECT '00000000-0000-0000-0000-0000000000f1', 'whatsapp_inbox','WhatsApp Inbox',  'Enable WhatsApp inbox',  true, 'active', '00000000-0000-0000-0000-000000000002', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM feature_flag_db.feature_flags WHERE key = 'whatsapp_inbox');

END $$;
