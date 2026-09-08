#!/usr/bin/env python3
"""
armar.py — genera index.html (castellano) y en.html (inglés) desde contenido/.

    python3 armar.py

La regla de la casa: un dato vive en un solo lugar. Los HTML que quedan en el
repo son los HTML finales —se abren y se ve lo que ve la persona—, pero nunca se
editan a mano: se toca el JSON y se vuelve a correr esto. Cada región que sale
del JSON queda envuelta en <!--cms:nombre--> ... <!--/cms:nombre--> para que el
panel de edición de web-editable la pueda regenerar sola más adelante.

`sitio.en.json` es una capa sobre `sitio.json`: sólo lleva lo que cambia. Las
listas se reemplazan enteras, porque un menú traducido es un menú entero.

Sin dependencias. Python 3.8+.
"""
import hashlib
import json
import html as H
from pathlib import Path
from urllib.parse import quote

AQUI = Path(__file__).parent
ES = json.loads((AQUI / "contenido/sitio.json").read_text(encoding="utf-8"))
EN_CAPA = json.loads((AQUI / "contenido/sitio.en.json").read_text(encoding="utf-8"))

def version(archivo):
    """Ocho caracteres del hash del archivo. Van como `?v=` en el enlace: sin
    esto el navegador sirve el CSS viejo de cache y una correccion no se ve."""
    return hashlib.sha1((AQUI / archivo).read_bytes()).hexdigest()[:8]


def medio(ruta):
    """Lo mismo para los videos y sus posters: si se recorta un video y la URL
    no cambia, el navegador sigue mostrando el de antes."""
    try:
        return f"{ruta}?v={version(ruta)}"
    except OSError:
        return ruta


URL = "https://davidtaranto96.github.io/mavenz-web/demo/"
RAIZ = "https://davidtaranto96.github.io/mavenz-web/"


def fundir(base, encima):
    """Mezcla profunda: lo de `encima` pisa a lo de `base`, clave por clave.
    Las listas se reemplazan enteras."""
    if isinstance(base, dict) and isinstance(encima, dict):
        salida = dict(base)
        for k, v in encima.items():
            salida[k] = fundir(base.get(k), v) if k in base else v
        return salida
    return encima if encima is not None else base


def e(t):
    return H.escape(str(t), quote=True)


def cms(nombre, contenido):
    return f"<!--cms:{nombre}-->{contenido}<!--/cms:{nombre}-->"


def img(foto, sizes, clase="", lazy=True):
    """<img> con srcset por los anchos que existen en img/. El ancho y el alto
    reales van en los atributos para que el navegador reserve el lugar y la
    página no salte cuando carga la foto."""
    anchos = foto["anchos"]
    srcset = ", ".join(f'{foto["src"]}-{w}.webp {w}w' for w in anchos)
    carga = (' loading="lazy" decoding="async"' if lazy
             else ' fetchpriority="high" decoding="async"')
    c = f' class="{clase}"' if clase else ""
    return (f'<img{c} src="{foto["src"]}-{anchos[-1]}.webp" srcset="{srcset}" '
            f'sizes="{sizes}" alt="{e(foto["alt"])}" '
            f'width="{foto["ancho"]}" height="{foto["alto"]}"{carga}>')


def wa(d, texto):
    n = d["contacto_datos"]["whatsapp"]
    return f'https://wa.me/{n}?text={quote(texto)}' if n else "#contacto"


# El trazo de la marca: la M de Mavenz como una sola onda continua.
ONDA = ("M 40 296 C 44 148, 206 96, 302 178 C 382 246, 322 336, 240 302 "
        "C 168 272, 288 196, 516 258 C 642 292, 700 138, 832 158 "
        "C 936 174, 898 298, 1002 314 C 1082 326, 1142 300, 1178 272")


# La dirección con la que entra cada sección. Que no se repita seguida es
# justamente lo que separa un diseño de un plugin.
DIRECCION = {"quienes": "izq", "universo": "escala", "metodo": "der", "espacio": "arriba",
             "proyectos": "izq", "red": "escala", "equipo": "izq", "mirada": "der",
             "contacto": "arriba"}


def fx(seccion):
    return f' data-fx="reveal" data-fx-desde="{DIRECCION[seccion]}"'


def indice(d, puntos):
    """Una raya por seccion de ESTA pagina. El rotulo sale de aria-label, asi la
    version visual y la accesible son el mismo dato."""
    rayas = "".join(f'<a href="#{i}" aria-label="{e(t)}"></a>' for i, t in puntos)
    return (f'<nav class="indice" data-indice aria-label="{e(d["interfaz"]["indice"])}">'
            f'{rayas}</nav>')


