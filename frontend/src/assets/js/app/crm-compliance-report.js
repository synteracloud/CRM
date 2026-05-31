/* Pakistan CRM — Compliance Report (J-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function initDatePickers() {
    var startInput = document.getElementById('compliancePeriodStart');
    var endInput   = document.getElementById('compliancePeriodEnd');
    if (startInput && window.flatpickr) {
      var startDate = new Date();
      startDate.setFullYear(startDate.getFullYear() - 1);
      flatpickr(startInput, { dateFormat: 'Y-m-d', defaultDate: startDate });
    }
    if (endInput && window.flatpickr) {
      flatpickr(endInput, { dateFormat: 'Y-m-d', defaultDate: new Date() });
    }
  }

  function generateReport(auditLog) {
    var totalEvents      = auditLog.length;
    var accessEvents     = auditLog.filter(function (e) {
      return ['create', 'login', 'export'].indexOf(e.action_type) !== -1;
    }).length;
    var privilegedEvents = auditLog.filter(function (e) {
      return ['delete', 'export'].indexOf(e.action_type) !== -1;
    }).length;
    var slaBreaches      = auditLog.filter(function (e) { return e.result === 'deny'; }).length;

    var el;
    el = document.getElementById('complianceTotalEvents');      if (el) el.textContent = totalEvents.toLocaleString();
    el = document.getElementById('complianceAccessEvents');     if (el) el.textContent = accessEvents.toLocaleString();
    el = document.getElementById('compliancePrivilegedEvents'); if (el) el.textContent = privilegedEvents.toLocaleString();
    el = document.getElementById('complianceSlaBreaches');      if (el) el.textContent = slaBreaches.toLocaleString();
    el = document.getElementById('complianceGeneratedAt');      if (el) el.textContent = new Date().toLocaleString();
  }

  function attachEventListeners(auditLog) {
    var startInput       = document.getElementById('compliancePeriodStart');
    var endInput         = document.getElementById('compliancePeriodEnd');
    var regulationSelect = document.getElementById('complianceRegulationSelect');
    var exportBtn        = document.getElementById('complianceExportPdfBtn');

    [startInput, endInput, regulationSelect].forEach(function (el) {
      if (el) el.addEventListener('change', function () { generateReport(auditLog); });
    });

    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        alert('PDF export will be available in the production release.');
      });
    }
  }

  function load() {
    initDatePickers();

    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.audits.list({ limit: 500 })
        .then(function (res) {
          var log = res.data || [];
          generateReport(log);
          attachEventListeners(log);
        })
        .catch(function () {
          var log = (_d && _d.AUDIT_LOG) || [];
          generateReport(log);
          attachEventListeners(log);
        });
    } else {
      var log = (_d && _d.AUDIT_LOG) || [];
      generateReport(log);
      attachEventListeners(log);
    }
  }

  load();

})();
