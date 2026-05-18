/* Pakistan CRM — API Wrapper */
/* Flip DUMMY_MODE to false when backend is live */

window.CRM_CONFIG = {
  DUMMY_MODE: true,
  BASE_URL: 'http://localhost:3000/api/v1',
  get token() { return localStorage.getItem('crm_token'); }
};

window.CRM_API = (function () {
  'use strict';

  const cfg = window.CRM_CONFIG;
  const d   = () => window.CRM_DUMMY;

  async function get(path, params) {
    const qs  = params ? '?' + new URLSearchParams(params).toString() : '';
    const res = await fetch(`${cfg.BASE_URL}${path}${qs}`, {
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  async function post(path, body) {
    const res = await fetch(`${cfg.BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  async function patch(path, body) {
    const res = await fetch(`${cfg.BASE_URL}${path}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${cfg.token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw await res.json();
    return res.json();
  }

  return {
    auth: {
      login:  (email, password) => cfg.DUMMY_MODE
        ? Promise.resolve({ data: { token: 'dummy-jwt-token', user: d().users.data[0] }, meta: {} })
        : post('/auth/login', { email, password }),
    },

    leads: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().leads)                          : get('/leads', params),
      get:    (id)        => cfg.DUMMY_MODE ? Promise.resolve({ data: d().leads.data.find(l => l.lead_id === id), meta: {} }) : get(`/leads/${id}`),
      patch:  (id, body)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { ...d().leads.data.find(l => l.lead_id === id), ...body }, meta: {} }) : patch(`/leads/${id}`, body),
      nextAction: (id)    => cfg.DUMMY_MODE ? Promise.resolve({ data: { suggestion: 'Schedule a follow-up call within 48 hours to maintain momentum.', confidence: 0.82 }, meta: {} }) : get(`/leads/${id}/next-action`),
    },

    followups: {
      list:     (params)   => cfg.DUMMY_MODE ? Promise.resolve(d().followups)                     : get('/followups', params),
      complete: (id)       => cfg.DUMMY_MODE ? Promise.resolve({ data: { followup_id: id, state: 'completed' }, meta: {} }) : patch(`/followups/${id}`, { state: 'completed' }),
    },

    opportunities: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().opportunities)                  : get('/opportunities', params),
      patch:  (id, body)  => cfg.DUMMY_MODE ? Promise.resolve({ data: { opp_id: id, ...body }, meta: {} }) : patch(`/opportunities/${id}`, body),
    },

    contacts: {
      list:   (params)    => cfg.DUMMY_MODE ? Promise.resolve(d().contacts)                       : get('/contacts', params),
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

    invoiceSummaries: {
      get:    (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: d().invoiceSummaries, meta: {} }) : get('/invoice-summaries', params),
    },

    forecasts: {
      get:    (params)    => cfg.DUMMY_MODE ? Promise.resolve({ data: d().forecasts, meta: {} }) : get('/forecasts', params),
    },

    users: {
      list:   ()          => cfg.DUMMY_MODE ? Promise.resolve(d().users)                          : get('/users'),
    },
  };
})();
