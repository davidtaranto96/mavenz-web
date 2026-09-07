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

# Los siete vértices del heptagrama, en porcentaje de la caja de la rueda.
# Radio 42 % desde el centro; el primero arriba y de ahí cada 360/7 grados.
VERTICES = [(50.00, 8.00), (82.84, 23.81), (90.95, 59.35), (68.22, 87.84),
            (31.78, 87.84), (9.05, 59.35), (17.16, 23.81)]


# La dirección con la que entra cada sección. Que no se repita seguida es
# justamente lo que separa un diseño de un plugin.
DIRECCION = {"quienes": "izq", "universo": "escala", "metodo": "der", "espacio": "arriba",
             "proyectos": "izq", "red": "escala", "equipo": "izq", "mirada": "der",
             "contacto": "arriba"}


def fx(seccion):
    return f' data-fx="reveal" data-fx-desde="{DIRECCION[seccion]}"'


def poligono(orden, opacidad):
    pts = " ".join(f"{VERTICES[i][0]},{VERTICES[i][1]}" for i in orden)
    return (f'<polygon points="{pts}" fill="none" stroke="var(--linea-acento)" '
            f'stroke-width="1" vector-effect="non-scaling-stroke" opacity="{opacidad}"/>')


# --------------------------------------------------------------------------- #
# Secciones
# --------------------------------------------------------------------------- #

def selector_idioma(d, lang):
    """El idioma en el que estás es texto; el otro es un enlace de verdad."""
    idi = d["idiomas"]
    otro = "en" if lang == "es" else "es"
    return (f'<span class="idioma">'
            f'<span class="idioma__on">{e(idi[lang]["rotulo"])}</span>'
            f'<span class="idioma__sep" aria-hidden="true">/</span>'
            f'<a class="idioma__off" href="{e(idi[otro]["href"])}" '
            f'hreflang="{e(idi[otro]["lang"])}" lang="{e(idi[otro]["lang"])}">'
            f'{e(idi[otro]["rotulo"])}</a></span>')


def indice(d):
    """Una raya por sección al costado. El rótulo sale de aria-label, así la
    versión visual y la accesible son el mismo dato."""
    puntos = ([("quienes", d["quienes"]["titulo"])]
              + [(x["id"], x["rotulo"]) for x in d["menu"]]
              + [("equipo", d["equipo"]["titulo"]), ("contacto", d["contacto"]["titulo"])])
    rayas = "".join(f'<a href="#{i}" aria-label="{e(t)}"></a>' for i, t in puntos)
    return f'<nav class="indice" data-indice aria-label="{e(d["interfaz"]["indice"])}">{rayas}</nav>'


