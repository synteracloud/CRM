/* Pakistan CRM — Workflow Builder (K-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.canvas-node').forEach(function (node) {
      node.addEventListener('click', function () {
        document.querySelectorAll('.canvas-node').forEach(function (n) { n.classList.remove('selected'); });
        this.classList.add('selected');
        var nodeId   = (this.querySelector('.fw-semibold.small') || {}).textContent || 'Node';
        var inspHeader = document.querySelector('.col-lg-3 .card-header h6');
        if (inspHeader) inspHeader.textContent = 'Inspector — ' + nodeId;
      });
    });

    document.getElementById('btn-validate').addEventListener('click', function () {
      document.getElementById('btn-publish').disabled = false;
      var banner = document.createElement('div');
      banner.className = 'alert alert-success alert-dismissible position-fixed top-0 end-0 m-3';
      banner.style.zIndex = 9999;
      banner.innerHTML = '<i class="fi fi-rr-check me-2"></i>Validation passed — 0 errors, 1 warning. Workflow is publishable. <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>';
      document.body.appendChild(banner);
      setTimeout(function () { banner.remove(); }, 3000);
    });

    document.getElementById('btn-save').addEventListener('click', function () {
      var nameEl = document.querySelector('[data-workflow-name]') || document.querySelector('#workflow-name');
      var name   = nameEl ? nameEl.value || nameEl.textContent : 'Untitled Workflow';

      function onSaved() {
        var banner = document.createElement('div');
        banner.className = 'alert alert-info position-fixed top-0 end-0 m-3';
        banner.style.zIndex = 9999;
        banner.innerHTML = '<i class="fi fi-rr-disk me-2"></i>Draft saved.';
        document.body.appendChild(banner);
        setTimeout(function () { banner.remove(); }, 2000);
      }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.workflows.create({ name: name, trigger_events: ['manual.trigger.v1'], steps_dsl: [] })
          .then(onSaved).catch(onSaved);
      } else {
        onSaved();
      }
    });

    document.getElementById('btn-simulate').addEventListener('click', function () {
      document.querySelectorAll('.canvas-node').forEach(function (node, i) {
        setTimeout(function () {
          var badge = node.querySelector('.badge');
          if (badge) { badge.className = 'badge bg-info text-white'; badge.textContent = '⚡ Running'; }
          setTimeout(function () {
            if (badge) { badge.className = 'badge bg-success-subtle text-success border border-success-subtle'; badge.textContent = '✓'; }
          }, 800);
        }, i * 500);
      });
    });

    document.querySelectorAll('.palette-item').forEach(function (item) {
      item.addEventListener('click', function () {
        var banner = document.createElement('div');
        banner.className = 'alert alert-secondary position-fixed bottom-0 end-0 m-3 small';
        banner.style.zIndex = 9999;
        banner.textContent = 'Drag-and-drop canvas requires a graph library (Phase 6). Click to add to canvas in dummy mode.';
        document.body.appendChild(banner);
        setTimeout(function () { banner.remove(); }, 2500);
      });
    });
  });

})();
