/* Pakistan CRM — Subscription Detail (C-09) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var subId = new URLSearchParams(window.location.search).get('id') || 'sub-001';

  function pkr(n) {
    if (!n && n !== 0) return '—';
    n = Number(n);
    if (n >= 10000000) return 'PKR ' + (n / 10000000).toFixed(2) + ' Cr';
    if (n >= 100000)   return 'PKR ' + (n / 100000).toFixed(2) + ' L';
    return 'PKR ' + n.toLocaleString('en-IN');
  }
  function fmtDate(iso) {
    if (!iso) return '—';
    var dt = new Date(iso);
    return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  var statusCfg = {
    draft:'bg-secondary-subtle text-secondary', trialing:'bg-info-subtle text-info',
    active:'bg-success-subtle text-success', past_due:'bg-danger-subtle text-danger',
    paused:'bg-warning-subtle text-warning', cancelled:'bg-secondary-subtle text-secondary',
    expired:'bg-secondary-subtle text-secondary'
  };
  function statusBadge(s) {
    var cls = statusCfg[s] || 'bg-secondary-subtle text-secondary';
    var lbl = (s || '').replace('_', ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return '<span class="badge ' + cls + '">' + lbl + '</span>';
  }

  function render(sub) {
    if (!sub) {
      if (_d && _d.subscriptions && _d.subscriptions.data && _d.subscriptions.data[0]) {
        render(_d.subscriptions.data[0]);
      }
      return;
    }

    /* Identity strip */
    $('#sub-breadcrumb').text(sub.subscription_id);
    $('#sub-id-display').text(sub.subscription_id);
    $('#sub-plan-label').text(sub.plan || sub.plan_code || '—');
    $('#sub-status-badge').html(statusBadge(sub.status));
    $('#sub-account-label').html('<i class="fi fi-rr-building me-1"></i>' + (sub.account_name || sub.account_id || '—'));
    $('#sub-mrr-strip').text(pkr(sub.mrr || 0));

    /* Context panel */
    $('#ctx-sub-status').html(statusBadge(sub.status));
    $('#ctx-plan').text(sub.plan || sub.plan_code || '—');
    $('#ctx-billing').text(sub.billing_cycle || (sub.renewal_date ? 'Recurring' : 'One-time'));
    $('#ctx-start-date').text(fmtDate(sub.start_date));
    $('#ctx-renewal-date').text(fmtDate(sub.renewal_date));
    $('#ctx-mrr').text(pkr(sub.mrr || 0));
    $('#ctx-arr').text(pkr(sub.mrr ? sub.mrr * 12 : 0));
    $('#ctx-account').text(sub.account_name || sub.account_id || '—');
    $('#ctx-sub-id').text(sub.subscription_id);

    /* Risk / churn panel */
    var churnRisk = sub.churn_risk || 'low';
    var churnCls  = { low:'bg-success-subtle text-success', medium:'bg-warning-subtle text-warning', high:'bg-danger-subtle text-danger' };
    var churnDesc = { low:'Healthy engagement, on-time payments', medium:'Some late payments or low activity', high:'At risk — intervention recommended' };
    $('#churn-risk-badge').html('<span class="badge ' + (churnCls[churnRisk] || 'bg-secondary-subtle text-secondary') + '">' + churnRisk.charAt(0).toUpperCase() + churnRisk.slice(1) + ' Risk</span>');
    $('#churn-risk-desc').text(churnDesc[churnRisk] || '');

    /* Action button gates */
    var canRenew   = sub.status === 'active' || sub.status === 'past_due';
    var canSuspend = sub.status === 'active';
    var canCancel  = sub.status !== 'cancelled' && sub.status !== 'expired';
    if (!canRenew)   $('#btn-sub-renew').prop('disabled', true);
    if (!canSuspend) $('#btn-sub-suspend').prop('disabled', true);
    if (!canCancel)  $('#btn-sub-cancel').prop('disabled', true);

    /* Invoice history (from dummy if no live subscription invoices) */
    var invoices = (_d && _d.invoices && _d.invoices.data) ? _d.invoices.data.filter(function (inv) {
      return inv.subscription_id === sub.subscription_id;
    }) : [];
    if (invoices.length === 0 && _d && _d.invoices && _d.invoices.data) {
      invoices = _d.invoices.data.slice(0, 3);
    }
    var invHtml = invoices.length
      ? invoices.map(function (inv) {
          return '<tr>' +
            '<td class="text-center">' + (inv.invoice_number || inv.invoice_id || '—') + '</td>' +
            '<td class="text-center">' + pkr(inv.total_amount || inv.amount || 0) + '</td>' +
            '<td class="text-center">' + statusBadge(inv.status || 'draft') + '</td>' +
            '<td class="text-center">' + fmtDate(inv.due_date) + '</td>' +
            '</tr>';
        }).join('')
      : '<tr><td colspan="4" class="text-center text-muted py-3">No invoices found.</td></tr>';
    $('#sub-invoice-history').html(invHtml);
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.subscriptions.list({ limit: 200 })
      .then(function (res) {
        var subs = res.data || [];
        var found = subs.filter(function (s) { return s.subscription_id === subId; })[0] || subs[0];
        render(found || null);
      })
      .catch(function () {
        var subs = (_d && _d.subscriptions && _d.subscriptions.data) || [];
        var found = subs.filter(function (s) { return s.subscription_id === subId; })[0] || subs[0];
        render(found || null);
      });
  } else {
    if (!_d) return;
    var subs = (_d.subscriptions && _d.subscriptions.data) || [];
    var found = subs.filter(function (s) { return s.subscription_id === subId; })[0] || subs[0];
    render(found || null);
  }

})();
