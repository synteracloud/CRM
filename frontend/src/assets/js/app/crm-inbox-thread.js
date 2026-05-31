/* Pakistan CRM — Conversation Thread (L-02) */

(function () {
  'use strict';

  var cfg    = window.CRM_CONFIG;
  var _d     = window.CRM_DUMMY;
  var convId = new URLSearchParams(window.location.search).get('id') || null;

  var INTENT_LABEL = {
    payment_query:      'Payment Query',
    follow_up_response: 'Follow-up Response',
    lead_inquiry:       'Lead Inquiry',
    support_request:    'Support Request',
    out_of_scope:       'Out of Scope',
  };
  var INTENT_ACTIONS = {
    payment_query:      [{ label:'View Invoice',  href:'app/invoices.html' },     { label:'Record Payment', href:'app/collections.html' }],
    follow_up_response: [{ label:'Open Lead',     href:'app/leads-detail.html' }, { label:'Log Follow-up',  href:'app/followups.html' }],
    lead_inquiry:       [{ label:'Create Lead',   href:'app/lead-new.html' },     { label:'View Leads',     href:'app/leads.html' }],
    support_request:    [{ label:'Open New Case', href:'app/case-new.html' },     { label:'View Cases',     href:'app/cases.html' }],
  };

  var DEMO_MSGS = [
    { dir:'in',    text:'Assalamu Alaikum! Sir, mera order deliver kab hoga?', time:'9:30 AM', ticks:'✓✓' },
    { dir:'system',text:'Intent detected: Payment Query' },
    { dir:'out',   text:'Wa Alaikum Assalam Tariq bhai! Let me check your order status right away.', time:'9:31 AM', ticks:'✓✓ 🔵' },
    { dir:'in',    text:'Sir, order delivery kab hogi? Advance payment kar di hai.', time:'9:45 AM', ticks:'✓' },
    { dir:'out',   text:'I can see your order ORD-2026-001 is marked as delivered. Please check with the delivery team at your end.', time:'9:47 AM', ticks:'✓✓' },
  ];

  var CH_ICON = { whatsapp:'<i class="fi fi-brands-whatsapp" style="color:#25D366"></i>', email:'<i class="fi fi-rr-envelope text-primary"></i>', sms:'<i class="fi fi-rr-comment text-muted"></i>' };

  function render(thread) {
    if (!thread) return;

    var cid = thread.conversation_id || thread.thread_id;
    document.getElementById('bc-contact').textContent = thread.contact_name || '—';

    var agentName = thread.assigned_agent_id || 'Unassigned';
    if (_d && _d.userMap && thread.assigned_agent_id) {
      agentName = (_d.userMap[thread.assigned_agent_id] || {}).display_name || thread.assigned_agent_id;
    }

    document.getElementById('ctx-info').innerHTML =
      '<div class="fw-semibold">' + (thread.contact_name || '—') + ' ' + (CH_ICON[thread.channel] || '') + '</div>' +
      '<div class="small text-muted">' + (thread.contact_phone || thread.contact_phone_e164 || '') + ' · Agent: ' + agentName + '</div>';

    document.getElementById('ctx-actions').innerHTML =
      '<button class="btn btn-sm btn-outline-secondary" id="btn-reassign" data-conv="' + cid + '">Reassign</button>' +
      '<button class="btn btn-sm btn-outline-danger ms-2" id="btn-close-conv" data-conv="' + cid + '">Close</button>';

    document.getElementById('btn-reassign').addEventListener('click', function () {
      var toAgent = window.prompt('Reassign to agent ID:');
      if (!toAgent) return;
      this.disabled = true;
      var btn = this;
      window.CRM_API.inbox.conversations.handoff(this.dataset.conv, { to_agent_id: toAgent, reason:'manual' })
        .then(function () { location.reload(); })
        .catch(function () { btn.disabled = false; });
    });
    document.getElementById('btn-close-conv').addEventListener('click', function () {
      if (!window.confirm('Close this conversation?')) return;
      this.disabled = true;
      var btn = this;
      window.CRM_API.inbox.conversations.handoff(this.dataset.conv, { to_agent_id: null, reason:'closed' })
        .then(function () { history.back(); })
        .catch(function () { btn.disabled = false; });
    });

    /* Messages */
    var msgs   = (cfg && !cfg.DUMMY_MODE && thread.messages) ? thread.messages : DEMO_MSGS;
    var msgsEl = document.getElementById('messages');
    msgsEl.innerHTML = msgs.map(function (m) {
      if (m.dir === 'system') {
        return '<div class="text-center small text-muted my-3"><span class="bg-light border rounded px-2 py-1">' + m.text + '</span></div>';
      }
      var isOut = m.dir === 'out';
      return '<div class="d-flex ' + (isOut ? 'justify-content-end' : '') + ' mb-3">' +
        '<div class="msg-bubble p-2 ' + (isOut ? 'msg-out' : 'msg-in') + '">' +
          '<div class="small">' + m.text + '</div>' +
          '<div class="d-flex justify-content-end gap-1 mt-1">' +
            '<span style="font-size:.65rem" class="text-muted">' + (m.time || m.created_at || '') + '</span>' +
            (m.ticks ? '<span style="font-size:.7rem">' + m.ticks + '</span>' : '') +
          '</div>' +
        '</div></div>';
    }).join('');
    msgsEl.scrollTop = msgsEl.scrollHeight;

    /* Customer context */
    var contact = {};
    if (_d && _d.contacts) {
      contact = _d.contacts.data.find(function (c) { return c.phone_e164 === (thread.contact_phone || thread.contact_phone_e164); }) || {};
    }
    document.getElementById('customer-ctx').innerHTML =
      '<dl class="row mb-0 small">' +
        '<dt class="col-6 text-muted">Contact</dt><dd class="col-6 fw-semibold">' + (contact.display_name || thread.contact_name || '—') + '</dd>' +
        '<dt class="col-6 text-muted">Account</dt><dd class="col-6">' + (contact.account_name || '—') + '</dd>' +
        '<dt class="col-6 text-muted">Open Cases</dt><dd class="col-6">' + (contact.open_cases || 0) + '</dd>' +
        '<dt class="col-6 text-muted">Plan Tier</dt><dd class="col-6">Growth</dd>' +
      '</dl>' +
      '<a href="app/contacts-detail.html' + (contact.contact_id ? '?id=' + contact.contact_id : '') + '" class="btn btn-xs btn-outline-primary mt-2">Open 360 View</a>';

    /* Intent */
    var intentLabel = INTENT_LABEL[thread.intent] || (thread.intent || 'Unknown');
    document.getElementById('intent-ctx').innerHTML =
      '<div class="d-flex align-items-center gap-2 mb-2"><span class="badge bg-warning-subtle text-warning border border-warning-subtle">' + intentLabel + '</span></div>' +
      '<div class="small text-muted">Classifier confidence: <strong>87%</strong></div>' +
      '<div class="small text-muted mt-1">Detected from latest inbound message</div>';

    /* Suggested actions */
    var actions = INTENT_ACTIONS[thread.intent] || [];
    document.getElementById('action-ctx').innerHTML = actions.length
      ? actions.map(function (a) { return '<a href="' + a.href + '" class="btn btn-sm btn-outline-primary w-100 mb-2">' + a.label + '</a>'; }).join('')
      : '<div class="text-muted small">No suggested actions.</div>';

    /* Send message */
    var sendBtn = document.getElementById('btn-chat-send');
    if (sendBtn) {
      sendBtn.addEventListener('click', function () {
        var input = document.getElementById('chat-input');
        var text  = input ? input.value.trim() : '';
        if (!text) return;
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.inbox.conversations.sendMessage(cid, text)
            .then(function () {
              input.value = '';
              var bubble = '<div class="d-flex justify-content-end mb-3"><div class="msg-bubble p-2 msg-out"><div class="small">' + text + '</div></div></div>';
              msgsEl.insertAdjacentHTML('beforeend', bubble);
              msgsEl.scrollTop = msgsEl.scrollHeight;
            }).catch(function () {});
        } else {
          if (input) input.value = '';
          var bubble = '<div class="d-flex justify-content-end mb-3"><div class="msg-bubble p-2 msg-out"><div class="small">' + text + '</div></div></div>';
          msgsEl.insertAdjacentHTML('beforeend', bubble);
          msgsEl.scrollTop = msgsEl.scrollHeight;
        }
      });
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      var prom = convId
        ? window.CRM_API.inbox.conversations.get(convId).catch(function () { return { data: null }; })
        : Promise.resolve({ data: null });
      prom.then(function (res) {
        var thread = res.data;
        if (!thread && _d && _d.messageThreads) thread = _d.messageThreads.data[0];
        render(thread);
      });
    } else {
      var threads = (_d && _d.messageThreads && _d.messageThreads.data) || [];
      var thread  = convId ? (threads.find(function (t) { return (t.conversation_id || t.thread_id) === convId; }) || threads[0]) : threads[0];
      render(thread || null);
    }
  });

})();
