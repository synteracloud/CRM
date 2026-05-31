/* Pakistan CRM — Account Profile (C-03) */

(function () {
  'use strict';

  var cfg       = window.CRM_CONFIG;
  var _d        = window.CRM_DUMMY;
  var accountId = new URLSearchParams(window.location.search).get('id') || 'a-002';

  function pkr(n) { if (!n) return '—'; n = Number(n); if (n >= 100000) return 'PKR ' + (n / 100000).toFixed(2) + ' L'; return 'PKR ' + n.toLocaleString('en-IN'); }
  var tierCls = { 'Enterprise':'bg-danger-subtle text-danger', 'Mid-Market':'bg-warning-subtle text-warning', 'SMB':'bg-info-subtle text-info' };

  function render(acc, contacts, opps, invoices) {
    if (!acc) {
      if (_d && _d.accounts && _d.accounts.data[0]) {
        render(_d.accounts.data[0], (_d.contacts && _d.contacts.data) || [], (_d.opportunities && _d.opportunities.data) || [], (_d.invoices && _d.invoices.data) || []);
      }
      return;
    }

    $('#acc-breadcrumb').text(acc.name);
    $('#acc-name').text(acc.name);
    $('#acc-city-label').html('<i class="fi fi-rr-marker me-1"></i>' + (acc.city || '—'));
    $('#acc-tier-badge').html('<span class="badge ' + (tierCls[acc.tier] || 'bg-secondary-subtle text-secondary') + '">' + (acc.tier || '—') + '</span>');
    $('#acc-industry-badge').html('<span class="badge bg-secondary-subtle text-secondary">' + (acc.industry || '—') + '</span>');

    $('#det-name').text(acc.name);
    $('#det-industry').text(acc.industry || '—');
    $('#det-tier').text(acc.tier || '—');
    $('#det-city').text(acc.city || '—');
    $('#det-owner').text(acc.owner_id || '—');
    $('#det-balance').text(acc.outstanding_balance > 0 ? pkr(acc.outstanding_balance) : '—')
      .toggleClass('text-danger', acc.outstanding_balance > 0)
      .toggleClass('text-muted', !acc.outstanding_balance);

    /* Contacts tab */
    var accContacts = contacts.filter(function (c) { return c.account_id === acc.account_id || c.account_name === acc.name; });
    $('#ctx-contacts').text(accContacts.length);
    $('#contacts-list').html(accContacts.length ? accContacts.map(function (c) {
      return '<div class="d-flex align-items-center justify-content-between py-2 border-bottom">' +
        '<div><div class="fw-semibold small">' + c.display_name + '</div>' +
        '<div class="text-muted" style="font-size:.75rem;">' + (c.phone_e164 || '—') + '</div></div>' +
        '<a href="app/contacts-detail.html?id=' + c.contact_id + '" class="btn btn-xs btn-outline-primary btn-sm">View</a></div>';
    }).join('') : '<p class="text-muted small text-center py-3">No contacts</p>');

    /* Opportunities tab */
    var accOpps = opps.filter(function (o) { return o.account_id === acc.account_id || o.account_name === acc.name; });
    $('#ctx-open-opps').text(accOpps.filter(function (o) { return o.stage !== 'closed_won' && o.stage !== 'closed_lost'; }).length);
    var stageCls = { proposal:'bg-primary-subtle text-primary', negotiation:'bg-warning-subtle text-warning', closed_won:'bg-success-subtle text-success', closed_lost:'bg-secondary-subtle text-secondary', qualification:'bg-info-subtle text-info', discovery:'bg-info-subtle text-info' };
    $('#opps-list').html(accOpps.length ? accOpps.map(function (o) {
      return '<div class="d-flex align-items-center justify-content-between py-2 border-bottom">' +
        '<div><div class="fw-semibold small">' + o.name + '</div>' +
        '<div class="text-muted" style="font-size:.75rem;">' + pkr(o.amount) + '</div></div>' +
        '<span class="badge ' + (stageCls[o.stage] || 'bg-secondary-subtle text-secondary') + '">' + o.stage + '</span></div>';
    }).join('') : '<p class="text-muted small text-center py-3">No opportunities</p>');

    /* Invoices tab */
    var accInvoices = invoices.filter(function (i) { return i.account_id === acc.account_id || i.account_name === acc.name; });
    var totalBal = accInvoices.reduce(function (s, i) { return s + Math.max(0, (Number(i.total_amount) || 0) - (Number(i.paid_amount) || 0)); }, 0);
    $('#ctx-balance').text(totalBal > 0 ? pkr(totalBal) : '—');
    var invCls = { paid:'bg-success-subtle text-success', overdue:'bg-danger-subtle text-danger', partial:'bg-warning-subtle text-warning', sent:'bg-info-subtle text-info', draft:'bg-secondary-subtle text-secondary' };
    $('#invoices-list').html(accInvoices.length ? accInvoices.map(function (i) {
      return '<div class="d-flex align-items-center justify-content-between py-2 border-bottom">' +
        '<div><div class="fw-semibold small">' + (i.invoice_number || i.invoice_id) + '</div>' +
        '<div class="text-muted" style="font-size:.75rem;">Due ' + (i.due_date || '—') + '</div></div>' +
        '<div class="text-end"><div>' + pkr(i.total_amount) + '</div>' +
        '<span class="badge ' + (invCls[i.status] || 'bg-secondary-subtle text-secondary') + '">' + i.status + '</span></div></div>';
    }).join('') : '<p class="text-muted small text-center py-3">No invoices</p>');
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.accounts.get(accountId).catch(function () { return { data: null }; }),
      window.CRM_API.contacts.list({ limit: 200 }).catch(function () { return { data: [] }; }),
      window.CRM_API.opportunities.list({ limit: 200 }).catch(function () { return { data: [] }; }),
      window.CRM_API.invoiceSummaries.get({ limit: 200 }).catch(function () { return { data: [] }; })
    ]).then(function (results) {
      var acc = results[0].data;
      if (!acc && _d && _d.accounts) acc = _d.accounts.data.filter(function (a) { return a.account_id === accountId; })[0];
      render(acc, results[1].data || [], results[2].data || [], Array.isArray(results[3].data) ? results[3].data : []);
    });
  } else {
    if (!_d) return;
    var accounts = (_d.accounts && _d.accounts.data) || [];
    var acc = accounts.filter(function (a) { return a.account_id === accountId; })[0] || accounts[0];
    render(acc, _d.contacts.data, _d.opportunities.data, (_d.invoices && _d.invoices.data) || []);
  }

})();
