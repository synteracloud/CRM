/* Pakistan CRM — Audit Report (H-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtTs(iso) {
    var dt = new Date(iso);
    return MONTHS[dt.getMonth()] + ' ' + dt.getDate() + ' · ' +
      dt.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
  }

  function render(auditLog) {
    var total      = auditLog.length;
    var denyEvents = auditLog.filter(function (e) { return e.result === 'deny'; });
    var privEvents = auditLog.filter(function (e) {
      return ['export', 'delete', 'admin_override', 'login'].indexOf(e.action_type) !== -1;
    });
    var denyRate   = total > 0 ? Math.round((denyEvents.length / total) * 100) : 0;

    $('#h06-total-entries').text(total);
    $('#h06-deny-count').text(denyEvents.length);
    $('#h06-deny-rate').text(denyRate + '% ');
    $('#h06-privileged-count').text(privEvents.length);

    $('#h06-chain-count').text(total);
    if (auditLog.length > 0) {
      var oldest = auditLog[auditLog.length - 1];
      var newest = auditLog[0];
      $('#h06-first-hash').text(oldest.hash || '—');
      $('#h06-latest-hash').text(newest.hash || '—');
    }

    /* Privileged access log table */
    var privHtml = privEvents.length
      ? privEvents.map(function (e) {
          return '<tr>' +
            '<td class="text-center">' + fmtTs(e.occurred_at) + '</td>' +
            '<td class="text-center">' + (e.actor_name || e.actor_id || '—') + '</td>' +
            '<td class="text-center text-capitalize">' + (e.action_type || '—') + '</td>' +
            '<td class="text-center">' + (e.resource_type || '—') + '</td>' +
            '<td class="text-center"><span class="badge ' + (e.result === 'deny' ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success') + '">' + (e.result || 'allow') + '</span></td>' +
            '</tr>';
        }).join('')
      : '<tr><td colspan="5" class="text-center text-muted py-3">No privileged events recorded.</td></tr>';
    $('#h06-priv-table-body').html(privHtml);

    /* Chart: events by action type */
    var isDark  = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    var textClr = isDark ? '#adb5bd' : '#6c757d';
    var gridClr = isDark ? '#343a40' : '#e9ecef';

    var allowByType = {}, denyByType = {};
    auditLog.forEach(function (e) {
      if (e.result === 'allow') allowByType[e.action_type] = (allowByType[e.action_type] || 0) + 1;
      else                      denyByType[e.action_type]  = (denyByType[e.action_type]  || 0) + 1;
    });
    var allTypes    = Object.keys(allowByType).concat(Object.keys(denyByType).filter(function (k) { return !allowByType[k]; }));
    var allowCounts = allTypes.map(function (t) { return allowByType[t] || 0; });
    var denyCounts  = allTypes.map(function (t) { return denyByType[t]  || 0; });

    var chartEl = document.querySelector('#H06ComplianceChart');
    if (chartEl && window.ApexCharts) {
      new ApexCharts(chartEl, {
        chart:   { type: 'bar', height: 260, toolbar: { show: false }, fontFamily: 'Instrument Sans, sans-serif', stacked: true },
        series:  [{ name: 'Allow', data: allowCounts }, { name: 'Deny', data: denyCounts }],
        xaxis:   { categories: allTypes.map(function (t) { return t.charAt(0).toUpperCase() + t.slice(1); }), labels: { style: { colors: textClr, fontSize: '12px' } } },
        yaxis:   { labels: { style: { colors: textClr, fontSize: '11px' } }, tickAmount: 4, min: 0 },
        colors:  ['#28a745', '#dc3545'],
        plotOptions: { bar: { borderRadius: 3, columnWidth: '50%' } },
        dataLabels: { enabled: false },
        grid:    { borderColor: gridClr },
        legend:  { position: 'top', labels: { colors: textClr } },
        tooltip: { y: { formatter: function (v) { return v + ' event' + (v === 1 ? '' : 's'); } } }
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
