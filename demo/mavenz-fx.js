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
        var hijos = mapa.get(en.target) || [en.target];
        hijos.forEach(function(el){
          el.style.animationPlayState = en.isIntersecting ? '' : 'paused';
        });
      });
    }, { rootMargin: '200px' });

    /* Se observa un ancestro con caja estable, no el elemento animado.
       El punto del Metodo viaja por un offset-path: su propio rectangulo se
       mueve en cada cuadro, el observador se pierde el reingreso y el punto
       queda pausado para siempre. */
    var mapa = new Map();
    var barrer = function(){
      lista('*').forEach(function(el){
        var cs = getComputedStyle(el);
        if (cs.animationName === 'none') return;
        if (cs.animationIterationCount.indexOf('infinite') === -1) return;
        if (el.closest('.fx-flu__i')) return;   // ese ya arranca pausado
        var ancla = el.closest('section, footer, header') || el;
        if (!mapa.has(ancla)) mapa.set(ancla, []);
        mapa.get(ancla).push(el);
      });
      mapa.forEach(function(_, ancla){ obs.observe(ancla); });
    };
    if (window.requestIdleCallback) requestIdleCallback(barrer, { timeout: 1200 });
    else setTimeout(barrer, 400);
  }


  /* ------------------------------------------------------------------------
     8. MALLA EN MOVIMIENTO
     Cada hilera persigue un objetivo que sale de la posicion del puntero.
     Hileras impares para un lado, pares para el otro. Sin puntero fino, la
     manda el avance del scroll por el bloque.
     ------------------------------------------------------------------------ */
  function malla(){
    lista('[data-fx-malla]').forEach(function(raiz){
      var hileras = lista('.fx-malla__r', raiz);
      if (!hileras.length || quieto.matches) return;

      var amp  = +(raiz.dataset.fxAmp || 190);
      var pos  = hileras.map(function(){ return 0; });
      var meta = hileras.map(function(){ return 0; });
      var vivo = false, corriendo = false;

      function objetivo(p){                       // p va de -1 a 1
        for (var i = 0; i < hileras.length; i++){
          var dir = i % 2 ? -1 : 1;
          var peso = 1 + (i % 3) * 0.34;          // las hileras no van todas igual
          meta[i] = p * amp * dir * peso;
        }
      }

      function paso(){
        if (!vivo){ corriendo = false; return; }
        corriendo = true;
        var quedan = false;
        for (var i = 0; i < hileras.length; i++){
          var d = meta[i] - pos[i];
          if (Math.abs(d) > 0.12){ pos[i] += d * 0.085; quedan = true; }
          else pos[i] = meta[i];
          hileras[i].style.transform = 'translate3d(' + pos[i].toFixed(2) + 'px,0,0)';
        }
        if (quedan) requestAnimationFrame(paso);
        else corriendo = false;
      }
      function arrancar(){ if (!corriendo && vivo) requestAnimationFrame(paso); }

      if (fino.matches){
        addEventListener('pointermove', function(e){
          if (!vivo) return;
          objetivo(limitar((e.clientX / innerWidth - 0.5) * 2, -1, 1));
          arrancar();
        }, { passive: true });
      }
      // en tactil no hay puntero: el avance del scroll por el bloque hace de eje
      addEventListener('scroll', function(){
        if (!vivo || fino.matches) return;
        var r = raiz.getBoundingClientRect();
        var p = 1 - 2 * ((r.top + r.height / 2) / innerHeight);
        objetivo(limitar(p, -1, 1));
        arrancar();
      }, { passive: true });

      if ('IntersectionObserver' in window){
        new IntersectionObserver(function(es){
          vivo = es[0].isIntersecting;
          if (vivo) arrancar();
        }, { rootMargin: '200px' }).observe(raiz);
      } else { vivo = true; }
    });
  }


  /* ------------------------------------------------------------------------
     9. LAS SEIS LECTURAS DEL MAPA
     La bajada promete seis territorios leidos con las mismas cuatro preguntas.
     Hasta ahora el panel estaba clavado en el primero: se clickeaba otro, el
     mapa volaba, y las respuestas seguian siendo las de Micro y Macrocentro.
     Los textos salen de contenido/mapa.json — un dato, un solo lugar.
     El alto se anima entre el valor medido antes y despues (FLIP), nunca
     con height:auto, que no es animable.
     ------------------------------------------------------------------------ */
  function territorios(){
    var panel = doc.getElementById('terr-panel');
    var btns  = lista('.terr');
    if (!panel || !btns.length) return;

    var datos = null, actual = 'micro';

    var PREGUNTAS = [
      ['¿Qué está cambiando?',        'cambia'],
      ['¿Quién lo elige?',            'quien'],
      ['¿Qué oportunidades aparecen?','oportunidades'],
      ['¿Qué ve Mavenz?',             'mavenz']
    ];

    function esc(t){
      return String(t).replace(/[&<>"]/g, function(c){
        return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c];
      });
    }

    function pintar(id){
      var d = datos && datos[id];
      if (!d) return;
      actual = id;

      var alto0 = panel.getBoundingClientRect().height;
      panel.innerHTML = PREGUNTAS.map(function(q){
        return '<div><p style="margin:0;font-size:13px;font-weight:720;color:#b7a28b">' + esc(q[0]) +
               '</p><p style="margin:4px 0 0;font-size:15px;line-height:1.5;color:#ffffff">' + esc(d[q[1]]) + '</p></div>';
      }).join('');

      if (!quieto.matches){
        panel.style.height = 'auto';
        var alto1 = panel.getBoundingClientRect().height;
        panel.style.height = alto0 + 'px';
        void panel.offsetHeight;
        panel.style.height = alto1 + 'px';
        var fin = function(e){
          if (e.propertyName !== 'height') return;
          panel.style.height = '';
          panel.removeEventListener('transitionend', fin);
        };
        panel.addEventListener('transitionend', fin);
      }

      btns.forEach(function(b){
        var on = b.dataset.terr === id;
        b.classList.toggle('terr-on', on);
        b.setAttribute('aria-current', on ? 'true' : 'false');
      });
    }

    btns.forEach(function(b){
      b.addEventListener('click', function(){
        window.dispatchEvent(new CustomEvent('mavenz:flyto', { detail: { id: b.dataset.terr } }));
        pintar(b.dataset.terr);
      });
    });
    // el click sobre el marcador del mapa tambien manda
    window.addEventListener('mavenz:territory', function(e){ pintar(e.detail.id); });

    fetch('contenido/mapa.json')
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(j){
        if (!j) return;
        datos = j;
        btns.forEach(function(b){ b.disabled = false; });
        // el HTML ya trae el primero pintado: no hace falta repintarlo al cargar
      })
      .catch(function(){ /* sin JSON queda el territorio por defecto del HTML */ });
  }


  /* ------------------------------------------------------------------------
     10. PRESUPUESTO DE VIDEO
     Habia cinco videos con autoplay+loop a la vez. autoplay ignora
     preload="none": el navegador los baja igual, y en Salta con datos eso ES
     la pagina. Ahora el src se enchufa recien cuando el video entra en vista,
     y suena uno solo: el que este mas cerca del centro de la pantalla.
     ------------------------------------------------------------------------ */
  function videos(){
    var vs = lista('video[data-src]');
    if (!vs.length) return;

    var ahorro = navigator.connection && navigator.connection.saveData;
    if (ahorro || quieto.matches) return;      // queda el poster, que ya esta puesto

    /* La visibilidad se recalcula de los rectangulos, no de un array que va
       llenando el observador: mantener ese estado sincronizado se desfasa en
       cuanto hay dos scrolls seguidos, y el video queda en pausa a la vista. */
    function elegir(){
      var centro = innerHeight / 2, mejor = null, dMin = Infinity;
      vs.forEach(function(v){
        var r = v.getBoundingClientRect();
        var visible = r.bottom > innerHeight * 0.1 && r.top < innerHeight * 0.9 && r.height > 0;
        if (!visible) return;
        var d = Math.abs(r.top + r.height / 2 - centro);
        if (d < dMin){ dMin = d; mejor = v; }
      });
      vs.forEach(function(v){
        if (v === mejor){
          if (!v.src && v.dataset.src) v.src = v.dataset.src;
          if (v.paused){
            var p = v.play();
            if (p && p.catch) p.catch(function(){});
          }
        } else if (!v.paused) v.pause();
      });
    }

    if (!('IntersectionObserver' in window)){
      vs.forEach(function(v){ if (v.dataset.src) v.src = v.dataset.src; });
      return;
    }

    var obs = new IntersectionObserver(function(){ elegir(); }, { threshold: [0, 0.25, 0.6] });

    vs.forEach(function(v){ obs.observe(v); });
    requestAnimationFrame(elegir);

    var pedido = false;
    addEventListener('scroll', function(){
      if (pedido) return;
      pedido = true;
      requestAnimationFrame(function(){ pedido = false; elegir(); });
    }, { passive: true });
  }


  /* ------------------------------------------------------------------------
     11. EL TRAZO SE DIBUJA CUANDO LO MIRAS
     mvDraw arrancaba al cargar. A cuatro pantallas de scroll el dibujo ya
     estaba terminado: el gesto mas propio de la marca no se veia nunca.
     ------------------------------------------------------------------------ */
  function trazos(){
    var paths = lista('path[style*="mvDraw"]');
    if (!paths.length) return;
    if (quieto.matches || !('IntersectionObserver' in window)) return;

    paths.forEach(function(p){ p.style.animationPlayState = 'paused'; });

    var obs = new IntersectionObserver(function(es){
      es.forEach(function(en){
        if (!en.isIntersecting) return;
        lista('path[style*="mvDraw"]', en.target).forEach(function(p){
          p.style.animationPlayState = 'running';
        });
        obs.unobserve(en.target);
      });
    }, { threshold: 0.2 });

    paths.forEach(function(p){
      var s = p.closest('section, footer');
      if (s) obs.observe(s);
      else p.style.animationPlayState = 'running';
    });
    // red de seguridad: si el observador nunca dispara, el trazo se dibuja igual
    setTimeout(function(){
      paths.forEach(function(p){ p.style.animationPlayState = 'running'; });
    }, 9000);
  }


  /* ------------------------------------------------------------------------
     12. ORBITA
     Muchas fichas, muy juntas, cada una girada en direccion RADIAL: a los
     costados se ven de frente y arriba y abajo de canto. Eso es lo que la
     hace leer como una cinta doblada en anillo y no como una ronda de fotos.
     La profundidad (arriba lejos, abajo cerca) manda escala y opacidad.
     ------------------------------------------------------------------------ */
  function orbita(){
    lista('[data-fx-orbita]').forEach(function(raiz){
      var anillo = raiz.querySelector('.fx-orbita__anillo');
      var escena = raiz.querySelector('.fx-orbita__escena') || raiz;
      if (!anillo) return;

      // el catalogo real: una ficha por imagen, con su nombre
      var base = lista('.fx-orbita__p', anillo);
      var m = base.length;
      if (m < 3) return;

      var datos = base.map(function(f){
        return { src: f.querySelector('img').getAttribute('src'),
                 nombre: f.dataset.nombre || '', pie: f.dataset.pie || '' };
      });

      // el anillo se rellena hasta quedar denso: las fichas se repiten y cada
      // una muestra apenas una astilla, que es justamente el efecto
      var N = +(raiz.dataset.fxN || 76);
      anillo.innerHTML = '';
      var fichas = [];
      for (var i = 0; i < N; i++){
        var d = datos[i % m];
        var f = document.createElement('figure');
        f.className = 'fx-orbita__p';
        f.dataset.k = String(i % m);
        var im = document.createElement('img');
        im.src = d.src; im.alt = ''; im.loading = 'lazy'; im.decoding = 'async';
        f.appendChild(im);
        anillo.appendChild(f);
        fichas.push(f);
      }

      var nombre = raiz.querySelector('.fx-orbita__nombre');
      var pie    = raiz.querySelector('.fx-orbita__pie');
      var fotos  = lista('.fx-orbita__foto img', raiz);

      var ang = 0, empuje = 0, t = 0, vivo = false, corriendo = false;
      var elegido = -1, fijado = -1, fMarcada = null;
      var vel = +(raiz.dataset.fxVel || 4.5);
      var arr = null, R = medir();

      function medir(){
        var r = escena.getBoundingClientRect();
        return { rx: r.width * 0.405, ry: r.height * 0.40 };
      }
      addEventListener('resize', function(){ R = medir(); colocar(); }, { passive: true });

      function mostrar(k){
        if (k === elegido) return;
        elegido = k;
        var d = datos[k];
        if (nombre) nombre.textContent = d.nombre;
        if (pie)    pie.textContent    = d.pie;
        fotos.forEach(function(im, j){ im.classList.toggle('mv-on', j === k); });
        fichas.forEach(function(f){ f.classList.toggle('mv-on', +f.dataset.k === k && f === fMarcada); });
      }
      function colocar(){
        var elegida = null, dMin = 1e9;
        for (var i = 0; i < N; i++){
          var a = (ang + (i / N) * 360) * Math.PI / 180;
          var ca = Math.cos(a), sa = Math.sin(a);
          var x = R.rx * ca;
          var y = R.ry * sa;

          // profundidad: arriba (sa=-1) lejos, abajo (sa=1) cerca
          var prof = (sa + 1) / 2;
          var esc = 0.80 + 0.32 * prof;
          // el giro sigue el radio
          var giro = Math.atan2(y, x) * 180 / Math.PI;
          /* Y el escorzo, que es lo que hace el efecto: la ficha se aplasta
             sobre su propio alto a medida que se pone de canto. A los costados
             (|ca|=1) se ve entera; arriba y abajo (|ca|=0) queda en una astilla.
             Va despues del rotate en la cadena, o sea que se aplica en el eje
             local de la ficha y no en el de la pantalla. */
          var canto = 0.10 + 0.90 * Math.pow(Math.abs(ca), 1.35);

          var f = fichas[i];
          f.style.transform =
            'translate(-50%,-50%) translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)' +
            ' rotate(' + giro.toFixed(2) + 'deg) scale(' + esc.toFixed(3) + ')' +
            ' scaleY(' + canto.toFixed(3) + ')';
          f.style.opacity = (0.2 + 0.8 * prof).toFixed(3);
          f.style.zIndex = String(Math.round(prof * 40));

          // la que manda el centro es la que pasa por el extremo izquierdo,
          // que es donde las fichas se ven mas de frente
          if (ca < 0){
            var dd = Math.abs(sa) + (1 + ca);
            if (dd < dMin){ dMin = dd; elegida = f; }
          }
        }
        if (elegida && fijado < 0){
          fMarcada = elegida;
          mostrar(+elegida.dataset.k);
        }
      }

      function paso(ahora){
        if (!vivo){ corriendo = false; return; }
        corriendo = true;
        var dt = t ? Math.min((ahora - t) / 1000, 0.05) : 0.016;
        t = ahora;
        empuje *= 0.93;
        if (!arr) ang += (vel + empuje * 30) * dt;
        colocar();
        requestAnimationFrame(paso);
      }

      var ultimo = window.scrollY;
      addEventListener('scroll', function(){
        var d = window.scrollY - ultimo;
        ultimo = window.scrollY;
        empuje = limitar(empuje + d / 200, -4, 4);
      }, { passive: true });

      raiz.addEventListener('pointerdown', function(e){
        if (e.button) return;
        arr = { x: e.clientX, a: ang, id: e.pointerId };
        raiz.setPointerCapture(e.pointerId);
      });
      raiz.addEventListener('pointermove', function(e){
        if (!arr || e.pointerId !== arr.id) return;
        ang = arr.a + (e.clientX - arr.x) * 0.4;
        colocar();
      });
      function soltar(){ arr = null; }
      raiz.addEventListener('pointerup', soltar);
      raiz.addEventListener('pointercancel', soltar);

      // pasar por encima de una ficha la trae al centro; al salir, sigue sola
      if (fino.matches){
        anillo.addEventListener('pointerover', function(e){
          var f = e.target.closest('.fx-orbita__p');
          if (!f || arr) return;
          fijado = +f.dataset.k;
          fMarcada = f;
          mostrar(fijado);
        });
        anillo.addEventListener('pointerleave', function(){ fijado = -1; });
      }

      colocar();
      if (quieto.matches) return;

      if ('IntersectionObserver' in window){
        new IntersectionObserver(function(es){
          vivo = es[0].isIntersecting;
          if (vivo && !corriendo){ t = 0; requestAnimationFrame(paso); }
        }, { rootMargin: '160px' }).observe(raiz);
      } else { vivo = true; requestAnimationFrame(paso); }
    });
  }


  /* ------------------------------------------------------------------------
     13. CAMPO DE FLUJO
     Miles de particulas siguiendo un campo vectorial de ruido. Es el fondo del
     hero y es literal: la marca se llama Generamos movimiento.

     Portado de flow-field de KokonutUI, que es MIT limpia y permite copiar el
     codigo. Adaptado a fondo claro (la estela se pinta con blanco en vez de
     negro) y a la paleta de la marca en vez del giro de tono, que es lo que
     hace que estos fondos se lean generados.
     ------------------------------------------------------------------------ */
  function campo(){
    lista('[data-fx-campo]').forEach(function(raiz){
      var lienzo = raiz.querySelector('canvas');
      if (!lienzo) return;
      var ctx = lienzo.getContext('2d', { alpha: false });
      if (!ctx) return;

      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var ancho = 0, alto = 0, t = 0, vivo = false, corriendo = false;
      var particulas = [];

      var FONDO = raiz.dataset.fxFondo || '255,255,255';
      var TINTAS = (raiz.dataset.fxTintas || '183,162,139|113,93,85|156,138,119').split('|')
        .map(function(c){ return c.split(',').map(Number); });
      var ESTELA = +(raiz.dataset.fxEstela || 0.055);

      function cuantas(){
        var a = ancho * alto;
        return limitar(Math.round(a / 1700), 260, 900);   // densidad por area, no fija
      }

      /* El campo: una serie trigonometrica de varias octavas. Devuelve un
         angulo que evoluciona con el tiempo, asi que la corriente nunca se
         repite igual. */
      function angulo(x, y, t){
        var s = 0.0022;
        return Math.sin(x * s + t * 0.0006) * Math.PI +
               Math.cos(y * s + t * 0.00045) * Math.PI +
               Math.sin((x + y) * s * 0.6 + t * 0.0008) * Math.PI * 0.6 +
               Math.cos((x - y) * s * 0.4 + t * 0.00055) * Math.PI * 0.4;
      }

      function nacer(){
        var vida = 180 + Math.floor(Math.random() * 280);
        var c = TINTAS[(Math.random() * TINTAS.length) | 0];
        return {
          x: Math.random() * ancho,
          y: Math.random() * alto,
          v: 0.9 + Math.random() * 1.5,
          r: 0.55 + Math.random() * 0.95,
          c: c,
          t: Math.floor(Math.random() * vida),
          T: vida
        };
      }

      function medir(){
        var r = raiz.getBoundingClientRect();
        ancho = Math.round(r.width);
        alto  = Math.round(r.height);
        if (!ancho || !alto) return;
        lienzo.width  = Math.round(ancho * dpr);
        lienzo.height = Math.round(alto * dpr);
        lienzo.style.width  = ancho + 'px';
        lienzo.style.height = alto + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.fillStyle = 'rgb(' + FONDO + ')';
        ctx.fillRect(0, 0, ancho, alto);
        var n = cuantas();
        particulas = [];
        for (var i = 0; i < n; i++) particulas.push(nacer());
      }

      function cuadro(){
        t++;
        // la estela: cada punto sobrevive unos cuadros y deja el rastro
        ctx.fillStyle = 'rgba(' + FONDO + ',' + ESTELA + ')';
        ctx.fillRect(0, 0, ancho, alto);

        for (var i = 0; i < particulas.length; i++){
          var p = particulas[i];
          var a = angulo(p.x, p.y, t);
          p.x += Math.cos(a) * p.v;
          p.y += Math.sin(a) * p.v;
          p.t++;

          if (p.t > p.T){ particulas[i] = nacer(); continue; }
          if (p.x < 0) p.x += ancho; else if (p.x > ancho) p.x -= ancho;
          if (p.y < 0) p.y += alto;  else if (p.y > alto)  p.y -= alto;

          var k = p.t / p.T;
          var op = Math.min(k * 8, 1) * Math.min((1 - k) * 6, 1) * 0.78;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, 6.2832);
          ctx.fillStyle = 'rgba(' + p.c[0] + ',' + p.c[1] + ',' + p.c[2] + ',' + op.toFixed(3) + ')';
          ctx.fill();
        }
      }

      function paso(){
        if (!vivo){ corriendo = false; return; }
        corriendo = true;
        cuadro();
        requestAnimationFrame(paso);
      }

      medir();
      var reMedir = null;
      addEventListener('resize', function(){
        clearTimeout(reMedir);
        reMedir = setTimeout(medir, 180);
      }, { passive: true });

      if (quieto.matches){
        for (var k = 0; k < 90; k++) cuadro();      // una sola imagen, quieta
        return;
      }

      if ('IntersectionObserver' in window){
        new IntersectionObserver(function(es){
          vivo = es[0].isIntersecting;
          if (vivo && !corriendo) requestAnimationFrame(paso);
        }, { rootMargin: '80px' }).observe(raiz);
      } else { vivo = true; requestAnimationFrame(paso); }
    });
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
    montar('malla',       malla);
    montar('territorios', territorios);
    montar('videos',      videos);
    montar('trazos',      trazos);
    montar('orbita',      orbita);
    montar('campo',       campo);
    montar('pausar',      pausar);
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', arrancar);
  else arrancar();
})();
