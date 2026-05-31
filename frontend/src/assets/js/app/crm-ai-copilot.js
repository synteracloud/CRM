/* Pakistan CRM — AI Copilot (M-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var INTENT_RESPONSES = {
    lead: function (msg) {
      var matches = (_d && _d.leads && _d.leads.data || []).filter(function (l) { return (l.contact_name || '').toLowerCase().includes(msg.toLowerCase()); }).slice(0, 3);
      if (!matches.length) return { text: 'I searched for leads matching your query but found no results.', actions: [] };
      return { text: 'I found ' + matches.length + ' matching lead(s):', cards: matches.map(function (l) { return { title: l.contact_name, sub: 'Stage: ' + l.stage + ' · PKR ' + (l.estimated_value || 0).toLocaleString('en-PK'), href: 'app/leads-detail.html?id=' + l.lead_id }; }) };
    },
    payment: function () {
      var inv = (_d && _d.invoices && _d.invoices.data || []).filter(function (i) { return i.status === 'overdue' || i.status === 'partial'; }).slice(0, 3);
      return { text: 'Here are the invoices requiring attention:', cards: inv.map(function (i) { return { title: i.invoice_number + ' — ' + i.account_name, sub: 'Balance: PKR ' + ((i.total_amount || 0) - (i.paid_amount || 0)).toLocaleString('en-PK') + ' · ' + i.status, href: 'app/invoices-detail.html' }; }), actions: [{ label: 'Record Payment', href: 'app/collections.html' }] };
    },
    followup: function () {
      var of = (_d && _d.overdueFollowups) || [];
      return { text: 'You have ' + of.length + ' overdue follow-up(s).', cards: of.slice(0, 1).map(function (f) { return { title: f.lead_name || f.lead_id, sub: 'Action: ' + f.action_type + ' · Level: ' + f.escalation_level, href: 'app/followups.html' }; }), actions: [{ label: 'View All', href: 'app/followups.html' }] };
    },
    case: function () {
      var cases = (_d && _d.cases && _d.cases.data || []).filter(function (c) { return c.status === 'OPEN'; }).slice(0, 2);
      return { text: 'Recent open cases for your attention:', cards: cases.map(function (c) { return { title: c.case_number + ' — ' + c.subject, sub: 'Priority: ' + c.priority + ' · SLA: ' + c.sla_state, href: 'app/cases-detail.html' }; }), actions: [{ label: 'Open New Case', href: 'app/case-new.html' }] };
    },
    oob: function () { return { text: "I can help with leads, payments, follow-ups, and support cases. Try: 'Show me overdue follow-ups' or 'Invoice status for City Pharma'.", actions: [] }; }
  };

  function classifyIntent(msg) {
    if (/lead|prospect|contact/i.test(msg)) return 'lead';
    if (/payment|invoice|collection|paid|bill/i.test(msg)) return 'payment';
    if (/follow[- ]?up|overdue|pending task/i.test(msg)) return 'followup';
    if (/case|ticket|support|issue/i.test(msg)) return 'case';
    return 'oob';
  }

  function renderCard(c) {
    return '<div class="border rounded p-2 mb-2" style="background:#fff">' +
      '<div class="fw-semibold small">' + c.title + '</div>' +
      '<div class="small text-muted">' + (c.sub || '') + '</div>' +
      '<a href="' + c.href + '" class="btn btn-xs btn-outline-primary mt-1">Open full record</a></div>';
  }

  function addMessage(role, content) {
    var histEl = document.getElementById('chat-history');
    if (!histEl) return;
    var isUser = role === 'user';
    var msgEl  = document.createElement('div');
    msgEl.className = 'd-flex ' + (isUser ? 'justify-content-end' : '') + ' mb-3';
    msgEl.innerHTML = '<div class="chat-msg p-2 ' + (isUser ? 'chat-out' : 'chat-in') + '">' +
      content +
      (!isUser ? '<div class="small text-muted mt-1" style="font-size:.65rem">Advisory · No auto-action</div>' : '') +
      '</div>';
    histEl.appendChild(msgEl);
    histEl.scrollTop = histEl.scrollHeight;
  }

  function addResponse(resp) {
    var html = '<div class="small">' + resp.text + '</div>';
    if (resp.cards) html += resp.cards.map(renderCard).join('');
    if (resp.actions && resp.actions.length) {
      html += '<div class="d-flex flex-wrap gap-2 mt-2">' +
        resp.actions.map(function (a) { return '<a href="' + a.href + '" class="btn btn-xs btn-primary">' + a.label + '</a>'; }).join('') + '</div>';
    }
    addMessage('ai', html);
  }

  function loadRiskFlags() {
    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        window.CRM_API.followups.list({ state: 'OVERDUE', limit: 10 }).catch(function () { return { data: [] }; }),
        window.CRM_API.cases.list({ limit: 20 }).catch(function () { return { data: [] }; }),
        window.CRM_API.ai.copilot.suggestions({ limit: 5 }).catch(function () { return { data: [] }; })
      ]).then(function (results) {
        var overdueFollowups = results[0].data || [];
        var breachedCases    = (results[1].data || []).filter(function (c) { return c.sla_state === 'breached'; });
        var suggestions      = results[2].data || [];

        var flags = [];
        if (overdueFollowups.length > 0) flags.push({ label: overdueFollowups.length + ' follow-up(s) overdue',       action: 'app/followups.html',          level:'danger'  });
        if (breachedCases.length > 0)    flags.push({ label: breachedCases.length + ' case(s) SLA breached',           action: 'app/cases.html',              level:'danger'  });
        if (flags.length === 0)          flags.push({ label: 'All follow-ups and SLAs on track',                        action: 'app/dashboard.html',          level:'success' });

        var flagsEl = document.getElementById('risk-flags');
        if (flagsEl) {
          flagsEl.innerHTML = flags.map(function (f) {
            return '<div class="d-flex align-items-center gap-2 p-3 border-bottom">' +
              '<i class="fi fi-rr-triangle-warning text-' + f.level + '"></i>' +
              '<div class="flex-grow-1 small">' + f.label + '</div>' +
              '<a href="' + f.action + '" class="btn btn-xs btn-outline-' + f.level + '">Fix</a>' +
              '<button class="btn btn-xs btn-link text-muted p-0" onclick="this.closest(\'.d-flex\').remove()">✕</button></div>';
          }).join('');
        }

        /* First suggestion card */
        if (suggestions.length > 0) {
          var sugg = suggestions[0];
          var suggBtn = document.getElementById('btn-dismiss-action');
          if (suggBtn) suggBtn.dataset.suggestionId = sugg.suggestion_id;
        }
      });
    } else {
      var overdueLeads  = (_d && _d.overdueFollowups && _d.overdueFollowups.length) || 0;
      var breachedCases = (_d && _d.cases && _d.cases.data.filter(function (c) { return c.sla_state === 'breached'; }).length) || 0;
      var flags = [];
      if (overdueLeads > 0)   flags.push({ label: overdueLeads + ' follow-up(s) overdue',    action: 'app/followups.html', level:'danger'  });
      if (breachedCases > 0)  flags.push({ label: breachedCases + ' case(s) SLA breached',   action: 'app/cases.html',     level:'danger'  });
      flags.push({ label: 'Pak Steel deal close date past', action: 'app/opportunities-detail.html', level:'warning' });
      var flagsEl = document.getElementById('risk-flags');
      if (flagsEl) {
        flagsEl.innerHTML = flags.map(function (f) {
          return '<div class="d-flex align-items-center gap-2 p-3 border-bottom">' +
            '<i class="fi fi-rr-triangle-warning text-' + f.level + '"></i>' +
            '<div class="flex-grow-1 small">' + f.label + '</div>' +
            '<a href="' + f.action + '" class="btn btn-xs btn-outline-' + f.level + '">Fix</a>' +
            '<button class="btn btn-xs btn-link text-muted p-0" onclick="this.closest(\'.d-flex\').remove()">✕</button></div>';
        }).join('');
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    loadRiskFlags();

    var dismissBtn = document.getElementById('btn-dismiss-action');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', function () {
        var suggId = this.dataset.suggestionId;
        if (cfg && !cfg.DUMMY_MODE && suggId) {
          window.CRM_API.ai.copilot.dismiss(suggId).catch(function () {});
        }
        var card = this.closest('.card');
        if (card) card.style.display = 'none';
      });
    }

    addMessage('ai', '<div class="small">Hello! I can help you find leads, check invoices, review follow-ups, or open support cases. Just ask naturally — in English or Urdu.</div>');

    function sendChat() {
      var input = document.getElementById('chat-input');
      var msg   = input.value.trim();
      if (!msg) return;
      addMessage('user', '<div class="small">' + msg + '</div>');
      input.value = '';

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.ai.copilot.query(msg)
          .then(function (res) {
            var r = res.data || {};
            addResponse({ text: r.summary || 'No results.', cards: (r.records || []).slice(0, 3).map(function (rec) {
              return { title: rec.contact_name || rec.title || rec.case_number || rec.lead_id || 'Record', sub: '', href: 'app/dashboard.html' };
            }), actions: r.actions || [] });
          })
          .catch(function () { addResponse(INTENT_RESPONSES.oob()); });
        return;
      }

      var intent   = classifyIntent(msg);
      var namedLead = (_d && _d.leads && _d.leads.data || []).find(function (l) { return msg.toLowerCase().includes((l.contact_name || '').split(' ')[0].toLowerCase()); });
      var resp = intent === 'lead' && namedLead
        ? { text:'Here is what I found for ' + namedLead.contact_name + ':', cards:[{ title:namedLead.contact_name, sub:'Stage: ' + namedLead.stage + ' · PKR ' + (namedLead.estimated_value || 0).toLocaleString('en-PK'), href:'app/leads-detail.html?id=' + namedLead.lead_id }], actions:[{ label:'Open Lead', href:'app/leads-detail.html?id=' + namedLead.lead_id }] }
        : (INTENT_RESPONSES[intent] ? INTENT_RESPONSES[intent](msg) : INTENT_RESPONSES.oob());

      setTimeout(function () { addResponse(resp); }, 400);
    }

    var sendBtn = document.getElementById('btn-chat-send');
    if (sendBtn) sendBtn.addEventListener('click', sendChat);
    var chatInput = document.getElementById('chat-input');
    if (chatInput) chatInput.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } });
  });

})();
