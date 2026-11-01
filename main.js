(function () {
  var CFG = window.URBANISIMA_CONFIG || {};
  var WA = CFG.WHATSAPP || '34722115251';
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

  /* ---------- Servicios: siempre los 14, ordenados por probabilidad según el perfil ---------- */
  var grid = document.getElementById('service-grid');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.svc'));
  var status = document.getElementById('svc-status');
  var tabs = document.querySelectorAll('.tab');
  var NAMES = { particulares: 'particulares', comunidades: 'comunidades de vecinos', empresas: 'empresas y naves industriales' };
  var currentCat = 'all', pickSlug = null;

  function titleOf(c) { return c.querySelector('h3').textContent; }
  function applyCategory(cat) {
    var before = cards.map(function (c) { return c.getBoundingClientRect(); });
    currentCat = cat;
    grid.dataset.cat = cat;
    tabs.forEach(function (t) {
      var on = t.dataset.filter === cat;
      t.classList.toggle('is-on', on); t.setAttribute('aria-selected', String(on));
    });
    var sorted = cat === 'all' ? cards.slice() : cards.slice().sort(function (a, b) { return a.dataset[cat] - b.dataset[cat]; });
    sorted.forEach(function (c, i) {
      c.style.order = i + 1;
      c.classList.toggle('is-top', cat !== 'all' && i < 3);
      c.classList.remove('is-pick');
      c.querySelector('.tag').textContent = 'Más solicitado';
    });
    var pick = pickSlug && grid.querySelector('[data-slug="' + pickSlug + '"]');
    if (pick) { // servicio que llega desde un anuncio: va primero
      pick.style.order = 0; pick.classList.add('is-pick', 'is-top'); pick.querySelector('.tag').textContent = 'Lo que buscas';
    }
    status.textContent = cat === 'all'
      ? 'Mostrando los 14 servicios'
      : 'Los 14 servicios, de más a menos solicitados por ' + NAMES[cat];
    if (!reduce) { // animación FLIP: las tarjetas se deslizan a su nueva posición
      cards.forEach(function (c, i) {
        var a2 = c.getBoundingClientRect(), dx = before[i].left - a2.left, dy = before[i].top - a2.top;
        if (!dx && !dy) return;
        c.style.transition = 'none'; c.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
        requestAnimationFrame(function () {
          c.style.transition = 'transform .5s cubic-bezier(.2,.8,.2,1), opacity .3s, box-shadow .2s, border-color .2s';
          c.style.transform = '';
        });
      });
    }
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { applyCategory(t.dataset.filter); }); });
  document.querySelectorAll('a[data-cat]').forEach(function (a) {
    a.addEventListener('click', function () { applyCategory(a.dataset.cat); });
  });

  /* ---------- Foco de luz que sigue al ratón ---------- */
  document.querySelectorAll('.svc, .benefits li').forEach(function (el) {
    el.classList.add('spot');
    el.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* ---------- Formularios: WhatsApp / correo, siempre con copia al correo de la empresa ---------- */
  var WHO = { particulares: 'Particular', comunidades: 'Comunidad de vecinos', empresas: 'Empresa / nave industrial' };
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
      mensaje: v.msg, pagina: location.href, web: d.get('web') || ''
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

  /* Formulario interactivo del hero (arriba): 2 pasos, opciones según el perfil */
  var hero = document.getElementById('hero-form');
  var panes = hero.querySelectorAll('.hf-pane');
  var hfStep = document.getElementById('hf-step'), hfFill = document.getElementById('hf-fill');
  var chips = document.getElementById('hf-chips'), hfSub = document.getElementById('hf-sub2');
  function heroGo(n) {
    panes.forEach(function (p) { p.classList.toggle('is-on', +p.dataset.pane === n); });
    hfStep.textContent = 'Paso ' + n + ' de 2';
    hfFill.style.width = (n * 50) + '%';
    hero.querySelector('.form-msg').textContent = '';
  }
  function buildChips(cat, wanted) {
    var top = cards.slice().sort(function (a, b) { return a.dataset[cat] - b.dataset[cat]; }).slice(0, 5).map(titleOf);
    if (wanted && top.indexOf(wanted) < 0) top.unshift(wanted);
    top.push('Otro');
    chips.innerHTML = '';
    top.forEach(function (t, i) {
      var l = document.createElement('label'); l.className = 'hf-chip';
      var inp = document.createElement('input'); inp.type = 'radio'; inp.name = 'servicio'; inp.value = t;
      inp.checked = wanted ? t === wanted : i === 0;
      var sp = document.createElement('span'); sp.textContent = t;
      l.appendChild(inp); l.appendChild(sp); chips.appendChild(l);
    });
    hfSub.textContent = 'Lo más pedido por ' + NAMES[cat] + '. Elige uno.';
  }
  hero.querySelectorAll('.cat').forEach(function (b) {
    b.addEventListener('click', function () {
      applyCategory(b.dataset.cat);
      buildChips(b.dataset.cat);
      heroGo(2);
      if (mobileMq.matches) { var r = hero.getBoundingClientRect(); if (r.top < 70 || r.bottom > innerHeight - 70) scrollTo({ top: scrollY + r.top - 76, behavior: reduce ? 'auto' : 'smooth' }); }
    });
  });
  document.getElementById('hf-back').addEventListener('click', function () { heroGo(1); });
  hero.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  hero.addEventListener('submit', function (e) {
    e.preventDefault();
    submitLead(hero, 'hero', true, e.submitter && e.submitter.value === 'email' ? 'email' : 'whatsapp');
  });

  /* Enlaces desde anuncios: ?perfil=comunidades&servicio=impermeabilizacion (y gclid/utm se guardan en tracking.js) */
  (function fromAds() {
    var q = new URLSearchParams(location.search), perfil = q.get('perfil'), slug = q.get('servicio');
    var card = slug && grid.querySelector('[data-slug="' + slug.replace(/[^a-z]/g, '') + '"]');
    if (card) pickSlug = card.dataset.slug;
    if (perfil && NAMES[perfil]) {
      applyCategory(perfil); buildChips(perfil, card ? titleOf(card) : null); heroGo(2);
    } else if (card) applyCategory('all');
    if (card) selectService(titleOf(card));
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
    var targets = document.querySelectorAll('.head, .benefits li, .contact-copy, .demo-copy');
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); ro.unobserve(en.target); }
      });
    }, { threshold: .1, rootMargin: '0px 0px -30px 0px' });
    targets.forEach(function (el) { el.classList.add('reveal'); ro.observe(el); });
  }

  /* ---------- Escena de lluvia: gotera vs. cubierta protegida ---------- */
  (function rain() {
    var cv = document.getElementById('rain');
    if (!cv || !cv.getContext) return;
    var ctx = cv.getContext('2d');
    var W = 600, H = 420, GROUND = 380, SLOPE = 110 / 190;
    var LEAKS = [232, 368], LEAK_W = 10;
    var safe = false, drops = [], splashes = [], puddle = [0, 0], stain = [0, 0], leaked = 0, running = false, frame = 0;
    var chip = document.getElementById('stage-chip'), count = document.getElementById('stage-count');

    function roofY(x) { return x <= 300 ? 220 - (x - 110) * SLOPE : 110 + (x - 300) * SLOPE; }
    function leakIdx(x) { for (var i = 0; i < LEAKS.length; i++) if (Math.abs(x - LEAKS[i]) < LEAK_W) return i; return -1; }
    function resize() {
      var dpr = Math.min(devicePixelRatio || 1, 2);
      cv.width = Math.round(cv.clientWidth * dpr);
      cv.height = Math.round(cv.clientHeight * dpr);
      ctx.setTransform(cv.width / W, 0, 0, cv.height / H, 0, 0);
    }
    function splash(x, y, n) {
      for (var i = 0; i < n; i++) splashes.push({ x: x, y: y, vx: (Math.random() - .5) * 3, vy: -(1 + Math.random() * 2), l: 16 });
    }
    function spawn() {
      for (var i = 0; i < 2; i++) drops.push({ x: Math.random() * W, y: -10, vx: .8, vy: 6 + Math.random() * 3, inside: false, li: -1 });
    }
    function update() {
      spawn();
      for (var i = drops.length - 1; i >= 0; i--) {
        var d = drops[i];
        d.x += d.vx; d.y += d.vy;
        var onHouse = d.x > 110 && d.x < 490;
        if (d.inside) {
          if (d.y >= GROUND - 2) { puddle[d.li] = Math.min(64, puddle[d.li] + 1.4); splash(d.x, GROUND - 2, 2); drops.splice(i, 1); }
        } else if (onHouse && d.y >= roofY(d.x)) {
          var li = leakIdx(d.x);
          if (!safe && li >= 0) { d.inside = true; d.li = li; d.vx = 0; leaked++; stain[li] = Math.min(1, stain[li] + .012); }
          else { splash(d.x, roofY(d.x), 2); drops.splice(i, 1); }
        } else if (!onHouse && d.y >= GROUND) { splash(d.x, GROUND, 2); drops.splice(i, 1); }
      }
      for (var j = splashes.length - 1; j >= 0; j--) {
        var s = splashes[j]; s.x += s.vx; s.y += s.vy; s.vy += .18; s.l--;
        if (s.l <= 0) splashes.splice(j, 1);
      }
      if (safe) for (var k = 0; k < 2; k++) { puddle[k] = Math.max(0, puddle[k] - .5); stain[k] = Math.max(0, stain[k] - .006); }
      if (++frame % 8 === 0) count.textContent = safe ? '0 filtraciones' : leaked + ' gotas dentro';
    }
    function draw() {
      var g = ctx.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, safe ? '#12395f' : '#0a1626'); g.addColorStop(1, safe ? '#1b5a8f' : '#12263d');
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = '#0c2238'; ctx.fillRect(0, GROUND, W, H - GROUND);
      // interior
      ctx.beginPath(); ctx.moveTo(150, GROUND); ctx.lineTo(150, 222); ctx.lineTo(300, 125); ctx.lineTo(450, 222); ctx.lineTo(450, GROUND); ctx.closePath();
      var ig = ctx.createLinearGradient(0, 120, 0, GROUND);
      if (safe) { ig.addColorStop(0, 'rgba(255,214,102,.55)'); ig.addColorStop(1, 'rgba(255,236,170,.28)'); }
      else { ig.addColorStop(0, 'rgba(8,20,34,.95)'); ig.addColorStop(1, 'rgba(18,34,52,.95)'); }
      ctx.fillStyle = ig; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.stroke();
      // ventanas
      [[185, 270], [365, 270]].forEach(function (p) {
        ctx.fillStyle = safe ? '#ffe28a' : '#1b3047'; ctx.fillRect(p[0], p[1], 50, 46);
        ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.lineWidth = 1.5; ctx.strokeRect(p[0], p[1], 50, 46);
        ctx.beginPath(); ctx.moveTo(p[0] + 25, p[1]); ctx.lineTo(p[0] + 25, p[1] + 46); ctx.stroke();
      });
      // manchas de humedad
      LEAKS.forEach(function (x, i) {
        if (stain[i] > 0) {
          var rg = ctx.createRadialGradient(x, roofY(x) + 12, 2, x, roofY(x) + 12, 16 + stain[i] * 34);
          rg.addColorStop(0, 'rgba(120,84,40,' + (.75 * stain[i]) + ')'); rg.addColorStop(1, 'rgba(120,84,40,0)');
          ctx.fillStyle = rg; ctx.fillRect(x - 60, roofY(x) - 10, 120, 100);
        }
        if (puddle[i] > 0) {
          ctx.fillStyle = 'rgba(120,190,255,.7)';
          ctx.beginPath(); ctx.ellipse(x, GROUND - 2, puddle[i], 1 + puddle[i] * .12, 0, 0, 7); ctx.fill();
        }
      });
      // cubierta
      ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      if (safe) { ctx.shadowColor = '#5cc8ff'; ctx.shadowBlur = 22; }
      ctx.lineWidth = 9; ctx.strokeStyle = safe ? '#fec200' : '#8795a5';
      ctx.beginPath(); ctx.moveTo(110, 220); ctx.lineTo(300, 110); ctx.lineTo(490, 220); ctx.stroke();
      ctx.shadowBlur = 0;
      if (safe) { // escudo
        ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(140,215,255,.8)'; ctx.setLineDash([6, 8]);
        ctx.beginPath(); ctx.moveTo(96, 214); ctx.lineTo(300, 92); ctx.lineTo(504, 214); ctx.stroke(); ctx.setLineDash([]);
      } else { // grietas
        ctx.fillStyle = '#050c15';
        LEAKS.forEach(function (x) { ctx.fillRect(x - 4, roofY(x) - 6, 8, 12); });
      }
      // gotas
      ctx.lineCap = 'round';
      drops.forEach(function (d) {
        ctx.strokeStyle = d.inside ? 'rgba(130,195,255,.95)' : 'rgba(190,220,255,.7)'; ctx.lineWidth = d.inside ? 2.2 : 1.4;
        ctx.beginPath(); ctx.moveTo(d.x - d.vx * 1.3, d.y - d.vy * 1.3); ctx.lineTo(d.x, d.y); ctx.stroke();
      });
      ctx.fillStyle = 'rgba(200,228,255,.85)';
      splashes.forEach(function (s) { ctx.globalAlpha = s.l / 16; ctx.fillRect(s.x, s.y, 2, 2); });
      ctx.globalAlpha = 1;
    }
    function loop() { if (!running) return; update(); draw(); requestAnimationFrame(loop); }
    function setMode(s) {
      safe = s; leaked = 0;
      chip.textContent = s ? 'Cubierta protegida' : 'Goteras activas';
      chip.className = 'chip ' + (s ? 'good' : 'bad');
      document.querySelectorAll('.sw').forEach(function (b) {
        var on = (b.dataset.mode === 'safe') === s;
        b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', String(on));
      });
      if (!running) { for (var i = 0; i < 30; i++) update(); draw(); }
    }
    document.querySelectorAll('.sw').forEach(function (b) {
      b.addEventListener('click', function () { setMode(b.dataset.mode === 'safe'); });
    });
    resize(); addEventListener('resize', function () { resize(); if (!running) draw(); });
    if (reduce) { setMode(false); return; }
    setMode(false);
    new IntersectionObserver(function (en) {
      var vis = en[0].isIntersecting;
      if (vis && !running) { running = true; loop(); } else if (!vis) running = false;
    }, { threshold: .15 }).observe(cv);
  })();

  /* ---------- Pie: año actual y volver arriba ---------- */
  var yr = document.getElementById('year'); if (yr) yr.textContent = new Date().getFullYear();
  var toTop = document.getElementById('to-top');
  if (toTop) toTop.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
})();
