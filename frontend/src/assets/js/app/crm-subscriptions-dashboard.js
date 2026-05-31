/* Pakistan CRM — Subscription Revenue Dashboard (A-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) {
    if (!n && n !== 0) return '—';
    n = Number(n);
    if (n >= 10000000) return 'PKR ' + (n / 10000000).toFixed(2) + ' Cr';
    if (n >= 100000)   return 'PKR ' + (n / 100000).toFixed(2) + ' L';
    return 'PKR ' + n.toLocaleString('en-IN');
  }

  var statusCfg = {
    draft:'bg-secondary-subtle text-secondary', trialing:'bg-info-subtle text-info',
    active:'bg-success-subtle text-success', past_due:'bg-danger-subtle text-danger',
    paused:'bg-warning-subtle text-warning', cancelled:'bg-secondary-subtle text-secondary',
    expired:'bg-secondary-subtle text-secondary'
  };
  function statusLabel(s) { return s.replace('_', ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); }); }
  var churnCls = { low:'bg-success-subtle text-success', medium:'bg-warning-subtle text-warning', high:'bg-danger-subtle text-danger' };

  /* Plan → approximate MRR when backend doesn't store it */
  var PLAN_MRR = { growth_monthly: 45000, growth_annual: 40000, enterprise_monthly: 120000, enterprise_annual: 100000, starter_monthly: 15000, starter_annual: 12000 };

  function computeKpi(subs) {
    var active     = subs.filter(function (s) { return s.status === 'active' || s.status === 'trialing'; });
    var mrr        = active.reduce(function (sum, s) { return sum + (s.mrr || PLAN_MRR[s.plan_code] || 0); }, 0);
    var arr        = mrr * 12;
    var pastDue    = subs.filter(function (s) { return s.status === 'past_due'; }).length;
    var churnFlags = subs.filter(function (s) { return s.churn_risk === 'high'; }).length;
    var renewed    = subs.filter(function (s) { return s.status === 'active' && s.renewal_date; }).length;
    var renewalRate= subs.length > 0 ? Math.round((renewed / Math.max(active.length, 1)) * 100) : 0;
    return { mrr: mrr, arr: arr, renewal_rate: renewalRate, churn_flag_count: churnFlags, past_due_count: pastDue };
  }

  function render(subs) {
    var kpi        = computeKpi(subs);
    var delinquent = subs.filter(function (s) { return s.status === 'past_due'; });

    /* Posture strip */
    var churnFlagCount = kpi.churn_flag_count || 0;
    $('#posture-churn-count').text(churnFlagCount);
    $('#posture-plural').text(churnFlagCount === 1 ? '' : 's');
    if (churnFlagCount === 0) { $('#posture-strip').removeClass('alert-danger').addClass('alert-success'); }

    /* KPI cards */
    $('#kpi-mrr').text(pkr(kpi.mrr || 0));
    $('#kpi-arr').text(pkr(kpi.arr || 0));
    $('#kpi-renewal-rate').text((kpi.renewal_rate || 0) + '%');

    /* Delinquent list */
    $('#delinquency-badge').text(delinquent.length);
    if (delinquent.length > 0) {
      var dlHtml = delinquent.map(function (s) {
        return '<a href="app/subscriptions-detail.html?id=' + s.subscription_id + '" class="list-group-item list-group-item-action py-2">' +
          '<div class="d-flex justify-content-between align-items-center">' +
          '<div><div class="fw-semibold small">' + (s.account_name || s.account_id || '—') + '</div>' +
          '<div class="text-muted" style="font-size:.75rem;">' + (s.plan || s.plan_code || '—') + '</div></div>' +
          '<span class="badge bg-danger-subtle text-danger">Past Due</span>' +
          '</div></a>';
      }).join('');
      $('#delinquent-list').html(dlHtml);
    }

    /* Status breakdown table */
    var activeSubs = subs.filter(function (s) { return ['active','trialing','past_due'].indexOf(s.status) !== -1; });
    var subRows    = activeSubs.map(function (s) {
      var stCls = statusCfg[s.status] || 'bg-secondary-subtle text-secondary';
      var chCls = churnCls[s.churn_risk] || 'bg-secondary-subtle text-secondary';
      var mrrVal= s.mrr || PLAN_MRR[s.plan_code] || 0;
      return '<tr>' +
        '<td class="text-center fw-semibold">' + (s.account_name || s.account_id || '—') + '</td>' +
        '<td class="text-center">' + (s.plan || s.plan_code || '—') + '</td>' +
        '<td class="text-center">' + pkr(mrrVal) + '</td>' +
        '<td class="text-center"><span class="badge ' + stCls + '">' + statusLabel(s.status) + '</span></td>' +
        '<td class="text-center">' + (s.renewal_date || '—') + '</td>' +
        '<td class="text-center"><span class="badge ' + chCls + '">' + (s.churn_risk ? (s.churn_risk.charAt(0).toUpperCase() + s.churn_risk.slice(1)) : '—') + '</span></td>' +
        '</tr>';
    }).join('');
    $('#sub-status-body').html(subRows || '<tr><td colspan="6" class="text-center text-muted py-3">No active subscriptions</td></tr>');

    /* Expansion vs churn */
    var expansionCount = subs.filter(function (s) { return s.status === 'active'; }).length;
    var churnCount     = subs.filter(function (s) { return s.status === 'cancelled' || s.status === 'expired'; }).length;
    var delta          = expansionCount - churnCount;
    var $deltaEl       = $('#expansion-churn-delta');
    if ($deltaEl.length) {
      $deltaEl.text((delta >= 0 ? '+' : '') + delta + ' net')
        .removeClass('text-success text-danger')
        .addClass(delta >= 0 ? 'text-success' : 'text-danger');
    }
    $('#expansion-count').text(expansionCount);
    $('#churn-count').text(churnCount);
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.subscriptions.list({ limit: 200 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.subscriptions && _d.subscriptions.data) || []); });
  } else {
    if (!_d) return;
    render((_d.subscriptions && _d.subscriptions.data) || []);
  }

})();
