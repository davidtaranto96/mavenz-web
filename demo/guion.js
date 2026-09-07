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
      document.body.removeAttribute('data-menu-abierto');
      boton.setAttribute('aria-expanded', 'false');
    };
    var abrir = function () {
      cabecera.setAttribute('data-menu', '');
      panel.setAttribute('data-abierto', '');
      document.body.setAttribute('data-menu-abierto', '');
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
  /* El globo de WhatsApp, por contexto                                      */
  /*                                                                         */
  /* Se esconde donde el visitante ya tiene el WhatsApp delante: el hero y   */
  /* el cierre. En el medio es el único camino a la conversión, y ahí está.  */
  /* ---------------------------------------------------------------------- */

  var globo = document.querySelector('[data-wa]');
  var tapan = document.querySelectorAll('.hero, #contacto');

  if (globo && tapan.length && 'IntersectionObserver' in window) {
    /* Un conjunto y no un contador: en la primera llamada llegan todas las
       secciones juntas, y con un contador la que no se ve le resta a la que
       sí, con lo que el globo nunca se escondía. */
    var tapando = [];
    var ojo = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        var i = tapando.indexOf(en.target);
        if (en.isIntersecting && i < 0) tapando.push(en.target);
        if (!en.isIntersecting && i >= 0) tapando.splice(i, 1);
      });
      if (tapando.length) globo.setAttribute('data-oculto', '');
      else globo.removeAttribute('data-oculto');
    }, { threshold: .05 });
    Array.prototype.forEach.call(tapan, function (s) { ojo.observe(s); });
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
      if (!menosMovimiento) {
        rueda.removeAttribute('data-cambio');
        void rueda.offsetWidth;               /* reinicia la animación */
        rueda.setAttribute('data-cambio', '');
      }
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
  /* El trazo de la marca se dibuja con el scroll                            */
  /* ---------------------------------------------------------------------- */

  var trazo = document.querySelector('.trazo-vivo');
  var heroCaja = document.querySelector('.hero');

  if (trazo && heroCaja && !menosMovimiento) {
    var pendienteTrazo = false;
    var dibujar = function () {
      pendienteTrazo = false;
      var y = window.scrollY;
      if (y <= 4) { trazo.style.removeProperty('--trazo'); return; }
      /* al cargar ya está casi entero (.72): un trazo a medio dibujar en el
         hero se lee cortado, no en progreso. El scroll lo termina. */
      var largo = heroCaja.offsetHeight * .55 || 1;
      var p = .72 + .28 * Math.min(1, y / largo);
      trazo.style.setProperty('--trazo', p.toFixed(3));
    };
    window.addEventListener('scroll', function () {
      if (pendienteTrazo) return;
      pendienteTrazo = true;
      requestAnimationFrame(dibujar);
    }, { passive: true });
  }

  /* ---------------------------------------------------------------------- */
  /* Cada sección entra con su propio gesto                                  */
  /*                                                                         */
  /* La dirección la hereda de la sección, no la elige cada bloque: todo     */
  /* entrando igual desde abajo se lee como plugin y no como diseño.         */
  /* ---------------------------------------------------------------------- */

  var secciones = Array.prototype.slice.call(document.querySelectorAll('[data-fx="reveal"]'));

  if (secciones.length && !menosMovimiento) {
    secciones.forEach(function (sec) {
      Array.prototype.forEach.call(sec.children, function (hijo, i) {
        hijo.setAttribute('data-entra', '');
        hijo.style.animationDelay = (Math.min(i, 5) * 0.07).toFixed(2) + 's';
      });
    });

    var abrir = function (sec) {
      if (sec.hasAttribute('data-visible')) return;
      sec.setAttribute('data-visible', '');
    };

    var ojoSec = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (!en.isIntersecting) return;
        abrir(en.target);
        ojoSec.unobserve(en.target);
      });
    }, { threshold: .12 });
    secciones.forEach(function (sec) { ojoSec.observe(sec); });

    /* Red de seguridad en cuatro capas: una sección que se queda invisible no
       es una animación fea, es contenido perdido. */
    var barrerSec = function () {
      secciones.forEach(function (sec) {
        var r = sec.getBoundingClientRect();
        if (r.top < (window.innerHeight || 0) && r.bottom > -200) abrir(sec);
      });
    };

    requestAnimationFrame(barrerSec);                          /* 1. primer cuadro */
    window.addEventListener('load', barrerSec, { once: true }); /* 2. con todo cargado */

    var pendienteBarrido = false;                              /* 3. al scrollear */
    window.addEventListener('scroll', function () {
      if (pendienteBarrido) return;
      pendienteBarrido = true;
      requestAnimationFrame(function () { pendienteBarrido = false; barrerSec(); });
    }, { passive: true });

    var vueltas = 0;                                           /* 4. cierre duro */
    var reloj = setInterval(function () {
      barrerSec();
      if (++vueltas > 150 || !document.querySelector('[data-fx="reveal"]:not([data-visible])')) {
        clearInterval(reloj);
      }
    }, 400);
  }

  /* ---------------------------------------------------------------------- */
  /* El nav se invierte según el bloque que tiene debajo                     */
  /*                                                                         */
  /* Se sondea qué hay debajo de la barra, no una lista de ids: agregar o    */
  /* reordenar secciones no rompe nada. Con la cortina el rect miente, así   */
  /* que se lee offsetTop.                                                   */
  /* ---------------------------------------------------------------------- */

  var conTema = Array.prototype.slice.call(document.querySelectorAll('[data-tema]'));

  if (cabecera && conTema.length) {
    var temaActual = '';
    var alturaNav = function () { return cabecera.offsetHeight / 2; };
    var mirarTema = function () {
      var y = window.scrollY + alturaNav();
      var tema = 'claro';
      for (var i = 0; i < conTema.length; i++) {
        var el = conTema[i];
        var top = el.offsetTop, alto = el.offsetHeight;
        if (y >= top && y < top + alto) tema = el.dataset.tema;
      }
      if (tema === temaActual) return;
      temaActual = tema;
      if (tema === 'oscuro') cabecera.setAttribute('data-tema', 'oscuro');
      else cabecera.removeAttribute('data-tema');
    };
    var pendienteTema = false;
    window.addEventListener('scroll', function () {
      if (pendienteTema) return;
      pendienteTema = true;
      requestAnimationFrame(function () { pendienteTema = false; mirarTema(); });
    }, { passive: true });
    window.addEventListener('resize', mirarTema);
    mirarTema();
  }

  /* ---------------------------------------------------------------------- */
  /* Índice lateral de rayas                                                 */
  /* ---------------------------------------------------------------------- */

  var indice = document.querySelector('[data-indice]');

  if (indice) {
    var rayas = Array.prototype.slice.call(indice.querySelectorAll('a'));
    var destinos = rayas.map(function (a) {
      return document.querySelector(a.getAttribute('href'));
    });
    var mirarIndice = function () {
      var y = window.scrollY + (window.innerHeight || 0) * .35;
      var activo = 0;
      destinos.forEach(function (el, i) { if (el && y >= el.offsetTop) activo = i; });
      rayas.forEach(function (a, i) {
        if (i === activo) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    };
    var pendienteIndice = false;
    window.addEventListener('scroll', function () {
      if (pendienteIndice) return;
      pendienteIndice = true;
      requestAnimationFrame(function () { pendienteIndice = false; mirarIndice(); });
    }, { passive: true });
    mirarIndice();
  }

  /* ---------------------------------------------------------------------- */
  /* El visor de fotos                                                       */
  /* ---------------------------------------------------------------------- */

  var visor = document.querySelector('[data-visor]');

  if (visor && typeof visor.showModal === 'function') {
    var pista = visor.querySelector('[data-visor-pista]');

    document.addEventListener('click', function (ev) {
      var disparo = ev.target.closest('[data-foto]');
      if (!disparo) return;
      ev.preventDefault();
      visor.showModal();
      var lamina = pista.querySelector('[data-lamina="' + disparo.dataset.foto + '"]');
      if (lamina) pista.scrollTo({ left: lamina.offsetLeft, behavior: 'auto' });
    });

    visor.addEventListener('click', function (ev) {
      /* el clic sobre el fondo del dialog cierra; sobre una lámina, no */
      if (ev.target === visor || ev.target.closest('[data-visor-cerrar]')) visor.close();
    });
  }

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