def cabecera(d, lang, aqui):
    m, ui, c = d["marca"], d["interfaz"], d["contacto"]
    enlaces = "".join(
        f'<a href="{e(p["archivo"])}"{" aria-current=\"page\"" if k == aqui else ""}>'
        f'{e(p["rotulo"])}</a>'
        for k, p in d["paginas"].items())
    return f'''<header class="cabecera" data-cabecera>
  <a class="cabecera__marca" href="index.html" aria-label="{e(m["nombre"])}"><img class="cabecera__logo cabecera__logo--tinta" src="../img/logo-horizontal.webp" alt="{e(m["nombre"])}" width="800" height="216" loading="eager" decoding="async"><img class="cabecera__logo cabecera__logo--papel" src="../img/logo-horizontal-claro.webp" alt="" width="800" height="216" loading="eager" decoding="async" aria-hidden="true"></a>
  <nav class="cabecera__enlaces" aria-label="{e(ui["menu"])}">{enlaces}</nav>
  <div class="cabecera__derecha">
    <a class="boton cabecera__reunion" href="{e(wa(d, c["wa_reunion"]))}" target="_blank" rel="noopener">{e(c["cta_reunion"])}</a>
    <button class="hamburguesa" type="button" data-menu-boton aria-expanded="false" aria-controls="menu-celular" aria-label="{e(ui["menu"])}">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
<div class="panel" id="menu-celular" data-menu-panel>{enlaces}<a class="boton" href="{e(wa(d, c["wa_reunion"]))}" target="_blank" rel="noopener">{e(c["cta_reunion"])}</a></div>'''


def hero(d):
    h = d["hero"]
    ecos = "".join(
        f'<path d="{ONDA}" fill="none" stroke="var(--linea-acento)" stroke-width="1" '
        f'vector-effect="non-scaling-stroke" opacity="{op}" transform="translate(0,{dy})"/>'
        for op, dy in ((".45", 54), (".28", 104)))
    return f'''<section class="hero cortina-fondo" data-tema="oscuro">
  {img(h["foto"], "100vw", "hero__foto", lazy=False)}
  <div class="hero__velo"></div>
  <div class="hero__trazos" aria-hidden="true">
    <svg class="eco" viewBox="0 0 1200 400" preserveAspectRatio="none">{ecos}</svg>
    <svg viewBox="0 0 1200 400" preserveAspectRatio="none">
      <path class="trazo-vivo" pathLength="1" d="{ONDA}" fill="none" stroke="var(--sobre-foto)" stroke-width="2.4" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    </svg>
  </div>
  <div class="hero__pie">
    <p class="hero__leyenda">{e(h["foto"]["alt"])}</p>
    <ul class="muestras" aria-hidden="true"><li></li><li></li><li></li><li></li><li></li><li></li><li></li></ul>
  </div>
  <div class="hero__texto">
    <h1 class="hero__titulo" data-letras>{e(h["titulo"])}</h1>
    <p class="hero__bajada">{e(h["bajada"])}</p>
    <p class="hero__apoyo">{e(h["apoyo"])}</p>
    <div class="hero__acciones">
      <a class="boton boton--claro" href="{e(h["cta1"]["href"])}">{e(h["cta1"]["rotulo"])}</a>
      <a class="subrayado subrayado--claro" href="{e(h["cta2"]["href"])}">{e(h["cta2"]["rotulo"])}</a>
    </div>
  </div>
</section>'''


def quienes(d):
    q = d["quienes"]
    piezas = "".join(
        f'<figure class="pieza">{img(x["foto"], "(min-width:64rem) 26rem, 45vw")}'
        f'<figcaption class="ficha__epigrafe">{e(x["epigrafe"])}</figcaption></figure>'
        for x in q["piezas"])
    return f'''<section class="seccion" id="quienes"{fx("quienes")}>
  <p class="margen seccion__margen">{e(q["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["copy"])}</p>
  </div>
  <div class="quienes__cierre"><p class="cita" data-formar>{e(q["cierre"])}</p></div>
  <div class="piezas">
    <p class="margen piezas__rotulo">{e(q["piezas_rotulo"])}</p>
    <div class="piezas__par">{piezas}</div>
  </div>
</section>'''


