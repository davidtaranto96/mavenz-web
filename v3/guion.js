/* ==========================================================================
   Mavenz v3 — guion único. Sin dependencias.

   Reglas que gobiernan este archivo, todas aprendidas a los golpes:
   · El estado oculto del reveal lo escribe el JS (html.fx-on), nunca el CSS
     solo. Si el JS no arranca, la página se ve entera.
   · Nada se mueve en bucle. El agua se abre una vez y queda quieta.
   · El rescate del reveal se dispara por geometría, jamás por reloj, y sólo
     sobre lo que ya pasó de largo: si rescata lo visible, le roba el
     escalonado al observer.
   ========================================================================== */
(function(){
'use strict';

var raiz   = document.documentElement;
var quieto = matchMedia('(prefers-reduced-motion: reduce)');
var hayIO  = 'IntersectionObserver' in window;
var grande = function(){ return matchMedia('(min-width:64rem) and (min-height:30rem)').matches };

function topAbsoluto(el){
  var y = 0;
  while (el){ y += el.offsetTop; el = el.offsetParent }
  return y;
}

/* ── 0. Títulos partidos en letras ───────────────────────────────────────
   Se parte por palabra y adentro por letra: una letra suelta como
   inline-block rompería la palabra en dos renglones. El texto entero queda
   en aria-label para el lector de pantalla. El índice se topea en 40 para
   que un título largo no tarde dos segundos. */

[].forEach.call(document.querySelectorAll('[data-fx~="letras"]'), function(el){
  var txt = el.textContent.replace(/\s+/g, ' ').trim();
  el.setAttribute('aria-label', txt);
  el.textContent = '';
  var i = 0;
  txt.split(' ').forEach(function(palabra, k, todas){
    var w = document.createElement('span');
    w.className = 'palabra';
    w.setAttribute('aria-hidden', 'true');
    palabra.split('').forEach(function(ch){
      var s = document.createElement('span');
      s.className = 'letra';
      s.textContent = ch;
      s.style.setProperty('--i', Math.min(i++, 40));
      w.appendChild(s);
    });
    el.appendChild(w);
    if (k < todas.length - 1) el.appendChild(document.createTextNode(' '));
  });
});

/* ── 1. Reveal ─────────────────────────────────────────────────────────── */

var piezas = [].slice.call(document.querySelectorAll('.reveal'));

function mostrar(el, retardo){
  if (el.classList.contains('visible')) return;
  el.style.setProperty('--fx-d', (retardo || 0) + 'ms');
  el.classList.add('visible');
}

if (!quieto.matches && hayIO){
  raiz.classList.add('fx-on');
  raiz.dataset.fxVivo = '1';   /* desarma el seguro de la cabecera */

  var ojo = new IntersectionObserver(function(entradas){
    entradas.forEach(function(e){
      if (!e.isIntersecting) return;
      var el = e.target;
      var hermanos = [].slice.call(el.parentNode.children)
                       .filter(function(n){ return n.classList && n.classList.contains('reveal') });
      var i = hermanos.indexOf(el);
      var retardo = (hermanos.length > 2 && i > 0) ? Math.min(i, 7) * 70 : 0;
      mostrar(el, retardo);
      ojo.unobserve(el);
    });
  }, { threshold: 0.14 });
  piezas.forEach(function(el){ ojo.observe(el) });

  /* Red 1 — cierre duro a 1400 ms + retardo máximo. */
  setTimeout(function(){
    piezas.forEach(function(el){
      if (el.classList.contains('visible')) return;
      var r = el.getBoundingClientRect();
      if (r.top < innerHeight * 0.95 && r.bottom > 0) mostrar(el, 0);
    });
  }, 1400 + 7 * 70);

  /* Red 2 — barrido por scroll, coalescido a rAF, SÓLO sobre lo que quedó
     arriba (r.bottom < 0). */
  var pendiente = false;
  function barrer(){
    pendiente = false;
    var quedan = false;
    piezas.forEach(function(el){
      if (el.classList.contains('visible')) return;
      quedan = true;
      if (el.getBoundingClientRect().bottom < 0) mostrar(el, 0);
    });
    if (!quedan){
      removeEventListener('scroll', pedir);
      removeEventListener('resize', pedir);
      clearInterval(reloj);
    }
  }
  function pedir(){ if (!pendiente){ pendiente = true; requestAnimationFrame(barrer) } }
  addEventListener('scroll', pedir, { passive:true });
  addEventListener('resize', pedir);

  /* Red 3 — reloj lento con tope. */
  var vueltas = 0;
  var reloj = setInterval(function(){
    if (++vueltas > 150){ clearInterval(reloj); return }
    barrer();
  }, 400);
} else {
  raiz.classList.remove('fx-on');
}

/* El h1 no espera al observer: entra apenas hay pintura. */
var h1 = document.querySelector('h1[data-fx~="letras"]');
if (h1) setTimeout(function(){ h1.classList.add('visible') }, 180);

/* ── 2. El trazo de la marca ─────────────────────────────────────────────
   Se dibuja una vez, al entrar en vista, y no vuelve a moverse. */

(function(){
  var trazos = [].slice.call(document.querySelectorAll('.trazo'));
  if (!trazos.length) return;
  if (quieto.matches || !hayIO){
    trazos.forEach(function(t){ t.classList.add('dibujado') });
    return;
  }
  var ojo = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      ojo.unobserve(e.target);
      var t = e.target;
      /* Un cuadro de aire: si la clase entra en el mismo cuadro que el
         estado inicial, la transición no ocurre. */
      requestAnimationFrame(function(){ requestAnimationFrame(function(){ t.classList.add('dibujado') }) });
    });
  }, { threshold: 0.2 });
  trazos.forEach(function(t){ ojo.observe(t) });
})();

