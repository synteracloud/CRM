/* Pakistan CRM — Collections Queue Page Driver */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  /* ── Module-level filter state ────────────────────────────────────── */
  var _collOverdueActive = false;
  var _amountMin = 0, _amountMax = 999999999;

  /* ── PKR formatter ────────────────────────────────────────────────── */
  function pkr(n) {
    return 'PKR ' + Number(n || 0).toLocaleString('en-IN');
  }

  /* ── KPI computation from raw invoice array ───────────────────────── */
  function computeKpi(invoices) {
    var today      = new Date().toISOString().slice(0, 7); // YYYY-MM
    var outstanding = 0, overdueCount = 0, overdueValue = 0, paidMonth = 0, totalDue = 0, totalPaid = 0;

    invoices.forEach(function (inv) {
      var amt = Number(inv.amount_due) || 0;
      if (inv.status !== 'paid' && inv.status !== 'void' && inv.status !== 'uncollectible') {
        outstanding += amt;
        totalDue += amt;
      }
      if (inv.is_overdue) {
        overdueCount++;
        overdueValue += amt;
      }
      if (inv.status === 'paid') {
        totalPaid += amt;
        if (inv.due_date && inv.due_date.startsWith(today)) paidMonth += amt;
      }
    });

    var collectionRate = totalDue > 0 ? Math.round((totalPaid / (totalDue + totalPaid)) * 100) : 0;

    return {
      total_outstanding:    outstanding,
      overdue_count:        overdueCount,
      overdue_value:        overdueValue,
      paid_this_month:      paidMonth,
      collection_rate:      collectionRate,
      paid_this_month_delta: undefined,
      collection_rate_delta: undefined
    };
  }

  /* ── Badge helpers ────────────────────────────────────────────────── */
  var statusBadge = {
    draft:         '<span class="badge bg-secondary-subtle text-secondary">Draft</span>',
    open:          '<span class="badge bg-warning-subtle text-warning">Open</span>',
    overdue:       '<span class="badge bg-danger-subtle text-danger">Overdue</span>',
    partial:       '<span class="badge bg-info-subtle text-info">Partial</span>',
    unpaid:        '<span class="badge bg-warning-subtle text-warning">Unpaid</span>',
    paid:          '<span class="badge bg-success-subtle text-success">Paid</span>',
    void:          '<span class="badge bg-dark-subtle text-dark">Void</span>',
    uncollectible: '<span class="badge bg-danger-subtle text-danger">Uncollectible</span>'
  };

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function fmtDate(iso) {
    if (!iso) return '—';
    var parts = iso.split('-');
    return MONTHS[parseInt(parts[1], 10) - 1] + ' ' + parseInt(parts[2], 10) + ', ' + parts[0];
  }

  /* ── Custom search extension ──────────────────────────────────────── */
  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    if (settings.nTable.id !== 'dt_Collections') return true;
    var rowNode = settings.aoData[dataIndex].nTr;
    if (_collOverdueActive && $(rowNode).data('overdue') !== 1) return false;
    var amount = parseFloat($(rowNode).data('amount')) || 0;
    if (amount < _amountMin || amount > _amountMax) return false;
    return true;
  });

  /* ── Core render — works with live or dummy data ──────────────────── */
  function render(rows, kpi) {
    /* KPI cards */
    $('#kpi-total-outstanding').text(pkr(kpi.total_outstanding));
    $('#kpi-overdue-inv').text(kpi.overdue_count);
    $('#kpi-paid-this-month').text(pkr(kpi.paid_this_month));
    $('#kpi-collection-rate').text(kpi.collection_rate + '%');

    /* KPI delta badges */
    if (kpi.paid_this_month_delta !== undefined) {
      var pd = kpi.paid_this_month_delta;
      $('#kpi-paid-delta').text((pd >= 0 ? '+' : '') + pd + '%')
        .removeClass('text-success text-danger')
        .addClass(pd >= 0 ? 'text-success' : 'text-danger');
    } else {
      $('#kpi-paid-delta').text('—');
    }
    if (kpi.collection_rate_delta !== undefined) {
      var rd = kpi.collection_rate_delta;
      $('#kpi-rate-delta').text((rd >= 0 ? '+' : '') + rd + '%')
        .removeClass('text-success text-danger')
        .addClass(rd >= 0 ? 'text-success' : 'text-danger');
    } else {
      $('#kpi-rate-delta').text('—');
    }

    /* Enforcement strip */
    var oc = kpi.overdue_count;
    $('#overdue-invoice-count').text(oc);
    $('#overdue-invoice-plural').text(oc === 1 ? ' is' : 's are');
    $('#overdue-total-value').text(pkr(kpi.overdue_value));
    if (oc === 0) $('#collections-posture-row').addClass('d-none');

    if (!$('#dt_Collections').length) return;

    var dtCollections = $('#dt_Collections').DataTable({
      data: rows,
      searching: true,
      pageLength: 10,
      select: false,
      lengthChange: false,
      info: true,
      paging: true,
      order: [[4, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Search invoices',
        paginate: {
          previous: "<i class='fi fi-rr-angle-left'></i>",
          next:     "<i class='fi fi-rr-angle-right'></i>",
          first:    "<i class='fi fi-rr-angle-double-left'></i>",
          last:     "<i class='fi fi-rr-angle-double-right'></i>"
        }
      },
      columns: [
        {
          data: 'invoice_number',
          className: 'dt-body-center',
          orderable: false,
          render: function (val, type) {
            if (type !== 'display') return val;
            return '<span class="fw-semibold">' + val + '</span>';
          }
        },
        {
          data: 'account_name',
          className: 'dt-body-center',
          render: function (val, type, row) {
            if (type !== 'display') return val;
            return '<div>' + val + '<div class="text-muted small">' + (row.account_tier || '') + '</div></div>';
          }
        },
        {
          data: 'amount_due',
          className: 'dt-body-center',
          render: function (val, type) {
            if (type !== 'display') return val;
            return '<span class="fw-semibold">' + pkr(val) + '</span>';
          }
        },
        {
          data: 'status',
          className: 'dt-body-center',
          render: function (val, type, row) {
            if (type !== 'display') return val;
            if (row && row.is_overdue) return statusBadge.overdue;
            return statusBadge[val] || val;
          }
        },
        {
          data: 'due_date',
          className: 'dt-body-center',
          render: function (val, type, row) {
            if (type === 'sort' || type === 'type') return val;
            var cls = row.is_overdue ? 'text-danger fw-semibold' : '';
            return '<span class="' + cls + '">' + fmtDate(val) + '</span>';
          }
        },
        {
          data: 'last_reminder_at',
          className: 'dt-body-center',
          render: function (val, type) {
            if (type !== 'display') return val;
            if (!val) return '<span class="text-muted">—</span>';
            var diff = Math.floor((Date.now() - new Date(val).getTime()) / 60000);
            if (diff < 60)   return diff + ' min ago';
            if (diff < 1440) return Math.floor(diff / 60) + ' hrs ago';
            if (diff < 2880) return 'Yesterday';
            return Math.floor(diff / 1440) + ' days ago';
          }
        },
        {
          data: null,
          className: 'dt-body-center',
          orderable: false,
          render: function (val, type) {
            if (type !== 'display') return '';
            return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
              '<ul class="dropdown-menu dropdown-menu-end">' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-dollar me-2 text-success"></i>Record Payment</a></li>' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-megaphone me-2 text-warning"></i>Send Reminder</a></li>' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-escalator me-2 text-danger"></i>Escalate</a></li>' +
              '</ul></div>';
          }
        }
      ],
      createdRow: function (row, data) {
        if (data.is_overdue) $(row).attr('data-overdue', 1);
        $(row).attr('data-amount', data.amount_due); /* fixed: was data.amount */
      },
      initComplete: function () {
        var dtSearch = $('#dt_Collections_wrapper .dt-search').detach();
        $('#dt_Collections_Search').append(dtSearch);
        $('#dt_Collections_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Collections_Search .dt-search label').remove();
        $('#dt_Collections_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    /* Filter chips */
    $('#coll-filter-status button').on('click', function () {
      $('#coll-filter-status button').removeClass('active');
      $(this).addClass('active');
      dtCollections.column(3).search($(this).data('filter')).draw();
    });

    $('#coll-filter-amount button').on('click', function () {
      $('#coll-filter-amount button').removeClass('active');
      $(this).addClass('active');
      _amountMin = parseFloat($(this).data('min')) || 0;
      _amountMax = parseFloat($(this).data('max')) || 999999999;
      dtCollections.draw();
    });

    $('#coll-filter-overdue, #show-overdue-invoices').on('click', function () {
      _collOverdueActive = !_collOverdueActive;
      $('#coll-filter-overdue').toggleClass('btn-danger btn-outline-danger');
      dtCollections.draw();
    });
  }

  /* ── Load: live API or dummy fallback ─────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.collections.list({ limit: 200 })
      .then(function (res) {
        var invoices = res.data || [];
        render(invoices, computeKpi(invoices));
      })
      .catch(function () {
        var fb = (_d && _d.collections && _d.collections.data) || [];
        render(fb, (_d && _d.collectionsKpi) || computeKpi(fb));
      });
  } else {
    if (!_d) return;
    render(_d.collections.data, _d.collectionsKpi);
  }

})();
