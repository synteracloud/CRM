/* Pakistan CRM — Routing Config (L-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var QUEUES = [
    { name:'General Support',  strategy:'round_robin',  auto_assign:true,  team:'All Agents' },
    { name:'Billing',          strategy:'least_loaded', auto_assign:true,  team:'Finance Team' },
    { name:'VIP Enterprise',   strategy:'claim_first',  auto_assign:false, team:'Senior Agents' },
    { name:'WhatsApp Inbound', strategy:'round_robin',  auto_assign:true,  team:'All Agents' },
  ];
  var ROUTING_RULES = [
    { priority:1, condition:'contact.account_tier = "Enterprise"', queue:'VIP Enterprise',  reason:'Enterprise tier → VIP queue' },
    { priority:2, condition:'intent = "payment_query"',            queue:'Billing',          reason:'Payment queries → billing queue' },
    { priority:3, condition:'channel = "whatsapp"',                queue:'WhatsApp Inbound', reason:'WhatsApp messages → dedicated queue' },
  ];
  var PRES_BADGE = { online:'<span class="badge bg-success">Online</span>', away:'<span class="badge bg-warning text-dark">Away</span>', busy:'<span class="badge bg-danger">Busy</span>', offline:'<span class="badge bg-secondary">Offline</span>' };

  function render(queues, users) {
    var queueData = queues.length ? queues : QUEUES;

    var queueTable = document.getElementById('queue-table');
    if (queueTable) {
      queueTable.innerHTML = queueData.map(function (q) {
        return '<tr><td class="text-center fw-semibold">' + (q.name || q.queue_id) + '</td>' +
          '<td class="text-center"><code class="small">' + (q.strategy || 'round_robin') + '</code></td>' +
          '<td class="text-center">' + (q.auto_assign !== false ? '<span class="badge bg-success">Yes</span>' : '<span class="badge bg-secondary">No</span>') + '</td>' +
          '<td class="text-center">' + (q.team || 'All Agents') + '</td>' +
          '<td class="text-center"><button class="btn btn-xs btn-outline-primary" disabled>Edit</button></td></tr>';
      }).join('');
    }

    var capTable = document.getElementById('capacity-table');
    if (capTable) {
      capTable.innerHTML = users.map(function (u) {
        var pres = { online:'online', away:'away', busy:'busy', offline:'offline' };
        var presKey = Object.keys(pres)[Math.floor(Math.abs(u.id.charCodeAt ? u.id.charCodeAt(u.id.length - 1) : 0) % 4)];
        return '<tr><td class="text-center fw-semibold">' + u.display_name + '</td>' +
          '<td class="text-center">' + PRES_BADGE[presKey] + '</td>' +
          '<td class="text-center"><input type="number" class="form-control form-control-sm text-center mx-auto" value="10" style="width:70px" disabled></td>' +
          '<td class="text-center">—</td></tr>';
      }).join('');
    }

    var rulesEl = document.getElementById('routing-rules');
    if (rulesEl) {
      rulesEl.innerHTML = ROUTING_RULES.map(function (r) {
        return '<div class="d-flex align-items-center gap-3 py-2 border-bottom">' +
          '<span class="badge bg-secondary-subtle text-secondary">#' + r.priority + '</span>' +
          '<div class="flex-grow-1"><div class="fw-semibold small">IF <code>' + r.condition + '</code></div>' +
          '<div class="small text-muted">→ Route to: <strong>' + r.queue + '</strong> · ' + r.reason + '</div></div>' +
          '<button class="btn btn-xs btn-outline-danger" disabled>Remove</button></div>';
      }).join('');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        window.CRM_API.inbox.queues.list().catch(function () { return { data: [] }; }),
        window.CRM_API.users.list().catch(function () { return { data: [] }; })
      ]).then(function (results) {
        render(results[0].data || [], results[1].data || []);
      });
    } else {
      render([], (_d && _d.users && _d.users.data) || []);
    }
  });

})();
