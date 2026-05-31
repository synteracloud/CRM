/* Pakistan CRM — Object Builder (K-02) */
/* Client-side layout designer — no live data fetch required */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG; // available for future field-definition API wiring

  var OBJECT_FIELDS = {
    lead: [
      { name:'contact_name', type:'text',     required:true,  label:'Contact Name' },
      { name:'phone_e164',   type:'phone',    required:true,  label:'Phone (E.164)' },
      { name:'email',        type:'email',    required:false, label:'Email' },
      { name:'stage',        type:'select',   required:true,  label:'Stage' },
      { name:'source',       type:'select',   required:false, label:'Source' },
      { name:'priority',     type:'select',   required:false, label:'Priority' },
      { name:'estimated_value',type:'number', required:false, label:'Estimated Value (PKR)' },
      { name:'owner_id',     type:'relation', required:false, label:'Owner' },
      { name:'created_at',   type:'datetime', required:false, label:'Created At' },
      { name:'updated_at',   type:'datetime', required:false, label:'Updated At' },
    ],
  };

  var TYPE_ICON = { text:'fi-rr-text', phone:'fi-rr-phone', email:'fi-rr-envelope', select:'fi-rr-list', number:'fi-rr-sort-numeric-down', relation:'fi-rr-link', datetime:'fi-rr-calendar' };
  var LAYOUT_SECTIONS = [
    { title:'Contact Information', fields:['contact_name','phone_e164','email'] },
    { title:'Pipeline',            fields:['stage','source','priority'] },
    { title:'Value & Assignment',  fields:['estimated_value','owner_id'] },
    { title:'Timestamps',          fields:['created_at','updated_at'] },
  ];

  document.addEventListener('DOMContentLoaded', function () {
    var fields = OBJECT_FIELDS.lead;
    document.getElementById('field-count').textContent = fields.length + ' fields';

    var listEl = document.getElementById('field-list');
    if (listEl) {
      listEl.innerHTML = fields.map(function (f) {
        return '<div class="d-flex align-items-center gap-2 px-3 py-2 border-bottom" draggable="true">' +
          '<i class="fi ' + (TYPE_ICON[f.type] || 'fi-rr-text') + ' text-muted small"></i>' +
          '<div class="flex-grow-1"><div class="fw-semibold small">' + f.label + '</div>' +
          '<div class="text-muted" style="font-size:.7rem">' + f.name + ' · ' + f.type + (f.required ? ' · required' : '') + '</div></div>' +
          (f.required ? '<span class="text-danger small">*</span>' : '') + '</div>';
      }).join('');
    }

    var canvasEl = document.getElementById('layout-canvas');
    if (canvasEl) {
      canvasEl.innerHTML = LAYOUT_SECTIONS.map(function (sec) {
        return '<div class="card mb-2 border-dashed" style="height:auto;border-style:dashed!important">' +
          '<div class="card-header py-1 small bg-light fw-semibold">' + sec.title + '</div>' +
          '<div class="card-body py-2"><div class="row g-2">' +
          sec.fields.map(function (fn) {
            var f = fields.find(function (x) { return x.name === fn; });
            return f ? '<div class="col-6"><div class="border rounded p-1 small text-center bg-white">' + f.label + (f.required ? ' <span class="text-danger">*</span>' : '') + '</div></div>' : '';
          }).join('') + '</div></div></div>';
      }).join('');
    }

    var previewEl = document.getElementById('layout-preview');
    if (previewEl) {
      previewEl.innerHTML = LAYOUT_SECTIONS.map(function (sec) {
        return '<div class="mb-3"><div class="small fw-semibold text-muted mb-1">' + sec.title + '</div>' +
          sec.fields.map(function (fn) {
            var f = fields.find(function (x) { return x.name === fn; });
            return f ? '<div class="mb-1"><label class="form-label small mb-0">' + f.label + '</label><input type="' + (f.type === 'number' ? 'number' : 'text') + '" class="form-control form-control-sm" placeholder="' + f.label + '" disabled></div>' : '';
          }).join('') + '</div>';
      }).join('');
    }

    var objectTypeEl = document.getElementById('object-type');
    if (objectTypeEl) {
      objectTypeEl.addEventListener('change', function () {
        var count = { lead:10, contact:12, opportunity:14, account:9, custom_project:6 };
        document.getElementById('field-count').textContent = (count[this.value] || 8) + ' fields';
      });
    }
  });

})();
