/* Comportamiento de las páginas de servicios (/servicios/…): menú, filtro por perfil y formulario de contacto.
   La portada usa main.js; aquí está solo lo necesario para estas páginas. */
(function () {
  var CFG = window.URBANISIMA_CONFIG || {};
  var WA = CFG.WHATSAPP || '34722115251';
  // El número de WhatsApp de config.js manda sobre cualquier enlace wa.me del HTML (se cambia en un solo sitio)
  document.querySelectorAll('a[href*="wa.me/"]').forEach(function (a) {
    a.setAttribute('href', a.getAttribute('href').replace(/wa\.me\/\+?\d+/, 'wa.me/' + WA));
  });
  var root = document.body.getAttribute('data-root') || '';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Menú móvil ---------- */
  var header = document.querySelector('.header'), burger = document.querySelector('.burger'), menu = document.getElementById('menu');
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

  /* ---------- Página /servicios/: los 14 servicios ordenados según el perfil ---------- */
  var grid = document.getElementById('hub-grid');
  if (grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.hub-card'));
    var tabs = document.querySelectorAll('.tab'), status = document.getElementById('svc-status');
    var NAMES = { particulares: 'viviendas particulares', comunidades: 'comunidades de vecinos', empresas: 'naves industriales' };
    cards.forEach(function (c, i) { c.dataset.i = i; });
    function apply(cat) {
      tabs.forEach(function (t) { var on = t.dataset.filter === cat; t.classList.toggle('is-on', on); t.setAttribute('aria-selected', String(on)); });
      var sorted = cat === 'all' ? cards.slice().sort(function (a, b) { return a.dataset.i - b.dataset.i; })
        : cards.slice().sort(function (a, b) { return a.dataset[cat] - b.dataset[cat]; });
      sorted.forEach(function (c, i) { c.style.order = i + 1; c.classList.toggle('is-top', cat !== 'all' && i < 3); });
      status.textContent = cat === 'all' ? 'Mostrando los 14 servicios' : 'Los 14 servicios, de más a menos solicitados por ' + NAMES[cat];
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { apply(t.dataset.filter); }); });
    var q = new URLSearchParams(location.search).get('perfil'); if (q && NAMES[q]) apply(q);
  }

  /* ---------- Formulario de contacto (correo o WhatsApp, con copia al correo) ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    function waLink(text) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(text); }
    function msgEl() { return form.querySelector('.form-msg'); }
    function fail(msg, field) { var m = msgEl(); m.className = 'form-msg'; m.textContent = msg; if (field) { field.classList.add('is-invalid'); field.focus(); } }
    function say(msg) { var m = msgEl(); m.className = 'form-msg ok'; m.textContent = msg; }
    function busy(on) { form.querySelectorAll('button[type=submit]').forEach(function (b) { b.disabled = on; }); form.classList.toggle('is-busy', on); }
    function valid(d) {
      var nombre = (d.get('nombre') || '').trim(), tel = (d.get('telefono') || '').trim(), email = (d.get('email') || '').trim(), msg = (d.get('mensaje') || '').trim();
      form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
      if (nombre.length < 2) { fail('Escribe tu nombre.', form.nombre); return null; }
      if (tel.replace(/\D/g, '').length < 9) { fail('Escribe un teléfono válido de 9 cifras.', form.telefono); return null; }
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { fail('Revisa el correo: parece incompleto.', form.email); return null; }
      if (msg.length < 10) { fail('Cuéntanos brevemente qué necesitas (mínimo 10 caracteres).', form.mensaje); return null; }
      if (!form.privacidad.checked) { fail('Acepta la política de privacidad para continuar.'); return null; }
      return { nombre: nombre, tel: tel, email: email, msg: msg };
    }
    function postLead(p) {
      if (!window.fetch) return Promise.resolve(false);
      var ctl = window.AbortController ? new AbortController() : null, t = setTimeout(function () { if (ctl) ctl.abort(); }, 8000);
      return fetch(root + (CFG.ENDPOINT || 'contact.php'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p), keepalive: true, signal: ctl ? ctl.signal : undefined })
        .then(function (r) { return r.ok ? r.json() : { ok: false }; }).then(function (r) { clearTimeout(t); return !!(r && r.ok); }).catch(function () { clearTimeout(t); return false; });
    }
    function thanks(canal) { location.href = root + 'gracias/?c=' + canal; }
    function submit(canal) {
      var d = new FormData(form); if (d.get('web')) return;
      var v = valid(d); if (!v) return;
      var servicio = d.get('servicio') || '', perfil = d.get('perfil') || '';
      var p = { origen: 'contacto', canal: canal, nombre: v.nombre, telefono: v.tel, email: v.email, servicio: servicio, perfil: perfil, mensaje: v.msg,
                pagina: location.href, web: '', privacidad: true, politica_version: '2026-11-01' };
      var a = window.UrbAttribution ? window.UrbAttribution() : {}; Object.keys(a).forEach(function (k) { p[k] = a[k]; });
      var text = ['Hola, soy ' + v.nombre + '.', 'Teléfono: ' + v.tel + (v.email ? '\nCorreo: ' + v.email : ''), perfil ? 'Soy: ' + perfil : '',
                  servicio ? 'Necesito: ' + servicio : '', '\n' + v.msg, '\nQuiero un presupuesto gratuito.'].filter(Boolean).join('\n');
      busy(true);
      if (canal === 'whatsapp') {
        var w = window.open(waLink(text), '_blank'); if (w) w.opener = null;
        say('Abriendo WhatsApp… y enviando copia al correo.');
        var done = false, go = function () { if (done) return; done = true; if (!w) location.href = waLink(text); else thanks('whatsapp'); };
        postLead(p).then(go); setTimeout(go, 3500);
      } else {
        say('Enviando…');
        postLead(p).then(function (ok) {
          if (ok) { thanks('email'); return; }
          busy(false);
          fail('No hemos podido enviarlo automáticamente. Hemos abierto tu programa de correo con el mensaje listo; también puedes usar WhatsApp.');
          location.href = 'mailto:' + (CFG.EMAIL || 'info@grupo-urbanisima.com') + '?subject=' + encodeURIComponent('Solicitud de presupuesto - ' + v.nombre) + '&body=' + encodeURIComponent(text);
        });
      }
    }
    form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
    form.addEventListener('submit', function (e) { e.preventDefault(); submit(e.submitter && e.submitter.value === 'email' ? 'email' : 'whatsapp'); });
  }

  /* ---------- Clics en teléfono y WhatsApp (medición) ---------- */
  document.addEventListener('click', function (e) {
    var q = e.target.closest && e.target.closest('[data-cta]');
    if (q && window.UrbTrack) window.UrbTrack('click_quote_cta', { ubicacion: q.getAttribute('data-cta') });
    var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
    if (a && window.UrbTrack) window.UrbTrack(a.href.indexOf('tel:') === 0 ? 'click_phone' : 'click_whatsapp');
  });

  var yr = document.getElementById('year'); if (yr) yr.textContent = new Date().getFullYear();

  /* Medición: vista de una página de servicio (solo se registra si el visitante aceptó cookies de medición) */
  var svName = document.body.getAttribute('data-servicio');
  if (svName) setTimeout(function () { if (window.UrbTrack) window.UrbTrack('service_view', { servicio: svName }); }, 800);
})();
