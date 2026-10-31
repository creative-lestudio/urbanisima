(function () {
  var WA = '34722115251';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var header = document.querySelector('.header');
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  var bar = document.querySelector('.progress span');
  if (!reduce) document.documentElement.classList.add('js');

  /* ---------- Scroll: cabecera + barra de progreso ---------- */
  function onScroll() {
    header.classList.toggle('solid', window.scrollY > 24);
    var h = document.documentElement.scrollHeight - innerHeight;
    if (bar && h > 0) bar.style.transform = 'scaleX(' + Math.min(scrollY / h, 1) + ')';
  }
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Menú móvil ---------- */
  function setMenu(open) {
    menu.classList.toggle('open', open);
    header.classList.toggle('menu-open', open);
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

  /* ---------- Filtro de servicios ---------- */
  var tabs = document.querySelectorAll('.tab');
  var cards = document.querySelectorAll('#service-grid .svc');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var f = tab.dataset.filter;
      tabs.forEach(function (t) {
        var on = t === tab;
        t.classList.toggle('is-on', on);
        t.setAttribute('aria-selected', String(on));
      });
      cards.forEach(function (c) { c.hidden = f !== 'all' && c.dataset.for.split(' ').indexOf(f) === -1; });
    });
  });

  /* ---------- Foco de luz que sigue al ratón ---------- */
  document.querySelectorAll('.svc, .benefits li, .steps li').forEach(function (el) {
    el.classList.add('spot');
    el.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* ---------- Envío a WhatsApp ---------- */
  function waLink(text) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(text); }
  function fail(form, msg, field) {
    var m = form.querySelector('.form-msg');
    m.className = 'form-msg'; m.textContent = msg;
    if (field) { field.classList.add('is-invalid'); field.focus(); }
  }
  function validContact(form, d) {
    var nombre = (d.get('nombre') || '').trim(), tel = (d.get('telefono') || '').trim();
    form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
    if (!nombre) { fail(form, 'Escribe tu nombre.', form.nombre); return null; }
    if (tel.replace(/\D/g, '').length < 9) { fail(form, 'Escribe un teléfono válido de 9 cifras.', form.telefono); return null; }
    if (form.privacidad && !form.privacidad.checked) { fail(form, 'Acepta la política de privacidad para continuar.'); return null; }
    return { nombre: nombre, tel: tel };
  }
  function sent(form) {
    var m = form.querySelector('.form-msg');
    m.className = 'form-msg ok'; m.textContent = 'Abriendo WhatsApp con tu mensaje…';
  }

  // Formulario rápido del hero
  var quick = document.getElementById('quick-form');
  quick.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  quick.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(quick), v = validContact(quick, d);
    if (!v) return;
    var text = 'Hola, soy ' + v.nombre + '. Mi teléfono es ' + v.tel + '.' +
      (d.get('servicio') ? ' Necesito: ' + d.get('servicio') + '.' : '') + ' Quiero un presupuesto gratuito.';
    sent(quick);
    window.open(waLink(text), '_blank', 'noopener');
  });

  /* ---------- Formulario por pasos ---------- */
  var form = document.getElementById('contact-form');
  var steps = form.querySelectorAll('.step');
  var label = document.getElementById('step-label');
  var fill = document.getElementById('bar-fill');
  var back = document.getElementById('btn-back');
  var cur = 1;
  function go(n) {
    cur = n;
    steps.forEach(function (s) { s.classList.toggle('is-on', +s.dataset.step === n); });
    label.textContent = 'Paso ' + n + ' de 3';
    fill.style.width = (n / 3 * 100) + '%';
    back.hidden = n === 1;
    form.querySelector('.form-msg').textContent = '';
  }
  form.addEventListener('change', function (e) {
    if (e.target.type !== 'radio') return;
    var n = +e.target.closest('.step').dataset.step;
    if (n < 3) setTimeout(function () { go(n + 1); }, 220);
  });
  back.addEventListener('click', function () { go(Math.max(1, cur - 1)); });
  form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(form), v = validContact(form, d);
    if (!v) return;
    var text = 'Hola, soy ' + v.nombre + '. Mi teléfono es ' + v.tel + '.' +
      (d.get('servicio') ? ' Necesito: ' + d.get('servicio') + '.' : '') +
      (d.get('cliente') ? ' Es para: ' + d.get('cliente') + '.' : '') +
      (d.get('mensaje') ? ' ' + d.get('mensaje').trim() : '') + ' Quiero un presupuesto gratuito.';
    sent(form);
    window.open(waLink(text), '_blank', 'noopener');
  });

  // "Pedir presupuesto" en una tarjeta: preselecciona el servicio y salta al paso 2
  document.querySelectorAll('[data-service]').forEach(function (a) {
    a.addEventListener('click', function () {
      var val = a.getAttribute('data-service');
      var radio = form.querySelector('input[name="servicio"][value="' + val.replace(/"/g, '') + '"]');
      if (!radio) {
        radio = form.querySelector('input[name="servicio"][value="Otro"]');
        form.mensaje.value = 'Me interesa: ' + val + '.';
      }
      radio.checked = true;
      go(2);
    });
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
    var targets = document.querySelectorAll('.head, .svc, .shot, .steps li, .benefits li, .faq details, .contact-copy, .demo-copy');
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
})();
