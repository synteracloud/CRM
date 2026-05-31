/* Pakistan CRM — Partner Detail (C-11) */

(function () {
  'use strict';

  var cfg       = window.CRM_CONFIG;
  var _d        = window.CRM_DUMMY;
  var partnerId = new URLSearchParams(window.location.search).get('id') || null;

  var TIER_BADGE = {
    Platinum:'<span class="badge bg-primary">Platinum</span>',
    Gold:    '<span class="badge bg-warning text-dark">Gold</span>',
    Silver:  '<span class="badge bg-secondary">Silver</span>',
  };
  var STATUS_BADGE = {
    active:  '<span class="badge bg-success-subtle text-success border border-success-subtle">Active</span>',
    inactive:'<span class="badge bg-secondary-subtle text-secondary">Inactive</span>',
  };

  function pkr(n) { return 'PKR ' + (n || 0).toLocaleString('en-PK'); }

  function render(partner, opps) {
    if (!partner) {
      if (_d && _d.partners && _d.partners.data[0]) render(_d.partners.data[0], (_d.opportunities && _d.opportunities.data) || []);
      return;
    }

    document.getElementById('bc-partner-name').textContent = partner.name;
    document.getElementById('partner-name').textContent    = partner.name;
    document.getElementById('tier-badge').innerHTML        = TIER_BADGE[partner.partner_tier] || partner.partner_tier;
    document.getElementById('status-badge').innerHTML      = STATUS_BADGE[partner.status] || partner.status;
    document.getElementById('partner-region').textContent  = (partner.region || '—') + (partner.city ? ' · ' + partner.city : '');
    document.getElementById('partner-contact').textContent = partner.contact_name || '—';
    document.getElementById('partner-email').textContent   = partner.contact_email || '—';

    var fieldsEl = document.getElementById('partner-fields');
    if (fieldsEl) {
      fieldsEl.innerHTML =
        '<div class="col-sm-6"><label class="small text-muted">Partner Name</label><p class="fw-semibold">' + partner.name + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Tier</label><p>' + (TIER_BADGE[partner.partner_tier] || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Region</label><p class="fw-semibold">' + (partner.region || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">City</label><p class="fw-semibold">' + (partner.city || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Contact Name</label><p class="fw-semibold">' + (partner.contact_name || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Contact Email</label><p class="fw-semibold">' + (partner.contact_email || '—') + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Status</label><p>' + (STATUS_BADGE[partner.status] || partner.status) + '</p></div>' +
        '<div class="col-sm-6"><label class="small text-muted">Member Since</label><p class="fw-semibold">' + (partner.created_at ? new Date(partner.created_at).getFullYear() : '—') + '</p></div>';
    }

    var oppCount = partner.attributed_opp_count || 0;
    var partnerOpps = opps.slice(0, Math.min(oppCount, 5));
    var oppsEl = document.getElementById('partner-opps-list');
    if (oppsEl) {
      oppsEl.innerHTML = partnerOpps.length ? partnerOpps.map(function (o) {
        return '<div class="d-flex align-items-center gap-3 py-2 border-bottom">' +
          '<div class="flex-grow-1"><div class="fw-semibold">' + o.name + '</div>' +
          '<div class="small text-muted">' + (o.account_name || '—') + ' · Stage: ' + (o.stage || '—') + '</div></div>' +
          '<div class="text-end"><div class="fw-semibold">' + pkr(o.amount) + '</div>' +
          '<div class="small text-muted">' + (o.probability || 0) + '% probability</div></div></div>';
      }).join('') : '<div class="text-muted small py-3 text-center">No attributed opportunities.</div>';
    }

    var commDue = partner.commission_due || 0;
    var commEl  = document.getElementById('commission-list');
    if (commEl) {
      commEl.innerHTML = commDue > 0
        ? '<div class="d-flex justify-content-between align-items-center py-2 border-bottom">' +
          '<div><div class="fw-semibold">Current Commission</div><div class="small text-muted">' + (partner.attributed_opp_count || 0) + ' attributed opportunities</div></div>' +
          '<div class="text-end"><div class="fw-bold text-success">' + pkr(commDue) + '</div><div class="small text-muted">Pending payment</div></div></div>' +
          '<div class="mt-3"><button class="btn btn-sm btn-success" id="btn-pay-commission" data-partner="' + partner.partner_id + '">Pay Commission</button></div>'
        : '<div class="text-muted small py-3 text-center">No commission due.</div>';
    }

    var ctxAttr = document.getElementById('context-attribution');
    if (ctxAttr) {
      ctxAttr.innerHTML = '<dl class="row mb-0 small">' +
        '<dt class="col-7 text-muted">Open Opps</dt><dd class="col-5 fw-semibold">' + (partner.attributed_opp_count || 0) + '</dd>' +
        '<dt class="col-7 text-muted">Region</dt><dd class="col-5">' + (partner.region || '—') + '</dd>' +
        '<dt class="col-7 text-muted">Tier</dt><dd class="col-5">' + (partner.partner_tier || '—') + '</dd></dl>';
    }

    var ctxComm = document.getElementById('context-commission');
    if (ctxComm) {
      ctxComm.innerHTML = '<div class="text-center py-2"><div class="small text-muted mb-1">Total Due</div>' +
        '<h3 class="fw-bold text-success mb-0">' + pkr(commDue) + '</h3></div>' +
        '<hr class="my-2">' +
        '<button class="btn btn-sm btn-success w-100" id="btn-pay-commission-ctx" data-partner="' + partner.partner_id + '">Pay Commission</button>';
    }

    /* Pay Commission buttons */
    document.querySelectorAll('#btn-pay-commission, #btn-pay-commission-ctx').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var ref = window.prompt('Payment reference (bank transfer / TRF number):');
        if (!ref) return;
        var pid = this.dataset.partner;
        window.CRM_API.partners.commissions(pid)
          .then(function (resp) {
            var commissions = resp.data || [];
            var approved    = commissions.find(function (c) { return c.status === 'approved'; });
            var pending     = commissions.find(function (c) { return c.status === 'pending'; });
            var target      = approved || pending;
            if (!target) { alert('No payable commission found.'); return; }
            var step = approved
              ? window.CRM_API.partners.payCommission(pid, target.commission_id, ref)
              : window.CRM_API.partners.approveCommission(pid, target.commission_id)
                  .then(function () { return window.CRM_API.partners.payCommission(pid, target.commission_id, ref); });
            return step;
          })
          .then(function () { location.reload(); })
          .catch(function () { alert('Error processing payment.'); });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        (partnerId ? window.CRM_API.partners.get(partnerId) : Promise.resolve({ data: null })).catch(function () { return { data: null }; }),
        window.CRM_API.opportunities.list({ limit: 50 }).catch(function () { return { data: [] }; })
      ]).then(function (results) {
        var p = results[0].data;
        if (!p && _d && _d.partners) p = _d.partners.data[0];
        render(p, results[1].data || []);
      });
    } else {
      if (!_d) return;
      var p = partnerId
        ? (_d.partners.data.filter(function (x) { return x.partner_id === partnerId; })[0] || _d.partners.data[0])
        : _d.partners.data[0];
      render(p, _d.opportunities.data);
    }
  });

})();
