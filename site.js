/* Comportamiento común de la web (portada y páginas de servicio): menú, cabecera, WhatsApp, barra móvil y medición. */
(function () {
  var CFG = window.URBANISIMA_CONFIG || {};
  var WA = CFG.WHATSAPP || '34722115251';
  // El número de WhatsApp de config.js manda sobre cualquier enlace wa.me del HTML (se cambia en un solo sitio)
  document.querySelectorAll('a[href*="wa.me/"]').forEach(function (a) {
    a.setAttribute('href', a.getAttribute('href').replace(/wa\.me\/\+?\d+/, 'wa.me/' + WA));
  });
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var header = document.querySelector('.header'), burger = document.querySelector('.burger'), menu = document.getElementById('menu');
  var mobileMq = matchMedia('(max-width: 760px)');
  if (!reduce) document.documentElement.classList.add('js');

  /* Cabecera: siempre clara; en móvil se oculta al bajar y reaparece al subir */
  var lastY = scrollY;
  function onScroll() {
    header.classList.toggle('scrolled', scrollY > 6);
    var dy = scrollY - lastY;
    if (mobileMq.matches && Math.abs(dy) > 6) { header.classList.toggle('hide', dy > 0 && scrollY > 60 && !menu.classList.contains('open')); lastY = scrollY; }
    else if (!mobileMq.matches) header.classList.remove('hide');
  }
  onScroll(); addEventListener('scroll', onScroll, { passive: true });
  if ('scrollRestoration' in history && !location.hash) history.scrollRestoration = 'manual';

  /* Menú móvil */
  function setMenu(open) {
    menu.classList.toggle('open', open); header.classList.toggle('menu-open', open);
    document.documentElement.style.overflow = open ? 'hidden' : '';
    burger.setAttribute('aria-expanded', String(open)); burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  }
  if (burger && menu) {
    burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  }

  /* Barra móvil (Llamar | Pedir presupuesto): se oculta mientras el formulario está en pantalla o el pie visible */
  var bar = document.querySelector('.sticky-cta');
  if (bar && 'IntersectionObserver' in window) {
    var vis = {};
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { vis[x.target.id || x.target.className] = x.isIntersecting; });
      bar.classList.toggle('is-hidden', Object.keys(vis).some(function (k) { return vis[k]; }));
    }, { threshold: .15 });
    document.querySelectorAll('[data-quote], .site-foot').forEach(function (el) { io.observe(el); });
  }

  /* ?ir=servicios|contacto|proceso|ventajas|faq (lo usan las redirecciones de las URLs antiguas) */
  (function goTo() {
    var id = new URLSearchParams(location.search).get('ir');
    if (!id || !/^(servicios|contacto|proteccion|proceso|ventajas|faq)$/.test(id)) return;
    if (id === 'proteccion') id = 'proceso';
    var el = document.getElementById(id); if (!el) return;
    setTimeout(function () { el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 400);
  })();

  /* Aparición suave de secciones (sin retrasar la interacción) */
  if ('IntersectionObserver' in window && !reduce) {
    var ro = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); ro.unobserve(x.target); } });
    }, { threshold: .08, rootMargin: '0px 0px -30px 0px' });
    document.querySelectorAll('.head, .grp, .steps li, .benefits li, .faq-list').forEach(function (el) { el.classList.add('reveal'); ro.observe(el); });
  }

  /* Medición: clics en teléfono, WhatsApp y botones de presupuesto (no son conversiones finales) */
  document.addEventListener('click', function (e) {
    if (!window.UrbTrack || !e.target.closest) return;
    var q = e.target.closest('[data-cta]');
    if (q) window.UrbTrack('click_quote_cta', { ubicacion: q.getAttribute('data-cta') });
    var a = e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
    if (a) window.UrbTrack(a.href.indexOf('tel:') === 0 ? 'click_phone' : 'click_whatsapp');
  });

  /* Pie: año actual y volver arriba */
  var yr = document.getElementById('year'); if (yr) yr.textContent = new Date().getFullYear();
  var toTop = document.getElementById('to-top');
  if (toTop) toTop.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
})();