/* ── 3. El agua del hero: se abre una vez y queda quieta ─────────────────
   `preload="none"` no alcanza: `autoplay` lo ignora y baja el archivo igual.
   Por eso el src vive en data-src y lo pone el JS cuando el hero está a la
   vista, después del primer cuadro. No hay loop: al terminar queda en el
   último cuadro y aparece "ver la onda otra vez". */

(function(){
  var v = document.querySelector('[data-video-dif]');
  if (!v || quieto.matches) return;
  var medio = v.closest('[data-onda]');
  var otra  = medio && medio.querySelector('[data-otra-onda]');

  function reproducir(){
    v.muted = true;                     /* iOS no reproduce sin esto */
    v.loop = false;
    var p = v.play();
    if (p && p.catch) p.catch(function(){});
  }
  function encender(){
    if (v.dataset.encendido) return;
    v.dataset.encendido = '1';
    v.src = v.getAttribute('data-src');
    v.load();
    v.addEventListener('playing', function(){ v.classList.add('lista') }, { once:true });
    v.addEventListener('ended', function(){
      if (otra){ otra.hidden = false; requestAnimationFrame(function(){ otra.classList.add('visible') }) }
    });
    reproducir();
  }
  function deNuevo(){
    if (!v.dataset.encendido){ encender(); return }
    v.currentTime = 0;
    reproducir();
    if (otra) otra.classList.remove('visible');
  }
  if (medio) medio.addEventListener('click', function(ev){
    if (ev.target.closest('a,button') && ev.target !== otra) return;
    deNuevo();
  });

  var arranque = function(){
    ('requestIdleCallback' in window) ? requestIdleCallback(encender, { timeout: 1200 })
                                      : setTimeout(encender, 500);
  };
  if (!hayIO){ arranque(); return }
  var ojo = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (e.isIntersecting){ ojo.unobserve(v); arranque() } });
  }, { rootMargin: '200px 0px' });
  ojo.observe(v);
})();

/* ── 4. La rueda conectada ───────────────────────────────────────────────
   El contenido sale de las cartas (<ol class="cartas">), que son lo que se
   ve en el celular: una sola fuente. Queda quieta y sólo se mueve cuando la
   tocás: no hay avance automático. */

