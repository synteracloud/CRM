/* Pakistan CRM — API Wrapper */
/* Flip DUMMY_MODE to false when backend is live */

/* Auto-detect production gateway URL based on hostname */
(function() {
  var host = window.location.hostname;
  var isLocal = host === 'localhost' || host === '127.0.0.1';
  window.__CRM_GATEWAY_URL = isLocal
    ? 'http://localhost:3000/api/v1'
    : 'https://crm-gateway-l3rm.onrender.com/api/v1';
})();

window.CRM_CONFIG = {
  DUMMY_MODE: false,
  BASE_URL: window.__CRM_GATEWAY_URL,
  tenantId: localStorage.getItem('crm_tenant_id') || '00000000-0000-0000-0000-000000000001',
  get token() { return localStorage.getItem('crm_token'); }
};

window.CRM_API = (function () {
  'use strict';

  const cfg = window.CRM_CONFIG;
  const d   = () => window.CRM_DUMMY;

  async function get(path, params) {
    const qs  = params ? '?' + new URLSearchParams(params).toString() : '';
    const res = await fetch(`${cfg.BASE_URL}${path}${qs}`, {
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId }
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  async function post(path, body) {
    const res = await fetch(`${cfg.BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  async function patch(path, body) {
    const res = await fetch(`${cfg.BASE_URL}${path}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  return {
    auth: {
      login:  (email, password) => cfg.DUMMY_MODE
        ? Promise.resolve({ data: { token: 'dummy-jwt-token', user: d().users.data[0] }, meta: {} })
        : post('/auth/sessions', { email, password }),
    },

    leads: {
      list:      (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().leads)                          : get('/leads', params),
      export:    ()         => cfg.DUMMY_MODE ? Promise.resolve({ data: [] })                       : fetch(`${cfg.BASE_URL}/leads/export`, { headers: { 'Authorization': `Bearer ${cfg.token}`, 'x-tenant-id': cfg.tenantId } }).then(r => r.blob()),
      import:    (body, ct) => cfg.DUMMY_MODE ? Promise.resolve({ data: { created: 0, skipped: 0, errors: [] } }) : fetch(`${cfg.BASE_URL}/leads/import`, { method: 'POST', headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': ct || 'application/json', 'x-tenant-id': cfg.tenantId }, body: typeof body === 'string' ? body : JSON.stringify(body) }).then(r => r.json()),
      get:       (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: d().leads.data.find(l => l.lead_id === id), meta: {} }) : get(`/leads/${id}`),
      create:    (body)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { lead_id: 'l-new-' + Date.now(), stage: 'new', created_at: new Date().toISOString(), ...body }, meta: {} }) : post('/leads', body),
      patch:     (id, body) => cfg.DUMMY_MODE ? Promise.resolve({ data: { ...d().leads.data.find(l => l.lead_id === id), ...body }, meta: {} }) : patch(`/leads/${id}`, body),
      nextAction:(id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { suggestion: 'Schedule a follow-up call within 48 hours to maintain momentum.', confidence: 0.82 }, meta: {} }) : get(`/leads/${id}/next-action`),
    },

    followups: {
      list:     (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().followups)                     : get('/followups', params),
      complete: (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { task_id: id, state: 'completed' }, meta: {} }) : post(`/followups/${id}/complete`, {}),
    },

    opportunities: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().opportunities)                  : get('/opportunities', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: d().opportunities.data.find(o => o.opportunity_id === id), meta: {} }) : get(`/opportunities/${id}`),
      create: (body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { opportunity_id: 'opp-new-' + Date.now(), stage: 'qualification', ...body }, meta: {} }) : post('/opportunities', body),
      patch:  (id, body)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { opportunity_id: id, ...body }, meta: {} }) : patch(`/opportunities/${id}`, body),
    },

    orgSettings: {
      get:    ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: { tenant_name:'Demo', timezone:'Asia/Karachi', date_format:'DD/MM/YYYY', language_default:'en', base_currency:'PKR', lakh_crore_notation:true, business_hours:{ start:'09:00', end:'19:00', days:['mon','tue','wed','thu','fri','sat'], timezone:'Asia/Karachi' } } })  : get('/org/settings'),
      update: (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { ...body } })                                                                                                                                          : patch('/org/settings', body),
    },

    roles: {
      list:   ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ role_id:'r-1', name:'sales_rep', label:'Sales Rep', is_system:true, active_user_count:2, permissions:[] }] })                                        : get('/roles'),
      create: (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { role_id:'r-new', ...body } })                                                                                                                         : post('/roles', body),
      update: (id, b)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { role_id:id, ...b } })                                                                                                                                 : patch(`/roles/${id}`, b),
    },

    notificationPreferences: {
      get:    ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: { events:{}, quiet_hours:{enabled:false,start:'22:00',end:'08:00',timezone:'Asia/Karachi'} } })                                                          : get('/notification-preferences'),
      update: (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { ...body } })                                                                                                                                           : patch('/notification-preferences', body),
    },

    featureFlags: {
      list:   ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [] })                                                                                                                                                    : get('/feature-flags'),
      update: (key, b) => cfg.DUMMY_MODE ? Promise.resolve({ data: { flag_key:key, ...b } })                                                                                                                               : patch(`/feature-flags/${key}`, b),
    },

    complianceSettings: {
      get:    ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: { retention_policies:{}, break_glass:{ require_two_approvers:true, ttl_hours:4 }, pdpa_mode:true } })                                                    : get('/compliance/settings'),
      update: (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { ...body } })                                                                                                                                           : patch('/compliance/settings', body),
    },

    privacy: {
      consentList:       ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [] })                                                                                                                                         : get('/privacy/consent'),
      consentGet:        (id)     => cfg.DUMMY_MODE ? Promise.resolve({ data: null })                                                                                                                                       : get(`/privacy/consent/${id}`),
      consentUpdate:     (id, b)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { contact_id:id, ...b } })                                                                                                                   : patch(`/privacy/consent/${id}`, b),
      dsrList:           ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [] })                                                                                                                                         : get('/privacy/requests'),
      dsrCreate:         (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { request_id:'dsr-new', status:'pending', ...body } })                                                                                       : post('/privacy/requests', body),
    },

    tenants: {
      current: ()      => cfg.DUMMY_MODE ? Promise.resolve({ data: { plan:'growth', plan_label:'Growth', seat_limit:25, seat_used:5, enabled_feature_count:4, entitlement_limit:10, entitlement_overage_count:0, entitlements_at_limit:0, active_sessions:2 } }) : get('/tenants/current'),
    },

    accounts: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().accounts || { data: [], meta: {} })                  : get('/accounts', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().accounts || { data: [] }).data.find(a => a.account_id === id), meta: {} }) : get(`/accounts/${id}`),
    },

    contacts: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().contacts)                       : get('/contacts', params),
      export: ()          => cfg.DUMMY_MODE ? Promise.resolve({ data: [] })                       : fetch(`${cfg.BASE_URL}/contacts/export`, { headers: { 'Authorization': `Bearer ${cfg.token}`, 'x-tenant-id': cfg.tenantId } }).then(r => r.blob()),
      import: (body, ct)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { created: 0, skipped: 0, errors: [] } }) : fetch(`${cfg.BASE_URL}/contacts/import`, { method: 'POST', headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': ct || 'application/json', 'x-tenant-id': cfg.tenantId }, body: typeof body === 'string' ? body : JSON.stringify(body) }).then(r => r.json()),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: d().contacts.data.find(c => c.contact_id === id), meta: {} }) : get(`/contacts/${id}`),
      create: (payload)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { contact_id: 'c-new-' + Date.now(), completeness_score: 50, created_at: new Date().toISOString(), ...payload }, meta: {} }) : post('/contacts', payload),
    },

    activities: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().activities)                     : get('/activities', params),
    },

    tasks: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().tasks)                          : get('/tasks', params),
      create: (body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { task_id: 't-new', ...body }, meta: {} }) : post('/tasks', body),
    },

    collections: {
      list:          (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().collections)                                                                            : get('/collections/invoices', params),
      recordPayment: (id, body) => cfg.DUMMY_MODE ? Promise.resolve({ data: { invoice_id: id, status: 'paid', ...body }, meta: {} })                               : post(`/collections/invoices/${id}/payments`, body),
      sendReminder:  (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { invoice_id: id, reminder_sent: true, sent_at: new Date().toISOString() }, meta: {} }) : post(`/collections/invoices/${id}/reminders`, {}),
    },

    orders: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().orders || { data: [], meta: {} })                    : get('/orders', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().orders || { data: [] }).data.find(o => o.order_id === id), meta: {} }) : get(`/orders/${id}`),
    },

    invoiceSummaries: {
      get:    (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: d().invoiceSummaries, meta: {} }) : get('/invoice-summaries', params),
      getById:(id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().invoices && d().invoices.data.find(i => i.invoice_id === id || i.invoice_number === id)) || null }) : get(`/invoice-summaries/${id}`),
    },

    subscriptions: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().subscriptions || { data: [], meta: {} })                     : get('/subscriptions', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().subscriptions || { data: [] }).data.find(s => s.subscription_id === id), meta: {} }) : get('/subscriptions', { id }),
    },

    audits: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: d().AUDIT_LOG || [], meta: {} })                         : get('/audits/events', params),
    },

    forecasts: {
      get:    (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: d().forecasts, meta: {} }) : get('/forecasts', params),
    },

    users: {
      list:   ()          => cfg.DUMMY_MODE ? Promise.resolve(d().users)                          : get('/users'),
    },

    priceBooks: {
      list:   ()          => cfg.DUMMY_MODE ? Promise.resolve(d().priceBooks)                      : get('/price-books'),
    },

    quotes: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().quotes)                          : get('/quotes', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: d().quotes.data.find(q => q.quote_id === id), meta: {} }) : get(`/quotes/${id}`),
      create: (body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { quote_id: 'q-new-' + Date.now(), status: 'draft', ...body }, meta: {} }) : post('/quotes', body),
    },

    cases: {
      list:        (params)        => cfg.DUMMY_MODE ? Promise.resolve(d().cases)                                                                                   : get('/cases', params),
      get:         (id)            => cfg.DUMMY_MODE ? Promise.resolve({ data: d().cases.data.find(c => c.case_id === id), meta: {} })                              : get(`/cases/${id}`),
      create:      (body)          => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: 'cs-new-' + Date.now(), status: 'OPEN', ...body }, meta: {} })            : post('/cases', body),
      assign:      (id, body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, ...body }, meta: {} })                                               : post(`/cases/${id}/assign`, body),
      addComment:  (id, body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { comment_id: 'cm-' + Date.now(), case_id: id, ...body }, meta: {} })               : post(`/cases/${id}/comments`, body),
      resolve:     (id, body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, status: 'RESOLVED', ...body }, meta: {} })                           : post(`/cases/${id}/resolve`, body),
      close:       (id, body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, status: 'CLOSED', ...body }, meta: {} })                             : post(`/cases/${id}/close`, body),
      reopen:      (id)            => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, status: 'OPEN' }, meta: {} })                                        : post(`/cases/${id}/reopen`, {}),
      escalate:    (id, body)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, status: 'ESCALATED', ...body }, meta: {} })                          : post(`/cases/${id}/escalate`, body),
      linkArticle: (id, articleId) => cfg.DUMMY_MODE ? Promise.resolve({ data: { case_id: id, article_id: articleId }, meta: {} })                                 : post(`/cases/${id}/link-article`, { article_id: articleId }),
    },

    knowledge: {
      list:    (params) => cfg.DUMMY_MODE ? Promise.resolve(d().knowledgeArticles || { data: [], meta: {} })                                                       : get('/knowledge/articles', params),
      get:     (id)     => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().knowledgeArticles || { data: [] }).data.find(a => a.article_id === id), meta: {} })       : get(`/knowledge/articles/${id}`),
      create:  (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { article_id: 'art-new-' + Date.now(), status: 'draft', ...body }, meta: {} })                 : post('/knowledge/articles', body),
      publish: (id)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { article_id: id, status: 'published' }, meta: {} })                                           : post(`/knowledge/articles/${id}/publish`, {}),
    },

    supportQueues: {
      list: () => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ queue_id: 'q-001', name: 'Tier 1 Support' }, { queue_id: 'q-002', name: 'Tier 2 Technical' }, { queue_id: 'q-003', name: 'Billing' }], meta: {} }) : get('/support/queues'),
    },

    inbox: {
      conversations: {
        list:        (params)      => cfg.DUMMY_MODE ? Promise.resolve(d().messageThreads || { data: [], meta: {} })                                                                     : get('/inbox/conversations', params),
        get:         (id)          => cfg.DUMMY_MODE ? Promise.resolve({ data: (d().messageThreads || { data: [] }).data.find(t => t.thread_id === id), meta: {} })                      : get(`/inbox/conversations/${id}`),
        claim:       (id)          => cfg.DUMMY_MODE ? Promise.resolve({ data: { conversation_id: id, assignment_reason: 'claimed' }, meta: {} })                                        : post(`/inbox/conversations/${id}/claim`, {}),
        handoff:     (id, body)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { handoff_id: 'hf-' + Date.now(), conversation_id: id, ...body }, meta: {} })                            : post(`/inbox/conversations/${id}/handoff`, body),
        sendMessage: (id, text)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { message_id: 'msg-' + Date.now(), direction: 'outbound', text }, meta: {} })                            : post(`/inbox/conversations/${id}/messages`, { text }),
      },
      presence: {
        list:   ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                                     : get('/inbox/presence'),
        update: (status) => cfg.DUMMY_MODE ? Promise.resolve({ data: { status }, meta: {} })                                                                                             : patch('/inbox/presence', { status }),  // uses PATCH via fetch directly
      },
      queues: {
        list:   ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ queue_id:'q-001', name:'General Support' }, { queue_id:'q-002', name:'Billing' }, { queue_id:'q-003', name:'VIP Enterprise' }], meta: {} }) : get('/inbox/queues'),
        stats:  (id)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { queue_id: id, open_count: 5, unassigned_count: 2, assigned_count: 3 }, meta: {} })                               : get(`/inbox/queues/${id}/stats`),
      },
    },

    workflows: {
      list:     (params)   => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ workflow_id:'wf-001', name:'Lead Follow-up Enforcement', status:'active', workflow_key:'lead_followup_enforcement' }, { workflow_id:'wf-002', name:'Collections Auto-Reminder', status:'active', workflow_key:'collections_reminder' }], meta: {} }) : get('/workflows', params),
      get:      (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { workflow_id: id }, meta: {} })                                                                                        : get(`/workflows/${id}`),
      create:   (body)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { workflow_id: 'wf-new-' + Date.now(), status: 'draft', ...body }, meta: {} })                                          : post('/workflows', body),
      publish:  (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { workflow_id: id, status: 'active' }, meta: {} })                                                                      : post(`/workflows/${id}/publish`, {}),
      simulate: (id, payload) => cfg.DUMMY_MODE ? Promise.resolve({ data: { workflow_id: id, simulated: true, steps: [] }, meta: {} })                                                        : post(`/workflows/${id}/simulate`, { trigger_payload: payload || {} }),
      stats:    (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { workflow_id: id, total_runs: 8, success_rate: 62 }, meta: {} })                                                       : get(`/workflows/${id}/stats`),
      runs: {
        list:   (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().workflowExecutions)                                                                                                        : get('/workflows/runs', params),
        get:    (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: d().workflowExecutions.data.find(e => e.execution_id === id), meta: {} })                                               : get(`/workflows/runs/${id}`),
        retry:  (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { execution_id: 'exec-retry-' + Date.now(), status: 'running' }, meta: {} })                                           : post(`/workflows/runs/${id}/retry`, {}),
        cancel: (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { execution_id: id, status: 'cancelled' }, meta: {} })                                                                 : post(`/workflows/runs/${id}/cancel`, {}),
      },
    },

    partners: {
      list:             (params)             => cfg.DUMMY_MODE ? Promise.resolve(d().partners)                                                                                                                         : get('/partners', params),
      get:              (id)                 => cfg.DUMMY_MODE ? Promise.resolve({ data: d().partners.data.find(p => p.partner_id === id), meta: {} })                                                                : get(`/partners/${id}`),
      create:           (body)               => cfg.DUMMY_MODE ? Promise.resolve({ data: { partner_id: 'p-new-' + Date.now(), status: 'active', ...body }, meta: {} })                                               : post('/partners', body),
      commissions:      (id)                 => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                                             : get(`/partners/${id}/commissions`),
      approveCommission:(partnerId, commId)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { commission_id: commId, status: 'approved' }, meta: {} })                                                                  : post(`/partners/${partnerId}/commissions/${commId}/approve`, {}),
      payCommission:    (partnerId, commId, ref) => cfg.DUMMY_MODE ? Promise.resolve({ data: { commission_id: commId, status: 'paid' }, meta: {} })                                                                  : post(`/partners/${partnerId}/commissions/${commId}/pay`, { payment_reference: ref }),
      dealRegistrations:(id)                 => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                                             : get(`/partners/${id}/deal-registrations`),
      registerDeal:     (id, body)           => cfg.DUMMY_MODE ? Promise.resolve({ data: { registration_id: 'reg-' + Date.now(), status: 'submitted', ...body }, meta: {} })                                        : post(`/partners/${id}/deal-registrations`, body),
      approveDealReg:   (regId)              => cfg.DUMMY_MODE ? Promise.resolve({ data: { registration_id: regId, status: 'approved' }, meta: {} })                                                                 : post(`/deal-registrations/${regId}/approve`, {}),
      rejectDealReg:    (regId, reason)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { registration_id: regId, status: 'rejected' }, meta: {} })                                                                 : post(`/deal-registrations/${regId}/reject`, { rejection_reason: reason }),
    },

    campaigns: {
      list:       (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().campaigns)                                                                                                                       : get('/campaigns', params),
      get:        (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: d().campaigns.data.find(c => c.campaign_id === id), meta: {} })                                                              : get(`/campaigns/${id}`),
      create:     (body)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { campaign_id: 'cmp-new-' + Date.now(), status: 'draft', ...body }, meta: {} })                                              : post('/campaigns', body),
      activate:   (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { campaign_id: id, status: 'active' }, meta: {} })                                                                          : post(`/campaigns/${id}/activate`, {}),
      pause:      (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { campaign_id: id, status: 'paused' }, meta: {} })                                                                          : post(`/campaigns/${id}/pause`, {}),
      resume:     (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { campaign_id: id, status: 'active' }, meta: {} })                                                                          : post(`/campaigns/${id}/resume`, {}),
      cancel:     (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { campaign_id: id, status: 'cancelled' }, meta: {} })                                                                       : post(`/campaigns/${id}/cancel`, {}),
      sends:      (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                                             : get(`/campaigns/${id}/sends`),
      conversions:(id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                                             : get(`/campaigns/${id}/conversions`),
    },

    segments: {
      list:     (params)  => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ segment_id:'seg-001', name:'All Active Leads', estimated_size:847 }, { segment_id:'seg-002', name:'SMB Prospects', estimated_size:312 }], meta: {} }) : get('/segments', params),
      get:      (id)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { segment_id: id }, meta: {} })                                                                                                : get(`/segments/${id}`),
      create:   (body)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { segment_id: 'seg-new-' + Date.now(), ...body }, meta: {} })                                                                   : post('/segments', body),
      validate: (id)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { segment_id: id, estimated_size: 250, sample: [] }, meta: {} })                                                               : post(`/segments/${id}/validate`, {}),
    },

    templates: {
      list:   (params)  => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ template_id:'tpl-001', name:'Eid Mubarak Offer', channel:'whatsapp_broadcast' }, { template_id:'tpl-002', name:'Q2 Product Launch Email', channel:'email' }], meta: {} }) : get('/templates', params),
      get:    (id)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { template_id: id }, meta: {} })                                                                                                 : get(`/templates/${id}`),
      create: (body)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { template_id: 'tpl-new-' + Date.now(), ...body }, meta: {} })                                                                   : post('/templates', body),
    },

    ai: {
      scores: {
        list:      (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                  : get('/ai/scores/leads', params),
        get:       (leadId)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { lead_id: leadId, score: 0, score_band: 'cold' }, meta: {} })                                  : get(`/ai/scores/leads/${leadId}`),
        recompute: (leadId)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { lead_id: leadId, is_stale: false, computed_at: new Date().toISOString() }, meta: {} })        : post(`/ai/scores/leads/${leadId}/recompute`, {}),
      },
      predictions: {
        churn:     (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                  : get('/ai/predictions/churn', params),
        churnById: (accountId) => cfg.DUMMY_MODE ? Promise.resolve({ data: { account_id: accountId, risk_band: 'low' }, meta: {} })                                       : get(`/ai/predictions/churn/${accountId}`),
      },
      estimates: {
        clv:       (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                  : get('/ai/estimates/clv', params),
        clvById:   (accountId) => cfg.DUMMY_MODE ? Promise.resolve({ data: { account_id: accountId, estimated_clv: 0 }, meta: {} })                                       : get(`/ai/estimates/clv/${accountId}`),
      },
      copilot: {
        suggestions: (params)  => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                  : get('/ai/copilot/suggestions', params),
        dismiss:   (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: { suggestion_id: id, is_dismissed: true }, meta: {} })                                          : post(`/ai/copilot/suggestions/${id}/dismiss`, {}),
        action:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: { suggestion_id: id, is_actioned: true }, meta: {} })                                           : post(`/ai/copilot/suggestions/${id}/action`, {}),
        query:     (text)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { intent: 'oob', summary: 'DUMMY_MODE active — live query disabled', records: [] }, meta: {} }) : post('/ai/copilot/query', { query: text }),
      },
      models: {
        list:      ()          => cfg.DUMMY_MODE ? Promise.resolve({ data: [], meta: {} })                                                                                  : get('/ai/models'),
        get:       (key)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { model_key: key }, meta: {} })                                                                 : get(`/ai/models/${key}`),
      },
    },

    billing: {
      plan:         ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: { plan_code:'plan_growth', plan_label:'Growth', billing_cycle:'annual', renewal_date:'2027-01-01', seat_limit:20, seat_used:5, is_trial:false, subscription_status:'active', monthly_price_pkr:5999, annual_price_pkr:61189 } }) : get('/billing/subscription'),
      invoices:     ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ invoice_number:'BILL-2026-001', period:'Jan 2026 – Dec 2026', amount_pkr:61189, status:'paid' },{ invoice_number:'BILL-2025-001', period:'Jan 2025 – Dec 2025', amount_pkr:59988, status:'paid' }] }) : get('/billing/invoices'),
      plans:        ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [] }) : get('/billing/plans'),
      entitlements: ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [] }) : get('/billing/entitlements'),
      upgrade:      (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { upgraded: true } })           : post('/billing/subscription/upgrade', body),
      downgrade:    (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { downgrade_scheduled: true } }) : post('/billing/subscription/downgrade', body),
    },

    integrations: {
      list:   ()             => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ provider:'whatsapp', status:'connected' },{ provider:'email', status:'connected' },{ provider:'sms', status:'disconnected' },{ provider:'push', status:'not_configured' }] }) : get('/integrations'),
      update: (provider, b)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { provider, ...b } })                                                                                     : patch(`/integrations/${provider}`, b),
      test:   (provider)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { ok: true, latency_ms: 42, message: 'Connection successful' } })                                         : post(`/integrations/${provider}/test`, {}),
    },

    governance: {
      classification: ()     => cfg.DUMMY_MODE ? Promise.resolve({ data: [] }) : get('/governance/classification'),
      retention:      ()     => cfg.DUMMY_MODE ? Promise.resolve({ data: [] }) : get('/governance/retention'),
      sarList:        ()     => cfg.DUMMY_MODE ? Promise.resolve({ data: [] }) : get('/governance/sar'),
      sarCreate:      (body) => cfg.DUMMY_MODE ? Promise.resolve({ data: { request_id:'sar-new', status:'pending', ...body } }) : post('/governance/sar', body),
    },

    reports: {
      list:    ()       => cfg.DUMMY_MODE ? Promise.resolve({ data: [{ report_id:'rpt-001', name:'Monthly Pipeline Summary', metrics:['weighted_pipeline'], chart_type:'bar' }] }) : get('/reports/definitions'),
      create:  (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { report_id:'rpt-new-' + Date.now(), ...body } })                                                              : post('/reports/definitions', body),
      execute: (body)   => cfg.DUMMY_MODE ? Promise.resolve({ data: { metric_key: body.metric_key, series: ['Dec','Jan','Feb','Mar','Apr','May'].map((l,i) => ({ label:l, value:i*100000 })), currency:null } }) : post('/reports/execute', body),
    },

    communications: {
      engagement: () => cfg.DUMMY_MODE ? Promise.resolve({ data: { delivery_rate:91, open_rate:57, reply_rate:18, failed_delivery_count:34, low_delivery_channel_count:0, whatsapp_opted_in:843, whatsapp_opt_out_rate:2.1, delivery_open_click_reply_rate:[{ channel:'whatsapp_broadcast', label:'Eid Offer', delivery:94, open:68, reply:22 },{ channel:'email', label:'Q2 Launch', delivery:88, open:42, reply:8 },{ channel:'whatsapp_broadcast', label:'Re-engage', delivery:91, open:55, reply:18 },{ channel:'email', label:'Enterprise', delivery:97, open:51, reply:12 },{ channel:'whatsapp_broadcast', label:'Ramadan', delivery:89, open:61, reply:19 }] } }) : get('/communications/engagement'),
    },

    territories: {
      list:        (params)       => cfg.DUMMY_MODE ? Promise.resolve(d().territories)                                                                                                              : get('/territories', params),
      get:         (id)           => cfg.DUMMY_MODE ? Promise.resolve({ data: d().territories.data.find(t => t.territory_id === id), meta: {} })                                                    : get(`/territories/${id}`),
      create:      (body)         => cfg.DUMMY_MODE ? Promise.resolve({ data: { territory_id: 't-new-' + Date.now(), is_active: true, ...body }, meta: {} })                                        : post('/territories', body),
      update:      (id, body)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { territory_id: id, ...body }, meta: {} })                                                                            : patch(`/territories/${id}`, body),  // uses fetch PATCH via crm-api
      addRule:     (id, body)     => cfg.DUMMY_MODE ? Promise.resolve({ data: { rule_id: 'r-new-' + Date.now(), territory_id: id, ...body }, meta: {} })                                           : post(`/territories/${id}/rules`, body),
      evaluate:    (subject)      => cfg.DUMMY_MODE ? Promise.resolve({ data: { winner: d().territories.data[0], candidates: d().territories.data, reason: 'single_match', matched_count: 1 }, meta: {} }) : post('/territories/assignments/evaluate', { subject }),
      performance: (id)           => cfg.DUMMY_MODE ? Promise.resolve({ data: { territory_id: id, open_leads: 38, conversion_rate: 21, collection_rate: 71 }, meta: {} })                          : get(`/territories/${id}/performance`),
    },
  };
})();

// Auto-seed dev JWT when not in dummy mode and no token stored.
// First page load may show empty data; one refresh is enough after the token is cached.
(function () {
  if (window.CRM_CONFIG && !window.CRM_CONFIG.DUMMY_MODE && !localStorage.getItem('crm_token')) {
    fetch('http://localhost:3000/dev-token')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (r) {
        if (r && r.data && r.data.token) {
          localStorage.setItem('crm_token', r.data.token);
          localStorage.setItem('crm_tenant_id', r.data.tenant_id);
          window.CRM_CONFIG.tenantId = r.data.tenant_id;
        }
      })
      .catch(function () {});
  }
}());
