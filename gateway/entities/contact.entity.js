const CONTACT_LIFECYCLE_STATUSES = new Set(['lead', 'customer', 'inactive']);

function createContactEntity({
  contact_id,
  tenant_id,
  account_id = null,
  owner_user_id,
  first_name,
  last_name,
  email = null,
  phone = null,
  lifecycle_status = 'lead',
  created_at,
  updated_at,
}) {
  return {
    contact_id,
    tenant_id,
    account_id,
    owner_user_id,
    first_name,
    last_name,
    email,
    phone,
    lifecycle_status,
    created_at,
    updated_at,
  };
}

function validateContactInput(payload, { partial = false } = {}) {
  const errors = [];

  if (!partial || payload.first_name !== undefined) {
    if (typeof payload.first_name !== 'string' || !payload.first_name.trim()) {
      errors.push({ field: 'first_name', reason: 'must_be_non_empty_string' });
    }
  }

  if (!partial || payload.last_name !== undefined) {
    if (typeof payload.last_name !== 'string' || !payload.last_name.trim()) {
      errors.push({ field: 'last_name', reason: 'must_be_non_empty_string' });
    }
  }

  if (!partial || payload.owner_user_id !== undefined) {
    if (payload.owner_user_id !== undefined && (typeof payload.owner_user_id !== 'string' || !payload.owner_user_id.trim())) {
      errors.push({ field: 'owner_user_id', reason: 'must_be_non_empty_string' });
    }
  }

  if (payload.lifecycle_status !== undefined && !CONTACT_LIFECYCLE_STATUSES.has(payload.lifecycle_status)) {
    errors.push({ field: 'lifecycle_status', reason: 'must_be_lead_customer_or_inactive' });
  }

  if (payload.account_id !== undefined && payload.account_id !== null && (typeof payload.account_id !== 'string' || !payload.account_id.trim())) {
    errors.push({ field: 'account_id', reason: 'must_be_string_or_null' });
  }

  return errors;
}

module.exports = {
  createContactEntity,
  validateContactInput,
};
