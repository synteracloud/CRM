/* Pakistan CRM — Data Governance Console (J-03) */
(function () {
  'use strict';
  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var CLASSIFY_CLS = {
    PII:       'bg-danger-subtle text-danger',
    financial: 'bg-warning-subtle text-warning',
    internal:  'bg-info-subtle text-info',
    public:    'bg-success-subtle text-success',
  };

  function renderClassification(list) {
    var rows = (list || []).map(function (r) {
      return '<tr>' +
        '<td class="text-center fw-semibold">' + r.entity + '</td>' +
        '<td class="text-center"><code>' + r.field + '</code></td>' +
        '<td class="text-center"><span class="badge ' + (CLASSIFY_CLS[r.classification] || 'bg-secondary-subtle text-secondary') + '">' + r.classification + '</span></td>' +
        '<td class="text-center">' + r.legal_basis + '</td>' +
        '</tr>';
    }).join('');
    $('#classification-body').html(rows);
  }

  function renderRetention(list) {
    var rows = (list || []).map(function (r) {
      return '<tr>' +
        '<td class="text-center">' + r.entity_class + '</td>' +
        '<td class="text-center fw-semibold">' + r.hot_period + '</td>' +
        '<td class="text-center">' + r.legal_basis + '</td>' +
        '<td class="text-center">' + r.deletion_schedule + '</td>' +
        '</tr>';
    }).join('');
    $('#retention-body').html(rows);
  }

  function renderSar(list) {
    var count = (list || []).length;
    $('#sar-badge').text(count);
    var html = count ? (list || []).map(function (s) {
      return '<div class="d-flex justify-content-between align-items-center py-2 border-bottom small">' +
        '<div><span class="fw-semibold">' + (s.request_type || 'export') + '</span>' +
        '<span class="text-muted ms-2">' + (s.contact_id || '—') + '</span></div>' +
        '<span class="badge bg-warning-subtle text-warning">' + (s.status || 'pending') + '</span>' +
        '</div>';
    }).join('') : '<p class="text-muted small text-center py-3">No pending subject access requests</p>';
    $('#sar-list').html(html);
  }

  function renderConsent(list) {
    var contacts = list || [];
    var html = contacts.slice(0, 5).map(function (c) {
      var name = c.contact_name || c.display_name || '—';
      var mktGranted = c.marketing && c.marketing.granted;
      return '<div class="d-flex justify-content-between align-items-center py-2 border-bottom small">' +
        '<span class="fw-semibold">' + name + '</span>' +
        '<div class="d-flex gap-2">' +
        '<span class="badge bg-success-subtle text-success">Service ✓</span>' +
        '<span class="badge ' + (mktGranted ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary') + '">Marketing</span>' +
        '</div></div>';
    }).join('');
    $('#consent-summary').html(
      html + '<p class="text-muted small text-center mt-2">Showing ' + Math.min(5, contacts.length) + ' of ' + contacts.length +
      ' contacts. <a href="app/privacy.html">View all in Consent &amp; Privacy Manager →</a></p>'
    );
  }

  // Dummy fallbacks matching gateway seed data
  var DUMMY_CLASS = [
    { entity:'Contact',       field:'phone_e164',    classification:'PII',       legal_basis:'Legitimate Interest' },
    { entity:'Contact',       field:'email',          classification:'PII',       legal_basis:'Legitimate Interest' },
    { entity:'Lead',          field:'contact_name',   classification:'PII',       legal_basis:'Legitimate Interest' },
    { entity:'Invoice',       field:'amount_due',     classification:'financial', legal_basis:'Contract Obligation' },
    { entity:'Payment',       field:'transaction_id', classification:'financial', legal_basis:'Contract Obligation' },
    { entity:'AuditLog',      field:'actor_id',       classification:'internal',  legal_basis:'Legal Obligation' },
    { entity:'ActivityEvent', field:'description',    classification:'internal',  legal_basis:'Legitimate Interest' },
    { entity:'Message',       field:'content',        classification:'PII',       legal_basis:'Consent' },
    { entity:'SessionToken',  field:'token_hash',     classification:'internal',  legal_basis:'Legal Obligation' },
    { entity:'Opportunity',   field:'amount',         classification:'financial', legal_basis:'Contract Obligation' },
  ];
  var DUMMY_RET = [
    { entity_class:'Financial records (Invoice, Payment)', hot_period:'7 years',  legal_basis:'Legal (SECP/FBR)',    deletion_schedule:'Annual purge after retention window' },
    { entity_class:'AuditLog',                            hot_period:'7 years',  legal_basis:'Legal Obligation',    deletion_schedule:'Annual purge' },
    { entity_class:'ActivityEvent',                       hot_period:'3 years',  legal_basis:'Legitimate Interest', deletion_schedule:'Rolling deletion' },
    { entity_class:'Contact / Lead',                      hot_period:'5 years',  legal_basis:'Consent + LI',        deletion_schedule:'On erasure request or inactivity' },
    { entity_class:'SessionToken',                        hot_period:'90 days',  legal_basis:'Security',            deletion_schedule:'Automated nightly cleanup' },
    { entity_class:'Message',                             hot_period:'2 years',  legal_basis:'Consent',             deletion_schedule:'Automated on expiry' },
  ];

  function dummyConsentContacts() {
    return (_d ? _d.contacts.data : []).map(function (c) {
      return { contact_name: c.display_name, marketing: { granted: c.tags && c.tags.indexOf('Customer') !== -1 } };
    });
  }

  if (cfg && !cfg.DUMMY_MODE) {
    CRM_API.governance.classification()
      .then(function (r) { renderClassification(r.data || r); })
      .catch(function () { renderClassification(DUMMY_CLASS); });

    CRM_API.governance.retention()
      .then(function (r) { renderRetention(r.data || r); })
      .catch(function () { renderRetention(DUMMY_RET); });

    CRM_API.governance.sarList()
      .then(function (r) { renderSar(r.data || r); })
      .catch(function () { renderSar([]); });

    CRM_API.privacy.consentList()
      .then(function (r) { renderConsent(r.data || []); })
      .catch(function () { renderConsent(dummyConsentContacts()); });
  } else {
    renderClassification(DUMMY_CLASS);
    renderRetention(DUMMY_RET);
    renderSar([]);
    renderConsent(dummyConsentContacts());
  }
})();
