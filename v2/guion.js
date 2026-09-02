/* ==========================================================================
   Mavenz — guion único. Sin dependencias.

   Reglas que gobiernan este archivo, todas aprendidas a los golpes:
   · El estado oculto del reveal lo escribe el JS, nunca el CSS solo. Si el
     JS no arranca, la página se ve entera.
   · Nada se mueve en bucle. Lo que se mueve solo, se frena fuera de pantalla.
   · El rescate del reveal se dispara por geometría, jamás por reloj, y sólo
     sobre lo que ya pasó de largo: si rescata lo visible, le roba el
     escalonado al observer.
   ========================================================================== */
(function(){
'use strict';

var raiz    = document.documentElement;
var quieto  = matchMedia('(prefers-reduced-motion: reduce)');
var chica   = function(){ return matchMedia('(max-width:63.99rem), (max-height:30rem)').matches };
var tactil  = !matchMedia('(hover:hover) and (pointer:fine)').matches;

/* ── 1. Reveal ──────────────────────────────────────────────────────────
   Duración y curva viven en el CSS. Acá sólo se decide CUÁNDO y con qué
   retardo. El escalonado es de 70 ms, tope en el séptimo hermano, y sólo
   si hay más de dos: con dos se lee como lag, con cinco como coreografía. */

var piezas = [].slice.call(document.querySelectorAll('[data-revelar]'));

function mostrar(el, retardo){
  if (el.classList.contains('visible')) return;
  el.style.setProperty('--fx-d', (retardo || 0) + 'ms');
  el.classList.add('visible');
}

if (!quieto.matches && piezas.length && 'IntersectionObserver' in window){
  raiz.classList.add('fx-on');
  raiz.dataset.fxVivo = '1';   /* desarma el seguro de la cabecera */

  var ojo = new IntersectionObserver(function(entradas){
    entradas.forEach(function(e){
      if (!e.isIntersecting) return;
      var el = e.target;
      var hermanos = [].slice.call(el.parentNode.children)
                       .filter(function(n){ return n.hasAttribute && n.hasAttribute('data-revelar') });
      var i = hermanos.indexOf(el);
      var retardo = (hermanos.length > 2 && i > 0) ? Math.min(i, 7) * 70 : 0;
      mostrar(el, retardo);
      ojo.unobserve(el);
    });
  }, { threshold: 0.14 });

  piezas.forEach(function(el){ ojo.observe(el) });

  /* Red 1 — cierre duro: si a los 1400 ms + retardo sigue apagado, se
     enciende igual. Cubre el caso del observer que nunca dispara. */
  setTimeout(function(){
    piezas.forEach(function(el){
      if (getComputedStyle(el).opacity < 0.95 && !el.classList.contains('visible')){
        var r = el.getBoundingClientRect();
        if (r.top < innerHeight * 0.95 && r.bottom > 0) mostrar(el, 0);
      }
    });
  }, 1400 + 7 * 70);

  /* Red 2 — barrido por scroll, coalescido a rAF. Mira SÓLO lo que quedó
     arriba del viewport (r.bottom < 0): un salto de 900 px con un viewport
     de 800 deja secciones en opacity 0 para siempre porque la ratio del
     observer va de 0 a 0 sin cruzar el umbral. Rescatar además lo visible
     le robaría el escalonado. */
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

  /* Red 3 — reloj lento con tope, por si scroll y resize nunca ocurren
     (una captura automática, una vista previa de WhatsApp). */
  var vueltas = 0;
  var reloj = setInterval(function(){
    if (++vueltas > 150){ clearInterval(reloj); return }
    barrer();
  }, 400);
}

/* ── 2. El anillo ───────────────────────────────────────────────────────
   Un componente, dos usos: el Universo y el Método. El contenido sale del
   <ul class="circuito"> que ya está en el HTML, así hay una sola fuente y
   la página funciona sin JS. */

[].forEach.call(document.querySelectorAll('[data-anillo]'), function(anillo){
  var marco  = anillo.closest('.anillo-marco') || anillo.parentNode;
  var fuente = marco.querySelector('[data-fuente-anillo]');
  if (!fuente) return;

  var datos = [].map.call(fuente.children, function(li){
    var nombre = (li.querySelector('h3') || {}).textContent || '';
    return {
      nombre: nombre,
      /* En la rueda va el rótulo corto: siete nombres largos sobre un
         anillo de 380 px chocan entre sí y pisan el centro. El nombre
         completo vive en el centro, que es donde se lee. */
      corto:  li.getAttribute('data-corto') || nombre,
      copy:   (li.querySelector('p') || {}).textContent || ''
    };
  });
  if (!datos.length) return;

  /* La descripción no entra adentro de un anillo de 380 px: vive al lado,
     en la columna que si no quedaría vacía. El centro sólo confirma cuál
     está elegida. */
  var detalle = marco.querySelector('[data-detalle]');
  var centro  = anillo.querySelector('.centro-corto');
  var cuenta  = detalle.querySelector('[data-cuenta]');
  var cuerpo  = detalle.querySelector('.cuerpo');
  var titulo  = cuerpo.querySelector('h3');
  var texto   = cuerpo.querySelector('p');
  var barrido = detalle.querySelector('.barrido');
  var arco    = anillo.querySelector('.arco');
  var nodos   = [];
  var activo  = -1;
  var solo    = null;   /* el temporizador del avance automático */

  /* Sólo se pasa la dirección; el radio y el corrimiento del rótulo los
     resuelve el CSS contra --lado, que es lo que cambia entre carriles. */

  datos.forEach(function(d, i){
    var ang = (-90 + i * (360 / datos.length)) * Math.PI / 180;
    var cx = Math.cos(ang), cy = Math.sin(ang);
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'anillo__nodo';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-selected', 'false');
    b.tabIndex = -1;
    var rot = document.createElement('span');
    rot.className = 'anillo__rotulo';
    rot.textContent = d.corto;
    b.appendChild(rot);
    b.style.setProperty('--cx', cx.toFixed(4));
    b.style.setProperty('--cy', cy.toFixed(4));
    b.addEventListener('click', function(){ frenar(); elegir(i) });
    b.addEventListener('focus', function(){ frenar(); elegir(i) });
    anillo.appendChild(b);
    nodos.push(b);
  });

  function elegir(i){
    if (i === activo) return;
    var primera = activo === -1;
    activo = i;

    nodos.forEach(function(n, k){
      n.setAttribute('aria-selected', k === i ? 'true' : 'false');
      n.tabIndex = k === i ? 0 : -1;
    });
    if (arco) arco.setAttribute('stroke-dasharray', ((i + 1) / datos.length * 100) + ' 100');

    if (primera || quieto.matches){ pintar() ; return }

    /* Fundido corto y barrido de luz: el fundido solo es demasiado suave
       para confirmar que el clic hizo algo. */
    cuerpo.classList.add('cambiando');
    setTimeout(function(){
      pintar();
      cuerpo.classList.remove('cambiando');
      if (barrido){
        barrido.classList.remove('corre');
        void barrido.offsetWidth;      /* sin esto, al segundo clic no pasa nada */
        barrido.classList.add('corre');
      }
    }, 180);
  }

  function pintar(){
    titulo.textContent = datos[activo].nombre;
    texto.textContent  = datos[activo].copy;
    if (centro) centro.textContent = datos[activo].corto;
    if (cuenta) cuenta.textContent = pad(activo + 1) + ' / ' + pad(datos.length);
  }
  function pad(n){ return n < 10 ? '0' + n : String(n) }

  /* Teclado de tablist: flechas mueven, Inicio y Fin van a los extremos. */
  anillo.addEventListener('keydown', function(ev){
    var salto = { ArrowRight:1, ArrowDown:1, ArrowLeft:-1, ArrowUp:-1 }[ev.key];
    var i = null;
    if (salto) i = (activo + salto + datos.length) % datos.length;
    else if (ev.key === 'Home') i = 0;
    else if (ev.key === 'End')  i = datos.length - 1;
    if (i === null) return;
    ev.preventDefault();
    frenar();
    nodos[i].focus();
  });

  function frenar(){ if (solo){ clearInterval(solo); solo = null } }
  function arrancar(){
    if (solo || quieto.matches || tactil || chica()) return;
    var cada = parseInt(anillo.getAttribute('data-auto'), 10);
    if (!cada) return;
    solo = setInterval(function(){ elegir((activo + 1) % datos.length) }, cada);
  }

  elegir(0);

  /* Avanza solo mientras se lo ve. Fuera de pantalla no gasta nada. */
  if ('IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      es.forEach(function(e){ e.isIntersecting ? arrancar() : frenar() });
    }, { threshold: 0.35 }).observe(anillo);
  }
  anillo.addEventListener('pointerenter', frenar);
});

