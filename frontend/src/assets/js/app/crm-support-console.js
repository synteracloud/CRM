/* Pakistan CRM — Support Console (E-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var SLA_COLOR  = { breached:'danger', at_risk:'warning', healthy:'success' };
  var PRI_BADGE  = { critical:'<span class="badge bg-danger">Critical</span>', high:'<span class="badge bg-danger-subtle text-danger border border-danger-subtle">High</span>', medium:'<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Medium</span>', low:'<span class="badge bg-secondary-subtle text-secondary">Low</span>' };
  var STATUS_BADGE = { OPEN:'<span class="badge bg-primary">Open</span>', ASSIGNED:'<span class="badge bg-info text-white">Assigned</span>', IN_PROGRESS:'<span class="badge bg-warning text-dark">In Progress</span>', ESCALATED:'<span class="badge bg-danger">Escalated</span>', WAITING_ON_CUSTOMER:'<span class="badge bg-secondary">Waiting</span>', RESOLVED:'<span class="badge bg-success">Resolved</span>' };

  var DEMO_THREAD = [
    { from:'customer', text:'Hi, I cannot access the dashboard after the recent update.', time:'09:15' },
    { from:'agent',    text:'Thank you. Can you share the error message you see?', time:'09:22' },
    { from:'customer', text:'It shows "Session expired" but I just logged in.', time:'09:25' },
    { from:'system',   text:'Case CS-2026-001 assigned.', time:'09:30' },
  ];

  var ESC_CONTROLS = {
    healthy:  '<div class="small text-muted mb-2">SLA healthy — reassign if needed.</div><button class="btn btn-sm btn-outline-secondary">Reassign</button>',
    at_risk:  '<div class="small text-warning mb-2"><i class="fi fi-rr-alarm-clock me-1"></i>SLA at risk — proactive escalation needed.</div><div class="d-flex gap-2"><button class="btn btn-sm btn-warning">Raise Priority</button><button class="btn btn-sm btn-outline-secondary">Reassign</button></div>',
    breached: '<div class="small text-danger mb-2"><i class="fi fi-rr-triangle-warning me-1"></i>SLA BREACHED — immediate action required.</div><div class="d-flex gap-2"><button class="btn btn-sm btn-danger">Page On-Call</button><button class="btn btn-sm btn-outline-danger">Manager Review</button></div>',
  };

  function renderThread(cs) {
    document.getElementById('thread-case-num').textContent   = cs.case_number + ' — ' + cs.subject;
    document.getElementById('thread-status-badge').innerHTML = STATUS_BADGE[cs.status] || cs.status;
    document.getElementById('thread-compose').style.display  = '';

    var bodyEl = document.getElementById('thread-body');
    bodyEl.innerHTML = DEMO_THREAD.map(function (m) {
      if (m.from === 'system') return '<div class="text-center small text-muted my-2">' + m.text + '</div>';
      var isAgent = m.from === 'agent';
      return '<div class="d-flex ' + (isAgent ? 'justify-content-end' : '') + ' gap-2 mb-2">' +
        (!isAgent ? '<div class="avatar avatar-xs rounded-circle bg-primary-subtle"><i class="fi fi-rr-user text-primary small"></i></div>' : '') +
        '<div class="p-2 rounded ' + (isAgent ? 'bg-primary-subtle' : 'bg-light') + '" style="max-width:75%">' +
        '<div class="small fw-semibold text-muted mb-1">' + (isAgent ? 'Agent' : (cs.contact_name || 'Customer')) + '</div>' +
        '<div class="small">' + m.text + '</div>' +
        '<div class="text-end small text-muted mt-1">' + m.time + '</div></div></div>';
    }).join('');

    document.getElementById('ctx-customer').innerHTML =
      '<dl class="row mb-0 small">' +
      '<dt class="col-6 text-muted">Contact</dt><dd class="col-6 fw-semibold">' + (cs.contact_name || '—') + '</dd>' +
      '<dt class="col-6 text-muted">Account</dt><dd class="col-6">' + (cs.account_name || '—') + '</dd>' +
      '<dt class="col-6 text-muted">Open Cases</dt><dd class="col-6">1</dd>' +
      '<dt class="col-6 text-muted">Priority</dt><dd class="col-6">' + (PRI_BADGE[cs.priority] || cs.priority) + '</dd></dl>';

    document.getElementById('ctx-escalation').innerHTML = ESC_CONTROLS[cs.sla_state] || ESC_CONTROLS.healthy;
  }

  function render(cases) {
    var queueCases = cases
      .filter(function (c) { return c.status !== 'RESOLVED' && c.status !== 'CLOSED'; })
      .sort(function (a, b) { return new Date(a.response_due_at) - new Date(b.response_due_at); });

    document.getElementById('queue-count').textContent = queueCases.length;

    if (queueCases.length) {
      var top   = queueCases[0];
      var due   = new Date(top.response_due_at);
      var color = SLA_COLOR[top.sla_state] || 'secondary';
      document.getElementById('global-sla-timer').className =
        'd-flex align-items-center gap-2 bg-' + color + '-subtle rounded px-3 py-1 border border-' + color + '-subtle';
      document.getElementById('sla-timer-display').className = 'fw-bold text-' + color;
      document.getElementById('sla-timer-display').textContent = due.toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' });
    }

    var listEl = document.getElementById('sla-queue-list');
    listEl.innerHTML = queueCases.map(function (cs, i) {
      var color = SLA_COLOR[cs.sla_state] || 'secondary';
      var due   = new Date(cs.response_due_at);
      return '<div class="list-group-item list-group-item-action cursor-pointer border-start border-3 border-' + color + '" style="cursor:pointer" data-idx="' + i + '">' +
        '<div class="d-flex align-items-center gap-2">' +
        '<span class="fw-semibold small">' + cs.case_number + '</span>' + (PRI_BADGE[cs.priority] || '') +
        '</div>' +
        '<div class="text-truncate small text-muted">' + cs.subject + '</div>' +
        '<div class="small text-' + color + '">Due: ' + due.toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' }) + '</div></div>';
    }).join('');

    listEl.querySelectorAll('[data-idx]').forEach(function (el) {
      el.addEventListener('click', function () {
        listEl.querySelectorAll('[data-idx]').forEach(function (e) { e.classList.remove('active'); });
        this.classList.add('active');
        renderThread(queueCases[parseInt(this.dataset.idx)]);
      });
    });

    if (queueCases.length) {
      var first = listEl.querySelector('[data-idx="0"]');
      if (first) first.classList.add('active');
      renderThread(queueCases[0]);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.cases.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.cases && _d.cases.data) || []); });
    } else {
      render((_d && _d.cases && _d.cases.data) || []);
    }
  });

})();
