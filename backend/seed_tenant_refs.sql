-- identity_auth_db: tenant_id, status, created_at
INSERT INTO identity_auth_db.tenant_ref (tenant_id, status, created_at) VALUES ('00000000-0000-0000-0000-000000000001', 'active', NOW()) ON CONFLICT (tenant_id) DO NOTHING;

-- contact_account_db: tenant_id, created_at
INSERT INTO contact_account_db.tenant_ref (tenant_id, created_at) VALUES ('00000000-0000-0000-0000-000000000001', NOW()) ON CONFLICT (tenant_id) DO NOTHING;

-- lead_management_db: tenant_id, created_at
INSERT INTO lead_management_db.tenant_ref (tenant_id, created_at) VALUES ('00000000-0000-0000-0000-000000000001', NOW()) ON CONFLICT (tenant_id) DO NOTHING;

-- opportunity_db: tenant_id, created_at
INSERT INTO opportunity_db.tenant_ref (tenant_id, created_at) VALUES ('00000000-0000-0000-0000-000000000001', NOW()) ON CONFLICT (tenant_id) DO NOTHING;

-- transaction_db: tenant_id, tenant_name, status, created_at, updated_at
INSERT INTO transaction_db.tenant_ref (tenant_id, tenant_name, status, created_at, updated_at) VALUES ('00000000-0000-0000-0000-000000000001', 'Dev Tenant', 'active', NOW(), NOW()) ON CONFLICT (tenant_id) DO NOTHING;

-- activity_task_db: tenant_id, tenant_name, status, created_at, updated_at
INSERT INTO activity_task_db.tenant_ref (tenant_id, tenant_name, status, created_at, updated_at) VALUES ('00000000-0000-0000-0000-000000000001', 'Dev Tenant', 'active', NOW(), NOW()) ON CONFLICT (tenant_id) DO NOTHING;
