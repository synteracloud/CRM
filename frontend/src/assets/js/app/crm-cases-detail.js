/* Pakistan CRM — Case Detail (C-05) */

(function () {
  'use strict';

  var cfg   = window.CRM_CONFIG;
  var _d    = window.CRM_DUMMY;
  var caseId = new URLSearchParams(window.location.search).get('id') || null;

  var SLA_BADGE    = { breached:'<span class="badge bg-danger">SLA Breached</span>', at_risk:'<span class="badge bg-warning text-dark">SLA At Risk</span>', healthy:'<span class="badge bg-success">SLA Healthy</span>' };
  var PRI_BADGE    = { critical:'<span class="badge bg-danger">Critical</span>', high:'<span class="badge bg-danger-subtle text-danger border border-danger-subtle">High</span>', medium:'<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Medium</span>', low:'<span class="badge bg-secondary-subtle text-secondary">Low</span>' };
  var STATUS_BADGE = { OPEN:'<span class="badge bg-primary">Open</span>', ASSIGNED:'<span class="badge bg-info text-white">Assigned</span>', IN_PROGRESS:'<span class="badge bg-warning text-dark">In Progress</span>', WAITING_ON_CUSTOMER:'<span class="badge bg-secondary">Waiting</span>', RESOLVED:'<span class="badge bg-success">Resolved</span>', ESCALATED:'<span class="badge bg-danger">Escalated</span>', CLOSED:'<span class="badge bg-dark text-white">Closed</span>' };

  var DEMO_MESSAGES = [
    { from:'customer', text:'Hi, I cannot access the CRM dashboard after the recent update.', time:'09:15' },
    { from:'agent',    text:'Thank you for reaching out. Can you please share the error message you see?', time:'09:22' },
    { from:'customer', text:'It shows "Session expired" but I just logged in.', time:'09:25' },
    { from:'system',   text:'Case assigned to Ahmed Raza.', time:'09:30' },
  ];

  function render(cs, allCases) {
    if (!cs) {
      if (_d && _d.cases && _d.cases.data[0]) render(_d.cases.data[0], _d.cases.data);
      return;
    }

    document.getElementById('bc-case-num').textContent  = cs.case_number;
    document.getElementById('case-number').textContent  = cs.case_number;
    document.getElementById('case-subject').textContent = cs.subject;
    document.getElementById('status-badge').innerHTML   = STATUS_BADGE[cs.status] || cs.status;
    document.getElementById('sla-badge').innerHTML      = SLA_BADGE[cs.sla_state] || cs.sla_state;
    document.getElementById('priority-badge').innerHTML = PRI_BADGE[cs.priority] || cs.priority;
    document.getElementById('contact-name').textContent = cs.contact_name || '—';
    document.getElementById('account-name').textContent = cs.account_name || '—';
    document.getElementById('case-queue').textContent   = cs.queue || '—';

    var timerBox = document.getElementById('sla-timer-box');
    var timerEl  = document.getElementById('sla-timer');
    if (cs.response_due_at) {
      var due = new Date(cs.response_due_at);
      var overdue = due < new Date();
      timerEl.textContent = due.toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' }) +
        ', ' + due.toLocaleDateString('en-PK', { day:'2-digit', month:'short' });
      if (overdue || cs.sla_state === 'breached') {
        timerBox.classList.add('border-danger', 'text-danger');
        timerEl.classList.add('text-danger');
      } else if (cs.sla_state === 'at_risk') {
        timerBox.classList.add('border-warning');
        timerEl.classList.add('text-warning');
      }
    }

    var btnClaim   = document.getElementById('btn-claim');
    var btnResolve = document.getElementById('btn-resolve');

    if (cs.status === 'OPEN' && !cs.assigned_to_id && btnClaim) btnClaim.style.display = '';
    if (cs.status !== 'RESOLVED' && btnResolve) btnResolve.style.display = '';

    if (btnClaim) {
      btnClaim.addEventListener('click', function () {
        btnClaim.disabled = true;
        window.CRM_API.cases.assign(cs.case_id, { assigned_to: 'current-user' })
          .then(function () { btnClaim.textContent = 'Claimed'; })
          .catch(function () { btnClaim.disabled = false; });
      });
    }
    if (btnResolve) {
      btnResolve.addEventListener('click', function () {
        var note = window.prompt('Resolution note (required):');
        if (!note) return;
        btnResolve.disabled = true;
        window.CRM_API.cases.resolve(cs.case_id, { resolution_note: note })
          .then(function () { location.reload(); })
          .catch(function () { btnResolve.disabled = false; });
      });
    }

    var threadEl = document.getElementById('conversation-thread');
    if (threadEl) {
      threadEl.innerHTML = DEMO_MESSAGES.map(function (m) {
        var isAgent = m.from === 'agent', isSystem = m.from === 'system';
        if (isSystem) return '<div class="text-center small text-muted my-1">' + m.text + '</div>';
        return '<div class="d-flex ' + (isAgent ? 'justify-content-end' : '') + ' gap-2">' +
          (!isAgent ? '<div class="avatar avatar-xs rounded-circle bg-primary-subtle"><i class="fi fi-rr-user text-primary small"></i></div>' : '') +
          '<div class="p-2 rounded ' + (isAgent ? 'bg-primary-subtle' : 'bg-light') + '" style="max-width:75%">' +
          '<div class="small fw-semibold text-muted mb-1">' + (m.from === 'customer' ? (cs.contact_name || 'Customer') : 'Agent') + '</div>' +
          '<div>' + m.text + '</div>' +
          '<div class="text-end small text-muted mt-1">' + m.time + '</div></div></div>';
      }).join('');
    }

    var fieldsEl = document.getElementById('case-fields-content');
    if (fieldsEl) {
      fieldsEl.innerHTML =
        '<div class="col-sm-6"><label class="small text-muted">Category</label><p class="fw-semibold">' + (cs.category || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Source</label><p class="fw-semibold">' + (cs.source || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Priority</label><p>' + (PRI_BADGE[cs.priority] || cs.priority) + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Queue</label><p class="fw-semibold">' + (cs.queue || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Created At</label><p class="fw-semibold">' + (cs.created_at ? new Date(cs.created_at).toLocaleDateString('en-PK') : '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">SLA Resolution Due</label><p class="fw-semibold text-danger">' + (cs.sla_resolution_due_at ? new Date(cs.sla_resolution_due_at).toLocaleDateString('en-PK') : '—') + '</p></div>';
    }

    var ctxCust = document.getElementById('context-customer');
    if (ctxCust) {
      ctxCust.innerHTML = '<dl class="row mb-0 small">' +
        '<dt class="col-5 text-muted">Contact</dt><dd class="col-7 fw-semibold">' + (cs.contact_name || '—') + '</dd>' +
        '<dt class="col-5 text-muted">Account</dt><dd class="col-7">' + (cs.account_name || '—') + '</dd>' +
        '<dt class="col-5 text-muted">Open Cases</dt><dd class="col-7">1</dd>' +
        '<dt class="col-5 text-muted">Plan Tier</dt><dd class="col-7">Growth</dd></dl>';
    }

    var escMap = {
      healthy:  '<div class="small text-muted">SLA healthy — ownership correction only.</div><button class="btn btn-sm btn-outline-secondary mt-2">Reassign</button>',
      at_risk:  '<div class="small text-warning mb-2"><i class="fi fi-rr-alarm-clock me-1"></i>SLA at risk — proactive action required.</div><div class="d-flex gap-2"><button class="btn btn-sm btn-warning">Raise Priority</button><button class="btn btn-sm btn-outline-secondary">Reassign</button></div>',
      breached: '<div class="small text-danger mb-2"><i class="fi fi-rr-triangle-warning me-1"></i>SLA breached — immediate escalation required.</div><div class="d-flex gap-2"><button class="btn btn-sm btn-danger">Page On-Call</button><button class="btn btn-sm btn-outline-secondary">Reassign</button></div>',
    };
    var ctxEsc = document.getElementById('context-escalation');
    if (ctxEsc) ctxEsc.innerHTML = escMap[cs.sla_state] || escMap.healthy;

    var related = (allCases || []).filter(function (c) { return c.account_id === cs.account_id && c.case_id !== cs.case_id; }).slice(0, 3);
    var relEl   = document.getElementById('related-cases');
    if (relEl) {
      relEl.innerHTML = related.length ? related.map(function (c) {
        return '<a href="app/cases-detail.html?id=' + (c.case_id || c.case_number) + '" class="list-group-item list-group-item-action d-flex align-items-center gap-2 py-2">' +
          '<span class="fw-semibold small">' + c.case_number + '</span>' +
          '<span class="text-truncate flex-grow-1 small text-muted">' + c.subject + '</span>' +
          (STATUS_BADGE[c.status] || c.status) + '</a>';
      }).join('') : '<div class="p-3 small text-muted">No related cases.</div>';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      var caseProm = caseId
        ? window.CRM_API.cases.get(caseId).catch(function () { return { data: null }; })
        : Promise.resolve({ data: null });
      Promise.all([
        caseProm,
        window.CRM_API.cases.list({ limit: 50 }).catch(function () { return { data: [] }; })
      ]).then(function (results) {
        var cs  = results[0].data || (results[1].data && results[1].data[0]);
        render(cs, results[1].data || []);
      });
    } else {
      if (!_d) return;
      var cs = caseId
        ? (_d.cases.data.filter(function (c) { return c.case_id === caseId || c.case_number === caseId; })[0] || _d.cases.data[0])
        : _d.cases.data[0];
      render(cs, _d.cases.data);
    }
  });

})();
