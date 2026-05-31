/* Pakistan CRM — Leads & Opportunities Page Driver */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  /* ── Helpers ──────────────────────────────────────────────────────── */
  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function fmtDate(iso) {
    if (!iso) return '—';
    var parts = iso.split('T')[0].split('-');
    return MONTHS[parseInt(parts[1], 10) - 1] + ' ' + parseInt(parts[2], 10) + ', ' + parts[0];
  }

  var srcMap = { whatsapp:'WhatsApp', web:'Website Form', referral:'Referral', manual:'Manual', campaign:'Campaign', import:'Import' };

  var stageBadge = {
    new:          '<span class="badge bg-primary-subtle text-primary">New</span>',
    qualifying:   '<span class="badge bg-info-subtle text-info">Qualifying</span>',
    nurturing:    '<span class="badge bg-warning-subtle text-warning">Nurturing</span>',
    proposal:     '<span class="badge bg-warning-subtle text-warning">Proposal</span>',
    negotiation:  '<span class="badge bg-info-subtle text-info">Negotiation</span>',
    won:          '<span class="badge bg-success-subtle text-success">Won</span>',
    lost:         '<span class="badge bg-danger-subtle text-danger">Lost</span>',
    disqualified: '<span class="badge bg-secondary-subtle text-secondary">Disqualified</span>'
  };

  var oppStageBadge = {
    discovery:    '<span class="badge bg-primary-subtle text-primary">Discovery</span>',
    qualification:'<span class="badge bg-info-subtle text-info">Qualification</span>',
    proposal:     '<span class="badge bg-warning-subtle text-warning">Proposal</span>',
    negotiation:  '<span class="badge bg-primary-subtle text-primary">Negotiation</span>',
    closed_won:   '<span class="badge bg-success-subtle text-success">Closed Won</span>',
    closed_lost:  '<span class="badge bg-danger-subtle text-danger">Closed Lost</span>'
  };

  var AVATARS_LEN = 10;

  function avatarImg(idx) {
    var n = (idx % AVATARS_LEN) + 1;
    return '<div class="avatar avatar-xxs rounded-circle me-2"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>';
  }

  /* ── KPI computation from live data ──────────────────────────────── */
  function computeLeadFunnelKpi(leads, opps) {
    var now     = new Date();
    var weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    var total      = leads.length;
    var newWeek    = leads.filter(function (l) { return l.created_at && l.created_at.slice(0, 10) >= weekAgo; }).length;
    var qualified  = leads.filter(function (l) { return ['proposal', 'negotiation', 'won'].indexOf(l.stage) !== -1; }).length;
    var wonCount   = leads.filter(function (l) { return l.stage === 'won'; }).length;
    var conversion = total > 0 ? (wonCount / total * 100).toFixed(1) + '%' : '0%';

    return {
      total:           total,
      new_week:        newWeek,
      qualified:       qualified,
      opportunities:   opps.length,
      conversion_rate: conversion,
      avg_latency:     '—',
      growth_delta:    undefined
    };
  }

  /* ── Overdue / follow-up map from followups ───────────────────────── */
  function buildFollowupMaps(followups) {
    var overdueLeadIds = {}, followupDueMap = {};
    followups.forEach(function (f) {
      if (f.state === 'overdue') overdueLeadIds[f.lead_id] = true;
      if (f.state !== 'completed') {
        if (!followupDueMap[f.lead_id] || f.due_at < followupDueMap[f.lead_id]) {
          followupDueMap[f.lead_id] = f.due_at;
        }
      }
    });
    return { overdueLeadIds: overdueLeadIds, followupDueMap: followupDueMap };
  }

  /* ── Module-level overdue filter state ───────────────────────────── */
  var _leadOverdueActive = false;

  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    if (settings.nTable.id !== 'dt_NewCustomers') return true;
    if (!_leadOverdueActive) return true;
    return $(settings.aoData[dataIndex].nTr).data('overdue') === 1;
  });

  /* ── Core render ──────────────────────────────────────────────────── */
  function render(leads, opps, followups, userMap) {
    var kpi   = computeLeadFunnelKpi(leads, opps);
    var maps  = buildFollowupMaps(followups);
    var overdue   = maps.overdueLeadIds;
    var dueMap    = maps.followupDueMap;

    /* KPI cards */
    $('#kpi-total-leads').text(kpi.total.toLocaleString('en-IN'));
    $('#kpi-new-leads').text(kpi.new_week.toLocaleString('en-IN'));
    $('#kpi-qualified-leads').text(kpi.qualified.toLocaleString('en-IN'));
    $('#kpi-opportunities').text(kpi.opportunities.toLocaleString('en-IN'));
    $('#kpi-conversion-rate').text(kpi.conversion_rate);
    $('#kpi-avg-latency').text(kpi.avg_latency);
    if (kpi.growth_delta) $('#kpi-leads-growth').text(kpi.growth_delta);

    /* Progress bar widths */
    document.querySelectorAll('.progress-bar[data-pct]').forEach(function (el) {
      el.style.width = el.getAttribute('data-pct') + '%';
    });

    /* ── 1. Lead Source Donut (Chart.js) — static data ────────────── */
    document.addEventListener('DOMContentLoaded', function () {
      var ctx = document.getElementById('leadSourceDonut');
      if (!ctx) return;
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Website', 'Email', 'LinkedIn'],
          datasets: [{
            data: [2310, 1850, 1320],
            backgroundColor: ['#5955D1', '#009966', '#F5A70D'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '65%',
          plugins: { legend: { display: false } }
        }
      });
    });

    /* ── 2. Opportunity Value Trend (ApexCharts) — static data ───── */
    var oppTrendEl = document.querySelector('#opportunityTrendChart');
    if (oppTrendEl) {
      new ApexCharts(oppTrendEl, {
        series: [{ name: 'Opportunity Value', data: [890000,760000,1020000,960000,880000,910000,940000,1000000,980000,920000,970000,1010000] }],
        chart: { height: 280, type: 'area', zoom: { enabled: false }, toolbar: { show: false } },
        colors: ['var(--bs-primary)'],
        fill: {
          type: 'gradient',
          gradient: { shade: 'light', type: 'vertical', shadeIntensity: 0.1, gradientToColors: ['var(--bs-primary)'], inverseColors: false, opacityFrom: 0.08, opacityTo: 0.01, stops: [20, 100] }
        },
        dataLabels: { enabled: false },
        stroke: { width: 2, curve: 'smooth', dashArray: 5 },
        markers: { size: 0, strokeColors: 'var(--bs-primary)', strokeWidth: 2, hover: { size: 6 } },
        yaxis: {
          min: 700000, max: 1100000, tickAmount: 5,
          labels: { formatter: function (v) { return '$' + (v / 1000) + 'K'; }, style: { colors: 'var(--bs-body-color)', fontSize: '13px', fontFamily: 'var(--bs-body-font-family)' } }
        },
        xaxis: {
          categories: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
          axisBorder: { color: 'var(--bs-border-color)' }, axisTicks: { show: false },
          labels: { style: { colors: 'var(--bs-body-color)', fontSize: '13px', fontFamily: 'var(--bs-body-font-family)' } }
        },
        tooltip: { y: { formatter: function (v) { return 'PKR ' + Number(v).toLocaleString('en-IN'); } } },
        grid: { borderColor: 'var(--bs-border-color)', strokeDashArray: 5, xaxis: { lines: { show: false } }, yaxis: { lines: { show: true } } },
        legend: { show: false }
      }).render();
    }

    /* ── 3. Lead Queue DataTable ──────────────────────────────────── */
    if ($('#dt_NewCustomers').length) {
      var dt_NewCustomers = $('#dt_NewCustomers').DataTable({
        data: leads,
        searching: true,
        pageLength: 6,
        select: false,
        lengthChange: false,
        info: true,
        paging: true,
        order: [[4, 'asc']],
        language: {
          search: '',
          searchPlaceholder: 'Search',
          paginate: {
            previous: "<i class='fi fi-rr-angle-left'></i>",
            next:     "<i class='fi fi-rr-angle-right'></i>",
            first:    "<i class='fi fi-rr-angle-double-left'></i>",
            last:     "<i class='fi fi-rr-angle-double-right'></i>"
          }
        },
        columns: [
          {
            data: 'contact_name',
            className: 'dt-body-left',
            orderable: false,
            render: function (val, type, row, meta) {
              if (type !== 'display') return val;
              return '<div class="d-flex align-items-center">' + avatarImg(meta.row) +
                '<div>' + val + '<div class="text-muted small">' + (row.contact_phone_e164 || '') + '</div></div></div>';
            }
          },
          {
            data: 'stage',
            className: 'dt-body-center',
            render: function (val, type) {
              if (type !== 'display') return val.charAt(0).toUpperCase() + val.slice(1).replace('_', ' ');
              return stageBadge[val] || val;
            }
          },
          {
            data: 'source',
            className: 'dt-body-center',
            render: function (val) { return srcMap[val] || val; }
          },
          {
            data: 'owner_id',
            className: 'dt-body-left',
            render: function (val, type, row, meta) {
              if (type !== 'display') return val;
              var u = userMap[val];
              if (!u) return val;
              var n = (meta.row % AVATARS_LEN) + 1;
              return '<div class="d-flex align-items-center">' +
                '<div class="avatar avatar-xxs rounded-circle me-2"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>' +
                u.display_name + '</div>';
            }
          },
          {
            data: 'lead_id',
            className: 'dt-body-center',
            render: function (val, type) {
              var due = dueMap[val];
              if (type === 'sort' || type === 'type') return due || '9999';
              if (!due) return '<span class="text-muted">—</span>';
              var isOver = overdue[val];
              var cls = isOver ? 'text-danger fw-semibold' : '';
              return '<span class="' + cls + '">' + fmtDate(due) + '</span>';
            }
          },
          {
            data: 'updated_at',
            className: 'dt-body-center',
            render: function (val, type) {
              if (type !== 'display') return val;
              return '<span class="text-muted small">' + fmtDate(val) + '</span>';
            }
          },
          {
            data: null,
            className: 'dt-body-center',
            orderable: false,
            render: function (val, type, row) {
              if (type !== 'display') return '';
              return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
                '<ul class="dropdown-menu dropdown-menu-end">' +
                '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-user-add me-2 text-primary"></i>Assign</a></li>' +
                '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-calendar-plus me-2 text-warning"></i>Schedule Follow-up</a></li>' +
                '<li><a class="dropdown-item" href="app/leads-detail.html?id=' + row.lead_id + '"><i class="fi fi-rr-arrow-right me-2"></i>Open Detail</a></li>' +
                '</ul></div>';
            }
          }
        ],
        createdRow: function (row, data) {
          if (overdue[data.lead_id]) $(row).attr('data-overdue', 1);
        },
        initComplete: function () {
          var dtSearch = $('#dt_NewCustomers_wrapper .dt-search').detach();
          $('#dt_NewCustomers_Search').append(dtSearch);
          $('#dt_NewCustomers_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
          $('#dt_NewCustomers_Search .dt-search label').remove();
          $('#dt_NewCustomers_wrapper > .row.mt-2.justify-content-between').first().remove();
        }
      });

      $('#lead-filter-stage button').on('click', function () {
        $('#lead-filter-stage button').removeClass('active');
        $(this).addClass('active');
        dt_NewCustomers.column(1).search($(this).data('filter')).draw();
      });

      $('#lead-filter-source button').on('click', function () {
        $('#lead-filter-source button').removeClass('active');
        $(this).addClass('active');
        dt_NewCustomers.column(2).search($(this).data('filter')).draw();
      });

      $('#lead-filter-overdue').on('click', function () {
        _leadOverdueActive = !_leadOverdueActive;
        $(this).toggleClass('btn-danger btn-outline-danger');
        dt_NewCustomers.draw();
      });
    }

    /* ── 4. Top Opportunities DataTable ──────────────────────────── */
    if ($('#dt_ScrollVertical').length) {
      $('#dt_ScrollVertical').DataTable({
        data: opps,
        searching: true,
        pageLength: 10,
        select: false,
        lengthChange: false,
        info: true,
        paging: true,
        order: [[4, 'desc']],
        language: {
          search: '',
          searchPlaceholder: 'Search',
          paginate: {
            previous: "<i class='fi fi-rr-angle-left'></i>",
            next:     "<i class='fi fi-rr-angle-right'></i>",
            first:    "<i class='fi fi-rr-angle-double-left'></i>",
            last:     "<i class='fi fi-rr-angle-double-right'></i>"
          }
        },
        columns: [
          {
            data: 'owner_id',
            className: 'dt-body-left',
            render: function (val, type, row, meta) {
              if (type !== 'display') return val;
              var u = userMap[val];
              var n = (meta.row % AVATARS_LEN) + 1;
              return '<div class="d-flex align-items-center">' +
                '<div class="avatar avatar-xxs rounded-circle me-2"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>' +
                (u ? u.display_name : val) + '</div>';
            }
          },
          { data: 'account_name', className: 'dt-body-left' },
          { data: 'name', className: 'dt-body-left' },
          {
            data: 'stage',
            className: 'dt-body-center',
            render: function (val, type) {
              return type === 'display' ? (oppStageBadge[val] || val) : val;
            }
          },
          {
            data: 'amount',
            className: 'dt-body-right',
            render: function (val, type) {
              if (type !== 'display') return val;
              return '<span class="fw-bold">PKR ' + Number(val).toLocaleString('en-IN') + '</span>';
            }
          },
          {
            data: 'close_date',
            className: 'dt-body-center',
            render: function (val, type) {
              if (type !== 'display') return val;
              return fmtDate(val);
            }
          }
        ],
        initComplete: function () {
          var dtSearch = $('#dt_ScrollVertical_wrapper .dt-search').detach();
          $('#dt_ScrollVertical_Search').append(dtSearch);
          $('#dt_ScrollVertical_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
          $('#dt_ScrollVertical_Search .dt-search label').remove();
          $('#dt_ScrollVertical_wrapper > .row.mt-2.justify-content-between').first().remove();
        }
      });
    }
  }

  /* ── Load: live API or dummy fallback ─────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.leads.list({ limit: 200 }),
      window.CRM_API.opportunities.list({ limit: 200 }),
      window.CRM_API.followups.list({ limit: 200 }),
      window.CRM_API.users.list()
    ])
    .then(function (results) {
      var leads     = (results[0].data) || [];
      var opps      = (results[1].data) || [];
      var followups = (results[2].data) || [];
      var users     = (results[3].data) || [];
      var userMap   = {};
      users.forEach(function (u) { userMap[u.id] = u; });
      render(leads, opps, followups, userMap);
    })
    .catch(function () {
      if (!_d) return;
      render(_d.leads.data, _d.opportunities.data, _d.followups.data, _d.userMap || {});
    });
  } else {
    if (!_d) return;
    render(_d.leads.data, _d.opportunities.data, _d.followups.data, _d.userMap || {});
  }

})();
