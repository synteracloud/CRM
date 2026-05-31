/* Pakistan CRM — Partners (B-11) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TIER_BADGE = {
    Platinum:'<span class="badge bg-primary">Platinum</span>',
    Gold:    '<span class="badge bg-warning text-dark">Gold</span>',
    Silver:  '<span class="badge bg-secondary">Silver</span>',
  };
  var STATUS_BADGE = {
    active:   '<span class="badge bg-success-subtle text-success border border-success-subtle">Active</span>',
    inactive: '<span class="badge bg-secondary-subtle text-secondary">Inactive</span>',
    suspended:'<span class="badge bg-danger-subtle text-danger">Suspended</span>',
  };

  function pkr(n) { return n ? 'PKR ' + Number(n).toLocaleString('en-PK') : 'PKR 0'; }

  function render(partners) {
    document.getElementById('kpi-total').textContent      = partners.length;
    document.getElementById('kpi-active').textContent     = partners.filter(function (p) { return p.status === 'active'; }).length;
    document.getElementById('kpi-opps').textContent       = partners.reduce(function (s, p) { return s + (p.attributed_opp_count || 0); }, 0);
    document.getElementById('kpi-commission').textContent = pkr(partners.reduce(function (s, p) { return s + (p.commission_due || 0); }, 0));

    var activeTier = '', activeStatus = '';

    var dt = $('#dt_Partners').DataTable({
      data: partners, pageLength: 10, order: [[1,'asc']],
      columns: [
        { data:'name',             className:'dt-body-left',   render:function (n) { return '<span class="fw-semibold">' + n + '</span>'; } },
        { data:'partner_tier',     className:'dt-body-center', render:function (t) { return TIER_BADGE[t] || t; }, defaultContent:'—' },
        { data:'region',           className:'dt-body-center', defaultContent:'—' },
        { data:'contact_name',     className:'dt-body-center', render:function (n, t, row) { return n + '<br><small class="text-muted">' + (row.contact_email || '') + '</small>'; }, defaultContent:'—' },
        { data:'status',           className:'dt-body-center', render:function (s) { return STATUS_BADGE[s] || s; }, defaultContent:'—' },
        { data:'attributed_opp_count', className:'dt-body-center', defaultContent:'0' },
        { data:'commission_due',   className:'dt-body-center', render:function (v, t) { return t !== 'display' ? v : (v > 0 ? '<span class="text-danger fw-semibold">' + pkr(v) + '</span>' : '<span class="text-muted">—</span>'); }, defaultContent:'0' },
        { data:null, className:'dt-body-center', orderable:false, render:function (v, t, row) { return t !== 'display' ? '' : '<a href="app/partners-detail.html?id=' + row.partner_id + '" class="btn btn-xs btn-outline-primary">View</a>'; } }
      ],
    });

    $('#filter-tier button').on('click', function () {
      $('#filter-tier button').removeClass('active'); $(this).addClass('active');
      activeTier = $(this).data('filter');
      dt.rows().every(function () { var r = this.data(); $(this.node()).toggle(!activeTier || r.partner_tier === activeTier); }); dt.draw(false);
    });
    $('#filter-status button').on('click', function () {
      $('#filter-status button').removeClass('active'); $(this).addClass('active');
      activeStatus = $(this).data('filter');
      dt.rows().every(function () { var r = this.data(); $(this.node()).toggle(!activeStatus || r.status === activeStatus); }); dt.draw(false);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.partners.list({ limit: 200 })
        .then(function (res) { render(res.data || []); })
        .catch(function () { render((_d && _d.partners && _d.partners.data) || []); });
    } else {
      render((_d && _d.partners && _d.partners.data) || []);
    }
  });

})();
