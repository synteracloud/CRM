'use strict';

/**
 * Shared Inbox routes.
 *
 * Docs: backend/docs/domain/shared-inbox.md
 * Mount: /api/v1/inbox/*
 *
 * Covers:
 *   GET/GET  /inbox/conversations[/:id]
 *   POST     /inbox/conversations/:id/claim
 *   POST     /inbox/conversations/:id/handoff
 *   POST     /inbox/conversations/:id/messages
 *   PATCH    /inbox/presence         (own status)
 *   GET      /inbox/presence         (supervisor view)
 *   GET/POST /inbox/queues
 *   PATCH    /inbox/queues/:id
 *   GET      /inbox/queues/:id/stats
 *
 * Assignment invariant (spec §1.2):
 *   Every conversation has exactly one assigned agent at any time.
 *   Claim is atomic (WHERE assigned_agent_id IS NULL).
 *   Only assigned agent OR supervisor can hand off.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_PRESENCE      = ['online', 'away', 'busy', 'offline'];
const VALID_HANDOFF_REASON = ['agent_unavailable', 'capacity_exceeded', 'skill_match', 'manual', 'escalation'];
const VALID_ROUTING_STRAT  = ['round_robin', 'least_loaded', 'claim_first', 'skill_based'];
const SUPERVISOR_ROLES     = ['manager', 'admin', 'tenant_admin', 'tenant_owner'];

// ── In-memory stores ──────────────────────────────────────────────────────────
// Seeded from CRM_DUMMY message thread shapes
const _memConversations = [
  { conversation_id:'th-001', tenant_id:'_all', contact_name:'Tariq Mehmood',   contact_phone:'+923011234567', channel:'whatsapp', state:'open',     assigned_agent_id:'u-001', assigned_at:'2026-05-29T09:00:00Z', queue_id:'q-001', assignment_reason:'auto_routed', handoff_count:0, last_handoff_at:null, unread_count:2, intent:'payment_query',      last_message_preview:'Sir, order delivery kab hogi?',        last_message_at:'2026-05-29T09:45:00Z' },
  { conversation_id:'th-002', tenant_id:'_all', contact_name:'Nadia Hussain',   contact_phone:'+923219876543', channel:'email',    state:'open',     assigned_agent_id:'u-002', assigned_at:'2026-05-29T08:00:00Z', queue_id:'q-002', assignment_reason:'auto_routed', handoff_count:0, last_handoff_at:null, unread_count:0, intent:'follow_up_response', last_message_preview:'Regarding invoice INV-2026-002...',     last_message_at:'2026-05-29T08:30:00Z' },
  { conversation_id:'th-003', tenant_id:'_all', contact_name:'Kamran Iqbal',    contact_phone:'+923331122334', channel:'whatsapp', state:'open',     assigned_agent_id:null,    assigned_at:null,                  queue_id:'q-001', assignment_reason:null,          handoff_count:0, last_handoff_at:null, unread_count:1, intent:'payment_query',      last_message_preview:'Payment kar diya, please confirm',      last_message_at:'2026-05-29T07:15:00Z' },
  { conversation_id:'th-004', tenant_id:'_all', contact_name:'Zara Ahmed',      contact_phone:'+923451234567', channel:'sms',      state:'open',     assigned_agent_id:'u-003', assigned_at:'2026-05-28T16:00:00Z', queue_id:'q-001', assignment_reason:'claimed',     handoff_count:0, last_handoff_at:null, unread_count:0, intent:'lead_inquiry',       last_message_preview:'Please call me regarding proposal',     last_message_at:'2026-05-28T16:00:00Z' },
  { conversation_id:'th-005', tenant_id:'_all', contact_name:'Imran Butt',      contact_phone:'+923001111222', channel:'whatsapp', state:'open',     assigned_agent_id:'u-002', assigned_at:'2026-05-28T14:00:00Z', queue_id:'q-001', assignment_reason:'auto_routed', handoff_count:1, last_handoff_at:'2026-05-28T15:00:00Z', unread_count:3, intent:'lead_inquiry', last_message_preview:'Contract terms mein ek cheez clear...', last_message_at:'2026-05-28T14:30:00Z' },
  { conversation_id:'th-006', tenant_id:'_all', contact_name:'+923112223344',   contact_phone:'+923112223344', channel:'whatsapp', state:'open',     assigned_agent_id:null,    assigned_at:null,                  queue_id:'q-001', assignment_reason:null,          handoff_count:0, last_handoff_at:null, unread_count:1, intent:'lead_inquiry',       last_message_preview:'Hello, I want to know about CRM',      last_message_at:'2026-05-28T11:00:00Z' },
  { conversation_id:'th-007', tenant_id:'_all', contact_name:'Hassan Mirza',    contact_phone:'+923049988776', channel:'email',    state:'resolved', assigned_agent_id:'u-004', assigned_at:'2026-05-27T15:00:00Z', queue_id:'q-002', assignment_reason:'auto_routed', handoff_count:0, last_handoff_at:null, unread_count:0, intent:'follow_up_response', last_message_preview:'Following up on our meeting yesterday', last_message_at:'2026-05-27T15:00:00Z' },
  { conversation_id:'th-008', tenant_id:'_all', contact_name:'Ayesha Siddiqui', contact_phone:'+923355566677', channel:'whatsapp', state:'resolved', assigned_agent_id:'u-005', assigned_at:'2026-05-27T10:00:00Z', queue_id:'q-003', assignment_reason:'auto_routed', handoff_count:0, last_handoff_at:null, unread_count:0, intent:'support_request',    last_message_preview:'Feature request: export to Excel',     last_message_at:'2026-05-27T10:00:00Z' },
];

const _memMessages = {
  'th-001': [
    { message_id:'msg-001', conversation_id:'th-001', direction:'inbound',  text:'Assalamu Alaikum! Sir, mera order deliver kab hoga?', occurred_at:'2026-05-29T09:30:00Z', sender_name:'Tariq Mehmood' },
    { message_id:'msg-002', conversation_id:'th-001', direction:'outbound', text:'Wa Alaikum Assalam! Let me check the delivery status for you right away.', occurred_at:'2026-05-29T09:31:00Z', sender_name:'Ahmed Raza' },
    { message_id:'msg-003', conversation_id:'th-001', direction:'inbound',  text:'Sir, order delivery kab hogi?', occurred_at:'2026-05-29T09:45:00Z', sender_name:'Tariq Mehmood' },
  ],
};

const _memHandoffs   = [];
const _memPresence   = [
  { agent_id:'u-001', tenant_id:'_all', status:'online',  open_conversation_count:3, max_concurrent:10, last_seen_at:'2026-05-29T09:50:00Z', updated_at:'2026-05-29T09:50:00Z' },
  { agent_id:'u-002', tenant_id:'_all', status:'away',    open_conversation_count:2, max_concurrent:10, last_seen_at:'2026-05-29T09:30:00Z', updated_at:'2026-05-29T09:30:00Z' },
  { agent_id:'u-003', tenant_id:'_all', status:'online',  open_conversation_count:1, max_concurrent:10, last_seen_at:'2026-05-29T09:48:00Z', updated_at:'2026-05-29T09:48:00Z' },
  { agent_id:'u-004', tenant_id:'_all', status:'busy',    open_conversation_count:10, max_concurrent:10, last_seen_at:'2026-05-29T09:00:00Z', updated_at:'2026-05-29T09:00:00Z' },
  { agent_id:'u-005', tenant_id:'_all', status:'offline', open_conversation_count:0, max_concurrent:10, last_seen_at:'2026-05-28T18:00:00Z', updated_at:'2026-05-28T18:00:00Z' },
];

const _memQueues = [
  { queue_id:'q-001', name:'General Support',  routing_strategy:'round_robin',  auto_assign:true,  skill_tags:[], team_id:null, is_active:true, created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { queue_id:'q-002', name:'Billing',           routing_strategy:'least_loaded', auto_assign:true,  skill_tags:[], team_id:null, is_active:true, created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { queue_id:'q-003', name:'VIP Enterprise',    routing_strategy:'claim_first',  auto_assign:false, skill_tags:[], team_id:null, is_active:true, created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
  { queue_id:'q-004', name:'WhatsApp Inbound',  routing_strategy:'round_robin',  auto_assign:true,  skill_tags:[], team_id:null, is_active:true, created_at:'2026-01-01T00:00:00Z', updated_at:'2026-01-01T00:00:00Z' },
];

function nowIso() { return new Date().toISOString(); }

// ── Router ────────────────────────────────────────────────────────────────────
const router = express.Router();

// GET /inbox/conversations — list (role-scoped)
router.get(
  '/conversations',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { state, channel, queue_id, assigned_agent_id } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memConversations.filter(c => c.tenant_id === tenantId || c.tenant_id === '_all');
    if (state)            rows = rows.filter(c => c.state            === state);
    if (channel)          rows = rows.filter(c => c.channel          === channel);
    if (queue_id)         rows = rows.filter(c => c.queue_id         === queue_id);
    if (assigned_agent_id) rows = rows.filter(c => c.assigned_agent_id === assigned_agent_id);

    // Sort by last_message_at DESC
    rows = rows.sort((a, b) => new Date(b.last_message_at) - new Date(a.last_message_at));

    const total = rows.length;
    const page  = rows.slice(offset, offset + limit);
    return respondSuccess(res, page, { count: page.length, total, limit, offset });
  },
);

// GET /inbox/conversations/:id — detail with message thread
router.get(
  '/conversations/:conversation_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { conversation_id } = req.params;

    const conv = _memConversations.find(c =>
      c.conversation_id === conversation_id && (c.tenant_id === tenantId || c.tenant_id === '_all')
    );
    if (!conv) return respondError(res, 404, 'NOT_FOUND', 'Conversation not found.');

    const messages = _memMessages[conversation_id] || [];
    return respondSuccess(res, { ...conv, messages });
  },
);

// POST /inbox/conversations/:id/claim — atomic claim from pool
router.post(
  '/conversations/:conversation_id/claim',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_WRITE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { conversation_id } = req.params;

    const conv = _memConversations.find(c =>
      c.conversation_id === conversation_id && (c.tenant_id === tenantId || c.tenant_id === '_all')
    );
    if (!conv) return respondError(res, 404, 'NOT_FOUND', 'Conversation not found.');

    // Atomic claim guard — spec §3.3
    if (conv.assigned_agent_id)
      return respondError(res, 409, 'CONFLICT', 'Conversation already assigned. Use handoff to reassign.');

    // Presence check
    const presence = _memPresence.find(p => p.agent_id === userId) || { status:'online', open_conversation_count:0, max_concurrent:10 };
    if (presence.status === 'busy' || presence.status === 'offline')
      return respondError(res, 422, 'AVAILABILITY_ERROR', `Cannot claim: agent status is ${presence.status}.`);
    if (presence.open_conversation_count >= presence.max_concurrent)
      return respondError(res, 422, 'CAPACITY_ERROR', 'Agent at maximum conversation capacity.');

    const ts = nowIso();
    conv.assigned_agent_id  = userId;
    conv.assigned_at        = ts;
    conv.assignment_reason  = 'claimed';
    presence.open_conversation_count += 1;

    return respondSuccess(res, conv);
  },
);

// POST /inbox/conversations/:id/handoff
router.post(
  '/conversations/:conversation_id/handoff',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_WRITE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const userRole = req.auth.role || 'agent';
    const { conversation_id } = req.params;
    const { to_agent_id = null, reason = 'manual', note } = req.body;

    if (!VALID_HANDOFF_REASON.includes(reason))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid handoff reason.', [{ field: 'reason', reason: `must_be_one_of_${VALID_HANDOFF_REASON.join('|')}` }]);

    const conv = _memConversations.find(c =>
      c.conversation_id === conversation_id && (c.tenant_id === tenantId || c.tenant_id === '_all')
    );
    if (!conv) return respondError(res, 404, 'NOT_FOUND', 'Conversation not found.');

    // Ownership guard — spec §3.4
    const isSupervisor = SUPERVISOR_ROLES.includes(userRole);
    if (!isSupervisor && conv.assigned_agent_id !== userId)
      return respondError(res, 403, 'FORBIDDEN', 'Only the assigned agent or a supervisor can hand off this conversation.');

    const ts = nowIso();
    const handoff = {
      handoff_id:       randomUUID(),
      conversation_id,
      tenant_id:        tenantId,
      from_agent_id:    conv.assigned_agent_id,
      to_agent_id,
      handoff_reason:   reason,
      note:             note || null,
      initiated_by:     userId,
      created_at:       ts,
    };
    _memHandoffs.push(handoff);

    // Update presence counts
    if (conv.assigned_agent_id) {
      const old = _memPresence.find(p => p.agent_id === conv.assigned_agent_id);
      if (old) old.open_conversation_count = Math.max(0, old.open_conversation_count - 1);
    }
    if (to_agent_id) {
      const newP = _memPresence.find(p => p.agent_id === to_agent_id);
      if (newP) newP.open_conversation_count += 1;
    }

    conv.assigned_agent_id = to_agent_id;
    conv.assigned_at       = to_agent_id ? ts : null;
    conv.assignment_reason = 'handoff';
    conv.handoff_count    += 1;
    conv.last_handoff_at   = ts;

    return res.status(201).json({ data: handoff, conversation: conv, meta: { request_id: req.request_id } });
  },
);

// POST /inbox/conversations/:id/messages — send message
router.post(
  '/conversations/:conversation_id/messages',
  requestValidationMiddleware(['text']),
  requireScopes([SCOPES.INBOX_WRITE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const userRole = req.auth.role || 'agent';
    const { conversation_id } = req.params;
    const { text } = req.body;

    const conv = _memConversations.find(c =>
      c.conversation_id === conversation_id && (c.tenant_id === tenantId || c.tenant_id === '_all')
    );
    if (!conv) return respondError(res, 404, 'NOT_FOUND', 'Conversation not found.');

    // Write access guard — spec §1.2: only assigned agent or supervisor
    const isSupervisor = SUPERVISOR_ROLES.includes(userRole);
    if (!isSupervisor && conv.assigned_agent_id !== userId)
      return respondError(res, 403, 'FORBIDDEN', 'Only the assigned agent or a supervisor can send messages on this conversation.');

    if (['resolved', 'closed'].includes(conv.state))
      return respondError(res, 409, 'CONFLICT', `Cannot send message on a ${conv.state} conversation.`);

    const ts = nowIso();
    const msg = {
      message_id:       randomUUID(),
      conversation_id,
      tenant_id:        tenantId,
      direction:        'outbound',
      text,
      occurred_at:      ts,
      sender_id:        userId,
      created_at:       ts,
    };

    if (!_memMessages[conversation_id]) _memMessages[conversation_id] = [];
    _memMessages[conversation_id].push(msg);

    conv.last_message_preview = text.length > 80 ? text.slice(0, 77) + '...' : text;
    conv.last_message_at      = ts;
    conv.unread_count         = 0;  // agent replied — reset unread

    return res.status(201).json({ data: msg, meta: { request_id: req.request_id } });
  },
);

// PATCH /inbox/presence — update own presence status
router.patch(
  '/presence',
  requestValidationMiddleware(['status']),
  requireScopes([SCOPES.INBOX_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { status } = req.body;

    if (!VALID_PRESENCE.includes(status))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid presence status.', [{ field: 'status', reason: `must_be_one_of_${VALID_PRESENCE.join('|')}` }]);

    const ts = nowIso();
    let presence = _memPresence.find(p => p.agent_id === userId);
    if (presence) {
      presence.status      = status;
      presence.updated_at  = ts;
      presence.last_seen_at = ts;
    } else {
      presence = { agent_id: userId, tenant_id: tenantId, status, open_conversation_count: 0, max_concurrent: 10, last_seen_at: ts, updated_at: ts };
      _memPresence.push(presence);
    }
    return respondSuccess(res, presence);
  },
);

// GET /inbox/presence — supervisor view of all agent statuses
router.get(
  '/presence',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_ADMIN]),
  async (req, res) => {
    return respondSuccess(res, _memPresence, { count: _memPresence.length });
  },
);

// GET /inbox/queues — list queues
router.get(
  '/queues',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_ADMIN]),
  async (req, res) => {
    return respondSuccess(res, _memQueues.filter(q => q.is_active), { count: _memQueues.filter(q => q.is_active).length });
  },
);

// POST /inbox/queues — create queue
router.post(
  '/queues',
  requestValidationMiddleware(['name']),
  requireScopes([SCOPES.INBOX_ADMIN]),
  async (req, res) => {
    const { name, routing_strategy = 'round_robin', auto_assign = true, skill_tags = [], team_id } = req.body;

    if (!VALID_ROUTING_STRAT.includes(routing_strategy))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid routing_strategy.', [{ field: 'routing_strategy', reason: `must_be_one_of_${VALID_ROUTING_STRAT.join('|')}` }]);

    const ts = nowIso();
    const queue = {
      queue_id:         randomUUID(),
      name,
      routing_strategy,
      auto_assign,
      skill_tags,
      team_id:          team_id || null,
      is_active:        true,
      created_at:       ts,
      updated_at:       ts,
    };
    _memQueues.push(queue);
    return res.status(201).json({ data: queue, meta: { request_id: req.request_id } });
  },
);

// PATCH /inbox/queues/:id
router.patch(
  '/queues/:queue_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_ADMIN]),
  async (req, res) => {
    const { queue_id } = req.params;
    const q = _memQueues.find(x => x.queue_id === queue_id);
    if (!q) return respondError(res, 404, 'NOT_FOUND', 'Queue not found.');

    const { name, routing_strategy, auto_assign, is_active } = req.body;
    if (name)              q.name              = name;
    if (routing_strategy)  q.routing_strategy  = routing_strategy;
    if (auto_assign !== undefined) q.auto_assign = auto_assign;
    if (is_active   !== undefined) q.is_active   = is_active;
    q.updated_at = nowIso();

    return respondSuccess(res, q);
  },
);

// GET /inbox/queues/:id/stats
router.get(
  '/queues/:queue_id/stats',
  requestValidationMiddleware(),
  requireScopes([SCOPES.INBOX_ADMIN]),
  async (req, res) => {
    const { queue_id } = req.params;
    const q = _memQueues.find(x => x.queue_id === queue_id);
    if (!q) return respondError(res, 404, 'NOT_FOUND', 'Queue not found.');

    const convs = _memConversations.filter(c => c.queue_id === queue_id && c.state === 'open');
    return respondSuccess(res, {
      queue_id,
      open_count:       convs.length,
      unassigned_count: convs.filter(c => !c.assigned_agent_id).length,
      assigned_count:   convs.filter(c =>  c.assigned_agent_id).length,
      avg_unread:       convs.length ? Math.round(convs.reduce((s, c) => s + (c.unread_count || 0), 0) / convs.length) : 0,
    });
  },
);

module.exports = router;
