/* Páginas de servicios (/servicios/…): filtro por tipo de cliente en el listado y medición de la vista del servicio. */
(function () {
  var grid = document.getElementById('hub-grid');
  if (grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.hub-card'));
    var tabs = document.querySelectorAll('.tab'), status = document.getElementById('svc-status');
    var NAMES = { particulares: 'viviendas particulares', comunidades: 'comunidades de vecinos', empresas: 'naves industriales' };
    cards.forEach(function (c, i) { c.dataset.i = i; });
    var apply = function (cat) {
      tabs.forEach(function (t) { var on = t.dataset.filter === cat; t.classList.toggle('is-on', on); t.setAttribute('aria-selected', String(on)); });
      var sorted = cat === 'all' ? cards.slice().sort(function (a, b) { return a.dataset.i - b.dataset.i; })
        : cards.slice().sort(function (a, b) { return a.dataset[cat] - b.dataset[cat]; });
      sorted.forEach(function (c, i) { c.style.order = i + 1; c.classList.toggle('is-top', cat !== 'all' && i < 3); });
      status.textContent = cat === 'all' ? 'Mostrando los 14 servicios' : 'Los 14 servicios, de más a menos solicitados por ' + NAMES[cat];
    };
    tabs.forEach(function (t) { t.addEventListener('click', function () { apply(t.dataset.filter); }); });
    var q = new URLSearchParams(location.search).get('perfil'); if (q && NAMES[q]) apply(q);
  }
  /* Medición: vista de una página de servicio (solo si el visitante aceptó cookies de medición) */
  var svName = document.body.getAttribute('data-servicio');
  if (svName) setTimeout(function () { if (window.UrbTrack) window.UrbTrack('service_view', { servicio: svName }); }, 800);
})();