def orbita(d):
    u = d["universo"]
    n = len(u["esferas"])
    nodos, paneles = [], []
    for i, sf in enumerate(u["esferas"]):
        # Repartidas sobre la circunferencia, arrancando arriba. El radio es 38 %
        # para que el rotulo no se coma el borde de la caja.
        import math
        ang = -math.pi / 2 + i * 2 * math.pi / n
        x, y = 50 + 38 * math.cos(ang), 50 + 38 * math.sin(ang)
        nodos.append(
            f'<button class="orbita__nodo" type="button" data-esfera="{sf["id"]}" '
            f'style="--x:{x:.2f}%;--y:{y:.2f}%" '
            f'aria-pressed="{"true" if i == 0 else "false"}">'
            f'<span class="orbita__punto" aria-hidden="true"></span>'
            f'<span class="orbita__n" aria-hidden="true">{e(sf["numero"])}</span>'
            f'<span class="orbita__nombre">{e(sf["nombre"])}</span></button>')
        paneles.append(
            f'<div class="orbita__panel" data-panel="{sf["id"]}" '
            f'aria-hidden="{"false" if i == 0 else "true"}">'
            f'<span class="orbita__panel-n" aria-hidden="true">({e(sf["numero"])})</span>'
            f'<h3>{e(sf["nombre"])}</h3><p>{e(sf["copy"])}</p></div>')
    a = u["anillo"]
    return f'''<section class="seccion universo" id="universo"{fx("universo")}>
  <div class="seccion__cabeza">
    <h2 class="titulo titulo--bordo" data-letras>{e(u["titulo"])}</h2>
    <p class="bajada">{e(u["intro"])}</p>
  </div>
  <div class="orbita" data-orbita style="--esferas:{n}">
    <svg class="orbita__dibujo" viewBox="0 0 100 100" aria-hidden="true">
      <circle class="orbita__anillo" data-anillo cx="50" cy="50" r="46" fill="none"
              stroke="var(--tinta-bordo)" stroke-width="1.4" vector-effect="non-scaling-stroke"/>
      <circle cx="50" cy="50" r="38" fill="none" stroke="var(--linea)"
              stroke-width="1" vector-effect="non-scaling-stroke"/>
    </svg>
    <p class="orbita__rotulo-anillo" aria-hidden="true">{e(a["nombre"])}</p>
    <div class="orbita__cara">{"".join(paneles)}</div>
    {"".join(nodos)}
  </div>
  <p class="orbita__anillo-copy"><strong>{e(a["nombre"])}.</strong> {e(a["copy"])}</p>
  <p class="orbita__ayuda">{e(u["ayuda"])}</p>
</section>'''


def mapa(d):
    """Los seis territorios del Mapa Mavenz. Es contenido de la clienta y está
    construido desde agosto: vuelve adentro del Universo, no como sección aparte."""
    mp = d["universo"]["mapa"]
    fichas = "".join(
        f'<details class="territorio" name="territorio" style="--n:{i}">'
        f'<summary class="territorio__cabeza">'
        f'<span class="territorio__n">{i + 1:02d}</span>'
        f'<span class="territorio__nombre">{e(t["nombre"])}</span>'
        f'<span class="territorio__bajada">{e(t["bajada"])}</span>'
        f'<span class="paso__signo" aria-hidden="true"></span></summary>'
        f'<div class="paso__cuerpo"><div><p>{e(t["cambia"])}</p>'
        f'<p class="territorio__quien"><span class="margen">{e(mp["rotulo_quien"])}</span> {e(t["quien"])}</p>'
        f'</div></div></details>'
        for i, t in enumerate(mp["territorios"]))
    return f'''<div class="mapa">
    <h3 class="mapa__titulo">{e(mp["titulo"])}</h3>
    <p class="mapa__intro">{e(mp["intro"])}</p>
    <div class="mapa__lista">{fichas}</div>
  </div>'''


