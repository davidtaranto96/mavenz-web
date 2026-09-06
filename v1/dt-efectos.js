/* ═══════════════════════════════════════════════════════════════════════
   dt-efectos.js — motor de los efectos declarados con data-fx
   Sin dependencias. Va en <head> SIN defer: la primera linea marca el html
   como "fx-on" antes de que pinte, y asi no hay salto de contenido visible.
   Todo el resto del trabajo espera a DOMContentLoaded.
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var raiz = document.documentElement;
  raiz.classList.add('fx-on');

  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)');
  var punteroFino = window.matchMedia('(hover: hover) and (pointer: fine)');
  var sinIO = !('IntersectionObserver' in window);

  /* Si el navegador no tiene IntersectionObserver, mostramos todo y listo. */
  if (sinIO) { raiz.classList.remove('fx-on'); }

  var $ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var num = function (el, attr, def) { var v = parseFloat(el.getAttribute(attr)); return isNaN(v) ? def : v; };

  /* Un solo rAF compartido para todo lo que depende del scroll. */
  var tareasScroll = [];
  var pendiente = false;
  function alScroll() {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(function () {
      pendiente = false;
      for (var i = 0; i < tareasScroll.length; i++) tareasScroll[i]();
    });
  }
  function enScroll(fn) {
    tareasScroll.push(fn);
    if (tareasScroll.length === 1) {
      window.addEventListener('scroll', alScroll, { passive: true });
      window.addEventListener('resize', alScroll, { passive: true });
    }
    fn();
  }

  function arrancar() {

    /* ── 1. REVEAL + SPLIT ────────────────────────────────────────────
       Un unico observer para los dos: ambos se disparan al entrar en pantalla.
       Por defecto se animan una sola vez (no se re-ocultan al subir).      */
    if (!sinIO) {
      var obs = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('fx-visto');
          obs.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });

      /* stagger: cada hijo directo entra con un retardo creciente */
      $('[data-fx-stagger]').forEach(function (grupo) {
        var paso = num(grupo, 'data-fx-stagger', 0) ||
                   parseFloat(getComputedStyle(grupo).getPropertyValue('--fx-stagger')) || 70;
        Array.prototype.forEach.call(grupo.children, function (hijo, i) {
          if (!hijo.hasAttribute('data-fx')) hijo.setAttribute('data-fx', 'reveal');
          hijo.style.setProperty('--fx-delay', (i * paso) + 'ms');
        });
      });

      /* split: envolver palabra por palabra, respetando el markup inline */
      $('[data-fx~="split"]').forEach(function (el) {
        if (el.dataset.fxPartido) return;
        var paso = num(el, 'data-fx-paso', 45);
        var n = 0;
        (function partir(nodo) {
          Array.prototype.slice.call(nodo.childNodes).forEach(function (hijo) {
            if (hijo.nodeType === 3) {
              var frag = document.createDocumentFragment();
              hijo.nodeValue.split(/(\s+)/).forEach(function (trozo) {
                if (!trozo) return;
                if (/^\s+$/.test(trozo)) { frag.appendChild(document.createTextNode(trozo)); return; }
                var s = document.createElement('span');
                s.className = 'fx-palabra';
                s.textContent = trozo;
                s.style.setProperty('--fx-i-delay', (n++ * paso) + 'ms');
                frag.appendChild(s);
              });
              nodo.replaceChild(frag, hijo);
            } else if (hijo.nodeType === 1 && !hijo.classList.contains('fx-palabra')) {
              partir(hijo);
            }
          });
        })(el);
        el.dataset.fxPartido = '1';
      });

      var pendientes = [];
      $('[data-fx~="reveal"], [data-fx~="split"], [data-fx~="contador"]').forEach(function (el) {
        obs.observe(el);
        pendientes.push(el);
      });

      /* Red de seguridad. Con un scroll rapido, un ancla (#seccion) o la tecla
         Fin, un elemento puede pasar de estar debajo de la pantalla a estar
         encima sin cruzar ningun umbral: el observer no se entera y ese bloque
         queda invisible para siempre. Si quedo por encima, lo mostramos.
         Como esta fuera de vista, la transicion no se ve: aparece ya puesto. */
      if (pendientes.length) {
        enScroll(function () {
          for (var i = pendientes.length - 1; i >= 0; i--) {
            var el = pendientes[i];
            if (el.classList.contains('fx-visto')) { pendientes.splice(i, 1); continue; }
            if (el.getBoundingClientRect().bottom < 0) {
              el.classList.add('fx-visto');
              obs.unobserve(el);
              pendientes.splice(i, 1);
            }
          }
        });
      }
    }

    /* ── 2. CONTADOR ──────────────────────────────────────────────────
       Ojo: una fila de numeros animados en el hero es la firma tipica de
       pagina hecha con IA. Usalo solo con numeros reales y fuera del hero. */
    $('[data-fx~="contador"]').forEach(function (el) {
      var destino = num(el, 'data-fx-hasta', parseFloat(el.textContent) || 0);
      var dec = (el.getAttribute('data-fx-decimales') | 0);
      var dur = num(el, 'data-fx-dur', 1400);
      var fmt = new Intl.NumberFormat('es-AR', { minimumFractionDigits: dec, maximumFractionDigits: dec });
      el.textContent = fmt.format(0);
      if (quieto.matches) { el.textContent = fmt.format(destino); return; }
      var lanzado = false;
      var mirar = function () {
        if (lanzado || !el.classList.contains('fx-visto')) return;
        lanzado = true;
        var t0 = performance.now();
        (function paso(t) {
          var p = Math.min((t - t0) / dur, 1);
          var e = 1 - Math.pow(1 - p, 3);           /* ease-out cubica */
          el.textContent = fmt.format(destino * e);
          if (p < 1) requestAnimationFrame(paso);
        })(t0);
      };
      new MutationObserver(mirar).observe(el, { attributes: true, attributeFilter: ['class'] });
      mirar();
    });

    /* ── 3. TILT ──────────────────────────────────────────────────────
       Solo con puntero fino y sin reduced-motion. En tactil no se engancha. */
    if (punteroFino.matches && !quieto.matches) {
      $('[data-fx~="tilt"]').forEach(function (el) {
        var max = num(el, 'data-fx-grados', 7);
        el.addEventListener('pointermove', function (ev) {
          var r = el.getBoundingClientRect();
          var px = (ev.clientX - r.left) / r.width - 0.5;
          var py = (ev.clientY - r.top) / r.height - 0.5;
          el.style.setProperty('--fx-ry', (px * max * 2).toFixed(2) + 'deg');
          el.style.setProperty('--fx-rx', (-py * max * 2).toFixed(2) + 'deg');
          el.classList.add('fx-activo');
        });
        el.addEventListener('pointerleave', function () {
          el.classList.remove('fx-activo');
          el.style.removeProperty('--fx-rx');
          el.style.removeProperty('--fx-ry');
        });
      });

      /* ── 4. SPOTLIGHT ── el halo sigue al cursor dentro de la tarjeta */
      $('[data-fx~="spotlight"]').forEach(function (el) {
        el.addEventListener('pointermove', function (ev) {
          var r = el.getBoundingClientRect();
          el.style.setProperty('--fx-x', (ev.clientX - r.left) + 'px');
          el.style.setProperty('--fx-y', (ev.clientY - r.top) + 'px');
        });
      });
    }

    /* ── 5. MARQUEE ───────────────────────────────────────────────────
       Envuelve los hijos en una pista y la duplica para que el loop cierre. */
    $('[data-fx~="marquee"]').forEach(function (el) {
      if (el.querySelector('.fx-pista')) return;
      var pista = document.createElement('div');
      pista.className = 'fx-pista';
      while (el.firstChild) pista.appendChild(el.firstChild);
      el.appendChild(pista);
      var copia = pista.cloneNode(true);
      copia.setAttribute('aria-hidden', 'true');
      el.appendChild(copia);
    });

    /* ── 6. BARRA DE PROGRESO ─────────────────────────────────────────── */
    var barras = $('[data-fx~="progreso"]');
    if (barras.length) {
      enScroll(function () {
        var alto = document.documentElement.scrollHeight - window.innerHeight;
        var p = alto > 0 ? window.scrollY / alto : 0;
        barras.forEach(function (b) { b.style.setProperty('--fx-progreso', Math.min(p, 1).toFixed(4)); });
      });
    }

    /* ── 7. NAV ───────────────────────────────────────────────────────
       .fx-scrolleado apenas se despega del tope.
       .fx-oculto solo si pediste data-fx-esconder: se va al bajar, vuelve al subir. */
    var navs = $('[data-fx~="nav"]');
    if (navs.length) {
      var ultimo = window.scrollY;
      enScroll(function () {
        var y = window.scrollY;
        navs.forEach(function (nav) {
          nav.classList.toggle('fx-scrolleado', y > num(nav, 'data-fx-desde-y', 24));
          if (nav.hasAttribute('data-fx-esconder')) {
            var bajando = y > ultimo && y > 220;
            nav.classList.toggle('fx-oculto', bajando);
          }
        });
        ultimo = y;
      });
    }

    /* ── 8. PARALLAX ──────────────────────────────────────────────────── */
    var paras = $('[data-fx~="parallax"]');
    if (paras.length && !quieto.matches) {
      enScroll(function () {
        var vh = window.innerHeight;
        if (!vh) return;            /* alto 0: rotando la pantalla o iframe oculto */
        paras.forEach(function (el) {
          var r = el.getBoundingClientRect();
          if (r.bottom < -200 || r.top > vh + 200) return;
          var centro = (r.top + r.height / 2 - vh / 2) / vh;   /* -1 .. 1 */
          var rec = num(el, 'data-fx-recorrido', 40);
          el.style.setProperty('--fx-par', (-centro * rec).toFixed(1) + 'px');
        });
      });
    }

    /* ── 9. CHISPA AL CLICK ───────────────────────────────────────────── */
    if (!quieto.matches) {
      $('[data-fx~="chispa"]').forEach(function (el) {
        el.addEventListener('pointerdown', function (ev) {
          var r = el.getBoundingClientRect();
          var d = Math.max(r.width, r.height) * 2;
          var onda = document.createElement('span');
          onda.className = 'fx-onda';
          onda.style.cssText = 'width:' + d + 'px;height:' + d + 'px;left:' +
            (ev.clientX - r.left) + 'px;top:' + (ev.clientY - r.top) + 'px';
          el.appendChild(onda);
          onda.addEventListener('animationend', function () { onda.remove(); });
        });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar);
  } else {
    arrancar();
  }
})();
