const ACCOUNT_STATUSES = new Set(['active', 'inactive', 'prospect']);

function createAccountEntity({
  account_id,
  tenant_id,
  owner_user_id,
  name,
  industry = null,
  segment = null,
  status = 'active',
  billing_address = null,
  created_at,
  updated_at,
}) {
  return {
    account_id,
    tenant_id,
    owner_user_id,
    name,
    industry,
    segment,
    status,
    billing_address,
    created_at,
    updated_at,
  };
}

function validateAccountInput(payload, { partial = false } = {}) {
  const errors = [];

  if (!partial || payload.name !== undefined) {
    if (typeof payload.name !== 'string' || !payload.name.trim()) {
      errors.push({ field: 'name', reason: 'must_be_non_empty_string' });
    }
  }

  if (!partial || payload.owner_user_id !== undefined) {
    if (payload.owner_user_id !== undefined && (typeof payload.owner_user_id !== 'string' || !payload.owner_user_id.trim())) {
      errors.push({ field: 'owner_user_id', reason: 'must_be_non_empty_string' });
    }
  }

  if (payload.status !== undefined && !ACCOUNT_STATUSES.has(payload.status)) {
    errors.push({ field: 'status', reason: 'must_be_active_inactive_or_prospect' });
  }

  return errors;
}

module.exports = {
  createAccountEntity,
  validateAccountInput,
};
