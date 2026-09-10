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

  /* La cabecera ya no acompana el scroll (09/09): se va con la pagina y la
     reemplaza el flotante. Su tema lo escribe el generador, no una sonda. */
  var cabecera = document.querySelector('[data-cabecera]');

  /* El menu de celular y el globo de WhatsApp se fueron (09/09): los dos
     viven ahora en el flotante de abajo a la derecha, modulo al final de
     este archivo. */

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

    /* Cuando la entrada termina se le saca el transform al bloque. Sin esto
       queda `translate: 0px` -- que NO es `none` -- y ese bloque pasa a ser el
       bloque contenedor de todo `position: fixed` que tenga adentro. Es lo que
       rompia el clavado del riel horizontal. Va con captura porque
       `animationend` no burbujea desde todos los navegadores por igual. */
    var relojEntrada;
    document.addEventListener('animationend', function (ev) {
      if (ev.animationName !== 'mvEntra') return;
      ev.target.setAttribute('data-entrado', '');
      /* Un solo refresh para toda la tanda: ScrollTrigger recalcula el bloque
         contenedor del pin recien cuando se lo pide, y refrescar por cada
         bloque que entra cuesta un reflow por bloque. */
      if (!window.ScrollTrigger) return;
      clearTimeout(relojEntrada);
      relojEntrada = setTimeout(function () { window.ScrollTrigger.refresh(); }, 220);
    }, true);

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

  var conTema = Array.prototype.slice.call(document.querySelectorAll('main [data-tema], footer[data-tema]'));

  var flotante = document.querySelector('[data-flotante]');

  if (flotante && conTema.length) {
    var temaFlotante = '';
    /* Una sola sonda, a la altura del flotante (abajo): la barra ya no se
       invierte porque no se mueve. */
    var temaEn = function (y) {
      var tema = 'claro';
      for (var i = 0; i < conTema.length; i++) {
        var el = conTema[i];
        var top = el.offsetTop, alto = el.offsetHeight;
        if (y >= top && y < top + alto) tema = el.dataset.tema;
      }
      return tema;
    };
    var mirarTema = function () {
      var t = temaEn(window.scrollY + (window.innerHeight || 0) - 60);
      if (t === temaFlotante) return;
      temaFlotante = t;
      if (t === 'oscuro') flotante.setAttribute('data-tema', 'oscuro');
      else flotante.removeAttribute('data-tema');
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
  /* Videos diferidos                                                        */
  /*                                                                         */
  /* preload="none" no alcanza: con autoplay el navegador se baja el archivo  */
  /* igual. La única forma es no tener src hasta que el video se vea.        */
  /* ---------------------------------------------------------------------- */

  var videos = Array.prototype.slice.call(document.querySelectorAll('[data-diferido]'));

  if (videos.length) {
    var arrancar = function (v) {
      var i = v.play();
      if (i && i.catch) i.catch(function () {});
    };
    /* Un video de fondo pesado no se baja en el teléfono: 3 MB de decorado
       sobre datos móviles no los paga nadie. El póster ya cuenta la escena, y
       la regla es cambiar de técnica, no apagar el bloque. */
    var pesado = window.matchMedia('(max-width: 63.99rem)').matches;
    var encender = function (v) {
      if (menosMovimiento) return;          /* con el póster alcanza */
      if (pesado && v.dataset.pesado === '1') return;
      if (v.dataset.encendido !== '1') {
        v.dataset.encendido = '1';
        v.src = v.dataset.src;
        v.muted = true;                     /* iOS no reproduce sin esto */
      }
      if (v.paused) arrancar(v);
    };

    /* Red de seguridad, igual que con el reveal: si el observador no dispara
       —pestaña en segundo plano, por ejemplo— el video se queda en el póster
       para siempre, y el cardenal es justo lo que hay que ver moverse. */
    var barrerVideos = function () {
      var alto = window.innerHeight || 0;
      videos.forEach(function (v) {
        var r = v.getBoundingClientRect();
        var aLaVista = r.bottom > -300 && r.top < alto + 300;
        if (aLaVista) encender(v);
        else if (v.dataset.encendido === '1') {
          if (!v.paused) v.pause();
          /* El cardenal dura 4 s y lo que importa es el trazo dibujandose. Si
             se retoma donde quedo, la segunda vez se ve un logo ya hecho: deja
             de ser una animacion y pasa a ser una imagen. Vuelve a cero. */
          if (v.hasAttribute('data-reinicia')) { try { v.currentTime = 0; } catch (x) {} }
        }
      });
    };

    if ('IntersectionObserver' in window) {
      var ojoVideo = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (en) {
          if (en.isIntersecting) encender(en.target);
          else if (en.target.dataset.encendido === '1' && !en.target.paused) en.target.pause();
        });
      }, { rootMargin: '300px 0px', threshold: .05 });
      videos.forEach(function (v) { ojoVideo.observe(v); });
    }

    var pendienteVid = false;
    window.addEventListener('scroll', function () {
      if (pendienteVid) return;
      pendienteVid = true;
      requestAnimationFrame(function () { pendienteVid = false; barrerVideos(); });
    }, { passive: true });
    requestAnimationFrame(barrerVideos);
    window.addEventListener('load', barrerVideos, { once: true });
    var vueltasVid = 0;
    var relojVid = setInterval(function () {
      barrerVideos();
      if (++vueltasVid > 150) clearInterval(relojVid);
    }, 400);
  }

  /* ---------------------------------------------------------------------- */
  /* El método en horizontal: la sección se clava y el carril avanza         */
  /*                                                                         */
  /* El carril mueve scrollLeft y no un transform: si el guion no corre,     */
  /* sigue siendo un estante que se desliza con el dedo.                     */
  /* ---------------------------------------------------------------------- */

  var anchoGrande = window.matchMedia('(min-width: 64rem)');

  document.querySelectorAll('[data-lateral]').forEach(function (caja) {
    var carril = caja.querySelector('[data-carril]');
    var pin = caja.querySelector('.lateral__pin');
    if (!carril || !pin) return;

    var sobra = function () { return carril.scrollWidth - carril.clientWidth; };

    var acomodar = function () {
      var corresponde = anchoGrande.matches && !menosMovimiento && sobra() > 4;
      if (!corresponde) {
        caja.removeAttribute('data-pin');
        caja.style.removeProperty('--alto-pin');
        return;
      }
      caja.setAttribute('data-pin', '');
      caja.style.removeProperty('--alto-pin');
      /* el alto de la caja es el del pin más lo que hay que recorrer de costado:
         ni un píxel de más, o la sección se llena de vacío */
      caja.style.setProperty('--alto-pin', (pin.offsetHeight + Math.round(sobra())) + 'px');
    };

    var mover = function () {
      if (!caja.hasAttribute('data-pin')) return;
      var recorrido = caja.offsetHeight - pin.offsetHeight;
      if (recorrido <= 0) return;
      var avance = Math.min(1, Math.max(0, -caja.getBoundingClientRect().top / recorrido));
      carril.scrollLeft = avance * sobra();
    };

    var pendienteLat = false;
    window.addEventListener('scroll', function () {
      if (pendienteLat) return;
      pendienteLat = true;
      requestAnimationFrame(function () { pendienteLat = false; mover(); });
    }, { passive: true });
    window.addEventListener('resize', function () { acomodar(); mover(); });
    acomodar();
    /* las fuentes y las fotos cambian el ancho después del primer layout */
    window.addEventListener('load', function () { acomodar(); mover(); }, { once: true });
    setTimeout(function () { acomodar(); mover(); }, 800);
  });

  /* ---------------------------------------------------------------------- */
  /* La foto de las secciones a sangre se queda quieta                       */
  /*                                                                         */
  /* Recorrido corto y escrito acá, no position:fixed: un fixed adentro de   */
  /* la sección no queda contenido por el overflow y pinta sobre toda la     */
  /* página. Sólo translate, que no provoca reflujo.                         */
  /* ---------------------------------------------------------------------- */

  var fondos = Array.prototype.slice.call(document.querySelectorAll('.sangre__fondo'));

  if (fondos.length && !menosMovimiento && window.matchMedia('(min-width: 64rem)').matches) {
    var correr = function () {
      var alto = window.innerHeight || 1;
      fondos.forEach(function (f) {
        var s = f.parentElement.getBoundingClientRect();
        if (s.bottom < 0 || s.top > alto) return;
        var avance = (alto - s.top) / (alto + s.height);   /* 0 a 1 al cruzar */
        f.style.translate = '0 ' + ((avance - .5) * 9).toFixed(2) + '%';
      });
    };
    var pendienteFondo = false;
    window.addEventListener('scroll', function () {
      if (pendienteFondo) return;
      pendienteFondo = true;
      requestAnimationFrame(function () { pendienteFondo = false; correr(); });
    }, { passive: true });
    correr();
  }

  /* ---------------------------------------------------------------------- */
  /* Palabras que se forman con el scroll                                    */
  /* ---------------------------------------------------------------------- */

  var frases = Array.prototype.slice.call(document.querySelectorAll('[data-formar]'));

  if (frases.length && !menosMovimiento) {
    frases.forEach(function (el) {
      var texto = el.textContent;
      el.setAttribute('aria-label', texto);
      el.textContent = '';
      texto.split(/(\s+)/).forEach(function (trozo) {
        if (/^\s+$/.test(trozo)) { el.appendChild(document.createTextNode(' ')); return; }
        var w = document.createElement('span');
        w.textContent = trozo;
        w.setAttribute('aria-hidden', 'true');
        w.style.opacity = '.14';
        el.appendChild(w);
      });
    });

    var formar = function () {
      frases.forEach(function (el) {
        var r = el.getBoundingClientRect();
        var alto = window.innerHeight || 1;
        /* de 0 a 1 mientras la frase cruza el tercio central de la pantalla */
        var avance = (alto * .78 - r.top) / (alto * .42);
        avance = Math.min(1, Math.max(0, avance));
        var palabras = el.querySelectorAll('span');
        var hasta = avance * palabras.length;
        palabras.forEach(function (w, i) {
          w.style.opacity = i < hasta ? '1' : '.14';
        });
      });
    };

    var pendienteFrase = false;
    window.addEventListener('scroll', function () {
      if (pendienteFrase) return;
      pendienteFrase = true;
      requestAnimationFrame(function () { pendienteFrase = false; formar(); });
    }, { passive: true });
    formar();
    /* seguro: a los 2 s, lo que ya pasó de largo queda entero */
    setTimeout(function () {
      frases.forEach(function (el) {
        if (el.getBoundingClientRect().top < 0)
          el.querySelectorAll('span').forEach(function (w) { w.style.opacity = '1'; });
      });
    }, 2000);
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


/* ==========================================================================
   REDISEÑO 08/09 — órbita, ciclo, cintas, solapas y el riel de mundos.
   Va aparte del motor de reveal de arriba a propósito: un elemento entra en
   UNA sola lista de animación. Dos animaciones de opacidad sobre el mismo
   nodo lo dejan invisible, y eso ya nos pasó.
   ========================================================================== */
(function () {
  'use strict';
  var menos = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* --- Scroll suave con Lenis, enganchado a ScrollTrigger ---------------- */
  /* ?sinlenis en la URL lo apaga: es la única forma cómoda de depurar el pin. */
  var lenis = null;
  function arrancarScroll() {
    var sin = /[?&]sinlenis/.test(location.search);
    if (menos || sin || !window.Lenis || !window.gsap) return;
    lenis = new window.Lenis({ lerp: 0.09, smoothWheel: true });
    /* Expuesto: el flotante lo para con el menu abierto (lenis.stop/start). */
    window.lenis = lenis;
    if (window.ScrollTrigger) {
      window.gsap.registerPlugin(window.ScrollTrigger);
      lenis.on('scroll', window.ScrollTrigger.update);
    }
    window.gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    window.gsap.ticker.lagSmoothing(0);
    $$('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        var el = document.getElementById(a.getAttribute('href').slice(1));
        if (!el) return;
        ev.preventDefault();
        lenis.scrollTo(el, { offset: -16 });   /* sin barra fija: un respiro y nada mas */
      });
    });
  }

  /* --- Las cintas se mueven por scroll, no por keyframe infinito --------- */
  /* Un @keyframes infinite corre para siempre aunque nadie lo mire; esto sólo
     gasta mientras la cinta está en pantalla. */
  function cintas() {
    var lista = $$('[data-cinta]');
    if (!lista.length || menos) return;
    var vivas = [];
    var obs = new IntersectionObserver(function (ent) {
      ent.forEach(function (x) {
        var i = vivas.indexOf(x.target);
        if (x.isIntersecting && i < 0) vivas.push(x.target);
        else if (!x.isIntersecting && i >= 0) vivas.splice(i, 1);
      });
    }, { rootMargin: '200px 0px' });
    lista.forEach(function (c) { obs.observe(c); });

    var pedido = false;
    function pintar() {
      pedido = false;
      vivas.forEach(function (c) {
        var riel = $('[data-cinta-riel]', c);
        if (!riel) return;
        var r = c.getBoundingClientRect();
        var vh = window.innerHeight || 1;
        /* 0 cuando la cinta entra por abajo, 1 cuando termina de salir arriba. */
        var p = (vh - r.top) / (vh + r.height);
        p = p < 0 ? 0 : p > 1 ? 1 : p;
        /* Una sola copia de recorrido: nunca se ve el hueco del final. */
        var copias = parseInt(c.getAttribute('data-copias'), 10) || 4;
        c.style.setProperty('--corrida', (p * riel.scrollWidth / copias).toFixed(1));
      });
    }
    function pedir() { if (!pedido) { pedido = true; requestAnimationFrame(pintar); } }
    window.addEventListener('scroll', pedir, { passive: true });
    window.addEventListener('resize', pedir);
    pedir();
  }

  /* --- Un diagrama circular: la órbita y el ciclo son el mismo mecanismo -- */
  function circular(caja, selNodo, selPanel, attrNodo, attrPanel, selTrazo, varTrazo) {
    if (!caja) return;
    var nodos = $$(selNodo, caja);
    /* Los paneles pueden vivir afuera del diagrama (en el Universo estan al
       costado, en .orbita__detalle): se buscan en la seccion entera. */
    var paneles = $$(selPanel, caja);
    if (!paneles.length) paneles = $$(selPanel, caja.closest('section') || document);
    if (!nodos.length) return;
    caja.setAttribute('data-lista', '1');

    var tocado = false;
    function activar(i) {
      nodos.forEach(function (n, j) { n.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
      paneles.forEach(function (p, j) { p.setAttribute('aria-hidden', j === i ? 'false' : 'true'); });
      /* Quien tenga algo que sincronizar (el carril de celular) escucha esto. */
      caja.dispatchEvent(new CustomEvent('mv:activar', { detail: i }));
      var trazo = selTrazo ? $(selTrazo, caja) : null;
      if (trazo && !menos) {
        /* El avance del trazo cuenta cuánto del ciclo llevás recorrido. */
        caja.style.setProperty(varTrazo, ((i + 1) / nodos.length).toFixed(3));
      }
    }
    nodos.forEach(function (n, i) {
      n.addEventListener('click', function () { tocado = true; activar(i); });
      n.addEventListener('focus', function () { activar(i); });
      /* Con puntero fino, pasar por encima ya elige (UNI-3: "al seleccionar
         o pasar sobre cada una") y congela el auto-avance igual que el clic.
         El toque no entra aca: pointerType es 'touch'. */
      n.addEventListener('pointerenter', function (e) {
        if (e.pointerType !== 'mouse') return;
        tocado = true;
        activar(i);
      });
    });
    activar(0);

    /* Sin puntero, la activa avanza sola con el scroll: el visitante las ve
       todas sin tener que tocar nada. Se detiene apenas toca una. */
    if (menos) return;
    caja.addEventListener('pointerdown', function () { tocado = true; });
    var obs = new IntersectionObserver(function (ent) {
      ent.forEach(function (x) {
        if (!x.isIntersecting || tocado) return;
        /* La posición dentro de la sección elige la esfera. */
        var r = caja.getBoundingClientRect();
        var vh = window.innerHeight || 1;
        var p = (vh * 0.8 - r.top) / (r.height + vh * 0.3);
        p = p < 0 ? 0 : p > 0.999 ? 0.999 : p;
        activar(Math.floor(p * nodos.length));
      });
    }, { threshold: [0, .2, .4, .6, .8, 1] });
    obs.observe(caja);

    var pedido = false;
    window.addEventListener('scroll', function () {
      if (tocado || pedido) return;
      pedido = true;
      requestAnimationFrame(function () {
        pedido = false;
        var r = caja.getBoundingClientRect();
        var vh = window.innerHeight || 1;
        if (r.bottom < 0 || r.top > vh) return;
        var p = (vh * 0.8 - r.top) / (r.height + vh * 0.3);
        p = p < 0 ? 0 : p > 0.999 ? 0.999 : p;
        activar(Math.floor(p * nodos.length));
      });
    }, { passive: true });
  }

  /* --- El anillo de Comunicación se dibuja antes que entren las esferas --- */
  function anillo() {
    var c = $('[data-anillo]');
    if (!c || menos) return;
    var orb = c.closest('[data-orbita]');
    if (!orb) return;
    orb.style.setProperty('--dibujo', '0');
    var obs = new IntersectionObserver(function (ent) {
      ent.forEach(function (x) {
        if (!x.isIntersecting) return;
        obs.disconnect();
        var t0 = null;
        (function paso(t) {
          if (t0 === null) t0 = t;
          var p = Math.min((t - t0) / 900, 1);
          orb.style.setProperty('--dibujo', (1 - Math.pow(1 - p, 3)).toFixed(3));
          if (p < 1) requestAnimationFrame(paso);
        })(performance.now());
      });
    }, { threshold: .3 });
    obs.observe(orb);
  }

  /* --- Las solapas de la ventana de contacto ----------------------------- */
  /* --- La cinta continua: infinita, pero solo mientras se la ve ------------ */
  /* El observer mira la CINTA (quieta), nunca el riel que se mueve: un riel
     en movimiento entra y sale del umbral solo y apaga lo que tiene que
     prender. La duracion sale del largo real para que la velocidad sea
     constante en px/s aunque cambie el cuerpo tipografico. */
  function cintasContinuas() {
    var lista = $$('[data-cinta-continua]');
    if (!lista.length) return;
    var medir = function (c) {
      var riel = $('[data-cinta-riel]', c);
      if (!riel) return;
      var vertical = c.classList.contains('cinta--vertical');
      var largo = (vertical ? riel.scrollHeight : riel.scrollWidth) / 2;
      var vel = parseFloat(c.getAttribute('data-velocidad')) || 120;
      c.style.setProperty('--cinta-dur', (largo / vel).toFixed(2) + 's');
    };
    lista.forEach(medir);
    window.addEventListener('resize', function () { lista.forEach(medir); });
    if (menos || !('IntersectionObserver' in window)) return;

    /* El foco de la cinta del hero: cada pieza se desenfoca segun su distancia
       al centro (hasta 3 px, cuantizado a medio pixel para no re-rasterizar
       cada cuadro) y se afina en el medio. Solo con puntero fino: en tactil un
       blur animado re-rasteriza y se lo paga en fps. */
    var conFoco = lista.filter(function (c) { return c.classList.contains('cinta--hero'); });
    if (conFoco.length && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      var enfocar = function () {
        conFoco.forEach(function (c) {
          if (!c.hasAttribute('data-vivo')) return;
          var vw = window.innerWidth || 1;
          $$('.cinta__pieza', c).forEach(function (p) {
            var r = p.getBoundingClientRect();
            var d = Math.abs((r.left + r.width / 2) / vw - .5) * 2;    /* 0 centro .. 1 borde */
            var b = Math.round(Math.max(0, d - .35) / .65 * 6) / 2;   /* 0 .. 3 px, de a .5 */
            p.style.setProperty('--foco', b + 'px');
          });
        });
        requestAnimationFrame(enfocar);
      };
      requestAnimationFrame(enfocar);
    }
    var obs = new IntersectionObserver(function (ent) {
      ent.forEach(function (x) {
        if (x.isIntersecting) x.target.setAttribute('data-vivo', '');
        else x.target.removeAttribute('data-vivo');
      });
    }, { rootMargin: '80px 0px' });
    lista.forEach(function (c) { obs.observe(c); });
  }

  /* --- Contacto: cuatro opciones, un formulario, tres tiempos ------------- */
  /* Al elegir una opcion cambia la linea de arriba y el motivo oculto. El
     cambio es el medido en la referencia: fade-out del bloque (170 ms) ->
     panel vacio (150 ms) -> filas entrando de arriba hacia abajo. El envio
     va a Web3Forms si hay clave; si no, arma el mensaje y abre WhatsApp, asi
     el sitio nunca queda con un boton que no hace nada. */
  function formulario() {
    var panel = $('[data-panel-contacto]');
    if (!panel) return;
    var solapas = $$('[data-solapa]', panel);
    var copia = $('[data-copia-motivo]', panel);
    var form = $('[data-formulario]', panel);
    if (!form || !solapas.length) return;
    var motivo = $('input[name="motivo"]', form);
    var estado = $('.formulario__estado', form);
    var enviar = $('.formulario__enviar', form);
    var cambiando = false;

    var aplicar = function (b) {
      solapas.forEach(function (o) {
        var es = o === b;
        o.setAttribute('aria-selected', es ? 'true' : 'false');
        o.setAttribute('tabindex', es ? '0' : '-1');
      });
      if (copia) copia.textContent = b.getAttribute('data-copia') || '';
      if (motivo) motivo.value = b.querySelector('.solapa__texto').textContent;
      form.setAttribute('data-wa', b.getAttribute('data-wa') || '');
    };

    var elegir = function (b, animar) {
      if (b.getAttribute('aria-selected') === 'true' || cambiando) return;
      if (!animar || menos) { aplicar(b); return; }
      cambiando = true;
      panel.setAttribute('data-saliendo', '');
      setTimeout(function () {
        aplicar(b);
        panel.removeAttribute('data-saliendo');
        panel.setAttribute('data-entrando', '');
        void panel.offsetWidth;                 /* que el estado "entrando" se pinte */
        setTimeout(function () {
          panel.removeAttribute('data-entrando');
          cambiando = false;
        }, 150);
      }, 170);
    };

    solapas.forEach(function (b, i) {
      b.addEventListener('click', function () { elegir(b, true); });
      b.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var sig = solapas[(i + d + solapas.length) % solapas.length];
        sig.focus();
        elegir(sig, true);
      });
    });

    /* ?motivo=oportunidad preselecciona: lo usan los paneles de proyectos. */
    var q = /[?&]motivo=([a-z]+)/.exec(window.location.search);
    var inicial = q && solapas.filter(function (b) { return b.getAttribute('data-solapa') === q[1]; })[0];
    aplicar(inicial || solapas[0]);

    /* Validacion propia: `novalidate` para que el aviso sea el nuestro y vaya
       al lector de pantalla por aria-live. */
    var validar = function () {
      var ok = true;
      $$('[required]', form).forEach(function (campo) {
        var fila = campo.closest('.campo');
        var viejo = fila && fila.querySelector('.campo__error');
        if (viejo) viejo.remove();
        var falta = !campo.value.trim();
        var mal = campo.type === 'email' && campo.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(campo.value);
        campo.setAttribute('aria-invalid', (falta || mal) ? 'true' : 'false');
        if (falta || mal) {
          ok = false;
          var p = document.createElement('p');
          p.className = 'campo__error';
          p.textContent = falta ? form.getAttribute('data-falta') : form.getAttribute('data-correo-invalido');
          fila.appendChild(p);
        }
      });
      return ok;
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validar()) { var primero = $('[aria-invalid="true"]', form); if (primero) primero.focus(); return; }
      var datos = {};
      $$('input, textarea', form).forEach(function (c) { if (c.name && c.type !== 'checkbox') datos[c.name] = c.value.trim(); });
      var clave = form.getAttribute('data-clave');
      if (!clave) {
        /* Sin servicio configurado: el mensaje viaja por WhatsApp, armado. */
        var texto = datos.motivo + '. ' + datos.nombre + (datos.telefono ? ' (' + datos.telefono + ')' : '') +
                    ' — ' + datos.email + '. ' + datos.mensaje;
        var base = form.getAttribute('data-wa') || form.getAttribute('data-wa-base');
        window.open(base.split('?')[0] + '?text=' + encodeURIComponent(texto), '_blank', 'noopener');
        return;
      }
      if ($('[name="botcheck"]', form).checked) return;   /* un bot lo marco */
      enviar.disabled = true;
      var rotulo = enviar.textContent;
      enviar.textContent = form.getAttribute('data-enviando');
      estado.textContent = '';
      var cuerpo = { access_key: clave, subject: form.getAttribute('data-asunto') + ' — ' + datos.motivo,
                     from_name: datos.nombre, motivo: datos.motivo, name: datos.nombre, email: datos.email,
                     telefono: datos.telefono, message: datos.mensaje };
      fetch(form.getAttribute('action'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(cuerpo)
      }).then(function (r) { return r.json(); }).then(function (r) {
        if (!r.success) throw new Error(r.message || 'sin exito');
        $$('.formulario__fila', form).forEach(function (f) { f.hidden = true; });
        estado.textContent = form.getAttribute('data-gracias');
      }).catch(function () {
        estado.textContent = form.getAttribute('data-error');
        enviar.disabled = false;
        enviar.textContent = rotulo;
      });
    });
  }

  /* --- El estante recorre en horizontal con la pantalla fijada ----------- */
  /* Sólo escritorio y sólo si GSAP llegó. Si no, el CSS deja el estante como
     carril nativo y se sigue pudiendo recorrer con el dedo o la rueda. */
  function fijarEstante() {
    var caja = $('[data-fijado]');
    if (!caja || menos || !window.gsap || !window.ScrollTrigger) return;
    if (!window.matchMedia('(min-width: 64rem)').matches) return;
    var riel = $('.estante', caja);
    if (!riel) return;
    var recorrido = function () { return Math.max(0, riel.scrollWidth - window.innerWidth * 0.86); };
    if (recorrido() <= 0) return;
    window.gsap.to(riel, {
      x: function () { return -recorrido(); },
      ease: 'none',
      scrollTrigger: {
        trigger: caja,
        start: 'center center',
        /* El recorrido horizontal no tiene por que costar un pixel de scroll
           por pixel de riel: a 1:1 el mundo de Cardinal se comia 4,3 pantallas
           contra 1,2 de los otros tres. A 0,75 el riel recorre lo mismo y pide
           un cuarto menos de rueda. */
        end: function () { return '+=' + Math.round(recorrido() * 0.75); },
        pin: true,
        scrub: 0.8,
        anticipatePin: 1,
        invalidateOnRefresh: true
      }
    });
  }

  /* --- 2. La nube de la red: entra escalonada y después deriva ----------- */
  /* El estado oculto lo escribe ACÁ, nunca el CSS: si el JS no corre, la nube
     se ve entera. El precio es un parpadeo posible y es el canje correcto. */
  function nubeRed() {
    var nube = $('.red__nube');
    if (!nube) return;
    if (menos) { nube.setAttribute('data-vivo', '1'); return; }
    nube.setAttribute('data-vivo', '0');

    var abierto = false;
    var abrir = function () {
      if (abierto) return;
      abierto = true;
      nube.setAttribute('data-vivo', '1');
    };
    /* Umbral bajo a propósito: la nube mide 276 px y en un notebook de 657 de
       alto nunca llega a 0,18 apenas entra. Medido acá: daba 0,105. */
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (ent) {
        ent.forEach(function (x) { if (x.isIntersecting) { abrir(); obs.disconnect(); } });
      }, { threshold: .05 });
      obs.observe(nube);
    }
    /* Barrido por scroll: el umbral es más permisivo que el del observer a
       propósito, y sólo abre lo que de verdad está a la vista. Nada de un
       temporizador ciego que la abra sin que nadie la haya visto. */
    var barrer = function () {
      if (abierto) return;
      var r = nube.getBoundingClientRect();
      var vh = window.innerHeight || 0;
      if (r.top < vh * 0.95 && r.bottom > 0) abrir();
    };
    requestAnimationFrame(barrer);
    window.addEventListener('load', barrer, { once: true });
    window.addEventListener('scroll', barrer, { passive: true });
    /* Cierre duro: si el visitante ya la dejó atrás, se muestra de una. */
    var vueltas = 0;
    var reloj = setInterval(function () {
      if (abierto || ++vueltas > 150) { clearInterval(reloj); return; }
      if (nube.getBoundingClientRect().bottom < 0) abrir();
    }, 400);

    var pedido = false;
    function derivar() {
      pedido = false;
      var r = nube.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      if (r.bottom < -100 || r.top > vh + 100) return;
      var t = (vh - r.top) / (vh + r.height);
      nube.style.setProperty('--deriva', ((t - .5) * 2).toFixed(3));
    }
    window.addEventListener('scroll', function () {
      if (!pedido) { pedido = true; requestAnimationFrame(derivar); }
    }, { passive: true });
    derivar();
  }

  /* --- El puente: el bistre sube con el scroll ---------------------------- */
  /* Escribe --mezcla (0..1) en el puente: 0 cuando asoma por abajo de la
     pantalla, 1 cuando su base llega al quinto superior. Solo transform: la
     capa de bistre se estira desde abajo (scale: 1 var(--mezcla)). */
  function puente() {
    var p = $('[data-puente]');
    if (!p || menos) return;
    var pedido = false;
    var medir = function () {
      pedido = false;
      var r = p.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      if (r.bottom < -vh || r.top > vh * 2) return;
      var t = (vh - r.top) / (vh * .8 + r.height);
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      p.style.setProperty('--mezcla', t.toFixed(3));
    };
    window.addEventListener('scroll', function () {
      if (pedido) return;
      pedido = true;
      requestAnimationFrame(medir);
    }, { passive: true });
    window.addEventListener('resize', medir);
    medir();
  }

  /* --- El carril de esferas en celular ------------------------------------ */
  /* Bajo 64rem las descripciones son un carril con scroll-snap: una tarjeta
     por vez, swipe o flechas. Se mantiene en sincronia con las esferas en
     los dos sentidos: elegir una esfera lleva el carril a su tarjeta, y
     deslizar el carril enciende la esfera que corresponde. Cuando el carril
     no scrollea (escritorio) no hace nada. */
  function carrilEsferas() {
    var caja = $('[data-orbita]');
    var carril = $('[data-carril-esferas]');
    if (!caja || !carril) return;
    var raiz = carril.closest('.universo') || document;
    var nodos = $$('.orbita__nodo', caja);
    var paneles = $$('.orbita__panel', carril);
    var ant = $('[data-carril-ant]', raiz);
    var sig = $('[data-carril-sig]', raiz);
    if (!nodos.length || !paneles.length) return;
    var actual = 0;
    var programado = false;

    var esCarril = function () { return carril.scrollWidth > carril.clientWidth + 4; };
    var izquierda = function () { return parseFloat(getComputedStyle(carril).paddingLeft) || 0; };
    var irA = function (i) {
      if (!esCarril()) return;
      var p = paneles[i];
      if (!p) return;
      programado = true;
      carril.scrollTo({ left: p.offsetLeft - izquierda(), behavior: menos ? 'auto' : 'smooth' });
      /* Mientras el carril viaja solo, sus eventos de scroll no cuentan. */
      clearTimeout(irA.t);
      irA.t = setTimeout(function () { programado = false; }, menos ? 50 : 600);
    };

    caja.addEventListener('mv:activar', function (e) {
      actual = e.detail;
      irA(actual);
    });

    var reloj = null;
    carril.addEventListener('scroll', function () {
      if (programado || !esCarril()) return;
      clearTimeout(reloj);
      reloj = setTimeout(function () {
        var x = carril.scrollLeft + izquierda();
        var mejor = 0, dist = Infinity;
        paneles.forEach(function (p, i) {
          var d = Math.abs(p.offsetLeft - x);
          if (d < dist) { dist = d; mejor = i; }
        });
        if (mejor !== actual) nodos[mejor].click();
      }, 80);
    }, { passive: true });

    var saltar = function (paso) {
      var n = nodos.length;
      nodos[(actual + paso + n) % n].click();
    };
    if (ant) ant.addEventListener('click', function () { saltar(-1); });
    if (sig) sig.addEventListener('click', function () { saltar(1); });
  }

  function arrancar() {
    arrancarScroll();
    nubeRed();
    fijarEstante();
    cintas();
    circular($('[data-orbita]'), '.orbita__nodo', '.orbita__panel',
             'data-esfera', 'data-panel', null, null);
    circular($('[data-ciclo]'), '.ciclo__nodo', '.ciclo__carta',
             'data-paso', 'data-carta', '[data-avance]', '--avance');
    anillo();
    puente();
    carrilEsferas();
    cintasContinuas();
    formulario();
  }

  /* Los scripts van con defer, así que el DOM ya está: pero si esto llegara a
     correr antes, se espera. Barato y evita un fallo silencioso. */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar, { once: true });
  } else {
    arrancar();
  }
})();

