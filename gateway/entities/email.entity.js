const EMAIL_STATUSES = new Set(['queued', 'sent', 'opened', 'clicked']);
const TRACKABLE_ENTITY_TYPES = new Set(['contact', 'lead']);

function createEmailEntity({
  email_id,
  tenant_id,
  entity_type,
  entity_id,
  to_email,
  from_email,
  subject,
  body_text,
  body_html = null,
  provider_message_id = null,
  status = 'queued',
  sent_at,
  first_opened_at = null,
  first_clicked_at = null,
  open_count = 0,
  click_count = 0,
  created_by_user_id,
  created_at,
  updated_at,
}) {
  return {
    email_id,
    tenant_id,
    entity_type,
    entity_id,
    to_email,
    from_email,
    subject,
    body_text,
    body_html,
    provider_message_id,
    status,
    sent_at,
    first_opened_at,
    first_clicked_at,
    open_count,
    click_count,
    created_by_user_id,
    created_at,
    updated_at,
  };
}

function createEmailEngagementLogEntity({
  email_engagement_log_id,
  tenant_id,
  email_id,
  entity_type,
  entity_id,
  event_type,
  event_time,
  link_url = null,
  user_agent = null,
  ip_address = null,
  created_at,
}) {
  return {
    email_engagement_log_id,
    tenant_id,
    email_id,
    entity_type,
    entity_id,
    event_type,
    event_time,
    link_url,
    user_agent,
    ip_address,
    created_at,
  };
}

function validateEmailCreateInput(payload) {
  const errors = [];

  if (!TRACKABLE_ENTITY_TYPES.has(payload.entity_type)) {
    errors.push({ field: 'entity_type', reason: 'must_be_contact_or_lead' });
  }

  if (typeof payload.entity_id !== 'string' || !payload.entity_id.trim()) {
    errors.push({ field: 'entity_id', reason: 'must_be_non_empty_string' });
  }

  if (typeof payload.to_email !== 'string' || !payload.to_email.trim()) {
    errors.push({ field: 'to_email', reason: 'must_be_non_empty_string' });
  }

  if (typeof payload.subject !== 'string' || !payload.subject.trim()) {
    errors.push({ field: 'subject', reason: 'must_be_non_empty_string' });
  }

  if (typeof payload.body_text !== 'string' || !payload.body_text.trim()) {
    errors.push({ field: 'body_text', reason: 'must_be_non_empty_string' });
  }

  if (payload.body_html !== undefined && payload.body_html !== null && typeof payload.body_html !== 'string') {
    errors.push({ field: 'body_html', reason: 'must_be_string_or_null' });
  }

  return errors;
}

function validateEmailEngagementEventInput(payload) {
  const errors = [];

  if (!['opened', 'clicked'].includes(payload.event_type)) {
    errors.push({ field: 'event_type', reason: 'must_be_opened_or_clicked' });
  }

  if (payload.event_time !== undefined && Number.isNaN(Date.parse(payload.event_time))) {
    errors.push({ field: 'event_time', reason: 'must_be_valid_rfc3339_timestamp' });
  }

  if (payload.link_url !== undefined && payload.link_url !== null && typeof payload.link_url !== 'string') {
    errors.push({ field: 'link_url', reason: 'must_be_string_or_null' });
  }

  return errors;
}

module.exports = {
  EMAIL_STATUSES,
  TRACKABLE_ENTITY_TYPES,
  createEmailEntity,
  createEmailEngagementLogEntity,
  validateEmailCreateInput,
  validateEmailEngagementEventInput,
};
