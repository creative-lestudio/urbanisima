/*
 * Cookies, consentimiento y medición de Google Ads.
 *
 * Diseñado según la LSSI-CE (art. 22.2), el RGPD y la Guía sobre el uso de las cookies de la AEPD:
 *  - Antes de que el usuario decida NO se carga ningún script de Google ni se guarda nada para publicidad.
 *  - "Aceptar todo" y "Rechazar todo" tienen el mismo aspecto y el mismo número de clics.
 *  - Panel "Configurar" con categorías desactivadas por defecto.
 *  - La decisión se puede cambiar en cualquier momento (enlace "Configurar cookies" del pie).
 *  - La decisión se recuerda como máximo 24 meses.
 *  - Si no hay GOOGLE_TAG_ID en config.js, la web no usa cookies de terceros y no muestra el banner.
 */
(function () {
  var C = window.URBANISIMA_CONFIG || {};
  var KEY = 'urb_consent', ATTR = 'urb_attr', VERSION = 2, MONTHS = 24;
  var FIELDS = ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  var inPage = location.pathname.replace(/\/[^\/]*$/, '/').split('/').filter(Boolean);

  function lsGet() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function lsSet(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  function ssDel(k) { try { sessionStorage.removeItem(k); } catch (e) {} }

  /* ---------- Decisión guardada (válida 24 meses) ---------- */
  function readConsent() {
    try {
      var c = JSON.parse(lsGet() || 'null');
      if (!c || c.v !== VERSION || !c.t) return null;
      var max = new Date(c.t); max.setMonth(max.getMonth() + MONTHS);
      return new Date() > max ? null : c;
    } catch (e) { return null; }
  }
  function saveConsent(a, p) { var c = { v: VERSION, a: !!a, p: !!p, t: new Date().toISOString() }; lsSet(JSON.stringify(c)); return c; }

  /* ---------- Origen del anuncio (gclid / UTM) ----------
     Se lee de la URL en memoria. Solo se guarda en el navegador (y solo se envía con el formulario)
     si el usuario ha aceptado la publicidad. */
  var mem = {};
  (function capture() {
    var q = new URLSearchParams(location.search);
    FIELDS.forEach(function (f) { var v = q.get(f); if (v) mem[f] = v.slice(0, 200); });
    if (Object.keys(mem).length) mem.landing = (location.pathname + location.search).slice(0, 250);
  })();
  function adsAllowed() { var c = readConsent(); return !!(c && c.p); }
  function persistAttribution() {
    if (!adsAllowed()) return;
    var cur = {}; try { cur = JSON.parse(ssGet(ATTR) || '{}'); } catch (e) {}
    Object.keys(mem).forEach(function (k) { cur[k] = mem[k]; });
    if (Object.keys(cur).length) ssSet(ATTR, JSON.stringify(cur));
  }
  window.UrbAttribution = function () {
    if (!adsAllowed()) return {};
    var a = {}; try { a = JSON.parse(ssGet(ATTR) || '{}'); } catch (e) {}
    Object.keys(mem).forEach(function (k) { a[k] = mem[k]; });
    if (document.referrer) a.referrer = document.referrer.slice(0, 200);
    return a;
  };

  /* ---------- Sin etiqueta de Google configurada: no hay cookies de terceros ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  if (!C.GOOGLE_TAG_ID) { window.UrbTrack = function () {}; return; }

  /* ---------- Carga de Google solo tras el consentimiento ---------- */
  var loaded = false;
  function applyToGoogle(c) {
    var ads = c.p ? 'granted' : 'denied', an = c.a ? 'granted' : 'denied';
    gtag('consent', 'update', { ad_storage: ads, ad_user_data: ads, ad_personalization: ads, analytics_storage: an });
  }
  function loadGoogle(c) {
    if (loaded || !(c.a || c.p)) return;
    loaded = true; window.gtag = gtag;
    gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' });
    applyToGoogle(c);
    var s = document.createElement('script');
    s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(C.GOOGLE_TAG_ID);
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', C.GOOGLE_TAG_ID);
  }
  function eraseGoogleCookies() {
    var host = location.hostname.split('.'), doms = ['', location.hostname, '.' + location.hostname];
    if (host.length > 2) doms.push('.' + host.slice(-2).join('.'));
    document.cookie.split(';').forEach(function (kv) {
      var n = kv.split('=')[0].trim();
      if (/^(_gcl_|_ga|_gid|_gac_|IDE$|test_cookie$)/.test(n)) doms.forEach(function (d) {
        document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
      });
    });
    ssDel(ATTR);
  }
  function decide(a, p) {
    var prev = readConsent(), c = saveConsent(a, p);
    if (c.p) persistAttribution(); else ssDel(ATTR);
    if (loaded) {
      applyToGoogle(c);
      if (prev && ((prev.a && !c.a) || (prev.p && !c.p))) { eraseGoogleCookies(); location.reload(); return; }
    } else loadGoogle(c);
    closeUi();
  }

  window.UrbTrack = function (name, params) {
    var c = readConsent(); if (!c || !loaded || !(c.a || c.p)) return;
    gtag('event', name, params || {});
    var to = C.CONVERSIONS && C.CONVERSIONS[name];
    if (to && c.p) gtag('event', 'conversion', { send_to: to });
  };

  /* ---------- Interfaz: banner + panel de configuración ---------- */
  var ui = null;
  function base() { return inPage.length && /^(gracias|aviso-legal|ley-proteccion-datos|aviso-ley-cookies|condiciones)$/.test(inPage[inPage.length - 1]) ? '../' : ''; }
  function closeUi() { if (ui) { ui.remove(); ui = null; } }
  function openUi(panel) {
    closeUi();
    var cur = readConsent() || { a: false, p: false };
    ui = document.createElement('div');
    ui.className = 'cookie-bar' + (panel ? ' is-panel' : ''); ui.setAttribute('role', 'dialog'); ui.setAttribute('aria-modal', 'false'); ui.setAttribute('aria-label', 'Preferencias de cookies');
    var more = '<a href="' + base() + 'aviso-ley-cookies/">Política de cookies</a>';
    if (!panel) {
      ui.innerHTML =
        '<div class="ck-text"><strong>Tu privacidad importa</strong><p>Usamos cookies propias y de Google para medir y mejorar nuestra publicidad, solo si las aceptas. ' +
        'Puedes aceptarlas, rechazarlas o elegir cuáles. ' + more + '.</p></div>' +
        '<div class="ck-actions"><button type="button" class="ck-btn" data-a="reject">Rechazar todo</button>' +
        '<button type="button" class="ck-btn" data-a="accept">Aceptar todo</button>' +
        '<button type="button" class="ck-link" data-a="config">Configurar</button></div>';
    } else {
      ui.innerHTML =
        '<div class="ck-text"><strong>Configurar cookies</strong>' +
        '<label class="ck-row"><span><b>Necesarias</b><small>Guardan tu decisión sobre las cookies. No se pueden desactivar.</small></span><input type="checkbox" checked disabled></label>' +
        '<label class="ck-row"><span><b>Medición</b><small>Estadísticas de uso de la web (Google).</small></span><input type="checkbox" id="ck-a"' + (cur.a ? ' checked' : '') + '></label>' +
        '<label class="ck-row"><span><b>Publicidad</b><small>Saber qué anuncios de Google Ads traen solicitudes y mostrar publicidad relevante. Incluye el identificador del clic del anuncio.</small></span><input type="checkbox" id="ck-p"' + (cur.p ? ' checked' : '') + '></label>' +
        '<p class="ck-more">' + more + '.</p></div>' +
        '<div class="ck-actions"><button type="button" class="ck-btn" data-a="reject">Rechazar todo</button>' +
        '<button type="button" class="ck-btn" data-a="save">Guardar selección</button>' +
        '<button type="button" class="ck-btn" data-a="accept">Aceptar todo</button></div>';
    }
    ui.addEventListener('click', function (e) {
      var a = e.target.getAttribute && e.target.getAttribute('data-a'); if (!a) return;
      if (a === 'accept') decide(true, true);
      else if (a === 'reject') decide(false, false);
      else if (a === 'config') openUi(true);
      else if (a === 'save') decide(ui.querySelector('#ck-a').checked, ui.querySelector('#ck-p').checked);
    });
    document.body.appendChild(ui);
    var first = ui.querySelector('button'); if (first && panel) first.focus();
  }

  /* ---------- Inicio ---------- */
  var cur = readConsent();
  function init() {
    document.querySelectorAll('[data-cookie-settings]').forEach(function (b) {
      b.hidden = false; b.addEventListener('click', function (e) { e.preventDefault(); openUi(true); });
    });
    if (cur) { loadGoogle(cur); persistAttribution(); } else openUi(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
