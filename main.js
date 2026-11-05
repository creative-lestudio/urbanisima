(function () {
  var CFG = window.URBANISIMA_CONFIG || {};
  var WA = CFG.WHATSAPP || '34722115251';
  // El número de WhatsApp de config.js manda sobre cualquier enlace wa.me del HTML (se cambia en un solo sitio)
  document.querySelectorAll('a[href*="wa.me/"]').forEach(function (a) {
    a.setAttribute('href', a.getAttribute('href').replace(/wa\.me\/\+?\d+/, 'wa.me/' + WA));
  });
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var header = document.querySelector('.header');
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  var bar = document.querySelector('.progress span');
  if (!reduce) document.documentElement.classList.add('js');

  /* ---------- Scroll: cabecera + barra de progreso ---------- */
  if ('scrollRestoration' in history && !location.hash) history.scrollRestoration = 'manual';
  var lastY = scrollY, mobileMq = matchMedia('(max-width: 760px)');
  function onScroll() {
    header.classList.toggle('solid', window.scrollY > 24);
    // En móvil la cabecera se oculta al bajar y reaparece al subir, para no tapar el contenido
    var dy = scrollY - lastY;
    if (mobileMq.matches && Math.abs(dy) > 6) {
      header.classList.toggle('hide', dy > 0 && scrollY > 30);
      lastY = scrollY;
    } else if (!mobileMq.matches) header.classList.remove('hide');
    var h = document.documentElement.scrollHeight - innerHeight;
    if (bar && h > 0) bar.style.transform = 'scaleX(' + Math.min(scrollY / h, 1) + ')';
  }
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Menú móvil ---------- */
  function setMenu(open) {
    menu.classList.toggle('open', open);
    header.classList.toggle('menu-open', open);
    document.documentElement.style.overflow = open ? 'hidden' : '';
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  }
  burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* ---------- Titular del hero: palabras que suben ---------- */
  (function splitHeadline() {
    var h1 = document.querySelector('.hero h1');
    if (!h1 || reduce) return;
    var i = 0;
    function wrap(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (t) {
            if (!t) return;
            if (/^\s+$/.test(t)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var s = document.createElement('span'); s.style.setProperty('--i', i++); s.textContent = t;
            w.appendChild(s); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1) wrap(n);
      });
    }
    wrap(h1);
  })();

  /* ---------- Perfil de cliente (opcional, viene de los anuncios con ?perfil=) ---------- */
  var NAMES = { particulares: 'viviendas particulares', comunidades: 'comunidades de vecinos', empresas: 'naves industriales' };
  var currentCat = 'all';

  /* ---------- Foco de luz que sigue al ratón ---------- */
  document.querySelectorAll('.grp, .benefits li').forEach(function (el) {
    el.classList.add('spot');
    el.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* ---------- Formularios: WhatsApp / correo, siempre con copia al correo de la empresa ---------- */
  var WHO = { particulares: 'Vivienda particular', comunidades: 'Comunidad de vecinos', empresas: 'Nave industrial' };
  function waLink(text) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(text); }
  function fail(form, msg, field) {
    var m = form.querySelector('.form-msg');
    m.className = 'form-msg'; m.textContent = msg;
    if (field) { field.classList.add('is-invalid'); field.focus(); }
  }
  function say(form, msg) { var m = form.querySelector('.form-msg'); m.className = 'form-msg ok'; m.textContent = msg; }
  function busy(form, on) {
    form.querySelectorAll('button[type=submit]').forEach(function (b) { b.disabled = on; });
    form.classList.toggle('is-busy', on);
  }
  function validContact(form, d, needMessage) {
    var nombre = (d.get('nombre') || '').trim(), tel = (d.get('telefono') || '').trim();
    var email = (d.get('email') || '').trim(), msg = (d.get('mensaje') || '').trim();
    form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
    if (nombre.length < 2) { fail(form, 'Escribe tu nombre.', form.nombre); return null; }
    if (tel.replace(/\D/g, '').length < 9) { fail(form, 'Escribe un teléfono válido de 9 cifras.', form.telefono); return null; }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { fail(form, 'Revisa el correo: parece incompleto.', form.email); return null; }
    if (needMessage && msg.length < 10) { fail(form, 'Cuéntanos brevemente qué necesitas (mínimo 10 caracteres).', form.mensaje); return null; }
    if (form.privacidad && !form.privacidad.checked) { fail(form, 'Acepta la política de privacidad para continuar.'); return null; }
    return { nombre: nombre, tel: tel, email: email, msg: msg };
  }
  function payload(origen, canal, d, v) {
    var p = {
      origen: origen, canal: canal, nombre: v.nombre, telefono: v.tel, email: v.email,
      servicio: d.get('servicio') || '', perfil: currentCat !== 'all' ? WHO[currentCat] : '',
      mensaje: v.msg, pagina: location.href, web: d.get('web') || '',
      privacidad: true, politica_version: '2026-11-01'
    };
    var a = window.UrbAttribution ? window.UrbAttribution() : {};
    Object.keys(a).forEach(function (k) { p[k] = a[k]; });
    return p;
  }
  function postLead(p) { // devuelve una promesa con true/false; nunca lanza error
    if (!window.fetch) return Promise.resolve(false);
    var ctl = window.AbortController ? new AbortController() : null;
    var t = setTimeout(function () { if (ctl) ctl.abort(); }, 8000);
    return fetch(CFG.ENDPOINT || 'contact.php', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p), keepalive: true, signal: ctl ? ctl.signal : undefined
    }).then(function (r) { return r.ok ? r.json() : { ok: false }; })
      .then(function (r) { clearTimeout(t); return !!(r && r.ok); })
      .catch(function () { clearTimeout(t); return false; });
  }
  function thanks(canal) { location.href = 'gracias/?c=' + canal; }
  function lines(v, d, p) {
    return ['Hola, soy ' + v.nombre + '.', 'Teléfono: ' + v.tel + (v.email ? '\nCorreo: ' + v.email : ''),
      p.perfil ? 'Soy: ' + p.perfil : '', d.get('servicio') ? 'Necesito: ' + d.get('servicio') : '',
      v.msg ? '\n' + v.msg : '', '\nQuiero un presupuesto gratuito.'].filter(Boolean).join('\n');
  }
  function submitLead(form, origen, needMessage, canal) {
    var d = new FormData(form);
    if (d.get('web')) return; // trampa anti-bots
    var v = validContact(form, d, needMessage);
    if (!v) return;
    var p = payload(origen, canal, d, v), text = lines(v, d, p);
    busy(form, true);
    if (canal === 'whatsapp') {
      // se abre WhatsApp al instante (clic del usuario) y, a la vez, se envía la copia al correo
      var w = window.open(waLink(text), '_blank'); if (w) w.opener = null;
      say(form, 'Abriendo WhatsApp… y enviando copia al correo.');
      var done = false, go = function () { if (done) return; done = true; if (!w) location.href = waLink(text); else thanks('whatsapp'); };
      postLead(p).then(go); setTimeout(go, 3500);
    } else {
      say(form, 'Enviando…');
      postLead(p).then(function (ok) {
        if (ok) { thanks('email'); return; }
        // plan B: si el servidor no responde, se abre el correo del usuario con el mensaje ya redactado
        busy(form, false);
        fail(form, 'No hemos podido enviarlo automáticamente. Hemos abierto tu programa de correo con el mensaje listo; también puedes usar WhatsApp.');
        location.href = 'mailto:' + (CFG.EMAIL || 'info@grupo-urbanisima.com') + '?subject=' + encodeURIComponent('Solicitud de presupuesto - ' + v.nombre) + '&body=' + encodeURIComponent(text);
      });
    }
  }

  /* Formulario de contacto (abajo): descripción obligatoria y dos botones */
  var contact = document.getElementById('contact-form');
  contact.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  contact.addEventListener('submit', function (e) {
    e.preventDefault();
    var canal = e.submitter && e.submitter.value === 'email' ? 'email' : 'whatsapp';
    submitLead(contact, 'contacto', true, canal);
  });

  // "Pedir presupuesto" en una tarjeta o en el pie: elige el servicio en el formulario de contacto
  var sel = document.getElementById('servicio-select');
  function selectService(t) {
    var ok = false;
    Array.prototype.forEach.call(sel.options, function (o) { if (o.value === t || o.text === t) ok = true; });
    sel.value = ok ? t : 'Otro';
  }
  document.querySelectorAll('[data-title]').forEach(function (a) {
    a.addEventListener('click', function () { selectService(a.getAttribute('data-title')); });
  });

  /* Formulario del hero (arriba): un solo paso */
  var hero = document.getElementById('hero-form');
  var heroSel = document.getElementById('hero-servicio');
  hero.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  hero.addEventListener('submit', function (e) {
    e.preventDefault();
    submitLead(hero, 'hero', true, e.submitter && e.submitter.value === 'email' ? 'email' : 'whatsapp');
  });
  function pickIn(select, t) {
    var ok = false;
    Array.prototype.forEach.call(select.options, function (o) { if (o.value === t || o.text === t) ok = true; });
    select.value = ok ? t : 'Otro';
  }
  // Los enlaces "Pedir presupuesto" de los servicios rellenan también el formulario de arriba
  document.querySelectorAll('[data-title]').forEach(function (a) {
    a.addEventListener('click', function () { pickIn(heroSel, a.getAttribute('data-title')); });
  });

  /* Enlaces desde anuncios: ?perfil=comunidades&servicio=impermeabilizacion (y gclid/utm se guardan en tracking.js) */
  (function fromAds() {
    var q = new URLSearchParams(location.search), perfil = q.get('perfil'), slug = q.get('servicio');
    if (perfil && NAMES[perfil]) currentCat = perfil;
    var a = slug && document.querySelector('[data-slug="' + slug.replace(/[^a-z]/g, '') + '"]');
    if (a) { var t = a.getAttribute('data-title'); pickIn(heroSel, t); selectService(t); }
  })();

  /* ?ir=servicios|contacto|proteccion|ventajas: baja a esa sección (lo usan las redirecciones de las URLs antiguas) */
  (function goTo() {
    var id = new URLSearchParams(location.search).get('ir');
    if (!id || !/^(servicios|contacto|proteccion|proceso|ventajas)$/.test(id)) return;
    if (id === 'proteccion') id = 'proceso';
    var el = document.getElementById(id); if (!el) return;
    setTimeout(function () { el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 400);
  })();

  /* Clics en teléfono y WhatsApp (medición de conversiones) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href*="wa.me"]');
    if (a && window.UrbTrack) window.UrbTrack(a.href.indexOf('tel:') === 0 ? 'click_call' : 'click_whatsapp');
  });

  /* ---------- Contadores ---------- */
  var els = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        var el = en.target, end = +el.dataset.count, t0 = performance.now();
        (function tick(t) {
          var p = Math.min((t - t0) / 1200, 1);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: .6 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Entrada suave al hacer scroll ---------- */
  if ('IntersectionObserver' in window && !reduce) {
    var targets = document.querySelectorAll('.head, .grp, .steps li, .benefits li, .contact-copy');
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); ro.unobserve(en.target); }
      });
    }, { threshold: .1, rootMargin: '0px 0px -30px 0px' });
    targets.forEach(function (el) { el.classList.add('reveal'); ro.observe(el); });
  }

  /* ---------- Pie: año actual y volver arriba ---------- */
  var yr = document.getElementById('year'); if (yr) yr.textContent = new Date().getFullYear();
  var toTop = document.getElementById('to-top');
  if (toTop) toTop.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
})();
