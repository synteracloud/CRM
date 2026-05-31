/* Pakistan CRM — Integration Settings (G-05) */
(function () {
  'use strict';
  var cfg = window.CRM_CONFIG;

  var BADGE_CLS = {
    connected:     'bg-success-subtle text-success',
    disconnected:  'bg-danger-subtle text-danger',
    not_configured:'bg-secondary-subtle text-secondary',
  };
  var BADGE_LABEL = {
    connected:     'Connected',
    disconnected:  'Disconnected',
    not_configured:'Not configured',
  };

  // Locate the card-header badge by finding the provider's icon within the card
  function $badge(provider) {
    var iconMap = { whatsapp: '.fi-brands-whatsapp', email: '.fi-rr-envelope' };
    var sel = iconMap[provider];
    return sel ? $(sel).closest('.card-header').find('.badge') : $();
  }

  function applyStatus(provider, status) {
    var $b = $badge(provider);
    if (!$b.length) return;
    var cls = BADGE_CLS[status] || 'bg-secondary-subtle text-secondary';
    $b.attr('class', 'badge ' + cls).text(BADGE_LABEL[status] || status);
  }

  function applyList(list) {
    (list || []).forEach(function (item) { applyStatus(item.provider, item.status); });
  }

  var dummyList = [
    { provider: 'whatsapp', status: 'connected' },
    { provider: 'email',    status: 'connected' },
    { provider: 'sms',      status: 'disconnected' },
    { provider: 'push',     status: 'not_configured' },
  ];

  if (cfg && !cfg.DUMMY_MODE) {
    CRM_API.integrations.list()
      .then(function (r) { applyList(r.data || r); })
      .catch(function () { applyList(dummyList); });
  } else {
    applyList(dummyList);
  }

  // Test Connection button handler
  $(document).on('click', 'button', function () {
    var $btn = $(this);
    if ($btn.text().trim() !== 'Test Connection') return;
    var provider = $btn.closest('.card').find('.fi-brands-whatsapp').length ? 'whatsapp' : 'email';
    $btn.html('<span class="spinner-border spinner-border-sm me-1"></span>Testing…').prop('disabled', true);
    function finish(ok, msg) {
      $btn.html((ok ? '<i class="fi fi-rr-check me-1"></i>' : '<i class="fi fi-rr-cross me-1"></i>') + msg)
          .toggleClass('btn-success', ok).toggleClass('btn-danger', !ok)
          .removeClass('btn-outline-primary').prop('disabled', false);
      applyStatus(provider, ok ? 'connected' : 'disconnected');
    }
    if (cfg && !cfg.DUMMY_MODE) {
      CRM_API.integrations.test(provider)
        .then(function (r) { var d = r.data || r; finish(!!d.ok, d.message || 'Done'); })
        .catch(function () { finish(false, 'Connection failed'); });
    } else {
      setTimeout(function () { finish(true, 'Connected'); }, 1200);
    }
  });
})();
