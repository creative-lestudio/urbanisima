/* Rellena los datos legales (CIF, registro, domicilio…) desde config.js en las páginas legales. */
(function () {
  var L = (window.URBANISIMA_CONFIG || {}).LEGAL || {};
  document.querySelectorAll('[data-legal]').forEach(function (el) {
    var v = L[el.getAttribute('data-legal')];
    if (v) el.textContent = v;
  });
})();
