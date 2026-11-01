/*
 * Medición para Google Ads con Consent Mode v2 y banner de cookies.
 * - Guarda gclid y UTM de la visita para enviarlos con cada solicitud (así sabes qué anuncio la generó).
 * - Solo carga la etiqueta de Google si GOOGLE_TAG_ID está configurado en config.js.
 */
(function () {
  var C = window.URBANISIMA_CONFIG || {};
  var KEY = 'urb_consent', ATTR = 'urb_attr';

  /* ---------- Atribución: gclid y UTM de la primera visita de la sesión ---------- */
  var FIELDS = ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  function read(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function write(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  (function capture() {
    var q = new URLSearchParams(location.search), cur = {}, found = false;
    try { cur = JSON.parse(read(ATTR) || '{}'); } catch (e) {}
    FIELDS.forEach(function (f) { var v = q.get(f); if (v) { cur[f] = v.slice(0, 200); found = true; } });
    if (found) { cur.landing = location.pathname + location.search; write(ATTR, JSON.stringify(cur)); }
  })();
  window.UrbAttribution = function () {
    var a = {}; try { a = JSON.parse(read(ATTR) || '{}'); } catch (e) {}
    if (document.referrer) a.referrer = document.referrer.slice(0, 200);
    return a;
  };

  /* ---------- Google tag + Consent Mode v2 ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  function grant(on) {
    var v = on ? 'granted' : 'denied';
    gtag('consent', 'update', { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
  }
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  if (!C.GOOGLE_TAG_ID) { window.UrbTrack = function () {}; return; }

  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied', wait_for_update: 500 });
  if (stored() === 'granted') grant(true);

  var s = document.createElement('script');
  s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(C.GOOGLE_TAG_ID);
  document.head.appendChild(s);
  gtag('js', new Date());
  gtag('config', C.GOOGLE_TAG_ID);

  /* eventos y conversiones */
  window.UrbTrack = function (name, params) {
    gtag('event', name, params || {});
    var to = C.CONVERSIONS && C.CONVERSIONS[name];
    if (to) gtag('event', 'conversion', { send_to: to });
  };

  /* ---------- Banner de cookies ---------- */
  if (!stored()) {
    var b = document.createElement('div');
    b.className = 'cookie-bar'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-label', 'Cookies');
    b.innerHTML = '<p>Usamos cookies de medición y publicidad de Google para saber qué anuncios funcionan y mejorar el servicio. ' +
      '<a href="' + (location.pathname.indexOf('/gracias') > -1 ? '../' : '') + 'aviso-ley-cookies/">Más información</a></p>' +
      '<div><button type="button" class="ck-no">Rechazar</button><button type="button" class="ck-yes">Aceptar</button></div>';
    document.body.appendChild(b);
    b.querySelector('.ck-yes').addEventListener('click', function () { store('granted'); grant(true); b.remove(); });
    b.querySelector('.ck-no').addEventListener('click', function () { store('denied'); grant(false); b.remove(); });
  }
})();
