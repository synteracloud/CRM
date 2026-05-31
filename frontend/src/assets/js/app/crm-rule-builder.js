/* Pakistan CRM — Rule Builder (K-03) */
/* Client-side rule DSL builder — no live data fetch required */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG; // available for future rule persistence API wiring

  var FIELDS     = ['quote.discount_pct', 'quote.total_amount', 'lead.stage', 'lead.estimated_value', 'contact.account_tier', 'opportunity.probability'];
  var OPERATORS  = ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'exists'];
  var ACTION_TYPES = ['require_approval', 'set_value', 'notify', 'block', 'assign_to'];

  var conditionCount = 0, actionCount = 0;

  function addConditionRow(field, op, value) {
    var id  = ++conditionCount;
    var row = document.createElement('div');
    row.className = 'd-flex align-items-center gap-2 mb-2 condition-row';
    row.dataset.id = id;
    row.innerHTML  =
      '<select class="form-select form-select-sm" style="flex:2">' + FIELDS.map(function (f) { return '<option value="' + f + '"' + (f === field ? ' selected' : '') + '>' + f + '</option>'; }).join('') + '</select>' +
      '<select class="form-select form-select-sm" style="flex:1">' + OPERATORS.map(function (o) { return '<option value="' + o + '"' + (o === op ? ' selected' : '') + '>' + o + '</option>'; }).join('') + '</select>' +
      '<input type="text" class="form-control form-control-sm" style="flex:2" value="' + (value || '') + '">' +
      '<button type="button" class="btn btn-xs btn-outline-danger remove-condition"><i class="fi fi-rr-x"></i></button>';
    document.getElementById('condition-rows').appendChild(row);
    row.querySelector('.remove-condition').addEventListener('click', function () { row.remove(); });
  }

  function addActionRow(type, value) {
    var id  = ++actionCount;
    var row = document.createElement('div');
    row.className = 'd-flex align-items-center gap-2 mb-2 action-row';
    row.dataset.id = id;
    row.innerHTML  =
      '<select class="form-select form-select-sm" style="flex:2">' + ACTION_TYPES.map(function (t) { return '<option value="' + t + '"' + (t === type ? ' selected' : '') + '>' + t + '</option>'; }).join('') + '</select>' +
      '<input type="text" class="form-control form-control-sm" style="flex:3" value="' + (value || '') + '" placeholder="Action value or target">' +
      '<button type="button" class="btn btn-xs btn-outline-danger remove-action"><i class="fi fi-rr-x"></i></button>';
    document.getElementById('action-rows').appendChild(row);
    row.querySelector('.remove-action').addEventListener('click', function () { row.remove(); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    addConditionRow('quote.discount_pct', 'gt', '10');
    addActionRow('require_approval', 'manager');
    addActionRow('notify', 'sales_manager');

    document.getElementById('btn-add-condition').addEventListener('click', function () { addConditionRow('quote.discount_pct', 'gt', ''); });
    document.getElementById('btn-add-action').addEventListener('click', function () { addActionRow('require_approval', ''); });

    document.getElementById('btn-test-rule').addEventListener('click', function () {
      var conditions = Array.from(document.querySelectorAll('.condition-row')).map(function (r) {
        var selects = r.querySelectorAll('select');
        var input   = r.querySelector('input');
        return { field: selects[0].value, op: selects[1].value, value: input.value };
      });
      var actions = Array.from(document.querySelectorAll('.action-row')).map(function (r) {
        return { type: r.querySelector('select').value, value: r.querySelector('input').value };
      });

      var testData = { 'quote.discount_pct': 12, 'quote.total_amount': 480000, 'lead.stage': 'proposal' };
      var passed   = conditions.every(function (c) {
        var val = testData[c.field];
        if (val === undefined) return false;
        if (c.op === 'gt')  return Number(val) > Number(c.value);
        if (c.op === 'gte') return Number(val) >= Number(c.value);
        if (c.op === 'lt')  return Number(val) < Number(c.value);
        if (c.op === 'eq')  return String(val) === c.value;
        return true;
      });

      document.getElementById('test-output').style.display = '';
      document.getElementById('test-result').innerHTML =
        '<div class="alert ' + (passed ? 'alert-success' : 'alert-secondary') + ' mb-2">' +
        '<strong>Result:</strong> Rule ' + (passed ? 'MATCHED' : 'DID NOT MATCH') + ' for sample data.</div>' +
        '<div class="small text-muted mb-2">Sample context: discount_pct=12, total=PKR 4,80,000</div>' +
        (passed ? '<div class="small"><strong>Actions triggered:</strong> ' + actions.map(function (a) { return a.type + '(' + a.value + ')'; }).join(', ') + '</div>' : '');
    });
  });

})();
