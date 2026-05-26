/* Pakistan CRM — Lead Detail Page Driver */

/* Advance Stage button: update strip badge on click */
document.addEventListener('DOMContentLoaded', function () {
  var stages = ['New', 'Contacted', 'Engaged', 'Qualified', 'Converted'];
  var stageBadgeClasses = {
    'New':       'bg-primary-subtle text-primary',
    'Contacted': 'bg-info-subtle text-info',
    'Engaged':   'bg-warning-subtle text-warning',
    'Qualified': 'bg-success-subtle text-success',
    'Converted': 'bg-dark-subtle text-dark'
  };

  var currentStageIdx = 0;

  document.querySelectorAll('[data-bs-target="#pane-pipeline"] ~ * .btn-primary, #pane-pipeline .btn-primary').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (currentStageIdx < stages.length - 1) {
        currentStageIdx++;
        var nextStage = stages[currentStageIdx];
        var $badge = document.getElementById('lead-stage-badge');
        if ($badge) {
          $badge.className = 'badge ' + (stageBadgeClasses[nextStage] || 'bg-secondary-subtle text-secondary');
          $badge.textContent = nextStage;
        }
        if (currentStageIdx < stages.length - 1) {
          btn.textContent = 'Advance to ' + stages[currentStageIdx + 1];
        } else {
          btn.disabled = true;
          btn.textContent = 'Fully Converted';
        }
      }
    });
  });
});
