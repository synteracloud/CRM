/* Pakistan CRM — Task Queue (B-07) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function isOverdue(task) { return task.status !== 'completed' && new Date(task.due_at) < new Date(); }
  function fmtDue(task) {
    var dd    = new Date(task.due_at);
    var label = dd.toLocaleDateString('en-PK', { day:'2-digit', month:'short', year:'numeric' });
    if (isOverdue(task)) return '<span class="text-danger fw-semibold">' + label + '</span> <span class="badge bg-danger-subtle text-danger ms-1">Overdue</span>';
    return label;
  }
  function statusBadge(status) {
    var c = { open:['bg-warning-subtle text-warning','Open'], in_progress:['bg-primary-subtle text-primary','In Progress'], completed:['bg-success-subtle text-success','Completed'] }[status] || ['bg-secondary-subtle text-secondary', status];
    return '<span class="badge ' + c[0] + '">' + c[1] + '</span>';
  }

  function render(tasks, users, leads, opps, contacts) {
    var userMap = {}, leadMap = {}, oppMap = {}, contactMap = {};
    users.forEach(function (u) { userMap[u.id] = u; });
    leads.forEach(function (l) { leadMap[l.lead_id] = l; });
    opps.forEach(function (o) { oppMap[o.opportunity_id] = o; });
    contacts.forEach(function (c) { contactMap[c.contact_id] = c; });

    function entityHtml(task) {
      if (!task.entity_type) return '<span class="text-muted">—</span>';
      var typeMap = { lead:['bg-info-subtle text-info','Lead'], opportunity:['bg-primary-subtle text-primary','Opportunity'], contact:['bg-secondary-subtle text-secondary','Contact'] };
      var c = typeMap[task.entity_type];
      if (!c) return '<span class="text-muted">—</span>';
      var name = '';
      if (task.entity_type === 'lead' && leadMap[task.entity_id])          name = leadMap[task.entity_id].contact_name;
      else if (task.entity_type === 'opportunity' && oppMap[task.entity_id]) name = oppMap[task.entity_id].name;
      else if (task.entity_type === 'contact' && contactMap[task.entity_id])name = contactMap[task.entity_id].display_name;
      return '<span class="badge ' + c[0] + ' me-1">' + c[1] + '</span>' + (name ? '<span class="text-body-secondary small">' + name + '</span>' : '');
    }
    function ownerHtml(ownerId, rowIdx) {
      var u = userMap[ownerId];
      if (!u) return ownerId || '—';
      var n = (rowIdx % 5) + 1;
      return '<div class="d-flex align-items-center justify-content-center gap-1"><div class="avatar avatar-xxs rounded-circle"><img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div><span>' + u.display_name + '</span></div>';
    }
    function actionHtml(task) {
      var completeBtn = task.status !== 'completed'
        ? '<button class="btn btn-subtle-success btn-sm btn-shadow btn-icon btn-complete-task me-1" data-task-id="' + task.task_id + '" title="Mark complete"><i class="fi fi-rr-check"></i></button>' : '';
      return completeBtn + '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
        '<ul class="dropdown-menu dropdown-menu-end">' +
        '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-clock me-2 text-warning"></i>Snooze</a></li>' +
        '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-user-add me-2 text-primary"></i>Reassign</a></li>' +
        '</ul></div>';
    }

    var sortedTasks = tasks.slice().sort(function (a, b) {
      var aO = isOverdue(a) ? 0 : 1, bO = isOverdue(b) ? 0 : 1;
      if (aO !== bO) return aO - bO;
      return new Date(a.due_at) - new Date(b.due_at);
    });

    function refreshKpis(dtInstance) {
      var all = dtInstance ? dtInstance.data().toArray() : tasks;
      $('#kpi-total-tasks').text(all.length);
      $('#kpi-open-tasks').text(all.filter(function (t) { return t.status === 'open' || t.status === 'in_progress'; }).length);
      $('#kpi-overdue-tasks').text(all.filter(isOverdue).length);
      $('#kpi-completed-tasks').text(all.filter(function (t) { return t.status === 'completed'; }).length);
    }
    refreshKpis(null);

    users.forEach(function (u) {
      var firstName = (u.display_name || '').split(' ')[0];
      $('#task-filter-owner').append('<li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="' + u.id + '">' + firstName + '</button></li>');
    });

    if (!$('#dt_Tasks').length) return;

    var _overdueOnly = false, _entityFilter = '', _ownerFilter = '';
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Tasks') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_overdueOnly  && !$row.data('overdue'))                      return false;
      if (_entityFilter && $row.data('entity-type') !== _entityFilter) return false;
      if (_ownerFilter  && $row.data('owner')        !== _ownerFilter) return false;
      return true;
    });

    var dtTasks = $('#dt_Tasks').DataTable({
      data: sortedTasks, searching:true, pageLength:10, select:false, lengthChange:false, info:true, paging:true, order:[],
      language:{ search:'', searchPlaceholder:'Search tasks…', paginate:{ previous:"<i class='fi fi-rr-angle-left'></i>", next:"<i class='fi fi-rr-angle-right'></i>", first:"<i class='fi fi-rr-angle-double-left'></i>", last:"<i class='fi fi-rr-angle-double-right'></i>" } },
      columns: [
        {
          data:'title', className:'dt-body-left',
          render:function (val, type, row) {
            if (type !== 'display') return val;
            var dot = row.priority === 'hot' ? '<span class="badge bg-danger-subtle text-danger me-1">hot</span>' : row.priority === 'warm' ? '<span class="badge bg-warning-subtle text-warning me-1">warm</span>' : '';
            return dot + val;
          }
        },
        { data:'entity_id', className:'dt-body-left', orderable:false, render:function (val, type, row) { return type !== 'display' ? (row.entity_type || '') : entityHtml(row); }, defaultContent:'—' },
        { data:'owner_id', className:'dt-body-center', render:function (val, type, row, meta) { return type !== 'display' ? val : ownerHtml(val, meta.row); }, defaultContent:'—' },
        { data:'due_at', className:'dt-body-center', render:function (val, type, row) { return type !== 'display' ? val : fmtDue(row); }, defaultContent:'—' },
        { data:'status', className:'dt-body-center', render:function (val, type) { return type !== 'display' ? val : statusBadge(val); }, defaultContent:'—' },
        { data:null, className:'dt-body-center', orderable:false, render:function (val, type, row) { return type !== 'display' ? '' : actionHtml(row); } }
      ],
      createdRow:function (row, data) {
        if (isOverdue(data))  $(row).attr('data-overdue', 1);
        if (data.entity_type) $(row).attr('data-entity-type', data.entity_type);
        $(row).attr('data-owner', data.owner_id || '');
      },
      initComplete:function () {
        var s = $('#dt_Tasks_wrapper .dt-search').detach();
        $('#dt_Tasks_Search').append(s);
        $('#dt_Tasks_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Tasks_Search .dt-search label').remove();
        $('#dt_Tasks_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#task-filter-entity button').on('click', function () { $('#task-filter-entity button').removeClass('active'); $(this).addClass('active'); _entityFilter = $(this).data('filter'); dtTasks.draw(); });
    $('#task-filter-owner').on('click', 'button', function () { $('#task-filter-owner button').removeClass('active'); $(this).addClass('active'); _ownerFilter = $(this).data('filter'); dtTasks.draw(); });
    $('#task-filter-overdue').on('click', function () { _overdueOnly = !_overdueOnly; $(this).toggleClass('btn-danger btn-outline-danger'); dtTasks.draw(); });

    $('#dt_Tasks').on('click', '.btn-complete-task', function () {
      var $tr = $(this).closest('tr');
      var rowData = dtTasks.row($tr).data();
      if (!rowData) return;
      var taskId = rowData.task_id;
      if (cfg && !cfg.DUMMY_MODE && taskId) {
        fetch(cfg.BASE_URL + '/tasks/' + taskId + '/complete', {
          method: 'POST', headers: { 'Authorization': 'Bearer ' + cfg.token, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId }
        }).catch(function () {});
      }
      rowData.status = 'completed';
      dtTasks.row($tr).data(rowData).draw(false);
      refreshKpis(dtTasks);
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.tasks.list({ limit: 200 }),
      window.CRM_API.users.list(),
      window.CRM_API.leads.list({ limit: 200 }),
      window.CRM_API.opportunities.list({ limit: 200 }),
      window.CRM_API.contacts.list({ limit: 200 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || [], results[2].data || [], results[3].data || [], results[4].data || []);
    }).catch(function () {
      render(
        (_d && _d.tasks && _d.tasks.data) || [],
        (_d && _d.users && _d.users.data) || [],
        (_d && _d.leads && _d.leads.data) || [],
        (_d && _d.opportunities && _d.opportunities.data) || [],
        (_d && _d.contacts && _d.contacts.data) || []
      );
    });
  } else {
    if (!_d) return;
    render(_d.tasks.data || [], _d.users.data || [], _d.leads.data || [], _d.opportunities.data || [], (_d.contacts && _d.contacts.data) || []);
  }

})();
