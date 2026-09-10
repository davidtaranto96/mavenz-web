/* ==========================================================================
   Mavenz — aviso de cookies

   Sin etiquetas de medición no hay nada que consentir, así que no hay aviso.
   Los IDs viven en el <body> (data-ga4, data-pixel), vacíos hasta que alguien
   los configure: no se le muestra a la gente un cartel por algo que todavía
   no existe, y no hay que acordarse de "activarlo" después.

   Aceptar carga GA4 y/o el pixel de Meta, según qué ID haya. Rechazar no
   carga nada y se acuerda. Escape cierra sin decidir y vuelve a preguntar la
   próxima vez. La decisión queda en localStorage, que es por origen: sirve
   para las tres páginas y los dos idiomas.

   Los eventos del sitio salen por window.mavenzEvento(nombre, datos) sin
   preguntar si hubo permiso: hasta que la persona decide se guardan en una
   cola con tope; si acepta salen todos, si rechaza se tiran. No hay medición
   encubierta y el código del sitio no se llena de "if (consintió)".

   Nada de document.write: las etiquetas entran como <script async> creados
   desde acá, recién después del sí. Va con defer, antes de guion.js.
   ========================================================================== */

(function () {
  'use strict';

  /* Con nombre propio y no "cookies" a secas: GitHub Pages sirve todos los
     sitios de David desde el mismo origen y el localStorage se comparte. */
  var CLAVE = 'mavenz.cookies';
  var TOPE  = 40;              /* eventos guardados antes de decidir; más que eso es una fuga */

  var GA4_ID   = '';
  var PIXEL_ID = '';
  var HAY_ETIQUETAS = null;    /* null: todavía no se leyó el <body> */

  var decision   = leer();     /* 'aceptar' | 'rechazar' | null */
  var cargado    = false;      /* las etiquetas ya están en la página */
  var cola       = [];
  var tarjeta    = null;       /* el aviso, mientras está abierto */
  var origenFoco = null;       /* a dónde vuelve el foco al cerrar */

  /* ---------------------------------------------------------------------- */
  /* La API de eventos. Existe siempre, aun sin etiquetas, para que el sitio */
  /* la llame sin tener que saber si hay medición.                           */
  /* ---------------------------------------------------------------------- */

  window.mavenzEvento = function (nombre, datos) {
    if (HAY_ETIQUETAS === false || decision === 'rechazar') return;   /* nada que medir, o dijo que no */
    if (cargado) { mandar(nombre, datos); return; }
    if (cola.length < TOPE) cola.push([nombre, datos]);                /* todavía no decidió: espera */
  };

  /* ---------------------------------------------------------------------- */
  /* Arranque                                                                */
  /* ---------------------------------------------------------------------- */

  function arrancar() {
    var cuerpo = document.body;
    GA4_ID   = (cuerpo.getAttribute('data-ga4')   || '').replace(/\s/g, '');
    PIXEL_ID = (cuerpo.getAttribute('data-pixel') || '').replace(/\s/g, '');
    HAY_ETIQUETAS = !!(GA4_ID || PIXEL_ID);

    /* Sin etiquetas no hay nada que consentir: ni aviso, ni enlace en el pie,
       ni localStorage. Lo que se haya encolado hasta acá se descarta. */
    if (!HAY_ETIQUETAS) { cola = []; return; }

    /* El enlace del pie viene oculto en el HTML y sólo aparece si hay algo
       que consentir. Es un <a> para que exista sin guion, pero acá no navega. */
    Array.prototype.forEach.call(document.querySelectorAll('[data-cookies-abrir]'), function (el) {
      el.removeAttribute('hidden');
      el.addEventListener('click', function (e) {
        e.preventDefault();
        abrir();
      });
    });

    if (decision === 'aceptar') cargar();
    else if (decision === null) abrir();
    /* 'rechazar': no se carga nada y no se vuelve a preguntar; el pie lo reabre. */
  }

  /* ---------------------------------------------------------------------- */
  /* El aviso                                                                */
  /* ---------------------------------------------------------------------- */

  function abrir() {
    if (tarjeta) { enfocar(); return; }                 /* ya está abierto: sólo llevar el foco */

    var plantilla = document.getElementById('cookies');
    if (!plantilla || !plantilla.content) return;       /* sin <template> no hay aviso; sin soporte, tampoco */
    var molde = plantilla.content.firstElementChild;
    if (!molde) return;

    origenFoco = document.activeElement;
    tarjeta = molde.cloneNode(true);
    /* Cuelga de <body> y de nada más: adentro de un bloque con transform el
       fixed se ancla a ese bloque y no a la ventana. */
    document.body.appendChild(tarjeta);
    tarjeta.addEventListener('click', alClic);
    document.addEventListener('keydown', alTecla);
    enfocar();
  }

  function cerrar() {
    if (!tarjeta) return;
    tarjeta.removeEventListener('click', alClic);
    document.removeEventListener('keydown', alTecla);
    tarjeta.parentNode.removeChild(tarjeta);
    tarjeta = null;

    /* El foco vuelve a donde estaba. Si estaba en el <body> (el aviso se
       abrió solo, al cargar) no hay a dónde volver: el navegador ya lo dejó
       ahí al sacar el botón. */
    if (origenFoco && origenFoco !== document.body && document.contains(origenFoco)) {
      origenFoco.focus({ preventScroll: true });
    }
    origenFoco = null;
  }

  /* El primer botón, sin scrollear: la tarjeta es fixed y ya está a la vista. */
  function enfocar() {
    var primero = tarjeta.querySelector('button');
    if (primero) primero.focus({ preventScroll: true });
  }

  function alClic(e) {
    var boton = e.target.closest('[data-cookies]');
    if (boton) decidir(boton.getAttribute('data-cookies'));
  }

  function alTecla(e) {
    if (e.key === 'Escape') cerrar();                  /* cierra sin decidir */
  }

  function decidir(valor) {
    if (valor !== 'aceptar' && valor !== 'rechazar') return;
    decision = valor;
    guardar(valor);
    if (valor === 'aceptar') cargar();
    else cola = [];                                    /* dijo que no: lo esperado se tira */
    cerrar();
  }

  /* ---------------------------------------------------------------------- */
  /* Las etiquetas: entran una sola vez, recién con el sí                    */
  /* ---------------------------------------------------------------------- */

  function cargar() {
    if (cargado) return;
    cargado = true;

    if (GA4_ID) {
      /* El mismo arranque que el snippet oficial, sin document.write: gtag
         es una cola hasta que llega el script, y el script la vacía. */
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', GA4_ID);
      script('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID));
    }

    if (PIXEL_ID) {
      /* Ídem para Meta: el stub oficial escrito a mano, legible. fbq encola
         hasta que carga fbevents.js, que lo reemplaza. */
      if (!window.fbq) {
        var fbq = function () {
          if (fbq.callMethod) fbq.callMethod.apply(fbq, arguments);
          else fbq.queue.push(arguments);
        };
        fbq.push = fbq;
        fbq.loaded = true;
        fbq.version = '2.0';
        fbq.queue = [];
        window.fbq = fbq;
        if (!window._fbq) window._fbq = fbq;
      }
      window.fbq('init', PIXEL_ID);
      window.fbq('track', 'PageView');
      script('https://connect.facebook.net/en_US/fbevents.js');
    }

    /* Lo que el sitio quiso medir antes del sí, ahora sale. */
    while (cola.length) {
      var ev = cola.shift();
      mandar(ev[0], ev[1]);
    }
  }

  function mandar(nombre, datos) {
    var d = datos || {};
    if (GA4_ID   && window.gtag) window.gtag('event', nombre, d);
    if (PIXEL_ID && window.fbq)  window.fbq('trackCustom', nombre, d);
  }

  function script(src) {
    var s = document.createElement('script');
    s.src = src;
    s.async = true;
    document.head.appendChild(s);
  }

  /* ---------------------------------------------------------------------- */
  /* La decisión, guardada                                                   */
  /*                                                                         */
  /* try/catch porque localStorage tira en Safari privado y con las cookies  */
  /* bloqueadas. Ahí el aviso vuelve a salir en cada carga, que es lo justo. */
  /* ---------------------------------------------------------------------- */

  function leer() {
    try {
      var v = window.localStorage.getItem(CLAVE);
      return (v === 'aceptar' || v === 'rechazar') ? v : null;
    } catch (e) {
      return null;
    }
  }

  function guardar(valor) {
    try { window.localStorage.setItem(CLAVE, valor); } catch (e) { /* sin memoria: se vuelve a preguntar */ }
  }

  /* Va con defer, así que el DOM ya está; si llegara a correr antes, espera.
     mavenzEvento ya quedó definida arriba, así que lo que se dispare mientras
     tanto se encola y no se pierde. */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar, { once: true });
  } else {
    arrancar();
  }
})();
