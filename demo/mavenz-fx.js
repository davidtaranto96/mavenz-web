/* ==========================================================================
   mavenz-fx — motor de efectos de la plataforma Mavenz
   Vanilla puro: cero dependencias, cero build, cero framework.
   Escrito de cero para este proyecto.

   Cada modulo se monta dentro de su propio try: si uno falla, los demas
   siguen andando y la pagina nunca queda rota ni en blanco.
   ========================================================================== */
(function(){
  'use strict';

  var doc = document;
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)');
  var fino   = window.matchMedia('(hover: hover) and (pointer: fine)');
  var lista  = function(s, r){ return Array.prototype.slice.call((r||doc).querySelectorAll(s)); };
  var limitar = function(v, a, b){ return v < a ? a : (v > b ? b : v); };

  function montar(nombre, fn){
    try { fn(); } catch (e) { if (window.console) console.warn('[mavenz-fx] ' + nombre, e); }
  }

  /* ------------------------------------------------------------------------
     1. BOTON ESPECULAR
     La luz del canto sigue al puntero. Un solo listener para toda la pagina,
     con las medidas cacheadas y el trabajo real dentro de un rAF.
     ------------------------------------------------------------------------ */
  function especular(){
    var els = lista('.fx-esp');
    if (!els.length || !fino.matches) return;

    var RADIO = 300, x = 0, y = 0, pedido = false, cajas = [];

    function medir(){
      cajas = els.map(function(el){ return { el: el, r: el.getBoundingClientRect() }; });
    }

    function pintar(){
      pedido = false;
      for (var i = 0; i < cajas.length; i++){
        var c = cajas[i], r = c.r;
        var dx = x - (r.left + r.width / 2);
        var dy = y - (r.top + r.height / 2);
        var d = Math.hypot(dx, dy);
        if (d > RADIO){
          if (c.el.classList.contains('fx-cerca')){
            c.el.classList.remove('fx-cerca');
            c.el.style.removeProperty('--fx-ang');
            c.el.style.removeProperty('--fx-int');
          }
          continue;
        }
        // angulo horario desde arriba, que es como mide conic-gradient
        var ang = Math.atan2(dx, -dy) * 180 / Math.PI + 90;
        c.el.classList.add('fx-cerca');
        c.el.style.setProperty('--fx-ang', ang.toFixed(1) + 'deg');
        c.el.style.setProperty('--fx-int', (0.34 + 0.66 * (1 - d / RADIO)).toFixed(3));
      }
    }

    medir();
    addEventListener('pointermove', function(e){
      x = e.clientX; y = e.clientY;
      if (!pedido){ pedido = true; requestAnimationFrame(pintar); }
    }, { passive: true });
    addEventListener('scroll', medir, { passive: true });
    addEventListener('resize', medir, { passive: true });
  }

  /* ------------------------------------------------------------------------
     2. CARRUSEL EN PROFUNDIDAD
     Las fichas retroceden en Z en vez de correrse de costado. Arrastre,
     rueda horizontal, flechas, puntos y teclado. La posicion se persigue
     con un amortiguado critico: se puede agarrar a mitad de camino.
     ------------------------------------------------------------------------ */
  function profundidad(){
    lista('[data-fx-prof]').forEach(function(raiz){
      var esc = raiz.querySelector('.fx-prof__esc');
      if (!esc) return;
      var fichas = lista('.fx-prof__t', esc);
      var n = fichas.length;
      if (n < 2) return;

      var cfg = {
        z:      +(raiz.dataset.fxZ || 250),
        ancho:  +(raiz.dataset.fxSpread || 132),
        giro:   +(raiz.dataset.fxTilt || 17),
        visibles: +(raiz.dataset.fxVis || 3)
      };

      var pos = 0, meta = 0, animando = false, activa = -1;
      var puntos = raiz.querySelector('.fx-prof__p');

      function dist(i, p){
        var d = i - p;
        d = ((d % n) + n) % n;
        if (d > n / 2) d -= n;
        return d;
      }

      function colocar(p){
        for (var i = 0; i < n; i++){
          var d = dist(i, p), a = Math.abs(d);
          var visible = a <= cfg.visibles + 0.5;
          var f = fichas[i];
          f.style.transform =
            'translate(-50%,-50%)' +
            ' translateX(' + (d * cfg.ancho).toFixed(1) + 'px)' +
            ' translateZ(' + (-a * cfg.z).toFixed(1) + 'px)' +
            ' rotateY(' + (-d * cfg.giro).toFixed(2) + 'deg)';
          f.style.opacity  = visible ? limitar(1 - a / (cfg.visibles + 1), 0, 1).toFixed(3) : '0';
          f.style.filter   = a > 0.05 ? 'blur(' + Math.min(a * 2.4, 7).toFixed(2) + 'px)' : 'none';
          f.style.zIndex   = String(50 - Math.round(a * 10));
          f.style.visibility = visible ? 'visible' : 'hidden';
          f.setAttribute('aria-hidden', a < 0.5 ? 'false' : 'true');
        }
        var act = ((Math.round(p) % n) + n) % n;
        if (act !== activa){
          activa = act;
          if (puntos) lista('button', puntos).forEach(function(b, k){
            b.setAttribute('aria-current', k === act ? 'true' : 'false');
          });
        }
      }

      function correr(){
        animando = true;
        var d = meta - pos;
        if (Math.abs(d) < 0.0012){
          pos = meta; colocar(pos); animando = false; return;
        }
        pos += d * 0.16;
        colocar(pos);
        requestAnimationFrame(correr);
      }

      function ir(p){
        meta = p;
        if (quieto.matches){ pos = meta; colocar(pos); return; }
        if (!animando) requestAnimationFrame(correr);
      }
      function mover(k){ ir(meta + k); }

      // flechas
      var ant = raiz.querySelector('.fx-prof__f--ant');
      var sig = raiz.querySelector('.fx-prof__f--sig');
      if (ant) ant.addEventListener('click', function(){ mover(-1); });
      if (sig) sig.addEventListener('click', function(){ mover(1); });

      // puntos
      if (puntos) lista('button', puntos).forEach(function(b, k){
        b.addEventListener('click', function(){
          ir(meta + dist(k, meta));   // el salto mas corto hasta k
        });
      });

      // teclado
      raiz.setAttribute('tabindex', '0');
      raiz.setAttribute('role', 'group');
      raiz.addEventListener('keydown', function(e){
        if (e.key === 'ArrowLeft'){ e.preventDefault(); mover(-1); }
        if (e.key === 'ArrowRight'){ e.preventDefault(); mover(1); }
      });

      // arrastre
      var arr = null;
      esc.addEventListener('pointerdown', function(e){
        if (e.button) return;
        arr = { x: e.clientX, p: meta, id: e.pointerId, movido: false };
        esc.setPointerCapture(e.pointerId);
      });
      esc.addEventListener('pointermove', function(e){
        if (!arr || e.pointerId !== arr.id) return;
        var dx = e.clientX - arr.x;
        if (Math.abs(dx) > 4) arr.movido = true;
        pos = meta = arr.p - dx / (cfg.ancho * 1.65);
        colocar(pos);
      });
      function soltar(e){
        if (!arr || (e && e.pointerId !== arr.id)) return;
        var caida = arr.movido;
        arr = null;
        if (caida) ir(Math.round(meta));
      }
      esc.addEventListener('pointerup', soltar);
      esc.addEventListener('pointercancel', soltar);

      // rueda horizontal — nunca secuestra el scroll vertical
      esc.addEventListener('wheel', function(e){
        if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
        e.preventDefault();
        ir(meta + limitar(e.deltaX / 120, -1, 1));
      }, { passive: false });

      // click en una ficha lateral la trae al frente
      fichas.forEach(function(f, i){
        f.addEventListener('click', function(){
          var d = dist(i, meta);
          if (Math.abs(d) > 0.4) ir(meta + d);
        });
      });

      colocar(0);
    });
  }

  /* ------------------------------------------------------------------------
     3. MENU FLUIDO
     El panel entra por el canto por donde entro el puntero y se va por el
     canto por donde salio. Es lo que hace que se lea como una direccion y
     no como un fundido.
     ------------------------------------------------------------------------ */
  function fluido(){
    lista('.fx-flu__i').forEach(function(it){
      var m = it.querySelector('.fx-flu__m');
      var w = it.querySelector('.fx-flu__mw');
      if (!m || !w) return;

      function canto(e){
        var r = it.getBoundingClientRect();
        return (e.clientY - r.top) < r.height / 2 ? -101 : 101;
      }
      var cinta = it.querySelector('.fx-flu__in');
      function correr(on){ if (cinta) cinta.style.animationPlayState = on ? 'running' : 'paused'; }

      function poner(s, sin){
        if (sin){ m.style.transition = 'none'; w.style.transition = 'none'; }
        m.style.transform = 'translate3d(0,' + s + '%,0)';
        w.style.transform = 'translate3d(0,' + (-s) + '%,0)';
        if (sin){ void m.offsetWidth; m.style.transition = ''; w.style.transition = ''; }
      }

      it.addEventListener('pointerenter', function(e){
        if (!fino.matches) return;
        poner(canto(e), true); correr(true);
        requestAnimationFrame(function(){ poner(0); });
      });
      it.addEventListener('pointerleave', function(e){
        if (!fino.matches) return;
        poner(canto(e));
        setTimeout(function(){ correr(false); }, 700);
      });
      it.addEventListener('focus', function(){ correr(true); poner(101, true); requestAnimationFrame(function(){ poner(0); }); });
      it.addEventListener('blur',  function(){ poner(101); setTimeout(function(){ correr(false); }, 700); });
    });
  }

  /* ------------------------------------------------------------------------
     4. CINTA CON VELOCIDAD
     Corre sola; el scroll la empuja. Pausada mientras no se la ve, para no
     gastar bateria con una animacion infinita fuera de pantalla.
     ------------------------------------------------------------------------ */
  function cinta(){
    lista('.fx-cinta').forEach(function(raiz){
      var pista = raiz.querySelector('.fx-cinta__p');
      if (!pista || quieto.matches) return;
      var grupo = pista.firstElementChild;
      if (!grupo) return;

      var base = +(raiz.dataset.fxVel || 42);        // px por segundo
      var dir  = raiz.dataset.fxDir === 'der' ? -1 : 1;
      var x = 0, ancho = 0, empuje = 0, t = 0, vivo = false, corriendo = false;

      function medir(){ ancho = grupo.getBoundingClientRect().width; }

      function paso(ahora){
        if (!vivo){ corriendo = false; return; }
        corriendo = true;
        var dt = t ? Math.min((ahora - t) / 1000, 0.05) : 0.016;
        t = ahora;
        empuje *= 0.92;
        x -= (base * (1 + Math.abs(empuje)) * dir) * dt;
        if (ancho){
          if (x <= -ancho) x += ancho;
          if (x > 0) x -= ancho;
        }
        pista.style.transform = 'translate3d(' + x.toFixed(2) + 'px,0,0)';
        requestAnimationFrame(paso);
      }

      var ultimo = window.scrollY;
      addEventListener('scroll', function(){
        var d = window.scrollY - ultimo;
        ultimo = window.scrollY;
        empuje = limitar(empuje + d / 260, -3.2, 3.2);
      }, { passive: true });

      medir();
      addEventListener('resize', medir, { passive: true });

      if ('IntersectionObserver' in window){
        new IntersectionObserver(function(es){
          vivo = es[0].isIntersecting;
          if (vivo && !corriendo){ t = 0; requestAnimationFrame(paso); }
        }, { rootMargin: '120px' }).observe(raiz);
      } else {
        vivo = true; requestAnimationFrame(paso);
      }
    });
  }

  /* ------------------------------------------------------------------------
     5. CORTINA
     El revelado mejora, nunca hace visible. Red de seguridad a los 2,5s:
     lo que siga tapado se destapa igual.
     ------------------------------------------------------------------------ */
  function cortina(){
    var els = lista('.fx-cortina');
    if (!els.length) return;
    function abrir(el){ el.classList.add('fx-visto'); }
    if (quieto.matches || !('IntersectionObserver' in window)){
      els.forEach(abrir); return;
    }
    var obs = new IntersectionObserver(function(es){
      es.forEach(function(en){
        if (en.isIntersecting){ abrir(en.target); obs.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function(el){ obs.observe(el); });
    setTimeout(function(){ els.forEach(abrir); }, 2500);
  }

  /* ------------------------------------------------------------------------
     6. IMAN
     ------------------------------------------------------------------------ */
  function iman(){
    var els = lista('.fx-iman');
    if (!els.length || !fino.matches || quieto.matches) return;
    var RADIO = 110, FUERZA = 0.3;
    addEventListener('pointermove', function(e){
      els.forEach(function(el){
        var r = el.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2);
        var dy = e.clientY - (r.top + r.height / 2);
        var d = Math.hypot(dx, dy);
        if (d < RADIO + Math.max(r.width, r.height) / 2){
          el.style.transform = 'translate(' + (dx * FUERZA).toFixed(1) + 'px,' + (dy * FUERZA).toFixed(1) + 'px)';
        } else if (el.style.transform){
          el.style.transform = '';
        }
      });
    }, { passive: true });
  }


  /* ------------------------------------------------------------------------
     7. PAUSAR LO QUE NO SE VE
     Una animacion infinita fuera de pantalla gasta bateria sin decir nada.
     Buscamos todo lo que tenga iteracion infinita — propio y heredado — y lo
     dormimos cuando sale del viewport.
     ------------------------------------------------------------------------ */
  function pausar(){
    if (!('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function(es){
      es.forEach(function(en){
        en.target.style.animationPlayState = en.isIntersecting ? '' : 'paused';
      });
    }, { rootMargin: '160px' });

    var barrer = function(){
      lista('*').forEach(function(el){
        var cs = getComputedStyle(el);
        if (cs.animationName === 'none') return;
        if (cs.animationIterationCount.indexOf('infinite') === -1) return;
        if (el.closest('.fx-flu__i')) return;   // ese ya arranca pausado
        obs.observe(el);
      });
    };
    if (window.requestIdleCallback) requestIdleCallback(barrer, { timeout: 1200 });
    else setTimeout(barrer, 400);
  }

  /* ------------------------------------------------------------------------
     arranque
     ------------------------------------------------------------------------ */
  function arrancar(){
    montar('especular',   especular);
    montar('profundidad', profundidad);
    montar('fluido',      fluido);
    montar('cinta',       cinta);
    montar('cortina',     cortina);
    montar('iman',        iman);
    montar('pausar',      pausar);
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', arrancar);
  else arrancar();
})();