def ciclo(d):
    import math
    m = d["metodo"]
    n = len(m["pasos"])
    nodos, cartas = [], []
    for i, p in enumerate(m["pasos"]):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        x, y = 50 + 36 * math.cos(ang), 50 + 36 * math.sin(ang)
        nodos.append(
            f'<button class="ciclo__nodo" type="button" data-paso="{i}" '
            f'style="--x:{x:.2f}%;--y:{y:.2f}%" '
            f'aria-pressed="{"true" if i == 0 else "false"}">'
            f'<span class="ciclo__punto" aria-hidden="true"></span>'
            f'<span class="ciclo__rotulo">{e(p["nombre"])}</span></button>')
        cartas.append(
            f'<article class="ciclo__carta" data-carta="{i}" '
            f'aria-hidden="{"false" if i == 0 else "true"}">'
            f'<span class="ciclo__n">{e(p["numero"])}</span>'
            f'<h3>{e(p["nombre"])}</h3><p>{e(p["copy"])}</p></article>')
    return f'''<section class="seccion ciclo-seccion" id="metodo"{fx("metodo")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <div class="ciclo" data-ciclo style="--pasos:{n}">
    <svg class="ciclo__dibujo" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="36" fill="none" stroke="var(--linea)"
              stroke-width="1" vector-effect="non-scaling-stroke"/>
      <circle class="ciclo__avance" data-avance cx="50" cy="50" r="36" fill="none"
              stroke="var(--tinta-bordo)" stroke-width="1.6" stroke-linecap="round"
              vector-effect="non-scaling-stroke" transform="rotate(-90 50 50)"/>
    </svg>
    <div class="ciclo__centro">{"".join(cartas)}</div>
    {"".join(nodos)}
  </div>
  <p class="ciclo__cierre">{e(m["cierre"])}</p>
</section>'''


def espacio(d):
    """A sangre y sobre una aérea quieta: es la sección que rompe la seguidilla
    de papel, y de paso existe visualmente aunque falte la foto del lugar."""
    x = d["espacio"]
    return f'''<section class="seccion adentro" id="espacio-bloque"{fx("espacio")}>
  {img(x["fondo"], "100vw", "sangre__fondo")}
  <div class="sangre__velo"></div>
  <div class="sangre__interior">
    <p class="margen margen--claro">{e(x["margen"])}</p>
    <div class="seccion__cabeza">
      <h2 class="titulo titulo--claro" data-letras>{e(x["titulo"])}</h2>
      <div>
        <p class="bajada bajada--clara">{e(x["copy"])}</p>
        <p class="espacio__nota">{e(x["nota"])}</p>
        <a class="subrayado subrayado--claro espacio__cta" href="{e(x["cta"]["href"])}" target="_blank" rel="noopener">{e(x["cta"]["rotulo"])}</a>
      </div>
    </div>
    <div class="hueco hueco--claro espacio__hueco">
      <p class="hueco__rotulo">{e(x["hueco"]["rotulo"])}</p>
      <p class="hueco__texto">{e(x["hueco"]["texto"])}</p>
    </div>
  </div>
</section>'''


def proyectos(d):
    p, ui = d["proyectos"], d["interfaz"]
    dest = p["destacado"]
    fichas = []
    for i, f in enumerate(p["estante"]):
        if f.get("solo_visor"):       # está en el visor, no en la grilla
            continue
        velo = ""
        if f.get("velo"):
            velo = ('<span class="ficha__velo"></span>'
                    f'<span class="ficha__sobretexto">{e(f["velo"])}</span>')
        # La foto abre el visor: en el celular las fichas son estampillas de 236 px.
        fichas.append(
            f'<figure class="ficha{" ficha--bn" if f.get("bn") else ""}" '
            f'style="--cols:{f["columnas"]};--prop:{f["proporcion"]}">'
            f'<button class="ficha__abrir" type="button" data-foto="{i + 1}" '
            f'aria-label="{e(ui["abrir_foto"])}: {e(f["epigrafe"])}">'
            f'{img(f["foto"], "(min-width:64rem) 34rem, 15rem")}{velo}</button>'
            f'<figcaption class="ficha__epigrafe">{e(f["epigrafe"])}</figcaption></figure>')
    h = p["hueco"]
    fichas.append(
        f'<figure class="ficha" style="--cols:{h["columnas"]};--prop:{h["proporcion"]}">'
        f'<div class="hueco ficha__hueco"><p class="hueco__texto">{e(h["texto"])}</p></div>'
        f'<figcaption class="ficha__epigrafe">{e(h["epigrafe"])}</figcaption></figure>')
    return f'''<section class="seccion adentro" id="proyectos-bloque"{fx("proyectos")}>
  <p class="margen seccion__margen">{e(p["margen"])}</p>
  <div class="seccion__cabeza seccion__cabeza--pie">
    <h2 class="titulo" data-letras>{e(p["titulo"])}</h2>
    <p class="bajada">{e(p["intro"])}</p>
  </div>
  <article class="proyecto">
    <video class="proyecto__fondo" data-diferido data-pesado="1" data-src="{e(medio(dest["fondo"]["src"]))}" poster="{e(medio(dest["fondo"]["poster"]))}" muted loop playsinline preload="none" aria-hidden="true"></video>
    <button class="proyecto__abrir" type="button" data-foto="0" aria-label="{e(ui["abrir_foto"])}: {e(dest["nombre"])}">
      {img(dest["foto"], "(min-width:64rem) 76vw, 100vw", "proyecto__foto")}
    </button>
    <div class="proyecto__velo"></div>
    <p class="proyecto__rotulo">{e(dest["rotulo_foto"])}</p>
    <div class="proyecto__pie">
      <h3 class="proyecto__nombre">{e(dest["nombre"])}</h3>
      <p class="proyecto__meta">{e(dest["meta"])}</p>
      <a class="subrayado subrayado--claro" href="{e(dest["href"])}">{e(dest["cta"])}</a>
    </div>
  </article>
  <div class="fijado" data-fijado><div class="estante">{"".join(fichas)}</div></div>
</section>'''


