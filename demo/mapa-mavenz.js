(function(){
const CSS = `
.mv-tiles{filter:grayscale(.85) invert(.92) sepia(.28) brightness(.78) contrast(1.02)}
.leaflet-container{background:#241718;font:12px Urbanist,sans-serif}
.mv-tip{background:#2a1b1c;color:#fff;border:1px solid rgba(183,161,138,.45);border-radius:999px;padding:4px 12px;font:600 12px Urbanist,sans-serif;letter-spacing:.02em;box-shadow:0 4px 14px rgba(0,0,0,.35)}
.mv-tip.mv-on{background:#b7a18a;color:#342223;border-color:#b7a18a}
.leaflet-tooltip-top:before{display:none}
.leaflet-control-attribution{background:rgba(36,23,24,.8)!important;color:#a1a7a8!important}
.leaflet-control-attribution a{color:#b7a18a!important}
.leaflet-bar a{background:#2a1b1c!important;color:#b7a18a!important;border-color:rgba(183,161,138,.3)!important}`;
const T = {
  micro:      {name:'Micro y Macrocentro',        points:[[-24.7883,-65.4106]], zoom:14},
  norte:      {name:'Zona Norte',                 points:[[-24.7180,-65.4045]], zoom:13},
  sanlorenzo: {name:'San Lorenzo',                points:[[-24.7339,-65.4863],[-24.7620,-65.4770]], zoom:13},
  aeropuerto: {name:'Zona Aeropuerto y San Luis', points:[[-24.8560,-65.4870]], zoom:13},
  cafayate:   {name:'Cafayate y Cachi',           points:[[-26.0730,-65.9764],[-25.1198,-66.1654]], zoom:11},
  vaqueros:   {name:'Vaqueros',                   points:[[-24.6897,-65.4054]], zoom:14}
};
class MapaMavenz extends HTMLElement {
  connectedCallback(){
    if(this._done) return; this._done = true;
    this.style.display='block'; if(!this.style.height) this.style.height='100%';
    if(!document.getElementById('mv-map-css')){
      const s=document.createElement('style'); s.id='mv-map-css'; s.textContent=CSS; document.head.appendChild(s);
    }
    this._init();
  }
  async _init(){
    let t=0; while(!window.L && t++<300) await new Promise(r=>setTimeout(r,50));
    if(!window.L || !this.isConnected) return;
    const el=document.createElement('div');
    el.style.cssText='width:100%;height:100%;background:#241718';
    this.appendChild(el);
    const map = this._map = L.map(el,{scrollWheelZoom:false});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors', className:'mv-tiles'}).addTo(map);
    const city=[]; this._tips={};
    Object.entries(T).forEach(([id,tr])=>{
      tr.points.forEach((p,i)=>{
        if(id!=='cafayate') city.push(p);
        const m=L.circleMarker(p,{radius:8,color:'#b7a18a',opacity:.25,weight:10,fillColor:'#b7a18a',fillOpacity:.95}).addTo(map);
        if(i===0){ m.bindTooltip(tr.name,{permanent:true,direction:'top',offset:[0,-10],className:'mv-tip'}); this._tips[id]=m; }
        m.on('click',()=>{ window.dispatchEvent(new CustomEvent('mavenz:territory',{detail:{id}})); this._go(id); });
      });
    });
    map.fitBounds(L.latLngBounds(city).pad(0.22));
    const tipVis=()=>{
      const z=map.getZoom();
      Object.values(this._tips).forEach(m=>{
        const el=m.getTooltip() && m.getTooltip().getElement();
        if(el) el.style.display = z>=12 ? '' : 'none';
      });
    };
    map.on('zoomend', tipVis);
    map.whenReady(tipVis);
    this._onFly = e=>this._go(e.detail.id);
    window.addEventListener('mavenz:flyto', this._onFly);
    this._ro = new ResizeObserver(()=>map.invalidateSize());
    this._ro.observe(this);
    setTimeout(()=>map.invalidateSize(),300);
  }
  _go(id){
    const tr=T[id]; if(!tr||!this._map) return;
    Object.entries(this._tips).forEach(([k,m])=>{
      const el=m.getTooltip() && m.getTooltip().getElement();
      if(el) el.classList.toggle('mv-on', k===id);
    });
    if(tr.points.length>1) this._map.flyToBounds(L.latLngBounds(tr.points).pad(0.4),{duration:1.3});
    else this._map.flyTo(tr.points[0], tr.zoom, {duration:1.3});
  }
  disconnectedCallback(){
    window.removeEventListener('mavenz:flyto', this._onFly);
    this._ro && this._ro.disconnect();
    this._map && this._map.remove();
  }
}
if(!customElements.get('mapa-mavenz')) customElements.define('mapa-mavenz', MapaMavenz);
})();
