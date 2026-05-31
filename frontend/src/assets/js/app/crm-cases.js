/* Pakistan CRM — Case Queue (B-05) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var SLA_BADGE = {
    breached: '<span class="badge bg-danger">Breached</span>',
    at_risk:  '<span class="badge bg-warning text-dark">At Risk</span>',
    healthy:  '<span class="badge bg-success">Healthy</span>',
  };
  var PRI_BADGE = {
    critical: '<span class="badge bg-danger">Critical</span>',
    high:     '<span class="badge bg-danger-subtle text-danger border border-danger-subtle">High</span>',
    medium:   '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Medium</span>',
    low:      '<span class="badge bg-secondary-subtle text-secondary">Low</span>',
  };
  var STATUS_BADGE = {
    OPEN:               '<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Open</span>',
    ASSIGNED:           '<span class="badge bg-info-subtle text-info border border-info-subtle">Assigned</span>',
    IN_PROGRESS:        '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">In Progress</span>',
    WAITING_ON_CUSTOMER:'<span class="badge bg-secondary-subtle text-secondary">Waiting</span>',
    RESOLVED:           '<span class="badge bg-success-subtle text-success border border-success-subtle">Resolved</span>',
    ESCALATED:          '<span class="badge bg-danger">Escalated</span>',
    CLOSED:             '<span class="badge bg-dark text-white">Closed</span>',
  };

  function fmtDue(iso) {
    if (!iso) return '—';
    var dt      = new Date(iso);
    var overdue = dt < new Date();
    var s = dt.toLocaleDateString('en-PK', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' });
    return overdue ? '<span class="text-danger fw-semibold">' + s + '</span>' : s;
  }

  function render(cases) {
    document.getElementById('kpi-open').textContent     = cases.filter(function (c) { return c.status !== 'RESOLVED' && c.status !== 'CLOSED'; }).length;
    document.getElementById('kpi-breached').textContent = cases.filter(function (c) { return c.sla_state === 'breached'; }).length;
    document.getElementById('kpi-atrisk').textContent   = cases.filter(function (c) { return c.sla_state === 'at_risk'; }).length;
    document.getElementById('kpi-resolved').textContent = cases.filter(function (c) { return c.status === 'RESOLVED'; }).length;

    var activeStatus = '', activeSla = '';

    var dt = $('#dt_Cases').DataTable({
      data: cases,
      pageLength: 10,
      order: [[7, 'asc']],
      columns: [
        { data: 'case_number',     className: 'dt-body-center', render: function (n) { return '<a href="app/cases-detail.html?id=' + n + '" class="fw-semibold">' + n + '</a>'; } },
        { data: 'subject',         className: 'dt-body-left',   render: function (s) { return '<span class="text-truncate d-inline-block" style="max-width:180px" title="' + s + '">' + s + '</span>'; } },
        { data: 'contact_name',    className: 'dt-body-center', defaultContent: '—' },
        { data: 'priority',        className: 'dt-body-center', render: function (p) { return PRI_BADGE[p] || p; } },
        { data: 'status',          className: 'dt-body-center', render: function (s) { return STATUS_BADGE[s] || s; } },
        { data: 'sla_state',       className: 'dt-body-center', render: function (s) { return SLA_BADGE[s] || s; } },
        { data: 'queue',           className: 'dt-body-center', defaultContent: '—' },
        { data: 'response_due_at', className: 'dt-body-center', render: fmtDue },
        { data: null,              className: 'dt-body-center', render: function (v, t, row) { return t !== 'display' ? '' : '<a href="app/cases-detail.html?id=' + (row.case_id || row.case_number) + '" class="btn btn-xs btn-outline-primary">Open</a>'; } },
      ],
    });

    function applyFilters() {
      dt.rows().every(function () {
        var row = this.data();
        var show = true;
        if (activeStatus && row.status !== activeStatus) show = false;
        if (activeSla    && row.sla_state !== activeSla)  show = false;
        $(this.node()).toggle(show);
      });
      dt.draw(false);
    }

    $('#filter-status button').on('click', function () {
      $('#filter-status button').removeClass('active');
      $(this).addClass('active');
      activeStatus = $(this).data('filter');
      applyFilters();
    });
    $('#filter-sla button').on('click', function () {
      $('#filter-sla button').removeClass('active');
      $(this).addClass('active');
      activeSla = $(this).data('sla');
      applyFilters();
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