def cardenal(d):
    """La pieza animada de Fractura: el ave se dibuja, se posa sobre la M del
    isotipo y cierra con la frase de ellos. Arranca al entrar en vista, una vez."""
    v = d["proyectos"]["destacado"]["video"]
    return f'''<figure class="cardenal" data-cardenal>
    <video class="cardenal__video" data-diferido data-src="{e(medio(v["src"]))}" poster="{e(medio(v["poster"]))}"
           muted playsinline preload="none" aria-label="{e(v["rotulo"])}"></video>
    <figcaption class="cardenal__texto">
      <p class="margen">{e(v["rotulo"])}</p>
      <p class="cardenal__copy">{e(v["copy"])}</p>
      <p class="cardenal__cierre">{e(v["cierre"])}</p>
    </figcaption>
  </figure>'''


def otros(d):
    """Porto y WA. Pendientes de confirmar con Vero: en el tablero marcó que
    entra sólo CARDINAL, y estos son de Grupo MDay."""
    p = d["proyectos"]
    fichas = "".join(
        f'<article class="otro">'
        f'<div class="otro__marco">{img(x["foto"], "(min-width:64rem) 34rem, 90vw")}</div>'
        f'<h3 class="otro__nombre">{e(x["nombre"])}</h3>'
        f'<p class="otro__meta">{e(x["meta"])}</p>'
        f'<p class="otro__copy">{e(x["copy"])}</p></article>'
        for x in p["otros"])
    return f'''<div class="otros">
    <p class="margen otros__rotulo">{e(p["otros_rotulo"])}</p>
    <div class="otros__par">{fichas}</div>
  </div>'''


def visor(d):
    """Lightbox de las fotos del proyecto. El swipe lo hace el navegador dentro
    de un carril con scroll-snap: la inercia y el frenado son los del sistema."""
    p, ui = d["proyectos"], d["interfaz"]
    todas = [p["destacado"]["foto"]] + [f["foto"] for f in p["estante"]]
    epis = [p["destacado"]["nombre"]] + [f["epigrafe"] for f in p["estante"]]
    laminas = "".join(
        f'<figure class="visor__lamina" data-lamina="{i}">'
        f'{img(f, "100vw")}'
        f'<figcaption>{e(t)}</figcaption></figure>'
        for i, (f, t) in enumerate(zip(todas, epis)))
    return f'''<dialog class="visor" data-visor aria-label="{e(p["destacado"]["nombre"])}">
    <button class="visor__cerrar" type="button" data-visor-cerrar aria-label="{e(ui["cerrar"])}">
      <span aria-hidden="true">&times;</span>
    </button>
    <div class="visor__pista" data-visor-pista>{laminas}</div>
  </dialog>'''


def red(d):
    """A sangre en tinta bordó. Es la otra que sale del papel: la que habla de
    gente, no de lugar, así las dos oscuras no se leen igual."""
    r = d["red"]
    nodos = "".join(
        f'<p class="red__nodo" data-peso="{n["peso"]}" '
        f'style="--x:{n["x"]}%;--y:{n["y"]}%;--sangria:{n["sangria"]}px">{e(n["nombre"])}</p>'
        for n in r["nodos"])
    return f'''<section class="sangre sangre--bordo red" id="red" data-tema="oscuro"{fx("red")}>
  <div class="sangre__interior">
    <h2 class="titulo titulo--claro" data-letras>{e(r["titulo"])}</h2>
    <p class="bajada bajada--clara bajada--angosta">{e(r["copy"])}</p>
    <div class="red__nube">{nodos}</div>
    <p class="cita cita--clara red__cierre">{e(r["cierre"])}</p>
  </div>
</section>'''


