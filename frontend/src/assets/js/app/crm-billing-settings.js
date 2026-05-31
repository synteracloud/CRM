/* Pakistan CRM — Billing Settings (G-04) */
/* P-016: JazzCash/Easypaisa payment method section stays static stub — not wired */
(function () {
  'use strict';
  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function renderSub(data) {
    $('#bill-plan').text(data.plan_label || 'Growth');
    $('#bill-seats').text((data.seat_used || 5) + ' / ' + (data.seat_limit || 20));
    $('#bill-renewal').text((data.renewal_date || '—').substring(0, 10));
  }

  function renderInvoices(list) {
    var pkr = window.CRM && window.CRM.components ? window.CRM.components.pkr : function (n) { return 'PKR ' + n; };
    var rows = (list || []).map(function (i) {
      return '<tr>' +
        '<td class="text-center fw-semibold">' + (i.invoice_number || '—') + '</td>' +
        '<td class="text-center">' + (i.period || '—') + '</td>' +
        '<td class="text-center">' + pkr(i.amount_pkr || 0) + '</td>' +
        '<td class="text-center"><span class="badge bg-success-subtle text-success">' + (i.status || 'paid') + '</span></td>' +
        '<td class="text-center"><button class="btn btn-xs btn-outline-secondary btn-sm waves-effect"><i class="fi fi-rr-download"></i></button></td>' +
        '</tr>';
    }).join('');
    $('#billing-invoices').html(rows || '<tr><td colspan="5" class="text-center text-muted py-3 small">No invoices found.</td></tr>');
  }

  var dummySub = {
    plan_label: (_d && _d.tenantKpi) ? _d.tenantKpi.plan_tier : 'Growth',
    seat_used:  (_d && _d.tenantKpi) ? _d.tenantKpi.seat_count : 5,
    seat_limit: (_d && _d.tenantKpi) ? _d.tenantKpi.seat_limit : 20,
    renewal_date: (_d && _d.tenantKpi) ? _d.tenantKpi.renewal_date : '2027-01-01',
  };
  var dummyInvoices = [
    { invoice_number: 'BILL-2026-001', period: 'Jan 2026 – Dec 2026', amount_pkr: 61189, status: 'paid' },
    { invoice_number: 'BILL-2025-001', period: 'Jan 2025 – Dec 2025', amount_pkr: 59988, status: 'paid' },
  ];

  if (cfg && !cfg.DUMMY_MODE) {
    CRM_API.billing.plan()
      .then(function (r) { renderSub(r.data || r); })
      .catch(function () { renderSub(dummySub); });
    CRM_API.billing.invoices()
      .then(function (r) { renderInvoices(r.data || r); })
      .catch(function () { renderInvoices(dummyInvoices); });
  } else {
    renderSub(dummySub);
    renderInvoices(dummyInvoices);
  }
})();
