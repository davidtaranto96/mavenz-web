/* ==========================================================================
   Mavenz — guion
   Lo único que se mueve es el trazo de la marca y los títulos entrando letra
   por letra. Nada corre en bucle, nada se mueve solo.

   El ocultado del reveal se escribe desde acá y nunca desde el CSS: si este
   archivo no carga, la página se ve entera.
   ========================================================================== */

(function () {
  'use strict';

  var menosMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------------- */
  /* Cabecera: una línea aparece cuando la página se despegó de arriba       */
  /* ---------------------------------------------------------------------- */

  var cabecera = document.querySelector('[data-cabecera]');
  if (cabecera) {
    var pendiente = false;
    var mirar = function () {
      pendiente = false;
      if (window.scrollY > 8) cabecera.setAttribute('data-scroll', '');
      else cabecera.removeAttribute('data-scroll');
    };
    window.addEventListener('scroll', function () {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(mirar);
    }, { passive: true });
    mirar();
  }

  /* ---------------------------------------------------------------------- */
  /* Menú de celular                                                         */
  /* ---------------------------------------------------------------------- */

  var boton = document.querySelector('[data-menu-boton]');
  var panel = document.querySelector('[data-menu-panel]');

  if (boton && panel && cabecera) {
    var cerrar = function () {
      cabecera.removeAttribute('data-menu');
      panel.removeAttribute('data-abierto');
      boton.setAttribute('aria-expanded', 'false');
    };
    var abrir = function () {
      cabecera.setAttribute('data-menu', '');
      panel.setAttribute('data-abierto', '');
      boton.setAttribute('aria-expanded', 'true');
    };

    boton.addEventListener('click', function () {
      if (boton.getAttribute('aria-expanded') === 'true') cerrar();
      else abrir();
    });

    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) cerrar();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && boton.getAttribute('aria-expanded') === 'true') {
        cerrar();
        boton.focus();
      }
    });

    var ancho = window.matchMedia('(min-width: 64rem)');
    var alAncho = function (m) { if (m.matches) cerrar(); };
    if (ancho.addEventListener) ancho.addEventListener('change', alAncho);
    else ancho.addListener(alAncho);
  }

  /* ---------------------------------------------------------------------- */
  /* La rueda del universo                                                   */
  /* ---------------------------------------------------------------------- */

  document.querySelectorAll('[data-rueda]').forEach(function (rueda) {
    var nodos = Array.prototype.slice.call(rueda.querySelectorAll('[data-cap]'));
    var paneles = Array.prototype.slice.call(rueda.querySelectorAll('[data-panel]'));
    if (!nodos.length) return;

    var elegir = function (id) {
      nodos.forEach(function (n) {
        n.setAttribute('aria-pressed', String(n.dataset.cap === id));
      });
      paneles.forEach(function (p) {
        p.setAttribute('aria-hidden', String(p.dataset.panel !== id));
      });
    };

    rueda.addEventListener('click', function (e) {
      var n = e.target.closest('[data-cap]');
      if (n) elegir(n.dataset.cap);
    });

    /* Las flechas recorren las capacidades sin sacar el foco de la rueda. */
    rueda.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      var actual = nodos.indexOf(e.target.closest('[data-cap]'));
      if (actual < 0) return;
      e.preventDefault();
      var paso = e.key === 'ArrowRight' ? 1 : -1;
      var siguiente = nodos[(actual + paso + nodos.length) % nodos.length];
      elegir(siguiente.dataset.cap);
      siguiente.focus();
    });
  });

  /* ---------------------------------------------------------------------- */
  /* Los títulos entran letra por letra                                      */
  /*                                                                         */
  /* Único efecto de scroll que pidió la clienta. Con red de seguridad en    */
  /* tres capas, porque un título que se queda invisible es peor que un      */
  /* título sin animación.                                                   */
  /* ---------------------------------------------------------------------- */

  var titulos = Array.prototype.slice.call(document.querySelectorAll('[data-letras]'));

  titulos.forEach(function (el) {
    if (el.dataset.partido === '1') return;
    var texto = el.textContent;
    el.dataset.partido = '1';
    el.setAttribute('aria-label', texto);          /* el lector lee el texto entero */
    el.textContent = '';

    texto.split(/(\s+)/).forEach(function (trozo) {
      if (/^\s+$/.test(trozo)) { el.appendChild(document.createTextNode(' ')); return; }
      var palabra = document.createElement('span');
      palabra.setAttribute('aria-hidden', 'true');
      palabra.style.display = 'inline-block';
      palabra.style.whiteSpace = 'nowrap';
      Array.prototype.forEach.call(trozo, function (letra) {
        var s = document.createElement('span');
        s.textContent = letra;
        if (!menosMovimiento) s.style.opacity = '0';
        palabra.appendChild(s);
      });
      el.appendChild(palabra);
    });
  });

  if (menosMovimiento) {
    titulos.forEach(function (el) {
      el.querySelectorAll('span span').forEach(function (s) { s.style.opacity = '1'; });
    });
  } else if (titulos.length) {
    var mostrar = function (el) {
      if (el.dataset.visto === '1') return;
      el.dataset.visto = '1';
      el.querySelectorAll('span span').forEach(function (s, i) {
        /* el escalonado se topa: un título largo no puede tardar dos segundos */
        var retraso = Math.min(i, 40) * 0.022;
        s.style.animation = 'mvLetra .5s var(--curva) ' + retraso.toFixed(3) + 's forwards';
      });
    };

    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (!en.isIntersecting) return;
        mostrar(en.target);
        observador.unobserve(en.target);
      });
    }, { threshold: .2 });
    titulos.forEach(function (el) { observador.observe(el); });

    /* Capa 1: lo que ya está en pantalla al cargar se revela en el primer cuadro. */
    var barrer = function () {
      titulos.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom > 0 && r.top < (window.innerHeight || 0)) mostrar(el);
      });
    };
    requestAnimationFrame(barrer);

    /* Capa 2: otra pasada cuando terminó de cargar todo. */
    window.addEventListener('load', barrer, { once: true });

    /* Capa 3: cierre duro. Si a 1,5 s algo sigue oculto y está cerca, se abre. */
    setTimeout(function () {
      titulos.forEach(function (el) {
        if (el.dataset.visto === '1') return;
        var r = el.getBoundingClientRect();
        if (r.bottom > -400 && r.top < (window.innerHeight || 0) + 400) mostrar(el);
      });
    }, 1500);
  }
})();