def mirada(d):
    m = d["mirada"]
    return f'''<section class="seccion" id="mirada"{fx("mirada")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <div class="mirada__hueco"><p>{e(m["hueco"])}</p></div>
</section>'''


def equipo(d):
    """Las dos que están detrás. Los retratos no existen todavía: el hueco queda
    a la vista, igual que en Espacio Mavenz, para que se vea qué falta."""
    q = d["equipo"]
    personas = "".join(
        f'<article class="persona">'
        f'<div class="hueco persona__hueco"><p class="hueco__rotulo">{e(x["hueco"])}</p></div>'
        f'<h3 class="persona__nombre">{e(x["nombre"])}</h3>'
        f'<p class="persona__rol">{e(x["rol"])}</p>'
        + (f'<p class="persona__linea">{e(x["linea"])}</p>' if x["linea"] else '')
        + '</article>'
        for x in q["personas"])
    return f'''<section class="seccion" id="equipo"{fx("equipo")}>
  <p class="margen seccion__margen">{e(q["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["intro"])}</p>
  </div>
  <div class="personas">{personas}</div>
</section>'''


def banda(d):
    """Corte panorámico a sangre entre dos bloques. El póster va primero y el
    video entra diferido: sin esto se baja 119 KB que nadie pidió todavía."""
    b = d["banda"]
    return (f'<div class="banda" aria-hidden="true">'
            f'<video class="banda__video" data-diferido data-src="{medio(b["src"])}" '
            f'poster="{medio(b["poster"])}" muted loop playsinline preload="none"></video></div>')


def contacto(d):
    c, cd = d["contacto"], d["contacto_datos"]
    correo = (f'<a class="subrayado subrayado--tenue" href="mailto:{e(cd["correo"])}">'
              f'{e(cd["correo"])}</a>' if cd["correo"] else "")
    solapas = "".join(
        f'<button class="solapa" type="button" data-solapa="{s_["id"]}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{e(s_["rotulo"])}</button>'
        for i, s_ in enumerate(c["solapas"]))
    cuerpos = "".join(
        f'<div class="solapa__cuerpo" data-cuerpo="{s_["id"]}" '
        f'aria-hidden="{"false" if i == 0 else "true"}">'
        f'<p>{e(s_["copy"])}</p>'
        f'<a class="boton" href="{e(wa(d, s_["rotulo"] + ". "))}" target="_blank" '
        f'rel="noopener">{e(c["cta_wa"])}</a></div>'
        for i, s_ in enumerate(c["solapas"]))
    motivos = "".join(
        f'<li><a class="subrayado subrayado--bordo" href="{e(wa(d, m["wa"]))}" '
        f'target="_blank" rel="noopener">{e(m["rotulo"])}</a></li>'
        for m in c["motivos"])
    return f'''<section class="seccion--ancha contacto" id="contacto"{fx("contacto")}>
  <p class="contacto__palabra" aria-hidden="true" data-palabra>{e(c["palabra"])}</p>
  <div class="contacto__caja">
    <div class="contacto__datos">
      <p class="contacto__apertura">{e(c["apertura"])}</p>
      <h2 class="contacto__titulo" data-letras>{e(c["titulo"])}</h2>
      <p class="margen">{e(c["bloque_datos"])}</p>
      <ul class="contacto__lista">
        <li><a class="subrayado" href="{e(wa(d, c["wa_general"]))}" target="_blank" rel="noopener">WhatsApp</a></li>
        <li>{correo}</li>
      </ul>
    </div>
    <div class="contacto__panel">
      <div class="solapas" role="group">{solapas}</div>
      {cuerpos}
      <div class="motivos">
        <p class="margen motivos__rotulo">{e(c["rotulo_motivos"])}</p>
        <ul class="motivos__lista">{motivos}</ul>
      </div>
    </div>
  </div>
</section>'''


