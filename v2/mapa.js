/* ==========================================================================
   El Mapa Mavenz — los seis territorios sobre el mapa real de Salta.

   Leaflet y los mosaicos NO se cargan con la página: entran cuando la
   sección se acerca. Son ~150 KB más los tiles, y la mayoría de las visitas
   nunca baja hasta acá.
   ========================================================================== */
(function(){
'use strict';

var seccion = document.getElementById('mapa');
if (!seccion) return;

var LEAFLET_JS  = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
var LEAFLET_CSS = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
var SRI_JS  = 'sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH';
var SRI_CSS = 'sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H';

var TERRITORIOS = {
  micro:      { puntos:[[-24.7883,-65.4106]] },
  norte:      { puntos:[[-24.7180,-65.4045]] },
  sanlorenzo: { puntos:[[-24.7339,-65.4863],[-24.7620,-65.4770]] },
  aeropuerto: { puntos:[[-24.8560,-65.4870]] },
  cafayate:   { puntos:[[-26.0730,-65.9764],[-25.1198,-66.1654]] },
  vaqueros:   { puntos:[[-24.6897,-65.4054]] }
};
var ORDEN = ['micro','norte','sanlorenzo','vaqueros','aeropuerto','cafayate'];

var quieto = matchMedia('(prefers-reduced-motion: reduce)');
var caja    = seccion.querySelector('[data-mapa]');
var lista   = seccion.querySelector('[data-territorios]');
var detalle = seccion.querySelector('[data-detalle-mapa]');
var datos   = null, mapa = null, capas = {}, activo = null, arrancado = false;
var elegido = false;   /* ¿alguien tocó un territorio? */

/* --- la lista y el detalle andan sin mapa: es contenido, no decoración --- */

function pintarDetalle(id){
  var t = datos[id]; if (!t) return;
  activo = id;
  [].forEach.call(lista.querySelectorAll('button'), function(b){
    b.setAttribute('aria-selected', b.getAttribute('data-id') === id ? 'true' : 'false');
  });
  detalle.querySelector('[data-cuenta]').textContent =
    pad(ORDEN.indexOf(id) + 1) + ' / ' + pad(ORDEN.length);
  detalle.querySelector('h3').textContent = t.nombre;
  detalle.querySelector('.bajada').textContent = t.bajada;
  detalle.querySelector('.lectura').textContent = t.mavenz;
  detalle.querySelector('.oportunidades').textContent = t.oportunidades;
  if (mapa && elegido) volar(id);
}
function pad(n){ return n < 10 ? '0' + n : String(n) }

function construirLista(){
  lista.innerHTML = '';
  ORDEN.forEach(function(id){
    var li = document.createElement('li');
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'territorio';
    b.setAttribute('data-id', id);
    b.setAttribute('aria-selected', 'false');
    b.textContent = datos[id].nombre;
    b.addEventListener('click', function(){ elegido = true; pintarDetalle(id) });
    li.appendChild(b); lista.appendChild(li);
  });
}

/* --------------------------------- el mapa, sólo cuando se acerca -------- */

function traer(url, sri, esCss){
  return new Promise(function(res, rej){
    var el;
    if (esCss){ el = document.createElement('link'); el.rel = 'stylesheet'; el.href = url }
    else { el = document.createElement('script'); el.src = url }
    el.integrity = sri; el.crossOrigin = 'anonymous';
    el.onload = res; el.onerror = rej;
    document.head.appendChild(el);
  });
}

/* Leaflet quiere valores, no variables: se leen del mismo :root para no
   escribir un HEX suelto. */
function tono(nombre){
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

function armarMapa(){
  if (arrancado || !window.L) return;
  arrancado = true;
  var L = window.L;
  mapa = L.map(caja, { scrollWheelZoom:false, zoomControl:true, attributionControl:true });
  /* Mosaicos de OpenStreetMap: sin clave y sin marca de agua. Los de CARTO
     que usaba la demo vieja ahora piden API key y escriben "API KEY
     REQUIRED" sobre todo el mapa. Para producción conviene un proveedor con
     plan propio (MapTiler, Stadia) o autoalojarlos; para la demo, esto
     alcanza. El tono lo pone un filtro estático, no una animación. */
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom:18, attribution:'© colaboradores de OpenStreetMap'
  }).addTo(mapa);

  var todos = [];
  ORDEN.forEach(function(id){
    var grupo = L.layerGroup().addTo(mapa);
    TERRITORIOS[id].puntos.forEach(function(p){
      todos.push(p);
      L.circleMarker(p, {
        radius:7, weight:2, fillOpacity:1,
        color:     tono('--acento'),
        fillColor: tono('--tinta')
      }).addTo(grupo).on('click', function(){ elegido = true; pintarDetalle(id) });
    });
    capas[id] = grupo;
  });
  /* Al abrir se ven los seis, que es de lo que habla la sección. Se vuela a
     uno sólo cuando alguien lo elige. */
  mapa.fitBounds(L.latLngBounds(todos).pad(0.18));
  caja.classList.add('listo');
}

function volar(id){
  var L = window.L; if (!L || !mapa) return;
  var ps = TERRITORIOS[id].puntos;
  var opciones = { duration: quieto.matches ? 0 : 1.1 };
  if (ps.length > 1) mapa.flyToBounds(L.latLngBounds(ps).pad(0.45), opciones);
  else mapa.flyTo(ps[0], 13, opciones);
}

/* ------------------------------------------------------------- arranque -- */

fetch('contenido/mapa.json')
  .then(function(r){ return r.json() })
  .then(function(j){
    datos = j;
    construirLista();
    pintarDetalle(ORDEN[0]);
    if (!('IntersectionObserver' in window)) return cargarMapa();
    var ojo = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if (!e.isIntersecting) return;
        ojo.unobserve(e.target);
        cargarMapa();
      });
    }, { rootMargin:'400px 0px' });
    ojo.observe(seccion);
  })
  .catch(function(){
    /* Sin el JSON la sección no tiene nada que decir: se saca del camino en
       vez de dejar un hueco. */
    seccion.hidden = true;
  });

function cargarMapa(){
  traer(LEAFLET_CSS, SRI_CSS, true)
    .then(function(){ return traer(LEAFLET_JS, SRI_JS, false) })
    .then(armarMapa)
    .catch(function(){ caja.classList.add('sin-mapa') });
}

})();