/* ── 2b. El trazo de la marca ───────────────────────────────────────────
   Se dibuja una vez, al entrar en vista, y no vuelve a moverse. Es el hilo
   que ata el sitio a la identidad de Fractura sin repetir el logo. */

(function(){
  var trazos = [].slice.call(document.querySelectorAll('.trazo'));
  if (!trazos.length) return;
  if (quieto.matches || !('IntersectionObserver' in window)){
    trazos.forEach(function(t){ t.classList.add('dibujado') });
    return;
  }
  var ojo = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      ojo.unobserve(e.target);
      var t = e.target;
      /* Un cuadro de aire antes de arrancar: si se agrega la clase en el
         mismo cuadro que el estado inicial, la transición no ocurre. */
      requestAnimationFrame(function(){
        requestAnimationFrame(function(){ t.classList.add('dibujado') });
      });
    });
  }, { threshold: 0.2 });
  trazos.forEach(function(t){ ojo.observe(t) });
})();

/* ── 3. Video del hero, diferido ─────────────────────────────────────────
   `preload="none"` no alcanza: `autoplay` lo ignora por especificación y el
   archivo se baja igual. Por eso el src vive en data-src y lo pone el JS.
   El póster ya está pintado; el video llega después, sin competirle al
   primer cuadro. */

