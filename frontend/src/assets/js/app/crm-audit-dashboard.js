/* Pakistan CRM — Platform Audit & Reliability Dashboard (A-13) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    var dt = new Date(iso);
    return MONTHS[dt.getMonth()] + ' ' + dt.getDate() + ', ' + dt.getFullYear() + ' ' +
      dt.toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit' });
  }

  function render(auditLog) {
    var total        = auditLog.length;
    var denyEvents   = auditLog.filter(function (e) { return e.result === 'deny'; });
    var denyRate     = total > 0 ? Math.round((denyEvents.length / total) * 100) : 0;
    var uniqueMap    = {};
    auditLog.forEach(function (e) { uniqueMap[e.actor_id || e.actor_name] = true; });
    var uniqueActors = Object.keys(uniqueMap).length;
    var exportEvents = auditLog.filter(function (e) { return e.action_type === 'export'; });
    var deleteEvents = auditLog.filter(function (e) { return e.action_type === 'delete'; });

    /* Posture strip */
    var $posture = $('#audit-posture-alert');
    if ($posture.length) {
      if (denyEvents.length === 0) {
        $posture.addClass('alert-success').removeClass('alert-warning');
        $('#audit-posture-icon').removeClass('fi-rr-shield-exclamation').addClass('fi-rr-shield-check');
      } else {
        $posture.addClass('alert-warning').removeClass('alert-success');
      }
    }
    $('#deny-count').text(denyEvents.length);
    $('#deny-plural').text(denyEvents.length === 1 ? '' : 's');

    /* Primary KPI */
    $('#kpi-audit-total').text(total);
    $('#kpi-deny-rate').text(denyRate + '%');
    $('#kpi-unique-actors').text(uniqueActors);

    /* Risk panel */
    $('#risk-export-count').text(exportEvents.length);
    $('#risk-delete-count').text(deleteEvents.length);
    $('#risk-anomaly-count').text(denyEvents.length);
    $('#deny-rate-bar').css('width', Math.min(denyRate * 5, 100) + '%');
    $('#deny-rate-label').text('Policy deny rate: ' + denyRate + '%');

    /* Deny events queue */
    $('#deny-queue-badge').text(denyEvents.length);
    var listHtml;
    if (denyEvents.length === 0) {
      listHtml = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-shield-check fs-3 d-block mb-2 opacity-25 text-success"></i>No policy deny events — access control is clean.</div>';
    } else {
      listHtml = '<ul class="list-group list-group-flush">' +
        denyEvents.map(function (e) {
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-center justify-content-between gap-3">' +
            '<div><div class="fw-semibold">' + (e.actor_name || e.actor_id || '—') + ' · <code class="small">' + (e.action_type || '—') + '</code></div>' +
            '<div class="text-muted small mt-1">' + (e.resource_type || '—') + ' ' + (e.resource_id || '') + ' · ' + (e.occurred_at ? fmtDate(e.occurred_at) : '—') + '</div></div>' +
            '<span class="badge bg-danger">DENY</span>' +
            '</div></li>';
        }).join('') + '</ul>';
    }
    $('#deny-events-list').html(listHtml);

    /* Trend chart: events by action type */
    var actionTypes = {};
    auditLog.forEach(function (e) { actionTypes[e.action_type] = (actionTypes[e.action_type] || 0) + 1; });
    var actions = Object.keys(actionTypes);
    var counts  = actions.map(function (a) { return actionTypes[a]; });

    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    var chartEl = document.querySelector('#AuditEventChart');
    if (chartEl && window.ApexCharts && actions.length > 0) {
      new ApexCharts(chartEl, {
        chart:   { type:'bar', height:240, toolbar:{ show:false }, fontFamily:'Instrument Sans, sans-serif' },
        series:  [{ name:'Events', data: counts }],
        xaxis:   { categories: actions.map(function (a) { return a.charAt(0).toUpperCase() + a.slice(1); }), labels:{ style:{ colors:textClr, fontSize:'12px' } } },
        yaxis:   { labels:{ style:{ colors:textClr, fontSize:'11px' } }, tickAmount: Math.max.apply(null, counts) || 5, min:0 },
        plotOptions: { bar:{ borderRadius:4, columnWidth:'50%', distributed:true } },
        colors:  ['#5955D1','#17a2b8','#ffc107','#dc3545','#28a745','#6c757d'],
        dataLabels: { enabled:true, style:{ fontSize:'12px', fontWeight:'600' } },
        grid:    { borderColor:gridClr }, legend:{ show:false },
        tooltip: { y:{ formatter:function (v) { return v + ' event' + (v === 1 ? '' : 's'); } } }
      }).render();
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.audits.list({ limit: 500 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.AUDIT_LOG) || []); });
  } else {
    render((_d && _d.AUDIT_LOG) || []);
  }

})();
