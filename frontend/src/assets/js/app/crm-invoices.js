/* Pakistan CRM — Invoice Queue (B-09) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) {
    if (!n && n !== 0) return '—';
    n = Number(n);
    if (n >= 10000000) return 'PKR ' + (n / 10000000).toFixed(2) + ' Cr';
    if (n >= 100000)   return 'PKR ' + (n / 100000).toFixed(2) + ' L';
    return 'PKR ' + n.toLocaleString('en-IN');
  }

  var statusCfg = {
    draft:   { label:'Draft',   cls:'bg-secondary-subtle text-secondary' },
    sent:    { label:'Sent',    cls:'bg-info-subtle text-info'           },
    paid:    { label:'Paid',    cls:'bg-success-subtle text-success'     },
    partial: { label:'Partial', cls:'bg-warning-subtle text-warning'     },
    overdue: { label:'Overdue', cls:'bg-danger-subtle text-danger'       },
    void:    { label:'Void',    cls:'bg-secondary-subtle text-secondary' }
  };

  function statusBadge(status) {
    var c = statusCfg[status] || { label:status, cls:'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '">' + c.label + '</span>';
  }

  function actionHtml(inv) {
    return '<div class="btn-group">' +
      '<button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown">' +
      '<i class="fi fi-rr-menu-dots"></i></button>' +
      '<ul class="dropdown-menu dropdown-menu-end">' +
      '<li><a class="dropdown-item" href="javascript:void(0);">' +
      '<i class="fi fi-rr-hand-holding-usd me-2 text-success"></i>Record Payment</a></li>' +
      '<li><a class="dropdown-item" href="javascript:void(0);">' +
      '<i class="fi fi-rr-download me-2 text-primary"></i>Download PDF</a></li>' +
      '<li><a class="dropdown-item" href="app/invoices-detail.html">' +
      '<i class="fi fi-rr-eye me-2 text-info"></i>Open Detail</a></li>' +
      '</ul></div>';
  }

  function render(invoices) {
    if (!$('#dt_Invoices').length) return;

    var totalInvoiced  = invoices.reduce(function (s, i) { return s + (Number(i.total_amount) || 0); }, 0);
    var totalPaid      = invoices.reduce(function (s, i) { return s + (Number(i.paid_amount)  || 0); }, 0);
    var outstanding    = totalInvoiced - totalPaid;
    var paidThisMonth  = invoices.filter(function (i) { return i.status === 'paid'; })
                                 .reduce(function (s, i) { return s + (Number(i.paid_amount) || 0); }, 0);
    var overdueCount   = invoices.filter(function (i) { return i.status === 'overdue'; }).length;

    $('#kpi-total-invoiced').text(pkr(totalInvoiced));
    $('#kpi-outstanding').text(pkr(outstanding));
    $('#kpi-paid-month').text(pkr(paidThisMonth));
    $('#kpi-overdue-count').text(overdueCount);

    var _statusFilter = '';

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Invoices') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_statusFilter && $row.data('status') !== _statusFilter) return false;
      return true;
    });

    var dtInvoices = $('#dt_Invoices').DataTable({
      data: invoices,
      searching: true,
      pageLength: 10,
      lengthChange: false,
      order: [[6, 'asc']],
      language: {
        search: '', searchPlaceholder: 'Search invoices…',
        paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" }
      },
      columns: [
        {
          data: 'invoice_number', className: 'dt-body-center',
          render: function (val) { return '<span class="fw-semibold">' + val + '</span>'; }
        },
        { data: 'account_name', className: 'dt-body-center', defaultContent: '—' },
        {
          data: 'total_amount', className: 'dt-body-center',
          render: function (val, type) { return type !== 'display' ? val : pkr(val); }
        },
        {
          data: 'paid_amount', className: 'dt-body-center',
          render: function (val, type) { return type !== 'display' ? val : pkr(val); }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) {
            if (type !== 'display') return (Number(row.total_amount) || 0) - (Number(row.paid_amount) || 0);
            var bal = (Number(row.total_amount) || 0) - (Number(row.paid_amount) || 0);
            return bal > 0
              ? '<span class="text-danger fw-semibold">' + pkr(bal) + '</span>'
              : '<span class="text-success">' + pkr(0) + '</span>';
          }
        },
        {
          data: 'status', className: 'dt-body-center',
          render: function (val, type) { return type !== 'display' ? val : statusBadge(val); }
        },
        {
          data: 'due_date', className: 'dt-body-center', defaultContent: '—',
          render: function (val, type, row) {
            if (type !== 'display') return val;
            return row.status === 'overdue'
              ? '<span class="text-danger fw-semibold">' + val + '</span>'
              : (val || '—');
          }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : actionHtml(row); }
        }
      ],
      createdRow: function (row, data) {
        $(row).attr('data-status', data.status || '');
      },
      initComplete: function () {
        var dtSearch = $('#dt_Invoices_wrapper .dt-search').detach();
        $('#dt_Invoices_Search').append(dtSearch);
        $('#dt_Invoices_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Invoices_Search .dt-search label').remove();
        $('#dt_Invoices_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#inv-filter-status button').on('click', function () {
      $('#inv-filter-status button').removeClass('active');
      $(this).addClass('active');
      _statusFilter = $(this).data('filter');
      dtInvoices.draw();
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.invoiceSummaries.get({ limit: 200 })
      .then(function (res) { render(Array.isArray(res.data) ? res.data : (res.data ? [res.data] : [])); })
      .catch(function () {
        var inv = (_d && _d.invoices && _d.invoices.data) || [];
        render(inv);
      });
  } else {
    if (!_d) return;
    render((_d.invoices && _d.invoices.data) || []);
  }

})();
