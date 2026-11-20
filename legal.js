/* Rellena los datos legales (CIF, registro, domicilio…) desde config.js en las páginas legales.
   Si un dato opcional está vacío, se oculta su línea en lugar de mostrar un texto pendiente. */
(function () {
  var L = (window.URBANISIMA_CONFIG || {}).LEGAL || {};
  document.querySelectorAll('[data-legal]').forEach(function (el) {
    var k = el.getAttribute('data-legal'), v = L[k];
    if (v) el.textContent = v;
    else if (k === 'REGISTRO_MERCANTIL') { var li = el.closest('li'); if (li) li.hidden = true; }
  });
})();
