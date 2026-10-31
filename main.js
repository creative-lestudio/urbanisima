(function () {
  var WA = '34722115251';
  var header = document.querySelector('.header');
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');

  // Cabecera: transparente sobre el hero, sólida al hacer scroll
  function onScroll() { header.classList.toggle('solid', window.scrollY > 24); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Menú móvil
  function setMenu(open) {
    menu.classList.toggle('open', open);
    header.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  }
  burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  // Filtro de servicios por tipo de cliente
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
      cards.forEach(function (c) {
        c.hidden = f !== 'all' && c.dataset.for.split(' ').indexOf(f) === -1;
      });
    });
  });

  // Preseleccionar servicio al pulsar "Pedir presupuesto" en una tarjeta
  var select = document.getElementById('servicio-select');
  document.querySelectorAll('[data-service]').forEach(function (a) {
    a.addEventListener('click', function () { select.value = a.getAttribute('data-service'); });
  });

  // Formularios -> WhatsApp (no necesita backend)
  function fail(form, msg, field) {
    var m = form.querySelector('.form-msg');
    m.className = 'form-msg';
    m.textContent = msg;
    if (field) { field.classList.add('is-invalid'); field.focus(); }
  }
  function handle(form) {
    form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(form);
      var nombre = (d.get('nombre') || '').trim();
      var tel = (d.get('telefono') || '').trim();
      form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
      if (!nombre) return fail(form, 'Escribe tu nombre.', form.nombre);
      if (tel.replace(/\D/g, '').length < 9) return fail(form, 'Escribe un teléfono válido de 9 cifras.', form.telefono);
      if (form.privacidad && !form.privacidad.checked) return fail(form, 'Acepta la política de privacidad para continuar.');
      var text = 'Hola, soy ' + nombre + '. Mi teléfono es ' + tel + '.' +
        (d.get('servicio') ? ' Necesito: ' + d.get('servicio') + '.' : '') +
        (d.get('mensaje') ? ' ' + d.get('mensaje').trim() : '') +
        ' Quiero un presupuesto gratuito.';
      var m = form.querySelector('.form-msg');
      m.className = 'form-msg ok';
      m.textContent = 'Abriendo WhatsApp con tu mensaje…';
      window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
    });
  }
  document.querySelectorAll('form').forEach(handle);

  // Contadores (el valor final ya está en el HTML; la animación es opcional)
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

  // Entrada suave de elementos al hacer scroll
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var targets = document.querySelectorAll('.head, .svc, .shot, .steps li, .benefits li, .faq details, .contact-copy');
    document.documentElement.classList.add('js');
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); ro.unobserve(en.target); }
      });
    }, { threshold: .1, rootMargin: '0px 0px -30px 0px' });
    targets.forEach(function (el) { el.classList.add('reveal'); ro.observe(el); });
  }
})();
