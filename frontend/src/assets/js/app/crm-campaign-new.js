/* Pakistan CRM — New Campaign Form (I-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TEMPLATES = {
    eid_offer:       'Eid Mubarak! 🌙 Celebrate with our special offer — 20% off on all CRM plans this Eid. Reply "YES" to claim. [P-017: Urdu version pending sign-off]',
    product_launch:  'Exciting news! We\'ve launched new features in NexLink CRM. Book a free demo: [link]. Reply "DEMO" to schedule.',
    reengagement:    'Aap ko miss kiya! We noticed you haven\'t logged in recently. Let us help you get back on track. Reply "HELP" for support.',
    payment_reminder:'Your invoice is due soon. Amount: {amount}. Pay now to avoid late fees. Reply "PAID" once done.',
  };

  var selectedSegment = '';
  var schedulePicker  = null;

  function setStep(n) {
    document.getElementById('step-1').style.display = n === 1 ? '' : 'none';
    document.getElementById('step-2').style.display = n === 2 ? '' : 'none';
    var ind2 = document.getElementById('step-2-ind');
    if (!ind2) return;
    var circle2 = ind2.querySelector('.avatar');
    if (n === 2) {
      ind2.classList.remove('opacity-50');
      if (circle2) circle2.classList.replace('bg-secondary', 'bg-primary');
    } else {
      ind2.classList.add('opacity-50');
      if (circle2) circle2.classList.replace('bg-primary', 'bg-secondary');
    }
  }

  function populateSegments(segments) {
    var container = document.getElementById('segment-buttons');
    if (!container || !segments.length) return;
    container.innerHTML = segments.map(function (seg) {
      return '<button type="button" class="btn btn-sm btn-outline-secondary" data-seg="' + seg.segment_id + '">' + seg.name + '</button>';
    }).join('');
    container.querySelectorAll('[data-seg]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        container.querySelectorAll('[data-seg]').forEach(function (b) { b.className = 'btn btn-sm btn-outline-secondary'; });
        this.className = 'btn btn-sm btn-primary';
        selectedSegment = this.dataset.seg;
        var selEl = document.getElementById('selected-segment');
        if (selEl) selEl.textContent = 'Selected: ' + this.textContent;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    /* Existing segment button delegation (fallback for static HTML) */
    document.querySelectorAll('[data-seg]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('[data-seg]').forEach(function (b) { b.className = 'btn btn-sm btn-outline-secondary'; });
        this.className = 'btn btn-sm btn-primary';
        selectedSegment = this.dataset.seg;
        var selEl = document.getElementById('selected-segment');
        if (selEl) selEl.textContent = 'Selected: ' + this.textContent;
      });
    });

    /* Load live segments for buttons */
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.segments.list({ limit: 20 })
        .then(function (res) { if (res.data && res.data.length) populateSegments(res.data); })
        .catch(function () {});
    }

    /* Step navigation */
    document.getElementById('btn-next-1').addEventListener('click', function () {
      var name = document.getElementById('campaign-name').value.trim();
      if (!name)           { alert('Please enter a campaign name.'); return; }
      if (!selectedSegment){ alert('Please select a segment.'); return; }
      setStep(2);
    });
    document.getElementById('btn-back-2').addEventListener('click', function () { setStep(1); });

    /* Template preview */
    document.getElementById('template-select').addEventListener('change', function () {
      var previewEl = document.getElementById('template-preview');
      if (previewEl) previewEl.textContent = TEMPLATES[this.value] || 'Select a template to preview.';
    });

    /* Trigger condition toggle */
    document.getElementById('trigger-condition').addEventListener('change', function () {
      var show = this.value === 'scheduled';
      var schedField = document.getElementById('schedule-field');
      if (schedField) schedField.style.display = show ? '' : 'none';
      if (show && typeof flatpickr !== 'undefined' && !schedulePicker) {
        schedulePicker = flatpickr('#schedule-dt', { enableTime:true, dateFormat:'d M Y H:i', minDate:'today' });
      }
    });

    /* Submit */
    document.getElementById('btn-submit').addEventListener('click', function () {
      var template  = document.getElementById('template-select').value;
      var name      = document.getElementById('campaign-name').value.trim();
      var typeEl    = document.getElementById('campaign-type');
      var type      = typeEl ? typeEl.value : 'whatsapp_broadcast';
      var triggerEl = document.getElementById('trigger-condition');
      var trigger   = triggerEl ? triggerEl.value : 'immediate';
      var schedEl   = document.getElementById('schedule-dt');
      var scheduledAt = (trigger === 'scheduled' && schedEl) ? schedEl.value || null : null;

      if (!template) { alert('Please select a message template.'); return; }

      var btn = this;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Creating…';

      var payload = { name: name, type: type, segment_id: selectedSegment || null, template_id: template, scheduled_at: scheduledAt };

      function onSuccess() {
        btn.disabled  = false;
        btn.innerHTML = 'Create Campaign';
        var toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
        toast.style.zIndex = 9999;
        toast.innerHTML = '<i class="fi fi-rr-check me-2"></i>Campaign created as draft.';
        document.body.appendChild(toast);
        setTimeout(function () { toast.remove(); window.location.href = 'app/marketing-workspace.html'; }, 1800);
      }
      function onError() {
        btn.disabled  = false;
        btn.innerHTML = 'Create Campaign';
        alert('Error creating campaign. Please try again.');
      }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.campaigns.create(payload).then(onSuccess).catch(onError);
      } else {
        setTimeout(onSuccess, 600);
      }
    });
  });

})();