(function(){
  var videos = [].slice.call(document.querySelectorAll('[data-video-dif]'));
  if (!videos.length || quieto.matches) return;

  function encender(v){
    if (v.dataset.encendido) return;
    v.dataset.encendido = '1';
    v.src = v.getAttribute('data-src');
    v.load();
    v.muted = true;                    /* iOS no reproduce sin esto */
    v.loop = true;
    var p = v.play();
    if (p && p.catch) p.catch(function(){});
    v.addEventListener('playing', function(){ v.classList.add('lista') }, { once:true });
  }

  if (!('IntersectionObserver' in window)){ videos.forEach(encender); return }

  var ojo = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      ojo.unobserve(e.target);
      /* Después del primer cuadro, nunca compitiéndole. */
      requestIdleCallback ? requestIdleCallback(function(){ encender(e.target) })
                          : setTimeout(function(){ encender(e.target) }, 600);
    });
  }, { rootMargin:'300px 0px' });

  videos.forEach(function(v){ ojo.observe(v) });
})();

/* ── 4. Cabecera, menú y sección activa ───────────────────────────────────
   Con secciones sticky, getBoundingClientRect miente: hay que leer offsetTop.
   Pero offsetTop es relativo al offsetParent, y el envase de la cortina es
   uno: sin subir la cadena, las secciones de adentro dan casi cero y el
   marcador de la barra se va a la primera de ellas. */

function topAbsoluto(el){
  var y = 0;
  while (el){ y += el.offsetTop; el = el.offsetParent }
  return y;
}


(function(){
  var cabecera = document.querySelector('header');
  var boton    = document.querySelector('.abrir-menu');
  var menu     = document.getElementById('menu');
  var enlaces  = [].slice.call(menu.querySelectorAll('a'));
  var destinos = enlaces.map(function(a){ return document.querySelector(a.getAttribute('href')) })
                        .filter(Boolean);

  boton.addEventListener('click', function(){
    var abierto = menu.getAttribute('data-abierto') === 'true';
    menu.setAttribute('data-abierto', abierto ? 'false' : 'true');
    boton.setAttribute('aria-expanded', abierto ? 'false' : 'true');
    boton.textContent = abierto ? 'Menú' : 'Cerrar';
  });
  enlaces.forEach(function(a){
    a.addEventListener('click', function(){
      menu.setAttribute('data-abierto', 'false');
      boton.setAttribute('aria-expanded', 'false');
      boton.textContent = 'Menú';
    });
  });
  addEventListener('keydown', function(e){
    if (e.key === 'Escape' && menu.getAttribute('data-abierto') === 'true') boton.click();
  });

  /* Con secciones sticky, getBoundingClientRect miente. Se lee offsetTop. */
  var pendiente = false;
  function mirar(){
    pendiente = false;
    cabecera.classList.toggle('pegada', scrollY > 24);
    var y = scrollY + cabecera.offsetHeight + 8;
    var actual = destinos[0];
    destinos.forEach(function(s){ if (topAbsoluto(s) <= y) actual = s });
    enlaces.forEach(function(a){
      a.setAttribute('aria-current', a.getAttribute('href') === '#' + actual.id ? 'true' : 'false');
    });
  }
  addEventListener('scroll', function(){
    if (!pendiente){ pendiente = true; requestAnimationFrame(mirar) }
  }, { passive:true });
  mirar();
})();

