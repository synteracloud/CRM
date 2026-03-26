const crypto = require('crypto');
const {
  createEmailEntity,
  createEmailEngagementLogEntity,
  validateEmailCreateInput,
  validateEmailEngagementEventInput,
  TRACKABLE_ENTITY_TYPES,
} = require('../entities/email.entity');

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function buildId(prefix) {
  return `${prefix}_${crypto.randomUUID()}`;
}

class EmailEngagementService {
  constructor() {
    this.emailsByTenant = new Map();
    this.logsByTenant = new Map();
  }

  getTenantMap(container, tenantId) {
    if (!container.has(tenantId)) {
      container.set(tenantId, new Map());
    }
    return container.get(tenantId);
  }

  getTenantList(container, tenantId) {
    if (!container.has(tenantId)) {
      container.set(tenantId, []);
    }
    return container.get(tenantId);
  }

  createEmail(tenantId, payload, actorUserId) {
    const errors = validateEmailCreateInput(payload);
    if (errors.length > 0) return { errors };

    const ts = nowIso();
    const email = createEmailEntity({
      email_id: buildId('eml'),
      tenant_id: tenantId,
      entity_type: payload.entity_type,
      entity_id: payload.entity_id,
      to_email: payload.to_email,
      from_email: payload.from_email || 'no-reply@crm.local',
      subject: payload.subject,
      body_text: payload.body_text,
      body_html: payload.body_html || null,
      provider_message_id: buildId('provider_msg'),
      status: 'sent',
      sent_at: ts,
      open_count: 0,
      click_count: 0,
      created_by_user_id: actorUserId,
      created_at: ts,
      updated_at: ts,
    });

    this.getTenantMap(this.emailsByTenant, tenantId).set(email.email_id, email);
    return { data: email };
  }

  getEmail(tenantId, emailId) {
    return this.getTenantMap(this.emailsByTenant, tenantId).get(emailId) || null;
  }

  listEmails(tenantId, { entity_type: entityType, entity_id: entityId } = {}) {
    return [...this.getTenantMap(this.emailsByTenant, tenantId).values()]
      .filter((email) => (!entityType || email.entity_type === entityType)
        && (!entityId || email.entity_id === entityId));
  }

  trackEvent(tenantId, emailId, payload) {
    const errors = validateEmailEngagementEventInput(payload);
    if (errors.length > 0) return { errors };

    const email = this.getEmail(tenantId, emailId);
    if (!email) return { notFound: true };

    const eventTime = payload.event_time || nowIso();
    const log = createEmailEngagementLogEntity({
      email_engagement_log_id: buildId('elog'),
      tenant_id: tenantId,
      email_id: email.email_id,
      entity_type: email.entity_type,
      entity_id: email.entity_id,
      event_type: payload.event_type,
      event_time: eventTime,
      link_url: payload.link_url || null,
      user_agent: payload.user_agent || null,
      ip_address: payload.ip_address || null,
      created_at: nowIso(),
    });

    this.getTenantList(this.logsByTenant, tenantId).push(log);

    if (payload.event_type === 'opened') {
      email.open_count += 1;
      if (!email.first_opened_at) {
        email.first_opened_at = eventTime;
      }
      if (email.status === 'sent') {
        email.status = 'opened';
      }
    }

    if (payload.event_type === 'clicked') {
      email.click_count += 1;
      if (!email.first_clicked_at) {
        email.first_clicked_at = eventTime;
      }
      if (email.status === 'sent' || email.status === 'opened') {
        email.status = 'clicked';
      }
    }

    email.updated_at = nowIso();

    return { data: { email, log } };
  }

  listLogs(tenantId, { email_id: emailId, entity_type: entityType, entity_id: entityId } = {}) {
    const logs = this.getTenantList(this.logsByTenant, tenantId);
    return logs.filter((log) => (!emailId || log.email_id === emailId)
      && (!entityType || log.entity_type === entityType)
      && (!entityId || log.entity_id === entityId));
  }

  getEntityEngagementMetrics(tenantId, entityType, entityId) {
    if (!TRACKABLE_ENTITY_TYPES.has(entityType)) {
      return { errors: [{ field: 'entity_type', reason: 'must_be_contact_or_lead' }] };
    }

    if (typeof entityId !== 'string' || !entityId.trim()) {
      return { errors: [{ field: 'entity_id', reason: 'must_be_non_empty_string' }] };
    }

    const scopedEmails = this.listEmails(tenantId, {
      entity_type: entityType,
      entity_id: entityId,
    });

    const sentCount = scopedEmails.length;
    const openedEmailCount = scopedEmails.filter((email) => email.open_count > 0).length;
    const clickedEmailCount = scopedEmails.filter((email) => email.click_count > 0).length;

    const openEvents = scopedEmails.reduce((total, email) => total + email.open_count, 0);
    const clickEvents = scopedEmails.reduce((total, email) => total + email.click_count, 0);

    const openRate = sentCount === 0 ? 0 : Number((openedEmailCount / sentCount).toFixed(4));
    const clickRate = sentCount === 0 ? 0 : Number((clickedEmailCount / sentCount).toFixed(4));

    return {
      data: {
        entity_type: entityType,
        entity_id: entityId,
        emails_sent: sentCount,
        unique_emails_opened: openedEmailCount,
        unique_emails_clicked: clickedEmailCount,
        total_open_events: openEvents,
        total_click_events: clickEvents,
        open_rate: openRate,
        click_rate: clickRate,
      },
    };
  }
}

const emailEngagementService = new EmailEngagementService();

module.exports = {
  emailEngagementService,
};
