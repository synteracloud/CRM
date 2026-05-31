/* Pakistan CRM — Customer 360 (C-02) */

(function () {
  'use strict';

  var cfg       = window.CRM_CONFIG;
  var _d        = window.CRM_DUMMY;
  var contactId = new URLSearchParams(window.location.search).get('id') || 'c-001';

  function fmtDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' });
  }
  function fmtPhone(e164) {
    if (!e164) return '—';
    var m = e164.match(/^\+92(\d{3})(\d{3})(\d{4})$/);
    return m ? '+92 ' + m[1] + ' ' + m[2] + ' ' + m[3] : e164;
  }
  function pkr(n) { return 'PKR ' + Number(n).toLocaleString('en-IN'); }
  function cap(str) { if (!str) return '—'; return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' '); }

  var ACTIVITY_CFG = { call:{ cls:'primary', icon:'fi fi-rr-phone-call' }, email:{ cls:'primary', icon:'fi fi-rr-envelope' }, whatsapp:{ cls:'success', icon:'fi fi-brands-whatsapp' }, meeting:{ cls:'warning', icon:'fi fi-rr-handshake' }, note:{ cls:'info', icon:'fi fi-rr-sticky-note' }, stage_change:{ cls:'secondary', icon:'fi fi-rr-exchange' }, deal_won:{ cls:'success', icon:'fi fi-rr-trophy' } };
  var TAG_CLR = { Lead:'primary', Hot:'danger', Warm:'warning', Cold:'secondary', Customer:'success', VIP:'warning', WhatsApp:'success', New:'info' };

  function render(contact, leads, activities) {
    if (!contact) {
      if (_d && _d.contacts && _d.contacts.data[0]) render(_d.contacts.data[0], (_d.leads && _d.leads.data) || [], (_d.activities && _d.activities.data) || []);
      return;
    }

    var avatarN = (parseInt((contact.contact_id || '0').replace(/\D/g, '') || '0', 10) % 5) + 1;

    $('#contact-breadcrumb').text(contact.display_name);
    $('#contact-avatar').attr({ src:'assets/images/avatar/avatar' + avatarN + '.webp', alt: contact.display_name });
    $('#contact-name').text(contact.display_name);
    $('#contact-phone').text(fmtPhone(contact.phone_e164));
    $('#contact-account-strip').text(contact.account_name || '—');

    var tagsHtml = (contact.tags || []).map(function (t) {
      var cls = TAG_CLR[t] || 'secondary';
      return '<span class="badge bg-' + cls + '-subtle text-' + cls + '">' + t + '</span>';
    }).join(' ');
    $('#contact-tags').html(tagsHtml);

    $('#ctx-completeness').text(contact.completeness_score || 0);
    $('#ctx-completeness-bar').css('width', (contact.completeness_score || 0) + '%');
    $('#ctx-open-cases').text(contact.open_cases || 0);
    $('#ctx-last-touch').text(contact.last_touchpoint || '—');

    var relLeads = leads.filter(function (l) { return l.contact_name === contact.display_name || l.contact_id === contact.contact_id; });
    var leadIds  = relLeads.map(function (l) { return l.lead_id; });
    var relActs  = activities.filter(function (a) { return a.entity_type === 'lead' && leadIds.indexOf(a.entity_id) !== -1; });

    /* Contact info tab */
    var infoEl = document.getElementById('contact-info-tab-content');
    if (infoEl) {
      infoEl.innerHTML =
        '<div class="row g-3 small">' +
        '<div class="col-sm-6"><label class="text-muted">Phone</label><p class="fw-semibold">' + fmtPhone(contact.phone_e164) + '</p></div>' +
        '<div class="col-sm-6"><label class="text-muted">Email</label><p class="fw-semibold">' + (contact.email || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="text-muted">Account</label><p class="fw-semibold">' + (contact.account_name || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="text-muted">Source</label><p class="fw-semibold">' + cap(contact.source) + '</p></div>' +
        '<div class="col-sm-6"><label class="text-muted">Status</label><p class="fw-semibold">' + cap(contact.status) + '</p></div>' +
        '<div class="col-sm-6"><label class="text-muted">Created At</label><p class="fw-semibold">' + fmtDate(contact.created_at) + '</p></div>' +
        '</div>';
    }

    /* Lead pipeline tab */
    var leadsEl = document.getElementById('contact-leads-list');
    if (leadsEl) {
      leadsEl.innerHTML = relLeads.length ? relLeads.map(function (l) {
        var STAGE_CLS = { new:'primary', qualifying:'info', proposal:'warning', negotiation:'danger', won:'success', lost:'secondary' };
        var cls = STAGE_CLS[l.stage] || 'secondary';
        return '<div class="d-flex justify-content-between align-items-center py-2 border-bottom">' +
          '<div><div class="fw-semibold small">' + l.contact_name + '</div>' +
          '<div class="text-muted" style="font-size:.75rem;">' + pkr(l.estimated_value || 0) + ' · ' + (l.source || '—') + '</div></div>' +
          '<span class="badge bg-' + cls + '-subtle text-' + cls + '">' + l.stage + '</span></div>';
      }).join('') : '<p class="text-muted small text-center py-3">No leads found for this contact.</p>';
    }

    /* Activity tab */
    var actEl = document.getElementById('contact-activity-list');
    if (actEl) {
      actEl.innerHTML = relActs.length ? relActs.map(function (a) {
        var c = ACTIVITY_CFG[a.activity_type] || { cls:'secondary', icon:'fi fi-rr-circle' };
        return '<div class="d-flex gap-3 py-2 border-bottom">' +
          '<div class="avatar avatar-sm rounded-circle bg-' + c.cls + '-subtle flex-shrink-0 d-flex align-items-center justify-content-center">' +
          '<i class="' + c.icon + ' text-' + c.cls + '"></i></div>' +
          '<div class="flex-grow-1">' +
          '<div class="small fw-semibold">' + (a.description || cap(a.activity_type)) + '</div>' +
          '<div class="text-muted" style="font-size:.75rem;">' + fmtDate(a.occurred_at ? a.occurred_at.substring(0, 10) : '') + ' · ' + (a.performed_by || '—') + '</div>' +
          '</div></div>';
      }).join('') : '<p class="text-muted small text-center py-3">No activity recorded.</p>';
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.contacts.get(contactId).catch(function () { return { data: null }; }),
      window.CRM_API.leads.list({ limit: 200 }).catch(function () { return { data: [] }; }),
      window.CRM_API.activities.list({ entity_id: contactId, limit: 50 }).catch(function () { return { data: [] }; })
    ]).then(function (results) {
      var c = results[0].data;
      if (!c && _d && _d.contacts) c = _d.contacts.data.filter(function (x) { return x.contact_id === contactId; })[0] || _d.contacts.data[0];
      render(c, results[1].data || [], results[2].data || []);
    });
  } else {
    if (!_d) return;
    var c = (_d.contacts.data.filter(function (x) { return x.contact_id === contactId; })[0]) || _d.contacts.data[0];
    render(c, _d.leads.data, _d.activities.data);
  }

})();
