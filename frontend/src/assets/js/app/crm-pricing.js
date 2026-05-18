document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('priceSwitchCheck');
  if (!toggle) return;
  toggle.addEventListener('change', function () {
    document.querySelectorAll('.price-monthly').forEach(function (el) {
      el.classList.toggle('d-none', toggle.checked);
    });
    document.querySelectorAll('.price-yearly').forEach(function (el) {
      el.classList.toggle('d-none', !toggle.checked);
    });
  });
});
