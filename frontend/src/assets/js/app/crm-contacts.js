/* Pakistan CRM — Contact List (B-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function computeKpi(rows) {
    var total      = rows.length;
    var waActive   = rows.filter(function (c) { return c.whatsapp_active || c.phone_e164; }).length;
    var openCases  = rows.reduce(function (s, c) { return s + (Number(c.open_cases) || 0); }, 0);
    var idleCount  = rows.filter(function (c) { return c.idle === 1 || c.idle === true; }).length;
    var now        = new Date();
    var weekAgo    = new Date(now.getTime() - 7 * 86400000);
    var newMonth   = rows.filter(function (c) { return c.created_at && new Date(c.created_at) > weekAgo; }).length;
    return { total: total, whatsapp_active: waActive, open_cases: openCases, idle_7d: idleCount, new_this_month: newMonth };
  }

  function render(rows) {
    var kpi = computeKpi(rows);

    $('#kpi-total-contacts').text(kpi.total.toLocaleString('en-IN'));
    $('#kpi-whatsapp-active').text(kpi.whatsapp_active.toLocaleString('en-IN'));
    $('#kpi-open-cases').text(kpi.open_cases);
    $('#kpi-idle-7d').text(kpi.idle_7d);

    if (kpi.new_this_month !== undefined) $('#kpi-contacts-new-month').text('+' + kpi.new_this_month);
    var waP = kpi.total > 0 ? Math.round(kpi.whatsapp_active / kpi.total * 1000) / 10 : 0;
    $('#kpi-whatsapp-pct').text(waP.toFixed(1));
    $('#kpi-cases-contact-count').text(kpi.open_cases);

    if (!$('#dt_Contacts').length) return;

    var _contactOpenCaseActive = false, _contactIdleActive = false;
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Contacts') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_contactOpenCaseActive && !$row.data('open-cases')) return false;
      if (_contactIdleActive && $row.data('idle') !== 1) return false;
      return true;
    });

    var dtContacts = $('#dt_Contacts').DataTable({
      data: rows,
      searching: true, pageLength: 10, select: false, lengthChange: false, info: true, paging: true, order: [[3,'asc']],
      language: { search:'', searchPlaceholder:'Search contacts', paginate:{ previous:"<i class='fi fi-rr-angle-left'></i>", next:"<i class='fi fi-rr-angle-right'></i>", first:"<i class='fi fi-rr-angle-double-left'></i>", last:"<i class='fi fi-rr-angle-double-right'></i>" } },
      columns: [
        {
          data:'display_name', className:'dt-body-left', orderable:false,
          render:function (val, type, row, meta) {
            if (type !== 'display') return val;
            var n = (meta.row % 10) + 1;
            return '<div class="d-flex align-items-center"><div class="avatar avatar-xxs rounded-circle me-2"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>' +
              '<div>' + val + '<div class="text-muted small">' + (row.email || '') + '</div></div></div>';
          }
        },
        { data:'phone_e164',     className:'dt-body-left', defaultContent:'—' },
        { data:'account_name',   className:'dt-body-left', defaultContent:'—' },
        { data:'last_touchpoint',className:'dt-body-center', defaultContent:'—' },
        {
          data:'open_cases', className:'dt-body-center',
          render:function (val, type) {
            if (type !== 'display') return val;
            return val > 0 ? '<span class="badge bg-warning-subtle text-warning">' + val + '</span>' : '<span class="text-muted">—</span>';
          },
          defaultContent:'0'
        },
        {
          data:'tags', className:'dt-body-left',
          render:function (val, type) {
            if (type !== 'display') return Array.isArray(val) ? val.join(' ') : (val || '');
            if (!Array.isArray(val) || !val.length) return '<span class="text-muted">—</span>';
            return val.map(function (t) { return '<span class="badge bg-primary-subtle text-primary me-1">' + t + '</span>'; }).join('');
          },
          defaultContent:''
        },
        {
          data:null, className:'dt-body-center', orderable:false,
          render:function (val, type, row) {
            if (type !== 'display') return '';
            return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
              '<ul class="dropdown-menu dropdown-menu-end">' +
              '<li><a class="dropdown-item" href="app/contacts-detail.html?id=' + (row.contact_id || '') + '"><i class="fi fi-rr-eye me-2 text-primary"></i>View Profile</a></li>' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-brands-whatsapp me-2 text-success"></i>WhatsApp</a></li>' +
              '</ul></div>';
          }
        }
      ],
      createdRow:function (row, data) {
        if (data.open_cases > 0) $(row).attr('data-open-cases', data.open_cases);
        if (data.idle === 1 || data.idle === true) $(row).attr('data-idle', 1);
      },
      initComplete:function () {
        var s = $('#dt_Contacts_wrapper .dt-search').detach();
        $('#dt_Contacts_Search').append(s);
        $('#dt_Contacts_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Contacts_Search .dt-search label').remove();
        $('#dt_Contacts_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#contact-filter-tag button').on('click', function () { $('#contact-filter-tag button').removeClass('active'); $(this).addClass('active'); dtContacts.column(5).search($(this).data('filter')).draw(); });
    $('#contact-filter-open-case').on('click', function () { _contactOpenCaseActive = !_contactOpenCaseActive; $(this).toggleClass('btn-warning btn-outline-warning'); dtContacts.draw(); });
    $('#contact-filter-idle').on('click', function () { _contactIdleActive = !_contactIdleActive; $(this).toggleClass('btn-info btn-outline-secondary'); dtContacts.draw(); });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.contacts.list({ limit: 200 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.contacts && _d.contacts.data) || []); });
  } else {
    if (!_d) return;
    render(_d.contacts.data || []);
  }

})();