def pie(d, lang):
    m = d["marca"]
    paginas = "".join(f'<a href="{e(p["archivo"])}">{e(p["rotulo"])}</a>'
                      for p in d["paginas"].values())
    redes = "".join(
        (f'<a href="{e(r["href"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>'
         if r["href"] else f'<span>{e(r["nombre"])}</span>')
        for r in d["redes"])
    return f'''<footer class="pie" data-tema="claro">
  <img class="pie__iso" src="../img/isotipo.webp" alt="{e(m["nombre"])}" width="600" height="381" loading="lazy" decoding="async">
  <nav class="pie__redes" aria-label="{e(m["nombre"])}">{redes}</nav>
  <div class="pie__abajo">
    <p class="pie__lugar">{e(m["lugar"])}</p>
    <nav class="pie__paginas" aria-label="{e(d["interfaz"]["menu"])}">{paginas}</nav>
  </div>
</footer>'''


def datos_estructurados(d):
    """Ficha de la organización para Google. Sólo lo que está confirmado: el
    correo y el WhatsApp quedan afuera hasta que Vero los confirme."""
    m = d["marca"]
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": m["nombre"],
        "url": URL,
        "description": m["definicion"],
        "logo": f"{RAIZ}img/logo-horizontal.webp",
        "address": {"@type": "PostalAddress", "addressLocality": "Salta",
                    "addressRegion": "Salta", "addressCountry": "AR"},
        "areaServed": {"@type": "AdministrativeArea", "name": "Salta, Argentina"},
    }


# --------------------------------------------------------------------------- #

def cascara(d, lang, slug, cuerpo, puntos):
    """El head, la cabecera y el pie son los mismos en las tres paginas. Se
    escriben una sola vez o se desincronizan: es el bug que mas caro sale."""
    m, ui, pg = d["marca"], d["interfaz"], d["paginas"][slug]
    titulo = f'{pg["titulo"]} — {m["nombre"]}' if slug != "inicio" else f'{m["nombre"]} — {m["mensaje"]}'
    canonica = URL + ("" if slug == "inicio" else pg["archivo"])
    return f'''<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(m["definicion"])} {e(d["hero"]["apoyo"])}">
<meta name="theme-color" content="#eeecec">
<link rel="canonical" href="{canonica}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_AR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(m["definicion"])}">
<meta property="og:image" content="{RAIZ}img/aerea-dia-1600.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.png">
<link rel="preload" href="../fuente/urbanist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../img/logo-horizontal-claro.webp" as="image" type="image/webp">
<link rel="stylesheet" href="estilos.css?v={version("estilos.css")}">
<script type="application/ld+json">{json.dumps(datos_estructurados(d), ensure_ascii=False)}</script>
</head>
<body data-pagina="{slug}">
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cms("cabecera", cabecera(d, lang, slug))}
<main class="contenido" id="contenido">
{cuerpo}
</main>
{cms("pie", pie(d, lang))}
{indice(d, puntos)}
<a class="wa" data-wa href="{e(wa(d, d["contacto"]["wa_general"]))}" target="_blank" rel="noopener" aria-label="{e(ui["whatsapp"])}">
  <span class="wa__punto" aria-hidden="true"></span>{e(ui["whatsapp"])}
</a>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.11/dist/lenis.min.js" defer></script>
<script src="guion.js?v={version("guion.js")}" defer></script>
</body>
</html>
'''


def pagina_inicio(d):
    """El relato. El trazo se dibuja, se cierra en orbita, se aprieta en ciclo
    y se abre en los cuatro mundos."""
    cuerpo = f'''{cms("hero", hero(d))}
<div class="dossier cortina-tapa" data-tema="claro"><div class="dossier__interior">
{cms("quienes", quienes(d))}
{cms("universo", orbita(d))}
{cms("metodo", ciclo(d))}
</div></div>
{cms("banda", banda(d))}
{cms("mundos", mundos(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("contacto", contacto(d))}
</div></div>'''
    puntos = [("quienes", d["quienes"]["titulo"]), ("universo", d["universo"]["titulo"]),
              ("metodo", d["metodo"]["titulo"]), ("mundos", d["mundos"]["rotulo"]),
              ("contacto", d["contacto"]["titulo"])]
    return cascara(d, "es", "inicio", cuerpo, puntos)


