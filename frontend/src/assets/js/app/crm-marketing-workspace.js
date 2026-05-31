/* Pakistan CRM — Marketing Workspace (F-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TYPE_BADGE = {
    whatsapp_broadcast:'<span class="badge bg-success-subtle text-success border border-success-subtle">WhatsApp</span>',
    email:             '<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Email</span>',
    sms:               '<span class="badge bg-info-subtle text-info border border-info-subtle">SMS</span>',
  };
  var STATUS_BADGE = {
    active:    '<span class="badge bg-success">Active</span>',
    completed: '<span class="badge bg-secondary">Completed</span>',
    draft:     '<span class="badge bg-light text-dark border">Draft</span>',
    paused:    '<span class="badge bg-warning text-dark">Paused</span>',
    cancelled: '<span class="badge bg-danger">Cancelled</span>',
  };

  function render(campaigns) {
    document.getElementById('kpi-total').textContent  = campaigns.length;
    document.getElementById('kpi-active').textContent = campaigns.filter(function (c) { return c.status === 'active'; }).length;
    document.getElementById('kpi-leads').textContent  = campaigns.reduce(function (s, c) { return s + (c.leads_generated || 0); }, 0);
    var delivered = campaigns.filter(function (c) { return c.delivery_rate > 0; });
    document.getElementById('kpi-delivery').textContent = delivered.length
      ? Math.round(delivered.reduce(function (s, c) { return s + c.delivery_rate; }, 0) / delivered.length) + '%' : '—';

    var activeFilter = '';
    var dt = $('#dt_Campaigns').DataTable({
      data: campaigns, pageLength: 10, order: [[0,'asc']],
      columns: [
        { data:'name',           className:'dt-body-left', render:function (n) { return '<span class="fw-semibold">' + n + '</span>'; } },
        { data:'type',           className:'dt-body-center', render:function (t) { return TYPE_BADGE[t] || t; } },
        { data:'status',         className:'dt-body-center', render:function (s) { return STATUS_BADGE[s] || s; } },
        { data:'segment_name',   className:'dt-body-center', defaultContent:'—' },
        { data:'reach',          className:'dt-body-center', render:function (r) { return r ? Number(r).toLocaleString() : '—'; } },
        { data:'delivery_rate',  className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'open_rate',      className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'reply_rate',     className:'dt-body-center', render:function (r) { return r ? r + '%' : '—'; } },
        { data:'leads_generated',className:'dt-body-center', render:function (r) { return r || '—'; } },
        { data:null,             className:'dt-body-center', render:function (v, t, row) { return t !== 'display' ? '' : '<a href="app/marketing-analytics.html" class="btn btn-xs btn-outline-primary">View</a>'; } },
      ],
    });

    $('#filter-status button').on('click', function () {
      $('#filter-status button').removeClass('active');
      $(this).addClass('active');
      activeFilter = $(this).data('filter');
      dt.rows().every(function () {
        var row = this.data();
        $(this.node()).toggle(!activeFilter || row.status === activeFilter);
      });
      dt.draw(false);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.campaigns.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.campaigns && _d.campaigns.data) || []); });
    } else {
      render((_d && _d.campaigns && _d.campaigns.data) || []);
    }
  });

})();