/* ── 5. La cortina ──────────────────────────────────────────────────────
   Si la sección que queda fija es más alta que la pantalla, `top:0` la deja
   cortada por abajo. Se corrige con top negativo, y se recalcula una vez
   más a los 800 ms: en el teléfono las fuentes y las fotos diferidas
   cambian la altura después del primer layout. */

(function(){
  var fondo = document.querySelector('.cortina > .cortina-fondo');
  if (!fondo) return;
  function ajustar(){
    if (!matchMedia('(min-width:64rem)').matches || quieto.matches){ fondo.style.top = ''; return }
    var sobra = fondo.offsetHeight - innerHeight;
    fondo.style.top = sobra > 0 ? (-sobra) + 'px' : '0px';
  }
  addEventListener('load', ajustar);
  addEventListener('resize', ajustar);
  setTimeout(ajustar, 800);
  ajustar();
})();

/* ── 6. El estante de proyectos ─────────────────────────────────────────
   Centra el elegido. Guarda de 4 px: si todo entra sin scroll, no se
   centra nada — mover una fila que ya se ve entera es ruido. */

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

/* ── 7. Formulario ──────────────────────────────────────────────────────
   Arma el mensaje ya escrito y le agrega de qué sección salió la consulta.
   PENDIENTE: el WhatsApp real de Mavenz. Mientras no esté, muestra el
   mensaje en vez de abrir un chat que no existe. */

var WHATSAPP_MAVENZ = '';   /* <-- número real, sin + ni espacios */

(function(){
  var form = document.querySelector('[data-formulario]');
  if (!form) return;
  var aviso = form.querySelector('[data-aviso]');

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var d = new FormData(form);
    var nombre = (d.get('nombre') || '').trim();
    var contacto = (d.get('contacto') || '').trim();
    if (!nombre || !contacto){
      aviso.textContent = 'Falta el nombre o el contacto.';
      return;
    }
    var texto = 'Hola Mavenz, soy ' + nombre + '. Motivo: ' + d.get('motivo') + '.'
              + (d.get('mensaje') ? ' ' + String(d.get('mensaje')).trim() : '')
              + ' Me pueden escribir a ' + contacto + '.'
              + ' (Desde la web, sección ' + seccionVisible() + ')';

    if (WHATSAPP_MAVENZ){
      open('https://wa.me/' + WHATSAPP_MAVENZ + '?text=' + encodeURIComponent(texto), '_blank', 'noopener');
      aviso.textContent = 'Listo, se abre WhatsApp con el mensaje escrito.';
    } else {
      aviso.textContent = 'Falta cargar el WhatsApp de Mavenz. El mensaje que saldría es: ' + texto;
    }
  });

  function seccionVisible(){
    var actual = 'inicio';
    [].forEach.call(document.querySelectorAll('main section[id]'), function(s){
      if (topAbsoluto(s) <= scrollY + 120) actual = s.id;
    });
    return actual;
  }
})();

/* ── 8. Pausa fuera de pantalla ─────────────────────────────────────────
   Se observan las <section>, no los elementos: ocho observers en vez de
   treinta. Y se pausa, no se apaga: `animation:none` pierde el progreso y
   la animación salta al volver. */

if ('IntersectionObserver' in window && !quieto.matches){
  var freno = new IntersectionObserver(function(es){
    es.forEach(function(e){ e.target.classList.toggle('fx-quieto', !e.isIntersecting) });
  }, { rootMargin:'250px 0px' });
  [].forEach.call(document.querySelectorAll('main section'), function(s){ freno.observe(s) });
}

})();
