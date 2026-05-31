/* Pakistan CRM — Omnichannel Inbox (L-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var CH_ICON = {
    whatsapp: '<i class="fi fi-brands-whatsapp ch-icon-wa"></i>',
    email:    '<i class="fi fi-rr-envelope ch-icon-em"></i>',
    sms:      '<i class="fi fi-rr-comment ch-icon-sms"></i>',
  };
  var INTENT_BADGE = {
    payment_query:      '<span class="badge bg-warning-subtle text-warning border border-warning-subtle intent-badge">Payment</span>',
    follow_up_response: '<span class="badge bg-info-subtle text-info border border-info-subtle intent-badge">Follow-up</span>',
    lead_inquiry:       '<span class="badge bg-primary-subtle text-primary border border-primary-subtle intent-badge">Lead</span>',
    support_request:    '<span class="badge bg-danger-subtle text-danger border border-danger-subtle intent-badge">Support</span>',
  };

  var DEMO_MESSAGES = {
    'th-001': [
      { dir:'in',  text:'Assalamu Alaikum! Sir, mera order deliver kab hoga?', time:'09:30', ticks:'✓✓' },
      { dir:'out', text:'Wa Alaikum Assalam! Let me check the delivery status for you right away.', time:'09:31', ticks:'✓✓ 🔵' },
      { dir:'in',  text:'Sir, order delivery kab hogi?', time:'09:45', ticks:'✓' },
    ],
    'th-002': [
      { dir:'in',  text:'Hello, I am writing regarding invoice INV-2026-002. It shows partial payment but I paid in full.', time:'08:15' },
      { dir:'out', text:'Thank you for reaching out. I will review the payment records and update you shortly.', time:'08:30' },
    ],
  };

  var _allThreads   = [];
  var _activeChannel = '';

  function relativeTime(iso) {
    var diff = (new Date() - new Date(iso)) / 1000;
    if (diff < 60)    return 'just now';
    if (diff < 3600)  return Math.floor(diff / 60) + 'm ago';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
    return Math.floor(diff / 86400) + 'd ago';
  }

  function renderThread(thread) {
    var agentName = '—';
    if (_d && _d.userMap && thread.assigned_agent_id) {
      agentName = (_d.userMap[thread.assigned_agent_id] || {}).display_name || thread.assigned_agent_id;
    } else if (thread.assigned_agent_id) {
      agentName = thread.assigned_agent_id;
    }

    document.getElementById('thread-header-strip').innerHTML =
      '<div class="avatar avatar-sm rounded-circle bg-primary-subtle d-flex align-items-center justify-content-center"><i class="fi fi-rr-user text-primary"></i></div>' +
      '<div class="flex-grow-1">' +
        '<div class="fw-semibold">' + (thread.contact_name || '—') + '</div>' +
        '<div class="small text-muted d-flex gap-2">' +
          '<span>' + (thread.contact_phone || thread.contact_phone_e164 || '') + '</span>' +
          '<span>·</span>' +
          '<span>Assigned: ' + agentName + '</span>' +
          '<span>·</span>' +
          '<span>' + (CH_ICON[thread.channel] || thread.channel) + '</span>' +
        '</div>' +
      '</div>' +
      '<div class="d-flex gap-2" id="thread-action-btns">' +
        (INTENT_BADGE[thread.intent] || '') +
        '<button class="btn btn-sm btn-outline-secondary" id="btn-reassign" data-conv="' + (thread.conversation_id || thread.thread_id) + '">Reassign</button>' +
        (!thread.assigned_agent_id ? '<button class="btn btn-sm btn-primary" id="btn-claim" data-conv="' + (thread.conversation_id || thread.thread_id) + '">Claim</button>' : '') +
      '</div>';

    var convId = thread.conversation_id || thread.thread_id;
    var msgs   = DEMO_MESSAGES[thread.thread_id || convId] || [
      { dir:'in', text: thread.last_message_preview || '—', time:'—', ticks:'✓' }
    ];
    document.getElementById('message-area').innerHTML = msgs.map(function (m) {
      var isOut = m.dir === 'out';
      return '<div class="d-flex ' + (isOut ? 'justify-content-end' : '') + ' mb-3">' +
        '<div class="msg-bubble p-2 ' + (isOut ? 'msg-bubble-out' : 'msg-bubble-in') + '">' +
          '<div class="small">' + m.text + '</div>' +
          '<div class="d-flex justify-content-end gap-1 mt-1">' +
            '<span style="font-size:.65rem" class="text-muted">' + (m.time || '') + '</span>' +
            (m.ticks ? '<span style="font-size:.7rem">' + m.ticks + '</span>' : '') +
          '</div>' +
        '</div></div>';
    }).join('');
    document.getElementById('compose-bar').style.display = '';

    /* Action button wiring */
    var actBtns = document.getElementById('thread-action-btns');
    if (actBtns) {
      actBtns.addEventListener('click', function (e) {
        var btn = e.target.closest('button');
        if (!btn) return;
        var cid = btn.dataset.conv;
        if (btn.id === 'btn-claim') {
          btn.disabled = true;
          window.CRM_API.inbox.conversations.claim(cid)
            .then(function () { btn.textContent = 'Claimed'; btn.className = 'btn btn-sm btn-success'; })
            .catch(function () { btn.disabled = false; });
        }
        if (btn.id === 'btn-reassign') {
          var toAgent = window.prompt('Reassign to agent ID:');
          if (!toAgent) return;
          btn.disabled = true;
          window.CRM_API.inbox.conversations.handoff(cid, { to_agent_id: toAgent, reason:'manual' })
            .then(function () { btn.disabled = false; })
            .catch(function () { btn.disabled = false; });
        }
      });
    }
  }

  function renderList(threads) {
    var listEl = document.getElementById('thread-list');
    listEl.innerHTML = threads.length ? threads.map(function (t) {
      return '<div class="thread-item p-3 border-bottom ' + (t.unread_count > 0 ? 'has-unread' : '') + '" data-id="' + (t.conversation_id || t.thread_id) + '">' +
        '<div class="d-flex align-items-start gap-2">' +
          (CH_ICON[t.channel] || '') +
          '<div class="flex-grow-1 overflow-hidden">' +
            '<div class="d-flex justify-content-between align-items-center">' +
              '<span class="fw-semibold ' + (t.unread_count > 0 ? 'text-body' : 'text-muted') + ' small text-truncate">' + (t.contact_name || '—') + '</span>' +
              '<span class="small text-muted ms-2">' + (t.last_message_at ? relativeTime(t.last_message_at) : '—') + '</span>' +
            '</div>' +
            '<div class="small text-truncate text-muted">' + (t.last_message_preview || '') + '</div>' +
            '<div class="d-flex gap-1 mt-1">' +
              (INTENT_BADGE[t.intent] || '') +
              (t.unread_count > 0 ? '<span class="badge bg-danger rounded-pill">' + t.unread_count + '</span>' : '') +
              (!t.assigned_agent_id ? '<span class="badge bg-secondary-subtle text-secondary intent-badge">Unassigned</span>' : '') +
            '</div>' +
          '</div>' +
        '</div></div>';
    }).join('') : '<div class="p-3 text-muted small text-center">No conversations.</div>';

    listEl.querySelectorAll('[data-id]').forEach(function (el) {
      el.addEventListener('click', function () {
        listEl.querySelectorAll('[data-id]').forEach(function (e) { e.classList.remove('active'); });
        this.classList.add('active');
        var tid = this.dataset.id;
        var thread = _allThreads.find(function (t) { return (t.conversation_id || t.thread_id) === tid; });
        if (thread) renderThread(thread);
      });
    });
  }

  function sendMessage() {
    var input  = document.getElementById('compose-input');
    var text   = input ? input.value.trim() : '';
    if (!text) return;

    /* Find active conversation ID */
    var active = document.querySelector('.thread-item.active');
    var convId = active ? active.dataset.id : null;
    if (!convId) return;

    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.inbox.conversations.sendMessage(convId, text)
        .then(function () {
          input.value = '';
          var msgArea = document.getElementById('message-area');
          var bubble = '<div class="d-flex justify-content-end mb-3"><div class="msg-bubble p-2 msg-bubble-out"><div class="small">' + text + '</div></div></div>';
          msgArea.insertAdjacentHTML('beforeend', bubble);
          msgArea.scrollTop = msgArea.scrollHeight;
        })
        .catch(function () {});
    } else {
      input.value = '';
      var msgArea = document.getElementById('message-area');
      var bubble = '<div class="d-flex justify-content-end mb-3"><div class="msg-bubble p-2 msg-bubble-out"><div class="small">' + text + '</div></div></div>';
      if (msgArea) { msgArea.insertAdjacentHTML('beforeend', bubble); msgArea.scrollTop = msgArea.scrollHeight; }
    }
  }

  function init(threads) {
    _allThreads = threads;
    renderList(threads);

    var first = threads[0];
    if (first) {
      var firstEl = document.querySelector('[data-id="' + (first.conversation_id || first.thread_id) + '"]');
      if (firstEl) firstEl.classList.add('active');
      renderThread(first);
    }

    /* Channel filter */
    document.querySelectorAll('#channel-filter button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('#channel-filter button').forEach(function (b) { b.classList.remove('active'); });
        this.classList.add('active');
        _activeChannel = this.dataset.ch;
        var filtered = _activeChannel ? _allThreads.filter(function (t) { return t.channel === _activeChannel; }) : _allThreads;
        renderList(filtered);
      });
    });

    /* Search */
    var searchEl = document.getElementById('thread-search');
    if (searchEl) {
      searchEl.addEventListener('input', function () {
        var q = this.value.toLowerCase();
        var filtered = _allThreads.filter(function (t) {
          return (t.contact_name || '').toLowerCase().includes(q) || (t.last_message_preview || '').toLowerCase().includes(q);
        });
        renderList(filtered);
      });
    }

    /* Send button */
    var sendBtn = document.getElementById('btn-send');
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    var composeInput = document.getElementById('compose-input');
    if (composeInput) composeInput.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.inbox.conversations.list({ limit: 50 })
        .then(function (res) { init(res.data || []); })
        .catch(function () { init((_d && _d.messageThreads && _d.messageThreads.data) || []); });
    } else {
      init((_d && _d.messageThreads && _d.messageThreads.data) || []);
    }
  });

})();
