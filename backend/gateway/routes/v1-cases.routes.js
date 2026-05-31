'use strict';

/**
 * Case Management routes.
 *
 * Docs:    backend/docs/domain/cases-domain.md
 * Service: services/cases/service.py (state machine + SLA)
 *
 * Mounts:
 *   /api/v1/cases/*          — case CRUD + actions
 *   /api/v1/support/queues/* — support queue management (exported as supportRouter)
 *
 * In-memory fallback active when DB_DISABLED=true or pg unavailable.
 * State machine enforced in both DB and in-memory paths.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

// ── State machine (mirrors cases/entities.py) ─────────────────────────────────
const ALLOWED_TRANSITIONS = {
  OPEN:                ['ASSIGNED', 'CLOSED'],
  ASSIGNED:            ['IN_PROGRESS', 'OPEN', 'ESCALATED'],
  IN_PROGRESS:         ['WAITING_ON_CUSTOMER', 'RESOLVED', 'ESCALATED'],
  WAITING_ON_CUSTOMER: ['IN_PROGRESS', 'RESOLVED', 'CLOSED'],
  RESOLVED:            ['CLOSED', 'IN_PROGRESS'],
  ESCALATED:           ['ASSIGNED', 'IN_PROGRESS'],
  CLOSED:              ['OPEN'],
};

const VALID_STATUSES  = Object.keys(ALLOWED_TRANSITIONS);
const VALID_PRIORITY  = ['critical', 'high', 'medium', 'low'];
const VALID_SOURCE    = ['whatsapp', 'web_form', 'email', 'phone', 'internal'];
const VALID_SLA_TIER  = ['tier_1_critical', 'tier_2_high', 'tier_3_standard', 'tier_4_low'];
const VALID_COMMENT_TYPES = ['internal_note', 'customer_reply', 'resolution', 'status_change', 'escalation_note'];
const VALID_ESC_REASON    = ['sla_first_response_breach', 'sla_resolution_breach', 'customer_request', 'manager_override'];
const ADMIN_ROLES         = ['admin', 'tenant_admin', 'tenant_owner', 'manager'];

// SLA defaults (hours) per tier — spec §2.5
const SLA_DEFAULTS = {
  tier_1_critical: { first_response: 1,  resolution: 8   },
  tier_2_high:     { first_response: 4,  resolution: 24  },
  tier_3_standard: { first_response: 8,  resolution: 72  },
  tier_4_low:      { first_response: 24, resolution: 168 },
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function nowIso() { return new Date().toISOString(); }

function caseNumberFor(seq) {
  return `CAS-${new Date().getFullYear()}-${String(seq).padStart(6, '0')}`;
}

function addBusinessHours(startIso, hours) {
  // Simple calendar-hours approximation for in-memory fallback.
  // Full PKT business-hours calculation lives in Python service.
  const d = new Date(startIso);
  d.setHours(d.getHours() + hours);
  return d.toISOString();
}

function canTransition(from, to) {
  return (ALLOWED_TRANSITIONS[from] || []).includes(to);
}

// ── In-memory stores (fallback when DB_DISABLED=true) ─────────────────────────
let _caseSeq = 1;
const _memCases       = [];
const _memComments    = [];
const _memEscalations = [];
const _memQueues      = [
  { queue_id: 'q-001', name: 'Tier 1 Support',  routing_strategy: 'round_robin',  sla_tier_default: 'tier_3_standard', is_active: true },
  { queue_id: 'q-002', name: 'Tier 2 Technical', routing_strategy: 'least_loaded', sla_tier_default: 'tier_2_high',     is_active: true },
  { queue_id: 'q-003', name: 'Billing',           routing_strategy: 'round_robin',  sla_tier_default: 'tier_3_standard', is_active: true },
  { queue_id: 'q-004', name: 'Escalation',        routing_strategy: 'manual',       sla_tier_default: 'tier_1_critical', is_active: true },
];

// ── Cases Router ──────────────────────────────────────────────────────────────
const casesRouter = express.Router();

// POST /cases — create
casesRouter.post(
  '/',
  requestValidationMiddleware(['subject']),
  requireScopes([SCOPES.CASES_CREATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const {
      subject, description, priority = 'medium', source = 'web_form',
      category, contact_id, account_id, lead_id,
      sla_tier = 'tier_3_standard', queue_id, custom_fields = {},
    } = req.body;

    if (!VALID_PRIORITY.includes(priority))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid priority.', [{ field: 'priority', reason: `must_be_one_of_${VALID_PRIORITY.join('|')}` }]);
    if (!VALID_SOURCE.includes(source))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid source.', [{ field: 'source', reason: `must_be_one_of_${VALID_SOURCE.join('|')}` }]);
    if (!VALID_SLA_TIER.includes(sla_tier))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid sla_tier.', [{ field: 'sla_tier', reason: `must_be_one_of_${VALID_SLA_TIER.join('|')}` }]);

    const ts  = nowIso();
    const sla = SLA_DEFAULTS[sla_tier];
    const newCase = {
      case_id:                    randomUUID(),
      tenant_id:                  tenantId,
      case_number:                caseNumberFor(_caseSeq++),
      subject,
      description:                description || null,
      status:                     'OPEN',
      priority,
      source,
      category:                   category || null,
      contact_id:                 contact_id || null,
      account_id:                 account_id || null,
      lead_id:                    lead_id || null,
      assigned_to:                null,
      assigned_team_id:           null,
      queue_id:                   queue_id || null,
      sla_tier,
      sla_first_response_due_at:  addBusinessHours(ts, sla.first_response),
      sla_resolution_due_at:      addBusinessHours(ts, sla.resolution),
      first_responded_at:         null,
      resolved_at:                null,
      resolution_confirmed_at:    null,
      closed_at:                  null,
      reopened_at:                null,
      reopen_count:               0,
      escalation_level:           0,
      tags:                       [],
      custom_fields,
      version_no:                 1,
      created_at:                 ts,
      updated_at:                 ts,
      created_by:                 userId,
      updated_by:                 userId,
    };

    _memCases.push(newCase);
    return res.status(201).json({ data: newCase, meta: { request_id: req.request_id } });
  },
);

// GET /cases — list
casesRouter.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { status, priority, assigned_to, queue_id, contact_id } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memCases.filter(c => c.tenant_id === tenantId);
    if (status)      rows = rows.filter(c => c.status      === status);
    if (priority)    rows = rows.filter(c => c.priority    === priority);
    if (assigned_to) rows = rows.filter(c => c.assigned_to === assigned_to);
    if (queue_id)    rows = rows.filter(c => c.queue_id    === queue_id);
    if (contact_id)  rows = rows.filter(c => c.contact_id  === contact_id);

    const total = rows.length;
    const page  = rows.slice(offset, offset + limit);
    return respondSuccess(res, page, { count: page.length, total, limit, offset });
  },
);

// GET /cases/:id — detail
casesRouter.get(
  '/:case_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { case_id } = req.params;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    const comments    = _memComments.filter(cm => cm.case_id === case_id);
    const escalations = _memEscalations.filter(e => e.case_id === case_id);
    return respondSuccess(res, { ...c, comments, escalations });
  },
);

// PATCH /cases/:id — update non-status fields
casesRouter.patch(
  '/:case_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { subject, priority, category, custom_fields, version_no } = req.body;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (version_no !== undefined && version_no !== c.version_no)
      return respondError(res, 409, 'CONFLICT', 'Optimistic concurrency conflict.', [{ field: 'version_no', reason: 'stale' }]);

    if (priority && !VALID_PRIORITY.includes(priority))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid priority.', [{ field: 'priority', reason: `must_be_one_of_${VALID_PRIORITY.join('|')}` }]);

    if (subject)        c.subject       = subject;
    if (priority)       c.priority      = priority;
    if (category)       c.category      = category;
    if (custom_fields)  c.custom_fields = { ...c.custom_fields, ...custom_fields };
    c.version_no   += 1;
    c.updated_at    = nowIso();
    c.updated_by    = userId;

    return respondSuccess(res, c);
  },
);

// POST /cases/:id/assign
casesRouter.post(
  '/:case_id/assign',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { assigned_to, assigned_team_id } = req.body;

    if (!assigned_to && !assigned_team_id)
      return respondError(res, 422, 'VALIDATION_ERROR', 'assigned_to or assigned_team_id is required.', []);

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (assigned_to)      c.assigned_to      = assigned_to;
    if (assigned_team_id) c.assigned_team_id = assigned_team_id;

    // Auto-transition OPEN → ASSIGNED
    if (c.status === 'OPEN' && assigned_to) c.status = 'ASSIGNED';

    c.updated_at = nowIso();
    c.updated_by = userId;
    c.version_no += 1;

    return respondSuccess(res, c);
  },
);

// POST /cases/:id/comments — add comment
casesRouter.post(
  '/:case_id/comments',
  requestValidationMiddleware(['body', 'comment_type']),
  requireScopes([SCOPES.CASES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { body, comment_type, attachment_urls = [] } = req.body;

    if (!VALID_COMMENT_TYPES.includes(comment_type))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid comment_type.', [{ field: 'comment_type', reason: `must_be_one_of_${VALID_COMMENT_TYPES.join('|')}` }]);

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');
    if (c.status === 'CLOSED') return respondError(res, 409, 'CONFLICT', 'Cannot add comment to a closed case.');

    const ts      = nowIso();
    const comment = {
      comment_id:             randomUUID(),
      case_id,
      tenant_id:              tenantId,
      comment_type,
      body,
      author_id:              userId,
      is_visible_to_customer: ['customer_reply', 'resolution'].includes(comment_type),
      attachment_urls,
      created_at:             ts,
      updated_at:             ts,
    };
    _memComments.push(comment);

    // Set first_responded_at on first outbound customer_reply — stops first-response SLA
    if (comment_type === 'customer_reply' && !c.first_responded_at) {
      c.first_responded_at = ts;
    }

    // Auto-transition ASSIGNED → IN_PROGRESS on first agent reply
    if (comment_type === 'customer_reply' && c.status === 'ASSIGNED') {
      c.status = 'IN_PROGRESS';
    }

    c.updated_at = ts;
    c.updated_by = userId;

    return res.status(201).json({ data: comment, meta: { request_id: req.request_id } });
  },
);

// POST /cases/:id/resolve
casesRouter.post(
  '/:case_id/resolve',
  requestValidationMiddleware(['resolution_note']),
  requireScopes([SCOPES.CASES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { resolution_note } = req.body;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (!canTransition(c.status, 'RESOLVED'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot transition from ${c.status} to RESOLVED.`);

    const ts = nowIso();

    // Create resolution comment automatically
    _memComments.push({
      comment_id:             randomUUID(),
      case_id,
      tenant_id:              tenantId,
      comment_type:           'resolution',
      body:                   resolution_note,
      author_id:              userId,
      is_visible_to_customer: true,
      attachment_urls:        [],
      created_at:             ts,
      updated_at:             ts,
    });

    c.status      = 'RESOLVED';
    c.resolved_at = ts;
    c.updated_at  = ts;
    c.updated_by  = userId;
    c.version_no += 1;

    return respondSuccess(res, c);
  },
);

// POST /cases/:id/close — force-close (admin/manager)
casesRouter.post(
  '/:case_id/close',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { close_reason } = req.body;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (!canTransition(c.status, 'CLOSED'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot close from status ${c.status}.`);

    const ts = nowIso();
    c.status                   = 'CLOSED';
    c.closed_at                = ts;
    c.resolution_confirmed_at  = c.resolution_confirmed_at || ts;
    c.updated_at               = ts;
    c.updated_by               = userId;
    c.version_no              += 1;

    if (close_reason) {
      _memComments.push({
        comment_id:             randomUUID(),
        case_id,
        tenant_id:              tenantId,
        comment_type:           'status_change',
        body:                   `Force closed: ${close_reason}`,
        author_id:              userId,
        is_visible_to_customer: false,
        attachment_urls:        [],
        created_at:             ts,
        updated_at:             ts,
      });
    }

    return respondSuccess(res, c);
  },
);

// POST /cases/:id/reopen
casesRouter.post(
  '/:case_id/reopen',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (c.status !== 'CLOSED')
      return respondError(res, 422, 'TRANSITION_ERROR', 'Only CLOSED cases can be reopened.');

    // 14-day reopen window — spec §3.1
    if (c.closed_at) {
      const daysSinceClosed = (Date.now() - new Date(c.closed_at).getTime()) / 86400000;
      if (daysSinceClosed > 14)
        return respondError(res, 422, 'REOPEN_WINDOW_EXPIRED', 'Reopen window (14 days) has expired.');
    }

    const ts = nowIso();
    c.status                    = 'OPEN';
    c.resolved_at               = null;
    c.closed_at                 = null;
    c.resolution_confirmed_at   = null;
    c.reopened_at               = ts;
    c.reopen_count             += 1;
    c.updated_at                = ts;
    c.updated_by                = userId;
    c.version_no               += 1;

    return respondSuccess(res, c);
  },
);

// POST /cases/:id/escalate — manager-override escalation
casesRouter.post(
  '/:case_id/escalate',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { escalation_reason = 'manager_override', escalated_to, escalated_to_team, note } = req.body;

    if (!VALID_ESC_REASON.includes(escalation_reason))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid escalation_reason.', [{ field: 'escalation_reason', reason: `must_be_one_of_${VALID_ESC_REASON.join('|')}` }]);

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');
    if (['RESOLVED', 'CLOSED'].includes(c.status))
      return respondError(res, 409, 'CONFLICT', 'Cannot escalate a resolved or closed case.');

    const ts = nowIso();
    const newLevel = Math.max(c.escalation_level, escalation_reason === 'customer_request' ? 3 : 3);

    const escalation = {
      escalation_id:     randomUUID(),
      case_id,
      tenant_id:         tenantId,
      escalation_level:  newLevel,
      escalation_reason,
      escalated_by:      userId,
      escalated_to:      escalated_to || null,
      escalated_to_team: escalated_to_team || null,
      note:              note || null,
      triggered_at:      ts,
      resolved_at:       null,
    };
    _memEscalations.push(escalation);

    c.status          = 'ESCALATED';
    c.escalation_level = newLevel;
    if (escalated_to)      c.assigned_to      = escalated_to;
    if (escalated_to_team) c.assigned_team_id = escalated_to_team;
    c.updated_at  = ts;
    c.updated_by  = userId;
    c.version_no += 1;

    return res.status(201).json({ data: escalation, case: c, meta: { request_id: req.request_id } });
  },
);

// POST /cases/:id/link-article
casesRouter.post(
  '/:case_id/link-article',
  requestValidationMiddleware(['article_id']),
  requireScopes([SCOPES.CASES_UPDATE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { case_id } = req.params;
    const { article_id } = req.body;

    const c = _memCases.find(x => x.case_id === case_id && x.tenant_id === tenantId);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Case not found.');

    if (!c.knowledge_article_ids) c.knowledge_article_ids = [];
    if (!c.knowledge_article_ids.includes(article_id)) {
      c.knowledge_article_ids.push(article_id);
    }
    c.updated_at = nowIso();
    c.updated_by = userId;

    return respondSuccess(res, { case_id, article_id, linked_at: c.updated_at });
  },
);

// ── Support Queues Router ─────────────────────────────────────────────────────
const supportRouter = express.Router();

// GET /support/queues
supportRouter.get(
  '/queues',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const queues = _memQueues.filter(q => q.is_active);
    return respondSuccess(res, queues, { count: queues.length });
  },
);

// POST /support/queues — admin only
supportRouter.post(
  '/queues',
  requestValidationMiddleware(['name']),
  requireScopes([SCOPES.CASES_ADMIN]),
  async (req, res) => {
    const { name, description, routing_strategy = 'round_robin', sla_tier_default = 'tier_3_standard', team_id } = req.body;
    const queue = {
      queue_id:         randomUUID(),
      name,
      description:      description || null,
      routing_strategy,
      sla_tier_default,
      skill_tags:       [],
      team_id:          team_id || null,
      is_active:        true,
      created_at:       nowIso(),
      updated_at:       nowIso(),
    };
    _memQueues.push(queue);
    return res.status(201).json({ data: queue, meta: { request_id: req.request_id } });
  },
);

// PATCH /support/queues/:id
supportRouter.patch(
  '/queues/:queue_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CASES_ADMIN]),
  async (req, res) => {
    const { queue_id } = req.params;
    const q = _memQueues.find(x => x.queue_id === queue_id);
    if (!q) return respondError(res, 404, 'NOT_FOUND', 'Queue not found.');

    const { name, description, routing_strategy, sla_tier_default, is_active } = req.body;
    if (name)              q.name              = name;
    if (description)       q.description       = description;
    if (routing_strategy)  q.routing_strategy  = routing_strategy;
    if (sla_tier_default)  q.sla_tier_default  = sla_tier_default;
    if (is_active !== undefined) q.is_active   = is_active;
    q.updated_at = nowIso();

    return respondSuccess(res, q);
  },
);

module.exports = { casesRouter, supportRouter };