/* ==========================================================================
   Flotante — guion
   Abre y cierra el menú de la esquina, lo hace aparecer en escritorio cuando
   la cabecera salió de la pantalla y lo esconde sobre #contacto. Reemplaza
   al bloque "Menú de celular" y al del globo de WhatsApp de guion.js.

   Lo que escribe:
     body[data-lejos]          la cabecera salió de la pantalla
     body[data-menu-abierto]   el sitio ya le pone overflow: hidden
     .flotante[data-abierto]   el panel está abierto
     .flotante[data-oculto]    hay que esconderlo (sobre #contacto)
   Lo que NO escribe: data-tema. Eso lo hace mirarTema, en guion.js, igual
   que con la cabecera y el índice.

   Sin librerías. Para probar desde la consola: window.__flotante.abrir() y
   window.__flotante.cerrar().
   ========================================================================== */

(function () {
  'use strict';

  /* Cuándo mandar el foco al primer enlace: cuando ya entró. El primero
     arranca a los .28s y tarda .15s (flotante.css); antes de eso el aro de
     foco aparecería sobre una palabra a medio llegar. */
  var ESPERA_FOCO = 430;

  function flotante() {
    var raiz = document.querySelector('[data-flotante]');
    if (!raiz) return;
    var boton = raiz.querySelector('[data-menu-boton]');
    var panel = raiz.querySelector('[data-menu-panel]');
    if (!boton || !panel) return;

    var menos = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var cuerpo = document.body;
    var temporizador = null;

    /* Lenis mueve el scroll a mano, así que el overflow: hidden del body no
       lo frena: hay que pararlo. Se le pide por su nombre y si no está (sin
       librería, ?sinlenis, menos movimiento) no pasa nada. */
    var lenis = function (orden) {
      var l = window.lenis;
      if (l && typeof l[orden] === 'function') l[orden]();
    };

    var abierto = function () {
      return boton.getAttribute('aria-expanded') === 'true';
    };

    var abrir = function () {
      if (abierto()) return;
      boton.setAttribute('aria-expanded', 'true');
      raiz.setAttribute('data-abierto', '');
      cuerpo.setAttribute('data-menu-abierto', '');
      lenis('stop');
      clearTimeout(temporizador);
      temporizador = setTimeout(function () {
        var primero = panel.querySelector('a[href]');
        /* preventScroll: el panel es fijo, no hay nada que scrollear, y sin
           esto algún navegador intenta igual y mueve el fondo. */
        if (primero && abierto()) primero.focus({ preventScroll: true });
      }, menos ? 0 : ESPERA_FOCO);
    };

    /* devolverFoco: al cerrar por teclado o por clic afuera el foco vuelve
       al botón. Por clic en un enlace no: la página se va a otro lado. */
    var cerrar = function (devolverFoco) {
      if (!abierto()) return;
      clearTimeout(temporizador);
      boton.setAttribute('aria-expanded', 'false');
      raiz.removeAttribute('data-abierto');
      cuerpo.removeAttribute('data-menu-abierto');
      lenis('start');
      if (devolverFoco) boton.focus({ preventScroll: true });
    };

    boton.addEventListener('click', function () {
      if (abierto()) cerrar(true);
      else abrir();
    });

    /* Clic en un enlace del panel: cierra. En CAPTURA, antes de que el enlace
       haga lo suyo: guion.js intercepta los href="#ancla" y los manda a
       lenis.scrollTo, y Lenis parado ignora el scrollTo. Primero se lo
       arranca (acá), después el enlace scrollea (allá). */
    panel.addEventListener('click', function (e) {
      if (e.target.closest('a[href]')) cerrar(false);
    }, true);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && abierto()) cerrar(true);
    });

    /* Clic fuera del flotante: cierra. Lo de adentro (botón, píldora, panel)
       no cuenta; el botón ya tiene su propio manejador. */
    document.addEventListener('click', function (e) {
      if (abierto() && !raiz.contains(e.target)) cerrar(true);
    });

    /* ------------------------------------------------------------------ */
    /* Escritorio: aparece cuando la cabecera salió de la pantalla         */
    /* ------------------------------------------------------------------ */

    var cabecera = document.querySelector('[data-cabecera]');
    if (cabecera && 'IntersectionObserver' in window) {
      var blanco = cabecera;
      /* Si la cabecera es sticky o fixed nunca "sale" de la pantalla y el
         observer diría siempre que está. En ese caso se mira una sonda de su
         misma altura clavada arriba del todo del documento, que sí se va. */
      var pos = getComputedStyle(cabecera).position;
      if (pos === 'sticky' || pos === 'fixed') {
        blanco = document.createElement('span');
        blanco.setAttribute('aria-hidden', 'true');
        blanco.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:' +
          cabecera.offsetHeight + 'px;pointer-events:none;visibility:hidden';
        cuerpo.insertBefore(blanco, cuerpo.firstChild);
      }
      new IntersectionObserver(function (entradas) {
        var en = entradas[entradas.length - 1];
        if (en.isIntersecting) cuerpo.removeAttribute('data-lejos');
        else cuerpo.setAttribute('data-lejos', '');
      }, { threshold: 0 }).observe(blanco);
    } else {
      /* Sin observer, mejor que esté siempre a que no esté nunca. */
      cuerpo.setAttribute('data-lejos', '');
    }

    /* ------------------------------------------------------------------ */
    /* Sobre #contacto se esconde: ahí el WhatsApp ya está delante        */
    /* ------------------------------------------------------------------ */

    var contacto = document.getElementById('contacto');
    if (contacto && 'IntersectionObserver' in window) {
      /* Dos medidas y no una: "se ve el 30% de la sección" falla cuando la
         sección es más alta que la pantalla (celular acostado: nunca llega al
         30%), así que también vale "la sección ocupa el 30% de la pantalla".
         Los umbrales de a diez para que el callback dispare a lo largo del
         recorrido y no sólo al entrar y salir. */
      new IntersectionObserver(function (entradas) {
        var en = entradas[entradas.length - 1];
        var altoPantalla = (en.rootBounds && en.rootBounds.height) || window.innerHeight || 1;
        var tapa = en.isIntersecting &&
          (en.intersectionRatio >= .3 || en.intersectionRect.height / altoPantalla >= .3);
        if (tapa) raiz.setAttribute('data-oculto', '');
        else raiz.removeAttribute('data-oculto');
      }, { threshold: [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1] }).observe(contacto);
    }

    window.__flotante = { abrir: abrir, cerrar: cerrar };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', flotante);
  else flotante();
})();
