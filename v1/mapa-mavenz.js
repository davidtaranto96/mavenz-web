(function(){
/* ==========================================================================
   <mapa-mavenz> — el Mapa Mavenz

   Claro y a color, con el relieve real de Salta abajo: la primera lectura
   tiene que ser "esto es mi provincia", no "esto es un mapa".

   Dos capas: sombreado de relieve (Esri, sin clave) abajo, y calles a color
   (CARTO Voyager, sin clave) arriba con opacidad, para que las montanas se
   sigan viendo a traves del callejero.
   ========================================================================== */

const CSS = `
.leaflet-container{background:#e9e4dd;font:12px Urbanist,system-ui,sans-serif}
.mv-calles{opacity:1}
/* El sombreado va ARRIBA del callejero, multiplicando: es como se compone un
   relieve en cartografia de verdad. Abajo y con opacidad no se ve nunca. */
.mv-relieve{ mix-blend-mode:multiply; opacity:.5; pointer-events:none }

/* ---- el pin: punto arena, aro que late hasta que lo tocan ---- */
.mv-pin{ cursor:pointer; background:none; border:0 }
.mv-pin i{
  position:absolute; left:50%; top:50%;
  width:16px; height:16px; margin:-8px 0 0 -8px;
  border-radius:999px;
  background:#8c6d4f;
  border:2.5px solid #fff;
  box-shadow:0 2px 8px rgba(42,27,28,.5);
  transition:transform .22s cubic-bezier(.16,1,.3,1), background .22s ease;
}
.mv-pin b{
  position:absolute; left:50%; top:50%;
  width:16px; height:16px; margin:-8px 0 0 -8px;
  border-radius:999px;
  border:2px solid #8c6d4f;
  opacity:0;
}
.mv-mapa:not(.mv-tocado) .mv-pin b{ animation:mvLate 2.6s cubic-bezier(.22,.61,.36,1) infinite }
@keyframes mvLate{
  0%   { transform:scale(1);   opacity:.75 }
  70%  { transform:scale(3.4); opacity:0 }
  100% { transform:scale(3.4); opacity:0 }
}
.mv-pin:hover i, .mv-pin:focus-visible i{ transform:scale(1.32); background:#3c2527 }
.mv-pin.mv-on i{ background:#3c2527; transform:scale(1.4) }

/* ---- la etiqueta ---- */
.mv-tip{
  background:#fffdfa; color:#3c2527;
  border:1px solid rgba(52,34,35,.18);
  border-radius:999px; padding:5px 13px;
  font:640 12.5px Urbanist,system-ui,sans-serif; letter-spacing:.01em;
  box-shadow:0 3px 12px rgba(42,27,28,.22);
  transition:background .22s ease, color .22s ease, border-color .22s ease;
}
.mv-tip.mv-on{ background:#3c2527; color:#fff; border-color:#3c2527 }
.leaflet-tooltip-top:before{ display:none }

/* ---- la invitacion a tocar ---- */
.mv-toca{
  position:absolute; left:50%; top:16px; z-index:700;
  transform:translateX(-50%);
  display:flex; align-items:center; gap:9px;
  padding:10px 18px;
  border-radius:999px;
  background:rgba(52,34,35,.9);
  -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);
  color:#fff;
  font:600 13px Urbanist,system-ui,sans-serif; letter-spacing:.012em;
  box-shadow:0 6px 22px rgba(20,10,11,.34);
  pointer-events:none;
  transition:opacity .4s ease, transform .4s cubic-bezier(.16,1,.3,1);
}
.mv-toca svg{ width:17px; height:17px; display:block }
.mv-mapa.mv-tocado .mv-toca{ opacity:0; transform:translateX(-50%) translateY(-9px) }

/* ---- controles y creditos, en el idioma de la marca ---- */
.leaflet-control-attribution{ background:rgba(255,253,250,.88)!important; color:#715d55!important; font-size:10.5px }
.leaflet-control-attribution a{ color:#8c6d4f!important }
.leaflet-bar a{
  background:#fffdfa!important; color:#3c2527!important;
  border-color:rgba(52,34,35,.16)!important;
  width:44px!important; height:44px!important; line-height:44px!important;
  font-size:19px!important;
}
.leaflet-bar a:hover{ background:#f2ece4!important }

@media (prefers-reduced-motion: reduce){
  .mv-mapa .mv-pin b{ animation:none!important }
}`;

const T = {
  micro:      {name:'Micro y Macrocentro',        points:[[-24.7883,-65.4106]], zoom:14},
  norte:      {name:'Zona Norte',                 points:[[-24.7180,-65.4045]], zoom:13},
  sanlorenzo: {name:'San Lorenzo',                points:[[-24.7339,-65.4863],[-24.7620,-65.4770]], zoom:13},
  aeropuerto: {name:'Zona Aeropuerto y San Luis', points:[[-24.8560,-65.4870]], zoom:13},
  cafayate:   {name:'Cafayate y Cachi',           points:[[-26.0730,-65.9764],[-25.1198,-66.1654]], zoom:11},
  vaqueros:   {name:'Vaqueros',                   points:[[-24.6897,-65.4054]], zoom:14}
};

const MANO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V11"/><path d="M12 11V4.5a1.5 1.5 0 0 1 3 0V11"/><path d="M15 11V6.5a1.5 1.5 0 0 1 3 0V13"/><path d="M9 11V9.5a1.5 1.5 0 0 0-3 0V14a7 7 0 0 0 7 7h1a7 7 0 0 0 7-7v-1"/></svg>';

class MapaMavenz extends HTMLElement {
  connectedCallback(){
    if(this._done) return; this._done = true;
    this.style.display='block';
    if(!this.style.height) this.style.height='100%';
    if(!document.getElementById('mv-map-css')){
      const s=document.createElement('style'); s.id='mv-map-css'; s.textContent=CSS;
      document.head.appendChild(s);
    }
    this._init();
  }

  async _init(){
    let t=0; while(!window.L && t++<300) await new Promise(r=>setTimeout(r,50));
    if(!window.L || !this.isConnected) return;

    const caja=document.createElement('div');
    caja.className='mv-mapa';
    caja.style.cssText='position:relative;width:100%;height:100%;background:#e9e4dd';
    this.appendChild(caja);

    const el=document.createElement('div');
    el.style.cssText='position:absolute;inset:0';
    caja.appendChild(el);

    const map = this._map = L.map(el,{scrollWheelZoom:false});

    // calles a color: la base
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      {maxZoom:19, className:'mv-calles',
       attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &middot; &copy; <a href="https://carto.com/attributions">CARTO</a>'}).addTo(map);
    // relieve encima, multiplicando: es lo que hace que se lea Salta y no "una ciudad"
    L.tileLayer('https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
      {maxZoom:16, className:'mv-relieve', attribution:'Relieve: Esri'}).addTo(map);

    const ciudad=[]; this._pins={}; this._tips={};
    Object.entries(T).forEach(([id,tr])=>{
      tr.points.forEach((p,i)=>{
        if(id!=='cafayate') ciudad.push(p);
        const icono = L.divIcon({className:'mv-pin', html:'<b></b><i></i>', iconSize:[26,26], iconAnchor:[13,13]});
        const m = L.marker(p,{icon:icono, keyboard:true, title:tr.name, alt:tr.name}).addTo(map);
        if(i===0){
          m.bindTooltip(tr.name,{permanent:true,direction:'top',offset:[0,-13],className:'mv-tip'});
          this._tips[id]=m;
          this._pins[id]=m;
        }
        m.on('click',()=>{
          window.dispatchEvent(new CustomEvent('mavenz:territory',{detail:{id}}));
          this._go(id);
        });
      });
    });

    map.fitBounds(L.latLngBounds(ciudad).pad(0.22));

    // la invitacion: se va sola en cuanto tocan algo
    const toca=document.createElement('div');
    toca.className='mv-toca';
    toca.innerHTML = MANO + '<span>Tocá un territorio</span>';
    caja.appendChild(toca);
    const tocado=()=>caja.classList.add('mv-tocado');
    ['pointerdown','wheel','keydown'].forEach(ev=>caja.addEventListener(ev,tocado,{passive:true,once:true}));
    window.addEventListener('mavenz:flyto',tocado,{once:true});
    setTimeout(tocado, 26000);

    const tipVis=()=>{
      const z=map.getZoom();
      Object.values(this._tips).forEach(m=>{
        const e=m.getTooltip() && m.getTooltip().getElement();
        if(e) e.style.display = z>=11 ? '' : 'none';
      });
    };
    map.on('zoomend', tipVis);
    map.whenReady(tipVis);

    this._onFly = e=>this._go(e.detail.id);
    window.addEventListener('mavenz:flyto', this._onFly);

    // el aro que late no gasta bateria fuera de pantalla
    if('IntersectionObserver' in window){
      this._io = new IntersectionObserver(es=>{
        caja.style.setProperty('--mv-play', es[0].isIntersecting ? 'running' : 'paused');
        caja.querySelectorAll('.mv-pin b').forEach(b=>{
          b.style.animationPlayState = es[0].isIntersecting ? '' : 'paused';
        });
      },{rootMargin:'120px'});
      this._io.observe(this);
    }

    this._ro = new ResizeObserver(()=>map.invalidateSize());
    this._ro.observe(this);
    setTimeout(()=>map.invalidateSize(),300);
  }

  _go(id){
    const tr=T[id]; if(!tr||!this._map) return;
    Object.entries(this._tips).forEach(([k,m])=>{
      const e=m.getTooltip() && m.getTooltip().getElement();
      if(e) e.classList.toggle('mv-on', k===id);
    });
    Object.entries(this._pins).forEach(([k,m])=>{
      const e=m.getElement();
      if(e) e.classList.toggle('mv-on', k===id);
    });
    if(tr.points.length>1) this._map.flyToBounds(L.latLngBounds(tr.points).pad(0.4),{duration:1.3});
    else this._map.flyTo(tr.points[0], tr.zoom, {duration:1.3});
  }

  disconnectedCallback(){
    window.removeEventListener('mavenz:flyto', this._onFly);
    this._ro && this._ro.disconnect();
    this._io && this._io.disconnect();
    this._map && this._map.remove();
  }
}
if(!customElements.get('mapa-mavenz')) customElements.define('mapa-mavenz', MapaMavenz);
})();
