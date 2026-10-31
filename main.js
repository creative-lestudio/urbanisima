(function () {
  var WA = '34722115251';

  // Menú móvil
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  function closeMenu() { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
  burger.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(open));
  });
  menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') closeMenu(); });

  // Preseleccionar servicio al pulsar "Pedir presupuesto" en una tarjeta
  var select = document.getElementById('servicio-select');
  document.querySelectorAll('[data-service]').forEach(function (a) {
    a.addEventListener('click', function () { select.value = a.getAttribute('data-service'); });
  });

  // Formularios -> WhatsApp (sin necesidad de backend)
  function handle(form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = form.querySelector('.form-msg');
      var d = new FormData(form);
      var nombre = (d.get('nombre') || '').trim();
      var tel = (d.get('telefono') || '').trim();
      msg.className = 'form-msg';
      if (!nombre || tel.replace(/\D/g, '').length < 9) {
        msg.textContent = 'Indica tu nombre y un teléfono válido.';
        return;
      }
      if (form.privacidad && !form.privacidad.checked) {
        msg.textContent = 'Debes aceptar la política de privacidad.';
        return;
      }
      var text = 'Hola, soy ' + nombre + '. Teléfono: ' + tel + '.' +
        (d.get('servicio') ? ' Necesito: ' + d.get('servicio') + '.' : '') +
        (d.get('mensaje') ? ' ' + d.get('mensaje').trim() : '') +
        ' Quiero un presupuesto gratuito.';
      msg.textContent = 'Abriendo WhatsApp…';
      msg.className = 'form-msg ok';
      window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
    });
  }
  document.querySelectorAll('form').forEach(handle);

  // Contadores
  var els = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
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
})();