def cabecera(d, lang):
    m, ui, c = d["marca"], d["interfaz"], d["contacto"]
    enlaces = "".join(f'<a href="#{s["id"]}">{e(s["rotulo"])}</a>' for s in d["menu"])
    return f'''<header class="cabecera" data-cabecera>
  <a class="cabecera__marca" href="#contenido" aria-label="{e(m["nombre"])}"><img class="cabecera__logo cabecera__logo--tinta" src="../img/logo-horizontal.webp" alt="{e(m["nombre"])}" width="800" height="216" loading="eager" decoding="async"><img class="cabecera__logo cabecera__logo--papel" src="../img/logo-horizontal-claro.webp" alt="" width="800" height="216" loading="eager" decoding="async" aria-hidden="true"></a>
  <nav class="cabecera__enlaces" aria-label="{e(ui["menu"])}">{enlaces}</nav>
  <div class="cabecera__derecha">
    {selector_idioma(d, lang)}
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


def universo(d):
    u = d["universo"]
    nodos, paneles = [], []
    for i, s in enumerate(u["esferas"]):
        x, y = VERTICES[i]
        tenue = "" if s["destacada"] else " data-tenue"
        primero = i == 0
        nodos.append(
            f'<button class="rueda__nodo" type="button" data-cap="{s["id"]}"{tenue} '
            f'style="--x:{x}%;--y:{y}%" aria-label="{e(s["nombre"])}" '
            f'aria-pressed="{"true" if primero else "false"}">'
            f'<span class="rueda__punto" aria-hidden="true"></span>'
            f'<span class="rueda__nombre">{e(s["nombre"])}</span></button>')
        paneles.append(
            f'<div class="rueda__panel" data-panel="{s["id"]}" aria-hidden="{"false" if primero else "true"}">'
            f'<h3>{e(s["nombre"])}</h3><p>{e(s["copy"])}</p></div>')
    return f'''<section class="seccion" id="universo"{fx("universo")}>
  <h2 class="titulo titulo--bordo" data-letras>{e(u["titulo"])}</h2>
  <p class="bajada bajada--angosta">{e(u["intro"])}</p>
  <div class="rueda" data-rueda>
    <svg class="rueda__dibujo" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="42" fill="none" stroke="var(--linea)" stroke-width="1" vector-effect="non-scaling-stroke"/>
      {poligono([0, 2, 4, 6, 1, 3, 5], ".55")}
      {poligono([0, 3, 6, 2, 5, 1, 4], ".34")}
    </svg>
    <div class="rueda__ficha">
      <div class="rueda__capa rueda__capa--2" aria-hidden="true"></div>
      <div class="rueda__capa rueda__capa--1" aria-hidden="true"></div>
      <div class="rueda__cara">{"".join(paneles)}</div>
    </div>
    {"".join(nodos)}
  </div>
  <p class="rueda__ayuda">{e(u["ayuda"])}</p>
  {mapa(d)}
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


def metodo(d):
    m = d["metodo"]
    nodos = "".join(
        f'<div class="metodo__nodo" style="--x:{p["x"]}%;--y:{p["y"]}%"'
        f'{" data-arriba" if p["arriba"] else ""}><span>{e(p["nombre"])}</span></div>'
        for p in m["pasos"])
    cartas = "".join(
        f'<article class="carta"><span class="carta__n">{i + 1:02d}</span>'
        f'<h3 class="carta__nombre">{e(p["nombre"])}</h3>'
        f'<p class="carta__copy">{e(p["copy"])}</p></article>'
        for i, p in enumerate(m["pasos"]))
    lista = (f'<div class="lateral" data-lateral style="--pasos:{len(m["pasos"])}">'
             f'<div class="lateral__pin"><div class="lateral__carril" data-carril>{cartas}</div></div></div>')
    return f'''<section class="seccion" id="metodo"{fx("metodo")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <div class="metodo__trazo">
    <svg viewBox="0 0 1200 400" preserveAspectRatio="none" aria-hidden="true">
      <path d="{ONDA}" fill="none" stroke="var(--tinta-bordo)" stroke-width="1.6" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    </svg>
    {nodos}
  </div>
  {lista}
</section>'''


