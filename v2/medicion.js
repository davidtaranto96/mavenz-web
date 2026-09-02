/* ==========================================================================
   Medición y consentimiento.

   Regla de DT System: sin etiquetas configuradas NO se muestra ningún banner.
   Mientras MEDICION.ga4 esté vacío, este archivo no carga nada, no deja
   cookies y no dibuja el aviso. Cargar el ID de abajo enciende las tres
   cosas a la vez.
   ========================================================================== */
(function(){
'use strict';

var MEDICION = {
  ga4: '',        // <-- PENDIENTE: G-XXXXXXXXXX de Mavenz
  meta: ''        // <-- PENDIENTE: ID del píxel de Meta
};

var hayEtiquetas = !!(MEDICION.ga4 || MEDICION.meta);

/* ── 1. Eventos ─────────────────────────────────────────────────────────
   Se registran siempre en dataLayer: no dejan cookie ni salen del
   navegador si no hay etiquetas, y el día que se enciendan ya está todo
   instrumentado sin tocar el HTML. */

window.dataLayer = window.dataLayer || [];
function anotar(evento, datos){
  window.dataLayer.push(Object.assign({ event: evento }, datos || {}));
  if (hayEtiquetas && window.gtag) window.gtag('event', evento, datos || {});
}

function seccionDe(el){
  var s = el.closest('section[id]');
  return s ? s.id : 'sin-seccion';
}

document.addEventListener('click', function(ev){
  var a = ev.target.closest('a.boton, a.enlace, .boton');
  if (!a) return;
  anotar('cta', {
    texto:   (a.textContent || '').trim().slice(0, 60),
    destino: a.getAttribute('href') || '',
    seccion: seccionDe(a)
  });
}, true);

var form = document.querySelector('[data-formulario]');
if (form) form.addEventListener('submit', function(){
  var motivo = form.querySelector('#motivo');
  anotar('consulta', { motivo: motivo ? motivo.value : '', seccion: seccionDe(form) });
});

[].forEach.call(document.querySelectorAll('[data-anillo]'), function(a){
  a.addEventListener('click', function(ev){
    var n = ev.target.closest('.anillo__nodo');
    if (n) anotar('esfera', { nombre: (n.textContent || '').trim(), seccion: seccionDe(a) });
  });
});

if (!hayEtiquetas) return;   /* hasta acá llega sin etiquetas: sin banner. */

/* ── 2. Las etiquetas ───────────────────────────────────────────────────── */

if (MEDICION.ga4){
  var g = document.createElement('script');
  g.async = true;
  g.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEDICION.ga4;
  document.head.appendChild(g);
  window.gtag = function(){ window.dataLayer.push(arguments) };
  window.gtag('js', new Date());
  window.gtag('config', MEDICION.ga4, { anonymize_ip: true });
}

/* ── 3. El aviso de cookies ─────────────────────────────────────────────
   Consentimiento por navegación: informa, no bloquea. Una sola línea, un
   solo botón. Cuelga de <body> y nunca de adentro de un bloque con reveal,
   o se queda invisible. */

var CLAVE = 'mavenz-cookies';
try { if (localStorage.getItem(CLAVE)) return } catch (e) { /* modo privado */ }

var aviso = document.createElement('div');
aviso.className = 'aviso-cookies';
aviso.setAttribute('role', 'region');
aviso.setAttribute('aria-label', 'Aviso de cookies');
aviso.innerHTML = '<p>Al navegar por este sitio <strong>aceptás el uso de cookies</strong> ' +
                  'para mejorar tu experiencia.</p>' +
                  '<button type="button" class="boton">Entendido</button>';
document.body.appendChild(aviso);

aviso.querySelector('button').addEventListener('click', function(){
  try { localStorage.setItem(CLAVE, '1') } catch (e) {}
  aviso.remove();
});

})();
