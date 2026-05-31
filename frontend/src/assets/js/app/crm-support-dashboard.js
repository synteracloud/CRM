/* Pakistan CRM — Support SLA Dashboard (A-07) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var SLA_BADGE = { breached:'<span class="badge bg-danger">Breached</span>', at_risk:'<span class="badge bg-warning text-dark">At Risk</span>', healthy:'<span class="badge bg-success">Healthy</span>' };
  var PRI_BADGE = { critical:'<span class="badge bg-danger">Critical</span>', high:'<span class="badge bg-danger-subtle text-danger border border-danger-subtle">High</span>', medium:'<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Medium</span>', low:'<span class="badge bg-secondary-subtle text-secondary border border-secondary-subtle">Low</span>' };

  function fmtDue(iso) {
    if (!iso) return '—';
    var d = new Date(iso), now = new Date(), diff = d - now;
    if (diff < 0) return '<span class="text-danger fw-semibold">' + d.toLocaleTimeString('en-PK', { hour:'2-digit', minute:'2-digit' }) + ' (overdue)</span>';
    return d.toLocaleDateString('en-PK', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' });
  }

  function computeKpi(cases) {
    var open    = cases.filter(function (c) { return c.status !== 'RESOLVED' && c.status !== 'CLOSED'; });
    var breached= cases.filter(function (c) { return c.sla_state === 'breached'; });
    var atRisk  = cases.filter(function (c) { return c.sla_state === 'at_risk'; });
    var breachRate = open.length > 0 ? Math.round(breached.length / open.length * 100) : 0;
    return {
      open_case_count: open.length,
      avg_first_response_minutes: 18,
      breach_rate: breachRate,
      at_risk_case_count: atRisk.length,
      sla_breach_count: breached.length,
      unacknowledged_breach_count: breached.filter(function (c) { return c.status === 'OPEN'; }).length
    };
  }

  function render(cases) {
    var kpi = computeKpi(cases);

    if (kpi.sla_breach_count > 0) {
      document.getElementById('posture-row').style.display = '';
      document.getElementById('posture-text').textContent =
        kpi.sla_breach_count + ' SLA breach' + (kpi.sla_breach_count > 1 ? 'es' : '') +
        ' active — ' + kpi.unacknowledged_breach_count + ' unacknowledged. Immediate escalation required.';
    }

    document.getElementById('kpi-open-cases').textContent = kpi.open_case_count;
    document.getElementById('kpi-avg-response').textContent = kpi.avg_first_response_minutes + ' min';
    document.getElementById('kpi-breach-rate').textContent = kpi.breach_rate + '%';
    document.getElementById('kpi-at-risk').textContent = kpi.at_risk_case_count;

    if (kpi.unacknowledged_breach_count > 0) {
      var anomalyRow = document.getElementById('anomaly-row');
      if (anomalyRow) {
        anomalyRow.style.display = '';
        document.getElementById('anomaly-text').textContent =
          kpi.unacknowledged_breach_count + ' breached case(s) unacknowledged — review required.';
      }
    }

    var queueCases = cases.filter(function (c) { return c.sla_state !== 'healthy' && c.status !== 'RESOLVED' && c.status !== 'CLOSED'; });
    $('#dt_SlaQueue').DataTable({
      data: queueCases, pageLength: 5, lengthChange: false, searching: false, order: [[3, 'asc']],
      columns: [
        { data: 'case_number', className: 'dt-body-center', render: function (n) { return '<a href="app/cases-detail.html?id=' + n + '" class="fw-semibold">' + n + '</a>'; } },
        { data: 'subject',     className: 'dt-body-left',   render: function (s) { return '<span class="text-truncate d-inline-block" style="max-width:160px" title="' + s + '">' + s + '</span>'; } },
        { data: 'priority',    className: 'dt-body-center', render: function (p) { return PRI_BADGE[p] || p; } },
        { data: 'sla_state',   className: 'dt-body-center', render: function (s) { return SLA_BADGE[s] || s; } },
        { data: 'queue',       className: 'dt-body-center', defaultContent: '—' },
        { data: 'response_due_at', className: 'dt-body-center', render: fmtDue },
      ],
    });

    new ApexCharts(document.getElementById('chart-case-trend'), {
      chart: { type:'area', height:220, toolbar:{ show:false } },
      series: [
        { name:'Open',     data: [8, 12, 9, 14, 11, queueCases.length] },
        { name:'Resolved', data: [5, 9, 7, 10, 8,  cases.filter(function (c) { return c.status === 'RESOLVED'; }).length] }
      ],
      xaxis: { categories: ['Dec','Jan','Feb','Mar','Apr','May'] },
      colors: ['#f05252','#0e9f6e'],
      stroke: { curve:'smooth', width:2 },
      fill:   { type:'gradient', gradient:{ shadeIntensity:1, opacityFrom:0.3, opacityTo:0.0 } },
      legend: { position:'top' }, dataLabels: { enabled:false },
    }).render();
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.cases.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.cases && _d.cases.data) || []); });
    } else {
      render((_d && _d.cases && _d.cases.data) || []);
    }
  });

})();