def espacio(d):
    """A sangre y sobre una aérea quieta: es la sección que rompe la seguidilla
    de papel, y de paso existe visualmente aunque falte la foto del lugar."""
    x = d["espacio"]
    return f'''<section class="sangre" id="espacio" data-tema="oscuro"{fx("espacio")}>
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
    return f'''<section class="seccion" id="proyectos"{fx("proyectos")}>
  <p class="margen seccion__margen">{e(p["margen"])}</p>
  <div class="seccion__cabeza seccion__cabeza--pie">
    <h2 class="titulo" data-letras>{e(p["titulo"])}</h2>
    <p class="bajada">{e(p["intro"])}</p>
  </div>
  <article class="proyecto">
    <video class="proyecto__fondo" data-diferido data-src="{e(medio(dest["fondo"]["src"]))}" poster="{e(medio(dest["fondo"]["poster"]))}" muted loop playsinline preload="none" aria-hidden="true"></video>
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
  <div class="estante">{"".join(fichas)}</div>
  {cardenal(d)}
  {otros(d)}
  {visor(d)}
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
    correo = (f'<a class="subrayado subrayado--tenue" href="mailto:{e(cd["correo"])}">{e(cd["correo"])}</a>'
              if cd["correo"] else "")
    motivos = "".join(
        f'<li><a class="subrayado subrayado--bordo" href="{e(wa(d, m["wa"]))}" '
        f'target="_blank" rel="noopener">{e(m["rotulo"])}</a></li>'
        for m in c["motivos"])
    return f'''<section class="seccion contacto" id="contacto"{fx("contacto")}>
  <p class="contacto__apertura">{e(c["apertura"])}</p>
  <h2 class="contacto__titulo" data-letras>{e(c["titulo"])}</h2>
  <div class="motivos">
    <p class="margen motivos__rotulo">{e(c["rotulo_motivos"])}</p>
    <ul class="motivos__lista">{motivos}</ul>
  </div>
  <div class="contacto__acciones">
    <a class="boton" href="{e(wa(d, c["wa_reunion"]))}" target="_blank" rel="noopener">{e(c["cta_reunion"])}</a>
    <a class="subrayado" href="{e(wa(d, c["wa_general"]))}" target="_blank" rel="noopener">{e(c["cta_wa"])}</a>
    {correo}
  </div>
</section>'''


def pie(d, lang):
    m = d["marca"]
    redes = "".join(
        (f'<a href="{e(r["href"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>'
         if r["href"] else f'<span>{e(r["nombre"])}</span>')
        for r in d["redes"])
    return f'''<footer class="pie" data-tema="claro">
  <img class="pie__iso" src="../img/isotipo.webp" alt="{e(m["nombre"])}" width="600" height="381" loading="lazy" decoding="async">
  <nav class="pie__redes" aria-label="{e(m["nombre"])}">{redes}</nav>
  <div class="pie__abajo">
    <p class="pie__lugar">{e(m["lugar"])}</p>
    {selector_idioma(d, lang)}
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

def pagina(d, lang):
    m, ui, idi = d["marca"], d["interfaz"], d["idiomas"]
    titulo = f'{m["nombre"]} — {m["mensaje"]}'
    canonica = URL if lang == "es" else URL + idi["en"]["href"]
    return f'''<!DOCTYPE html>
<html lang="{e(idi[lang]["lang"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(m["definicion"])} {e(d["hero"]["apoyo"])}">
<meta name="theme-color" content="#eeecec">
<link rel="canonical" href="{canonica}">
<link rel="alternate" hreflang="es-AR" href="{URL}">
<link rel="alternate" hreflang="en" href="{URL}{idi["en"]["href"]}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{e(idi[lang]["og"])}">
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
<body>
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cms("cabecera", cabecera(d, lang))}
<main class="contenido" id="contenido">
{cms("hero", hero(d))}
<div class="dossier cortina-tapa" data-tema="claro"><div class="dossier__interior">
{cms("quienes", quienes(d))}
{cms("universo", universo(d))}
{cms("metodo", metodo(d))}
</div></div>
{cms("banda", banda(d))}
{cms("espacio", espacio(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("proyectos", proyectos(d))}
</div></div>
{cms("red", red(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("equipo", equipo(d))}
{cms("mirada", mirada(d))}
{cms("contacto", contacto(d))}
</div></div>
</main>
{cms("pie", pie(d, lang))}
{indice(d)}
<a class="wa" data-wa href="{e(wa(d, d["contacto"]["wa_general"]))}" target="_blank" rel="noopener" aria-label="{e(ui["whatsapp"])}">
  <span class="wa__punto" aria-hidden="true"></span>{e(ui["whatsapp"])}
</a>
<script src="guion.js?v={version("guion.js")}" defer></script>
</body>
</html>
'''


def main():
    for lang, datos, archivo in (("es", ES, "index.html"),
                                 ("en", fundir(ES, EN_CAPA), "en.html")):
        (AQUI / archivo).write_text(pagina(datos, lang), encoding="utf-8")
        print(f"{archivo} armado ({lang})")


if __name__ == "__main__":
    main()
