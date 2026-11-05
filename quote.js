/* Sistema único de presupuesto: se monta en cada <div data-quote> (portada y páginas de servicio).
   3 pasos: ¿Qué necesitas? > ¿Dónde y cuándo? > ¿Cómo te contactamos?
   Atributos opcionales del contenedor: data-service="<título del servicio>" (precarga), data-icon="<id de icono>".
   También acepta ?servicio=<clave> y ?perfil=particulares|comunidades|empresas (enlaces de anuncios). */
(function () {
  var holders = document.querySelectorAll('[data-quote]');
  if (!holders.length) return;
  var CFG = window.URBANISIMA_CONFIG || {};
  var SV = window.URB_SERVICES || {};            // clave -> título (assets/servicios-data.js, generado)
  var WA = CFG.WHATSAPP || '34722115251';
  var ROOT = document.body.getAttribute('data-root') || '';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var WHO = { particulares: 'Particular', comunidades: 'Comunidad de vecinos', empresas: 'Empresa o nave industrial' };
  var qs = new URLSearchParams(location.search);
  var perfilQS = WHO[qs.get('perfil')] ? WHO[qs.get('perfil')] : '';
  var keyQS = (qs.get('servicio') || '').replace(/[^a-z]/g, '');

  var TILES = [ // clave del servicio que se envía, icono, texto
    ['goteras', 'drop', 'Reparar goteras o humedades'],
    ['tejados', 'roof', 'Reparar un tejado'],
    ['impermeabilizacion', 'umbrella', 'Impermeabilizar una terraza'],
    ['reforma', 'hammer', 'Realizar una reforma'],
    ['fachadas', 'building', 'Reparar una fachada']
  ];
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function ico(n) { return '<svg class="i" aria-hidden="true"><use href="#i-' + n + '"/></svg>'; }
  function track(n, p) { if (window.UrbTrack) window.UrbTrack(n, p); }

  holders.forEach(function (holder, idx) { mount(holder, idx); });

  function mount(holder, idx) {
    var pre = holder.getAttribute('data-service') || (keyQS && SV[keyQS]) || '';
    var preIcon = holder.getAttribute('data-icon') || 'tools';
    var id = 'q' + idx + '-';
    var tiles = TILES.map(function (t) { return { v: SV[t[0]] || t[2], i: t[1], l: t[2] }; });
    tiles.push({ v: 'Otro', i: 'chat', l: 'Otro trabajo' });
    if (pre && !tiles.some(function (t) { return t.v === pre; })) tiles.unshift({ v: pre, i: preIcon, l: pre });
    var tileHtml = tiles.map(function (t, k) {
      return '<label class="q-tile"><input type="radio" name="servicio" value="' + esc(t.v) + '"' + (t.v === pre ? ' checked' : '') + '>' +
        '<span class="q-ico">' + ico(t.i) + '</span><span class="q-txt">' + esc(t.l) + '</span></label>';
    }).join('');

    holder.innerHTML =
      '<form class="q" novalidate aria-labelledby="' + id + 't">' +
      '<div class="q-top"><span class="q-step" aria-live="polite">Paso 1 de 3</span><span class="q-bar" aria-hidden="true"><i></i></span></div>' +

      '<fieldset class="q-pane" data-pane="1"><legend id="' + id + 't">¿Qué necesitas?</legend>' +
        '<div class="q-tiles">' + tileHtml + '</div>' +
        '<p class="q-err" role="alert"></p>' +
        '<div class="q-nav"><button type="button" class="btn q-next"' + (pre ? '' : ' hidden') + ' data-go="2">Continuar ' + ico('arrow') + '</button></div>' +
      '</fieldset>' +

      '<fieldset class="q-pane" data-pane="2" hidden><legend>¿Dónde y cuándo?</legend>' +
        '<div class="q-field"><label for="' + id + 'loc">Localidad o código postal</label>' +
        '<input id="' + id + 'loc" name="localidad" type="text" autocomplete="address-level2" enterkeyhint="next" placeholder="Ej.: Torrent o 46900"></div>' +
        '<div class="q-field"><span class="q-lab" id="' + id + 'ul">¿Qué urgencia tiene?</span>' +
        '<div class="q-chips" role="radiogroup" aria-labelledby="' + id + 'ul">' +
          ['Sin prisa', 'Próximas semanas', 'Urgente'].map(function (u, k) {
            return '<label class="q-chip"><input type="radio" name="urgencia" value="' + u + '"' + (k === 0 ? ' checked' : '') + '><span>' + u + '</span></label>';
          }).join('') + '</div></div>' +
        '<div class="q-field"><label for="' + id + 'msg">Descripción <small>(opcional)</small></label>' +
        '<textarea id="' + id + 'msg" name="mensaje" rows="2" maxlength="1500" placeholder="Ej.: gotera en el salón cuando llueve, tejado de 80 m²…"></textarea></div>' +
        '<div class="q-field"><span class="q-lab">Fotos <small>(opcional, máximo 3)</small></span>' +
        '<label class="q-photo" for="' + id + 'ph">' + ico('camera') + '<span class="q-ph-txt">Añadir fotos</span></label>' +
        '<input id="' + id + 'ph" class="q-file" type="file" accept="image/jpeg,image/png,image/webp" multiple></div>' +
        '<p class="q-err" role="alert"></p>' +
        '<div class="q-nav"><button type="button" class="q-back" data-go="1">← Atrás</button><button type="button" class="btn q-next" data-go="3">Continuar ' + ico('arrow') + '</button></div>' +
      '</fieldset>' +

      '<fieldset class="q-pane" data-pane="3" hidden><legend>¿Cómo te contactamos?</legend>' +
        '<div class="q-row"><div class="q-field"><label for="' + id + 'n">Nombre</label><input id="' + id + 'n" name="nombre" type="text" autocomplete="name" enterkeyhint="next"></div>' +
        '<div class="q-field"><label for="' + id + 't3">Teléfono</label><input id="' + id + 't3" name="telefono" type="tel" inputmode="tel" autocomplete="tel" enterkeyhint="next" placeholder="6XX XXX XXX"></div></div>' +
        '<div class="q-field"><label for="' + id + 'm">Correo <small>(opcional)</small></label><input id="' + id + 'm" name="email" type="email" inputmode="email" autocomplete="email" enterkeyhint="done"></div>' +
        '<input class="q-trap" name="web" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">' +
        '<label class="q-check"><input type="checkbox" name="privacidad"> <span>He leído y acepto la <a href="' + ROOT + 'ley-proteccion-datos/" target="_blank" rel="noopener">política de privacidad</a></span></label>' +
        '<p class="q-err" role="alert"></p>' +
        '<div class="q-send"><button type="submit" name="canal" value="email" class="btn q-submit">Enviar solicitud</button>' +
        '<button type="submit" name="canal" value="whatsapp" class="btn btn-ghost-dark q-wa">' + ico('chat') + ' Continuar por WhatsApp</button></div>' +
        '<p class="q-hint">Visita gratuita y presupuesto sin compromiso. Si continúas por WhatsApp también recibimos tu solicitud por correo (con las fotos, si las has añadido); las fotos no se adjuntan al chat de WhatsApp.</p>' +
        '<details class="q-rgpd"><summary>Información básica sobre protección de datos</summary><p><strong>Responsable:</strong> Grupo Urbanisima S.L.U. <strong>Finalidad:</strong> atender tu solicitud de presupuesto. <strong>Legitimación:</strong> tu consentimiento y medidas precontractuales. <strong>Destinatarios:</strong> no se ceden datos salvo obligación legal; usamos proveedores de alojamiento y correo y, si eliges WhatsApp, esa plataforma. <strong>Derechos:</strong> acceso, rectificación, supresión, oposición, limitación y portabilidad en info@grupo-urbanisima.com; puedes reclamar ante la AEPD. <a href="' + ROOT + 'ley-proteccion-datos/" target="_blank" rel="noopener">Más información</a></p></details>' +
        '<div class="q-nav"><button type="button" class="q-back" data-go="2">← Atrás</button></div>' +
      '</fieldset>' +
      '<p class="q-status" role="status" aria-live="polite"></p>' +
      '</form>';

    var form = holder.querySelector('form'), panes = form.querySelectorAll('.q-pane');
    var stepEl = form.querySelector('.q-step'), fill = form.querySelector('.q-bar i');
    var step = 1, started = false, photos = [], sent = false;
    fill.style.width = '33%';

    function err(msg, field) {
      var p = form.querySelector('.q-pane:not([hidden]) .q-err'); if (p) p.textContent = msg || '';
      form.querySelectorAll('.is-invalid').forEach(function (x) { x.classList.remove('is-invalid'); });
      if (field) { field.classList.add('is-invalid'); field.setAttribute('aria-invalid', 'true'); field.focus(); }
    }
    function go(n, focus) {
      step = n;
      panes.forEach(function (p) { p.hidden = +p.dataset.pane !== n; });
      stepEl.textContent = 'Paso ' + n + ' de 3'; fill.style.width = Math.round(n * 100 / 3) + '%';
      form.querySelectorAll('.q-err').forEach(function (e) { e.textContent = ''; });
      if (focus === false) return;
      var f = n === 1 ? form.querySelector('.q-tile input:checked') : form.querySelector('.q-pane:not([hidden]) input:not([type=radio]):not([type=file]):not(.q-trap):not([type=checkbox]), .q-pane:not([hidden]) textarea');
      if (f) f.focus({ preventScroll: true });
      var r = holder.getBoundingClientRect();
      if (r.top < 70 || r.bottom > innerHeight) scrollTo({ top: scrollY + r.top - 84, behavior: reduce ? 'auto' : 'smooth' });
    }
    function chosen() { var c = form.querySelector('input[name=servicio]:checked'); return c ? c.value : ''; }
    function ok1() { if (!chosen()) { err('Elige qué necesitas para continuar.'); return false; } return true; }
    function ok2() {
      var l = form.localidad;
      if (l.value.trim().length < 3) { err('Indica tu localidad o código postal.', l); return false; } return true;
    }
    function ok3() {
      var n = form.nombre, t = form.telefono, m = form.email;
      if (n.value.trim().length < 2) { err('Escribe tu nombre.', n); return false; }
      if (t.value.replace(/\D/g, '').length < 9) { err('Escribe un teléfono válido de 9 cifras.', t); return false; }
      if (m.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(m.value.trim())) { err('Revisa el correo: parece incompleto.', m); return false; }
      if (!form.privacidad.checked) { err('Acepta la política de privacidad para continuar.', form.privacidad); return false; }
      return true;
    }
    function next() {
      if (step === 1 && ok1()) { track('form_step_complete', { step: 1 }); go(2); }
      else if (step === 2 && ok2()) { track('form_step_complete', { step: 2 }); go(3); }
    }
    function start() { if (!started) { started = true; track('form_start', { servicio: chosen() }); } }

    form.addEventListener('focusin', start);
    form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); e.target.removeAttribute('aria-invalid'); });
    form.addEventListener('change', function (e) {
      if (e.target.name === 'servicio') {
        form.querySelector('.q-pane[data-pane="1"] .q-next').hidden = false; err('');
        setTimeout(function () { if (step === 1) next(); }, reduce ? 0 : 180);   // avanza solo al elegir
      }
    });
    form.querySelectorAll('[data-go]').forEach(function (b) {
      b.addEventListener('click', function () { var n = +b.dataset.go; if (n > step) next(); else go(n); });
    });

    /* Fotos: se reducen en el navegador (máx. 1600 px) para un envío rápido */
    var fileIn = form.querySelector('.q-file'), phTxt = form.querySelector('.q-ph-txt');
    function shrink(file) {
      return new Promise(function (res) {
        var img = new Image(), url = URL.createObjectURL(file);
        img.onload = function () {
          var k = Math.min(1, 1600 / Math.max(img.width, img.height)), c = document.createElement('canvas');
          c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
          c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
          c.toBlob(function (b) { res(b); }, 'image/jpeg', .82);
        };
        img.onerror = function () { URL.revokeObjectURL(url); res(null); };
        img.src = url;
      });
    }
    fileIn.addEventListener('change', function () {
      var list = Array.prototype.slice.call(fileIn.files, 0, 3);
      phTxt.textContent = 'Preparando fotos…';
      Promise.all(list.map(shrink)).then(function (b) {
        photos = b.filter(Boolean);
        phTxt.textContent = photos.length ? photos.length + (photos.length === 1 ? ' foto lista' : ' fotos listas') + ' · cambiar' : 'Añadir fotos';
        if (fileIn.files.length > 3) err('Solo se envían las 3 primeras fotos.');
      });
    });

    /* Envío */
    function postLead(p) {
      var ctl = window.AbortController ? new AbortController() : null;
      var t = setTimeout(function () { if (ctl) ctl.abort(); }, photos.length ? 30000 : 8000);
      var opts = { method: 'POST', signal: ctl ? ctl.signal : undefined };
      if (photos.length) {
        var fd = new FormData(); fd.append('data', JSON.stringify(p));
        photos.forEach(function (f, i) { fd.append('fotos[]', f, 'foto-' + (i + 1) + '.jpg'); });
        opts.body = fd;
      } else { opts.headers = { 'Content-Type': 'application/json' }; opts.body = JSON.stringify(p); opts.keepalive = true; }
      return fetch(CFG.ENDPOINT ? ROOT + CFG.ENDPOINT : ROOT + 'contact.php', opts)
        .then(function (r) { return r.ok ? r.json() : { ok: false }; })
        .then(function (r) { clearTimeout(t); return !!(r && r.ok); })
        .catch(function () { clearTimeout(t); return false; });
    }
    function busy(on) { form.querySelectorAll('button').forEach(function (b) { b.disabled = on; }); form.classList.toggle('is-busy', on); }
    function say(m) { form.querySelector('.q-status').textContent = m; }
    function waText(p) {
      return ['Hola, soy ' + p.nombre + '. Quiero pedir un presupuesto gratuito.', 'Servicio: ' + p.servicio, 'Localidad: ' + p.localidad,
        'Urgencia: ' + p.urgencia, p.mensaje ? 'Descripción: ' + p.mensaje : '', 'Mi teléfono: ' + p.telefono].filter(Boolean).join('\n');
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (step < 3) { next(); return; }                       // Enter en los primeros pasos solo avanza
      if (form.web.value) return;                             // trampa antiespam
      if (sent) { say('Ya hemos recibido tu solicitud. En breve nos pondremos en contacto.'); return; }
      if (!ok1() && step !== 1) { go(1); return; }
      if (!ok2()) { go(2); err('Indica tu localidad o código postal.', form.localidad); return; }
      if (!ok3()) return;
      var canal = e.submitter && e.submitter.value === 'email' ? 'email' : 'whatsapp';
      var p = {
        origen: 'presupuesto', canal: canal, nombre: form.nombre.value.trim(), telefono: form.telefono.value.trim(), email: form.email.value.trim(),
        servicio: chosen(), localidad: form.localidad.value.trim(), urgencia: form.urgencia.value, perfil: perfilQS,
        mensaje: form.mensaje.value.trim(), pagina: location.href, web: '', privacidad: true, politica_version: '2026-11-01'
      };
      var a = window.UrbAttribution ? window.UrbAttribution() : {};
      Object.keys(a).forEach(function (k) { p[k] = a[k]; });
      busy(true);
      if (canal === 'whatsapp') {
        var w = window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(waText(p)), '_blank'); if (w) w.opener = null;
        sent = true; say('Abriendo WhatsApp y registrando tu solicitud…');
        var done = false, fin = function () { if (done) return; done = true; if (!w) location.href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent(waText(p)); else location.href = ROOT + 'gracias/?c=whatsapp'; };
        postLead(p).then(fin); setTimeout(fin, photos.length ? 31000 : 3500);
      } else {
        say('Enviando…');
        postLead(p).then(function (okk) {
          if (okk) { sent = true; location.href = ROOT + 'gracias/?c=email'; return; }
          busy(false); say('');
          err('No hemos podido enviarla. Inténtalo de nuevo, usa WhatsApp o llámanos al 722 115 251.');
        });
      }
    });

    if (perfilQS && !holder.dataset.mounted) holder.dataset.perfil = perfilQS;
    holder.dataset.mounted = '1';
    if (pre) go(1, false);
  }
})();
