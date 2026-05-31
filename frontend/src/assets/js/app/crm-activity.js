/* Pakistan CRM — Activity Feed (B-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var eventCfg = {
    call:         { icon:'fi-rr-phone',         label:'Call',         cls:'bg-primary-subtle text-primary'     },
    email:        { icon:'fi-rr-envelope',       label:'Email',        cls:'bg-info-subtle text-info'           },
    whatsapp:     { icon:'fi-brands-whatsapp',   label:'WhatsApp',     cls:'bg-success-subtle text-success'     },
    meeting:      { icon:'fi-rr-calendar',       label:'Meeting',      cls:'bg-warning-subtle text-warning'     },
    note:         { icon:'fi-rr-note',           label:'Note',         cls:'bg-secondary-subtle text-secondary' },
    stage_change: { icon:'fi-rr-arrows-repeat',  label:'Stage Change', cls:'bg-primary-subtle text-primary'     },
    deal_won:     { icon:'fi-rr-trophy',         label:'Deal Won',     cls:'bg-success-subtle text-success'     }
  };

  function relTime(iso) {
    var diff = Math.floor((new Date() - new Date(iso)) / 86400000);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Yesterday';
    if (diff < 7)   return diff + ' days ago';
    return new Date(iso).toLocaleDateString('en-PK', { day:'2-digit', month:'short', year:'numeric' });
  }
  function eventBadge(type) {
    var c = eventCfg[type] || { icon:'fi-rr-circle', label:type, cls:'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '"><i class="' + c.icon + ' me-1"></i>' + c.label + '</span>';
  }
  function linkedRecordHtml(activity, leadMap, oppMap) {
    var typeMap = { lead:['bg-info-subtle text-info','Lead'], opportunity:['bg-primary-subtle text-primary','Opportunity'], contact:['bg-secondary-subtle text-secondary','Contact'] };
    var cfg2 = typeMap[activity.entity_type];
    if (!cfg2) return '<span class="text-muted">—</span>';
    var name = '';
    if (activity.entity_type === 'lead' && leadMap[activity.entity_id])        name = leadMap[activity.entity_id].contact_name;
    else if (activity.entity_type === 'opportunity' && oppMap[activity.entity_id]) name = oppMap[activity.entity_id].name;
    return '<span class="badge ' + cfg2[0] + ' me-1">' + cfg2[1] + '</span>' + (name ? '<span class="text-body-secondary small">' + name + '</span>' : '');
  }
  function actorHtml(userId, userMap, rowIdx) {
    var u = userMap[userId];
    if (!u) return userId || '—';
    var n = (rowIdx % 5) + 1;
    return '<div class="d-flex align-items-center justify-content-center gap-1"><div class="avatar avatar-xxs rounded-circle"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div><span>' + u.display_name + '</span></div>';
  }
  function actionHtml() {
    return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
      '<ul class="dropdown-menu dropdown-menu-end">' +
      '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-eye me-2 text-primary"></i>View Record</a></li>' +
      '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-clipboard-list me-2 text-secondary"></i>View Audit Detail</a></li>' +
      '</ul></div>';
  }

  function render(activities, users, leads, opps) {
    var userMap = {}, leadMap = {}, oppMap = {};
    users.forEach(function (u) { userMap[u.id] = u; });
    leads.forEach(function (l) { leadMap[l.lead_id] = l; });
    opps.forEach(function (o) { oppMap[o.opportunity_id] = o; });

    var sorted = activities.slice().sort(function (a, b) { return new Date(b.occurred_at) - new Date(a.occurred_at); });

    $('#kpi-total-activities').text(activities.length);
    $('#kpi-calls').text(activities.filter(function (a) { return a.activity_type === 'call'; }).length);
    $('#kpi-meetings').text(activities.filter(function (a) { return a.activity_type === 'meeting'; }).length);
    $('#kpi-deals-won').text(activities.filter(function (a) { return a.activity_type === 'deal_won'; }).length);

    users.forEach(function (u) {
      var firstName = (u.display_name || '').split(' ')[0];
      $('#activity-filter-actor').append('<li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="' + u.id + '">' + firstName + '</button></li>');
    });

    if (!$('#dt_Activities').length) return;

    var _typeFilter = '', _actorFilter = '';
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Activities') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_typeFilter  && $row.data('type')  !== _typeFilter)  return false;
      if (_actorFilter && $row.data('actor') !== _actorFilter) return false;
      return true;
    });

    var dtActivities = $('#dt_Activities').DataTable({
      data: sorted, searching:true, pageLength:10, select:false, lengthChange:false, info:true, paging:true, order:[],
      language:{ search:'', searchPlaceholder:'Search activities…', paginate:{ previous:"<i class='fi fi-rr-angle-left'></i>", next:"<i class='fi fi-rr-angle-right'></i>", first:"<i class='fi fi-rr-angle-double-left'></i>", last:"<i class='fi fi-rr-angle-double-right'></i>" } },
      columns: [
        { data:'activity_type', className:'dt-body-center', render:function (val, type) { return type !== 'display' ? val : eventBadge(val); } },
        { data:'description',   className:'dt-body-left', defaultContent:'—' },
        { data:'performed_by',  className:'dt-body-center', render:function (val, type, row, meta) { return type !== 'display' ? val : actorHtml(val, userMap, meta.row); }, defaultContent:'—' },
        { data:'entity_id',     className:'dt-body-left', orderable:false, render:function (val, type, row) { return type !== 'display' ? (row.entity_type || '') : linkedRecordHtml(row, leadMap, oppMap); }, defaultContent:'—' },
        { data:'occurred_at',   className:'dt-body-center', render:function (val, type) { return type !== 'display' ? val : relTime(val); }, defaultContent:'—' },
        { data:null, className:'dt-body-center', orderable:false, render:function (val, type) { return type !== 'display' ? '' : actionHtml(); } }
      ],
      createdRow:function (row, data) { $(row).attr('data-type', data.activity_type || '').attr('data-actor', data.performed_by || ''); },
      initComplete:function () {
        var s = $('#dt_Activities_wrapper .dt-search').detach();
        $('#dt_Activities_Search').append(s);
        $('#dt_Activities_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Activities_Search .dt-search label').remove();
        $('#dt_Activities_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#activity-filter-type button').on('click', function () { $('#activity-filter-type button').removeClass('active'); $(this).addClass('active'); _typeFilter = $(this).data('filter'); dtActivities.draw(); });
    $('#activity-filter-actor').on('click', 'button', function () { $('#activity-filter-actor button').removeClass('active'); $(this).addClass('active'); _actorFilter = $(this).data('filter'); dtActivities.draw(); });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.activities.list({ limit: 500 }),
      window.CRM_API.users.list(),
      window.CRM_API.leads.list({ limit: 200 }),
      window.CRM_API.opportunities.list({ limit: 200 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || [], results[2].data || [], results[3].data || []);
    }).catch(function () {
      render(
        (_d && _d.activities && _d.activities.data) || [],
        (_d && _d.users && _d.users.data) || [],
        (_d && _d.leads && _d.leads.data) || [],
        (_d && _d.opportunities && _d.opportunities.data) || []
      );
    });
  } else {
    if (!_d) return;
    render(_d.activities.data || [], _d.users.data || [], _d.leads.data || [], _d.opportunities.data || []);
  }

})();