(function(){
  var marco  = document.querySelector('[data-rueda-marco]');
  var rueda  = marco && marco.querySelector('[data-rueda]');
  var fuente = document.querySelector('[data-cartas]');
  if (!rueda || !fuente) return;

  var datos = [].map.call(fuente.children, function(li){
    return {
      nombre:    (li.querySelector('h3') || {}).textContent || '',
      copy:      (li.querySelector('p')  || {}).textContent || '',
      corto:     li.getAttribute('data-corto') || '',
      destacada: li.classList.contains('carta--destacada')
    };
  });
  if (!datos.length) return;

  var detalle = marco.querySelector('[data-detalle]');
  var cuenta  = detalle.querySelector('[data-cuenta]');
  var cuerpo  = detalle.querySelector('.rueda__cuerpo');
  var titulo  = cuerpo.querySelector('h3');
  var texto   = cuerpo.querySelector('p');
  var corto   = rueda.querySelector('[data-corto-activo]');
  var arco    = rueda.querySelector('.rueda__arco');
  var nodos   = [];
  var activo  = -1;

  datos.forEach(function(d, i){
    var ang = (-90 + i * (360 / datos.length)) * Math.PI / 180;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'rueda__nodo' + (d.destacada ? ' rueda__nodo--destacada' : '');
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-selected', 'false');
    b.tabIndex = -1;
    var rot = document.createElement('span');
    rot.className = 'rueda__rotulo';
    rot.textContent = d.corto;
    b.appendChild(rot);
    b.style.setProperty('--cx', Math.cos(ang).toFixed(4));
    b.style.setProperty('--cy', Math.sin(ang).toFixed(4));
    b.addEventListener('click', function(){ elegir(i) });
    b.addEventListener('focus', function(){ elegir(i) });
    rueda.appendChild(b);
    nodos.push(b);
  });

  function pad(n){ return n < 10 ? '0' + n : String(n) }
  function pintar(){
    titulo.textContent = datos[activo].nombre;
    texto.textContent  = datos[activo].copy;
    if (corto)  corto.textContent  = datos[activo].corto;
    if (cuenta) cuenta.textContent = pad(activo + 1) + ' / ' + pad(datos.length);
  }
  function elegir(i){
    if (i === activo) return;
    var primera = activo === -1;
    activo = i;
    nodos.forEach(function(n, k){
      n.setAttribute('aria-selected', k === i ? 'true' : 'false');
      n.tabIndex = k === i ? 0 : -1;
    });
    if (arco) arco.setAttribute('stroke-dasharray', ((i + 1) / datos.length * 100).toFixed(2) + ' 100');
    if (primera || quieto.matches){ pintar(); return }
    cuerpo.classList.add('cambiando');
    if (corto) corto.classList.add('cambiando');
    setTimeout(function(){
      pintar();
      cuerpo.classList.remove('cambiando');
      if (corto) corto.classList.remove('cambiando');
    }, 170);
  }

  var ant = detalle.querySelector('[data-anterior]');
  var sig = detalle.querySelector('[data-siguiente]');
  if (ant) ant.addEventListener('click', function(){ elegir((activo - 1 + datos.length) % datos.length) });
  if (sig) sig.addEventListener('click', function(){ elegir((activo + 1) % datos.length) });

  rueda.addEventListener('keydown', function(ev){
    var salto = { ArrowRight:1, ArrowDown:1, ArrowLeft:-1, ArrowUp:-1 }[ev.key];
    var i = null;
    if (salto) i = (activo + salto + datos.length) % datos.length;
    else if (ev.key === 'Home') i = 0;
    else if (ev.key === 'End')  i = datos.length - 1;
    if (i === null) return;
    ev.preventDefault();
    nodos[i].focus();
  });

  elegir(0);
})();

/* ── 5. El hilo del método ───────────────────────────────────────────────
   Un solo trazo que baja uniendo los cinco pasos. El camino pasa por los
   nodos reales del DOM (así sirve en cualquier alto y en las dos columnas)
   y se dibuja con el scroll: el avance es geometría, no un reloj. */

(function(){
  var hilo = document.querySelector('[data-hilo]');
  if (!hilo) return;
  var svg   = hilo.querySelector('.hilo__trazo');
  var path  = svg.querySelector('path');
  var nodos = [].slice.call(hilo.querySelectorAll('[data-nodo]'));
  if (nodos.length < 2) return;

  function trazar(){
    var base = hilo.getBoundingClientRect();
    var W = Math.round(base.width), H = Math.round(base.height);
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('preserveAspectRatio', 'none');
    var pts = nodos.map(function(n){
      var r = n.getBoundingClientRect();
      return { x: r.left - base.left + r.width / 2, y: r.top - base.top + r.height / 2 };
    });
    var d = 'M ' + pts[0].x.toFixed(1) + ' ' + pts[0].y.toFixed(1);
    for (var i = 1; i < pts.length; i++){
      var a = pts[i - 1], b = pts[i];
      var dy = b.y - a.y, dx = b.x - a.x;
      if (Math.abs(dx) < 4){
        /* Nodos alineados (celular): la línea igual ondula un poco. Es la
           ese de la marca, no una regla. */
        var onda = (i % 2 ? 26 : -26);
        d += ' C ' + (a.x + onda).toFixed(1) + ' ' + (a.y + dy * 0.55).toFixed(1)
           + ', '  + (b.x - onda).toFixed(1) + ' ' + (b.y - dy * 0.55).toFixed(1)
           + ', '  + b.x.toFixed(1) + ' ' + b.y.toFixed(1);
      } else {
        /* Dos columnas: baja por la canaleta del número (a la izquierda del
           texto, donde no hay nada) y entra al paso siguiente de costado.
           Una diagonal directa cruzaría el texto del paso anterior. */
        d += ' C ' + a.x.toFixed(1) + ' ' + b.y.toFixed(1)
           + ', '  + (a.x + dx * 0.45).toFixed(1) + ' ' + b.y.toFixed(1)
           + ', '  + b.x.toFixed(1) + ' ' + b.y.toFixed(1);
      }
    }
    path.setAttribute('d', d);
  }

  var pendiente = false;
  function avanzar(){
    pendiente = false;
    if (quieto.matches){ path.style.setProperty('--hilo', 0); return }
    var r = hilo.getBoundingClientRect();
    /* Progreso: cuánto del hilo quedó por encima del 78% de la pantalla. */
    var p = (innerHeight * 0.78 - r.top) / r.height;
    p = Math.max(0, Math.min(1, p));
    path.style.setProperty('--hilo', (1 - p).toFixed(3));
  }
  function pedir(){ if (!pendiente){ pendiente = true; requestAnimationFrame(avanzar) } }

  trazar(); avanzar();
  addEventListener('scroll', pedir, { passive:true });
  addEventListener('resize', function(){ trazar(); pedir() });
  addEventListener('load', function(){ trazar(); pedir() });
  setTimeout(function(){ trazar(); pedir() }, 800);   /* fuentes y fotos diferidas cambian el alto */
})();

