/* Pakistan CRM — Tenant & Entitlement Dashboard (A-11) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function render(tenant, users, flags) {
    var seatUsed      = users.length || tenant.seat_used || 0;
    var seatLimit     = tenant.seat_limit || 25;
    var featEnabled   = flags.filter(function (f) { return f.enabled; }).length || tenant.enabled_feature_count || 0;
    var featLimit     = tenant.entitlement_limit || 10;
    var overages      = tenant.entitlement_overage_count || 0;
    var atLimit       = tenant.entitlements_at_limit || 0;
    var sessions      = tenant.active_sessions || 0;

    /* KPI strip */
    $('#kpi-plan-tier').text(tenant.plan_label || tenant.plan || '—');
    $('#kpi-renewal').text('Renewal ' + (tenant.renewal_date || '—'));
    $('#kpi-seats').text(seatUsed + ' / ' + seatLimit);
    $('#kpi-seat-limit').text('of ' + seatLimit + ' seats');
    $('#kpi-features').text(featEnabled);
    $('#kpi-feature-limit').text('of ' + featLimit + ' entitlements');
    $('#kpi-sessions').text(sessions);

    /* Summary section */
    $('#sum-plan').text(tenant.plan_label || tenant.plan || '—');
    $('#sum-seats').text(seatUsed + ' of ' + seatLimit);
    $('#sum-renewal').text(tenant.renewal_date || '—');
    $('#sum-sessions').text(sessions);
    var util = featLimit ? Math.round((featEnabled / featLimit) * 100) + '%' : '—';
    $('#sum-util').text(util);
    if (overages > 0) {
      $('#sum-overages').text(overages + ' overage(s)').removeClass('text-success').addClass('text-danger');
    }

    /* Entitlements at limit queue */
    $('#at-limit-badge').text(atLimit);
    var nearLimit = flags.filter(function (f) { return f.enabled; }).slice(0, atLimit);
    if (nearLimit.length > 0) {
      var html = nearLimit.map(function (f) {
        return '<div class="list-group-item py-2 small">' +
          '<div class="fw-semibold">' + (f.label || f.flag_key) + '</div>' +
          '<div class="text-muted">' + (f.description || f.rule_type || '') + '</div></div>';
      }).join('');
      $('#entitlement-list').html(html);
    } else {
      $('#entitlement-list').html('<div class="list-group-item py-3 text-muted small text-center">No entitlements nearing limit</div>');
    }

    /* User list (seat usage context) */
    if (users.length > 0) {
      var ROLE_CLR = { sales_rep:'primary', sales_manager:'info', admin:'danger', tenant_admin:'danger' };
      var userHtml = users.slice(0, 6).map(function (u, i) {
        var n   = (i % 5) + 1;
        var cls = ROLE_CLR[u.role] || 'secondary';
        return '<div class="d-flex align-items-center gap-2 py-2 border-bottom small">' +
          '<img src="assets/images/avatar/avatar' + n + '.webp" class="avatar avatar-xxs rounded-circle" alt="">' +
          '<div class="flex-grow-1"><div class="fw-semibold">' + u.display_name + '</div><div class="text-muted" style="font-size:.75rem;">' + u.email + '</div></div>' +
          '<span class="badge bg-' + cls + '-subtle text-' + cls + '">' + (u.role || '').replace(/_/g, ' ') + '</span>' +
          '</div>';
      }).join('');
      var userListEl = document.getElementById('user-seat-list');
      if (userListEl) userListEl.innerHTML = userHtml;
    }
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.tenants.current(),
      window.CRM_API.users.list(),
      window.CRM_API.featureFlags.list().catch(function () { return { data: [] }; })
    ]).then(function (results) {
      render(results[0].data || {}, results[1].data || [], results[2].data || []);
    }).catch(function () {
      var kpi   = (_d && _d.tenantKpi)    || {};
      var flags = (_d && _d.featureFlags && _d.featureFlags.data) || [];
      render(kpi, (_d && _d.users && _d.users.data) || [], flags);
    });
  } else {
    var kpi   = (_d && _d.tenantKpi)    || {};
    var flags = (_d && _d.featureFlags && _d.featureFlags.data) || [];
    render(kpi, (_d && _d.users && _d.users.data) || [], flags);
  }

})();