def pagina_about(d):
    """Quienes son. Lo que falta se muestra como hueco, no se disimula."""
    pg = d["paginas"]["about"]
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("quienes", quienes(d))}
{cms("equipo", equipo(d))}
{cms("mirada", mirada(d))}
</div></div>
{cms("red", red(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("contacto", contacto(d))}
</div></div>'''
    puntos = [("quienes", d["quienes"]["titulo"]), ("equipo", d["equipo"]["titulo"]),
              ("mirada", d["mirada"]["titulo"]), ("red", d["red"]["titulo"]),
              ("contacto", d["contacto"]["titulo"])]
    return cascara(d, "es", "about", cuerpo, puntos)


def pagina_proyectos(d):
    """Cada proyecto es un mundo de color entero, y del ultimo se vuelve al
    primero. Es literal lo que pidio Vero: que sea un loop."""
    pg, lista = d["paginas"]["proyectos"], d["mundos"]["lista"]
    # Lo que va adentro de cada mundo. Son las secciones que ya existian: no se
    # reescribe contenido, se lo mete en su color.
    dentro = {"cardinal":    proyectos(d) + cardenal(d),
              "desarrollos": otros(d),
              "espacio":     espacio(d),
              "territorio":  mapa(d)}
    n = len(lista)
    bloques = "".join(
        mundo_pleno(w, i, n, dentro[w["id"]], lista[(i + 1) % n]["id"])
        for i, w in enumerate(lista))
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
<div class="riel" data-riel>{bloques}</div>
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("contacto", contacto(d))}
</div></div>
{visor(d)}'''
    puntos = [(w["id"], w["nombre"]) for w in lista] + [("contacto", d["contacto"]["titulo"])]
    return cascara(d, "es", "proyectos", cuerpo, puntos)


def cinta(texto, tono="tinta", titulo=False):
    """El nombre de la seccion en cinta gigante. La repeticion es decorativa:
    la primera copia es el texto de verdad, el resto va aria-hidden.

    Con titulo=True la cinta ES el encabezado de la seccion. Sin esto un mundo
    entero queda sin h2: se rompe el indice del documento y el lector de
    pantalla no tiene por donde entrar."""
    et = "h2" if titulo else "span"
    copias = f'<{et} class="cinta__pieza">{e(texto)}</{et}>' + "".join(
        f'<span class="cinta__pieza" aria-hidden="true">{e(texto)}</span>'
        for _ in range(3))
    return (f'<div class="cinta cinta--{tono}" data-cinta>'
            f'<div class="cinta__riel" data-cinta-riel>{copias}</div></div>')


def mundos(d):
    w = d["mundos"]
    paneles = "".join(
        f'<a class="mundo" href="{e(x["href"])}" data-tinta="{e(x["tinta"])}" '
        f'style="--i:{i}">'
        f'<span class="mundo__marca" aria-hidden="true">M</span>'
        f'<span class="mundo__nombre">{e(x["nombre"])}</span>'
        f'<span class="mundo__bajada">{e(x["bajada"])}</span>'
        f'<span class="mundo__cierre">{e(x["cierre"])}<span aria-hidden="true"> &#8594;</span></span>'
        f'</a>'
        for i, x in enumerate(w["lista"]))
    return f'''<section class="seccion seccion--ancha mundos-seccion" id="mundos"{fx("proyectos")}>
  <p class="margen">{e(w["rotulo"])}</p>
  <div class="mundos">{paneles}</div>
  <p class="mundos__ayuda">{e(w["ayuda"])}</p>
</section>'''


DESDE_MUNDO = ("escala", "izq", "der", "arriba")


def mundo_pleno(w, i, total, cuerpo, siguiente):
    paso = f'{i + 1:02d} / {total:02d}'
    salto = (f'<a class="mundo-pleno__next" href="#{siguiente}">'
             f'<span class="mundo-pleno__next-r">{e(paso)}</span>'
             f'<span class="mundo-pleno__next-t">Siguiente'
             f'<span aria-hidden="true"> &#8595;</span></span></a>')
    return f'''<section class="mundo-pleno" id="{w["id"]}" data-tinta="{e(w["tinta"])}"
         data-tema="oscuro" data-mundo="{i}"
         data-fx="reveal" data-fx-desde="{DESDE_MUNDO[i % len(DESDE_MUNDO)]}">
  {cinta(w["nombre"], "papel", titulo=True)}
  <div class="mundo-pleno__interior">
    <p class="mundo-pleno__bajada">{e(w["bajada"])}</p>
    {cuerpo}
  </div>
  {salto}
</section>'''


def main():
    # Solo castellano por ahora: el copy en ingles lo debe la clienta.
    # fundir() y sitio.en.json siguen en pie para cuando llegue.
    for slug, armar in (("inicio", pagina_inicio), ("about", pagina_about),
                        ("proyectos", pagina_proyectos)):
        archivo = ES["paginas"][slug]["archivo"]
        (AQUI / archivo).write_text(armar(ES), encoding="utf-8")
        print(f"{archivo} armado")


if __name__ == "__main__":
    main()


