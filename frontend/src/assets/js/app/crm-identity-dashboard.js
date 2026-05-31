/* Pakistan CRM — Identity & Access Posture Dashboard (A-12) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var ESCALATED = { 'u-002': ['audit_read'], 'u-003': ['user_manage', 'role_edit'] };
  var ROLE_CLR  = { sales_rep:'primary', sales_manager:'info', admin:'danger', tenant_admin:'danger' };

  function render(users, auditLog) {
    var privileged     = users.filter(function (u) { return u.role === 'sales_manager' || u.role === 'admin' || u.role === 'tenant_admin'; });
    var escalatedUsers = users.filter(function (u) { return !!ESCALATED[u.id]; });
    var denyEvents     = auditLog.filter(function (e) { return e.result === 'deny'; });
    var loginEvents    = auditLog.filter(function (e) { return e.action_type === 'login'; });

    /* Posture strip */
    $('#privileged-count').text(privileged.length);
    $('#privileged-plural').text(privileged.length === 1 ? ' holds' : 's hold');

    /* Primary KPI */
    $('#kpi-active-users').text(users.length);
    $('#kpi-privileged-users').text(privileged.length);
    $('#kpi-audit-entries').text(auditLog.length);

    /* Risk panel */
    var activeActors = {};
    loginEvents.forEach(function (e) { activeActors[e.actor_id] = true; });
    var dormantCount = users.filter(function (u) { return !activeActors[u.id]; }).length;
    $('#risk-deny-count').text(denyEvents.length);
    $('#risk-login-count').text(loginEvents.length);
    $('#risk-dormant').text(dormantCount);

    /* Execution queue: escalated permissions */
    $('#escalation-badge').text(escalatedUsers.length);
    var listHtml;
    if (escalatedUsers.length === 0) {
      listHtml = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-badge-check fs-3 d-block mb-2 opacity-25"></i>No privilege escalation detected.</div>';
    } else {
      listHtml = '<ul class="list-group list-group-flush">' +
        escalatedUsers.map(function (u) {
          var esc     = ESCALATED[u.id] || [];
          var avatarN = (parseInt((u.id || '0').replace(/\D/g, '') || '0', 10) % 5) + 1;
          var roleCls = ROLE_CLR[u.role] || 'secondary';
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-center justify-content-between gap-3">' +
            '<div class="d-flex align-items-center gap-2">' +
            '<div class="avatar avatar-sm rounded-circle"><img src="assets/images/avatar/avatar' + avatarN + '.webp" alt=""></div>' +
            '<div><div class="fw-semibold">' + u.display_name + '</div>' +
            '<div class="text-muted small">' +
            '<span class="badge bg-' + roleCls + '-subtle text-' + roleCls + '">' + (u.role || '').replace(/_/g, ' ') + '</span> · ' + u.email +
            '</div></div></div>' +
            '<div class="text-end"><div class="text-danger small"><code>' + esc.join(', ') + '</code></div>' +
            '<div class="text-muted small">exceeds role definition</div></div></div></li>';
        }).join('') + '</ul>';
    }
    $('#escalation-list').html(listHtml);

    /* Activity chart */
    var userCounts  = {};
    auditLog.forEach(function (e) {
      var name = e.actor_name || e.actor_id || 'Unknown';
      userCounts[name] = (userCounts[name] || 0) + 1;
    });
    var actorNames  = Object.keys(userCounts);
    var actorCounts = actorNames.map(function (n) { return userCounts[n]; });

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    var chartEl = document.querySelector('#IdentityActivityChart');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:   { type:'bar', height:240, toolbar:{show:false}, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Events', data: actorCounts }],
        xaxis:   { categories: actorNames, labels:{ style:{ colors:textClr, fontSize:'11px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' } }, tickAmount: Math.max.apply(null, actorCounts) || 5, min:0 },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'50%', distributed:true } },
        colors:  ['#5955D1','#17a2b8','#ffc107','#dc3545','#28a745'],
        dataLabels: { enabled:true, style:{ fontSize:'11px', fontWeight:'600' } },
        grid:    { borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return v + ' event' + (v === 1 ? '' : 's'); } } }
      }).render();
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.users.list(),
      window.CRM_API.audits.list({ limit: 500 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || []);
    }).catch(function () {
      render((_d && _d.users && _d.users.data) || [], (_d && _d.AUDIT_LOG) || []);
    });
  } else {
    if (!_d) return;
    render(_d.users.data, _d.AUDIT_LOG || []);
  }

})();