/* ── 6. Cabecera, menú y sección activa ─────────────────────────────────── */

(function(){
  var cabecera = document.querySelector('[data-cabecera]');
  var boton    = document.querySelector('[data-abrir]');
  var menu     = document.querySelector('[data-menu]');
  if (!cabecera || !boton || !menu) return;
  var rotulos  = { abrir: boton.textContent, cerrar: boton.getAttribute('data-cerrar') || 'Cerrar' };
  var enlaces  = [].slice.call(menu.querySelectorAll('ul a'));
  var destinos = enlaces.map(function(a){ return document.querySelector(a.getAttribute('href')) }).filter(Boolean);

  function fijar(abierto){
    menu.setAttribute('data-abierto', abierto ? 'true' : 'false');
    boton.setAttribute('aria-expanded', abierto ? 'true' : 'false');
    boton.textContent = abierto ? rotulos.cerrar : rotulos.abrir;
    /* En html y no en body: body con overflow no propaga al viewport cuando
       html ya tiene overflow-x:clip. */
    raiz.style.overflowY = (abierto && !grande()) ? 'hidden' : '';
  }
  boton.addEventListener('click', function(){ fijar(menu.getAttribute('data-abierto') !== 'true') });
  [].forEach.call(menu.querySelectorAll('a'), function(a){ a.addEventListener('click', function(){ fijar(false) }) });
  addEventListener('keydown', function(e){ if (e.key === 'Escape' && menu.getAttribute('data-abierto') === 'true') fijar(false) });
  addEventListener('resize', function(){ if (grande()) fijar(false) });

  var pendiente = false;
  function mirar(){
    pendiente = false;
    cabecera.classList.toggle('pegada', scrollY > 16);
    var y = scrollY + cabecera.offsetHeight + 12;
    var actual = null;
    destinos.forEach(function(s){ if (topAbsoluto(s) <= y) actual = s });
    enlaces.forEach(function(a){
      var es = actual && a.getAttribute('href') === '#' + actual.id;
      if (es) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
  }
  addEventListener('scroll', function(){ if (!pendiente){ pendiente = true; requestAnimationFrame(mirar) } }, { passive:true });
  mirar();
})();

/* ── 7. El estante ───────────────────────────────────────────────────────
   En el celular, tocar una foto la centra. Guarda de 4 px: si todo entra
   sin scroll (escritorio, donde es una mesa), no se mueve nada. */

(function(){
  var estante = document.querySelector('[data-estante]');
  if (!estante) return;
  [].forEach.call(estante.children, function(item){
    item.addEventListener('click', function(){
      if (estante.scrollWidth <= estante.clientWidth + 4) return;
      var izq = item.offsetLeft - (estante.clientWidth - item.offsetWidth) / 2;
      estante.scrollTo({ left: izq, behavior: quieto.matches ? 'auto' : 'smooth' });
    });
  });
})();

/* ── 8. Formulario ───────────────────────────────────────────────────────
   Arma el mensaje ya escrito. Mientras no esté el WhatsApp de Mavenz,
   muestra el mensaje en pantalla en vez de abrir un chat que no existe. */

(function(){
  var form = document.querySelector('[data-formulario]');
  if (!form) return;
  var aviso = form.querySelector('[data-aviso]');
  var numero = form.getAttribute('data-whatsapp') || '';

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var d = new FormData(form);
    var nombre = String(d.get('nombre') || '').trim();
    var contacto = String(d.get('contacto') || '').trim();
    if (!nombre || !contacto){
      aviso.textContent = form.getAttribute('data-falta');
      (nombre ? form.contacto : form.nombre).focus();
      return;
    }
    var texto = 'Hola Mavenz, soy ' + nombre + '. ' + d.get('motivo') + '.'
              + (d.get('mensaje') ? ' ' + String(d.get('mensaje')).trim() : '')
              + ' Me pueden escribir a ' + contacto + '.';
    if (numero){
      open('https://wa.me/' + numero + '?text=' + encodeURIComponent(texto), '_blank', 'noopener');
      aviso.textContent = form.getAttribute('data-listo');
    } else {
      aviso.textContent = form.getAttribute('data-sin-numero') + ' ' + texto;
    }
  });
})();

})();
