/* Pakistan CRM — Audit Log (J-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var auditTable;

  function initDateRange() {
    var el = document.getElementById('auditDateRange');
    if (el && window.flatpickr) {
      flatpickr(el, {
        mode: 'range', dateFormat: 'Y-m-d',
        defaultDate: [new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), new Date()]
      });
    }
  }

  function initActorFilter(users) {
    var select = document.getElementById('auditActorFilter');
    if (!select) return;
    users.forEach(function (u) {
      var opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = u.display_name;
      select.appendChild(opt);
    });
    ['auditActorFilter', 'auditActionFilter', 'auditResourceFilter', 'auditResultFilter'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('change', function () { if (auditTable) auditTable.draw(); });
    });
    var exportBtn = document.getElementById('auditExportBtn');
    if (exportBtn) exportBtn.addEventListener('click', exportCsv);
  }

  function exportCsv() {
    if (!auditTable) return;
    var rows = auditTable.rows({ search: 'applied' }).data().toArray();
    var csv  = 'Timestamp,Actor,Action,Resource,Result\n' + rows.map(function (r) {
      return [r.occurred_at, r.actor_name || r.actor_id, r.action_type, (r.resource_type || '') + ' ' + (r.resource_id || ''), r.result].join(',');
    }).join('\n');
    var a = document.createElement('a');
    a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    a.download = 'audit-log.csv';
    a.click();
  }

  function render(log) {
    var totalBadge = document.getElementById('audit-total-badge');
    var denyBadge  = document.getElementById('audit-deny-badge');
    var denyCount  = log.filter(function (e) { return e.result === 'deny'; }).length;
    if (totalBadge) totalBadge.textContent = log.length + ' events';
    if (denyBadge)  denyBadge.textContent  = denyCount + ' denied';

    var el = document.getElementById('dt_AuditLog');
    if (!el || !window.DataTable) return;

    auditTable = new DataTable('#dt_AuditLog', {
      data: log,
      columns: [
        {
          data: 'occurred_at', className: 'dt-body-center',
          render: function (v) { return new Date(v).toLocaleString(); }
        },
        { data: 'actor_name', defaultContent: '—', className: 'dt-body-left' },
        { data: 'action_type', defaultContent: '—', className: 'dt-body-left' },
        {
          data: null, className: 'dt-body-left',
          render: function (v, t, row) { return (row.resource_type || '') + ' ' + (row.resource_id || ''); }
        },
        {
          data: 'result', defaultContent: 'allow', className: 'dt-body-center',
          render: function (v, t) {
            if (t !== 'display') return v;
            var cls = v === 'deny' ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success';
            return '<span class="badge ' + cls + '">' + (v || 'allow') + '</span>';
          }
        },
        { data: 'ip', defaultContent: '—', className: 'dt-body-center' },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (v, t, row) {
            if (t !== 'display') return '';
            return '<button class="btn btn-xs btn-outline-secondary waves-effect" onclick="alert(\'Evidence: \' + JSON.stringify(' + JSON.stringify({ actor: row.actor_name, action: row.action_type, resource: row.resource_type, result: row.result }) + '))">' +
              '<i class="fi fi-rr-eye me-1"></i>Evidence</button>';
          }
        }
      ],
      order: [[0, 'desc']],
      pageLength: 25,
      lengthChange: false,
      searching: true,
      language: {
        search: '', searchPlaceholder: 'Filter log…',
        paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" }
      }
    });
  }

  function load() {
    initDateRange();
    var users = (_d && _d.users && _d.users.data) || [];

    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        window.CRM_API.audits.list({ limit: 200 }),
        window.CRM_API.users.list()
      ]).then(function (results) {
        initActorFilter(results[1].data || users);
        render(results[0].data || []);
      }).catch(function () {
        initActorFilter(users);
        render((_d && _d.AUDIT_LOG) || []);
      });
    } else {
      initActorFilter(users);
      render((_d && _d.AUDIT_LOG) || []);
    }
  }

  load();

})();
