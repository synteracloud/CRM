/* Pakistan CRM — Support Analytics (H-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var SLA_BADGE    = { breached:'<span class="badge bg-danger">Breached</span>', at_risk:'<span class="badge bg-warning text-dark">At Risk</span>', healthy:'<span class="badge bg-success">Healthy</span>' };
  var PRI_BADGE    = { critical:'<span class="badge bg-danger">Critical</span>', high:'<span class="badge bg-danger-subtle text-danger border border-danger-subtle">High</span>', medium:'<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Medium</span>', low:'<span class="badge bg-secondary-subtle text-secondary">Low</span>' };
  var STATUS_BADGE = { OPEN:'<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Open</span>', ASSIGNED:'<span class="badge bg-info-subtle text-info border border-info-subtle">Assigned</span>', IN_PROGRESS:'<span class="badge bg-warning-subtle text-warning border border-warning-subtle">In Progress</span>', RESOLVED:'<span class="badge bg-success-subtle text-success border border-success-subtle">Resolved</span>', ESCALATED:'<span class="badge bg-danger">Escalated</span>', WAITING_ON_CUSTOMER:'<span class="badge bg-secondary-subtle text-secondary">Waiting</span>', CLOSED:'<span class="badge bg-dark text-white">Closed</span>' };

  function render(cases) {
    if (typeof flatpickr !== 'undefined') {
      flatpickr('#date-range-picker', { mode:'range', dateFormat:'d M Y', defaultDate:[new Date(Date.now() - 29 * 86400000), new Date()] });
    }

    var kpi = (_d && _d.caseSlaKpi) || {
      open_case_count: cases.filter(function (c) { return c.status !== 'RESOLVED' && c.status !== 'CLOSED'; }).length,
      breach_rate: cases.length > 0 ? Math.round(cases.filter(function (c) { return c.sla_state === 'breached'; }).length / cases.length * 100) : 0,
      avg_first_response_minutes: 18
    };

    document.getElementById('kpi-open').textContent     = kpi.open_case_count || 0;
    document.getElementById('kpi-breach').textContent   = (kpi.breach_rate || 0) + '%';
    document.getElementById('kpi-response').textContent = (kpi.avg_first_response_minutes || 0) + ' min';
    document.getElementById('kpi-resolved').textContent = cases.filter(function (c) { return c.status === 'RESOLVED'; }).length;

    new ApexCharts(document.getElementById('chart-breach'), {
      chart: { type:'line', height:260, toolbar:{ show:false } },
      series: [{ name:'SLA Breach %', data:[8,12,10,15,14, kpi.breach_rate || 0] }],
      xaxis:  { categories:['Dec','Jan','Feb','Mar','Apr','May'] },
      colors: ['#f05252'], stroke:{ curve:'smooth', width:2 }, markers:{ size:4 }, dataLabels:{ enabled:false },
    }).render();

    var sourceCounts = {};
    cases.forEach(function (c) { sourceCounts[c.source] = (sourceCounts[c.source] || 0) + 1; });
    if (Object.keys(sourceCounts).length > 0) {
      new ApexCharts(document.getElementById('chart-source'), {
        chart: { type:'donut', height:260 },
        series: Object.values(sourceCounts),
        labels: Object.keys(sourceCounts).map(function (s) { return s.replace('_',' ').replace(/\b\w/g, function (l) { return l.toUpperCase(); }); }),
        colors: ['#3f83f8','#0e9f6e','#f05252','#9061f9'],
        legend: { position:'bottom' }, dataLabels: { enabled:true },
      }).render();
    }

    $('#dt_SupportCases').DataTable({
      data: cases, pageLength: 10, order: [[6,'desc']],
      columns: [
        { data:'case_number', className:'dt-body-center', render:function (n) { return '<a href="app/cases-detail.html?id=' + n + '" class="fw-semibold">' + n + '</a>'; } },
        { data:'subject',     className:'dt-body-left',   render:function (s) { return '<span class="text-truncate d-inline-block" style="max-width:160px" title="' + s + '">' + s + '</span>'; } },
        { data:'priority',    className:'dt-body-center', render:function (p) { return PRI_BADGE[p] || p; } },
        { data:'status',      className:'dt-body-center', render:function (s) { return STATUS_BADGE[s] || s; } },
        { data:'sla_state',   className:'dt-body-center', render:function (s) { return SLA_BADGE[s] || s; } },
        { data:'source',      className:'dt-body-center', defaultContent:'—' },
        { data:'created_at',  className:'dt-body-center', render:function (t) { return t ? new Date(t).toLocaleDateString('en-PK') : '—'; } },
      ],
    });
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
