#!/usr/bin/env python3
"""
armar.py — genera las paginas del sitio, en cada idioma, desde contenido/.

    python3 armar.py                 arma todo (ES en demo/, EN en demo/en/)
    python3 armar.py --plantilla en  vuelca la estructura de textos para traducir

La regla de la casa: un dato vive en un solo lugar. Los HTML que quedan en el
repo son los HTML finales —se abren y se ve lo que ve la persona—, pero nunca se
editan a mano: se toca el JSON y se vuelve a correr esto. Cada región que sale
del JSON queda envuelta en <!--cms:nombre--> ... <!--/cms:nombre--> para que el
panel de edición de web-editable la pueda regenerar sola más adelante.

`sitio.en.json` es una capa sobre `sitio.json`: sólo lleva lo que cambia. Una
lista de fichas se funde posicion por posicion (la capa trae solo los textos, no
repite fotos ni ids); una lista de textos sueltos se reemplaza entera.

Sin dependencias. Python 3.8+.
"""
import hashlib
import json
import sys
import html as H
from pathlib import Path
from urllib.parse import quote

AQUI = Path(__file__).parent
ES = json.loads((AQUI / "contenido/sitio.json").read_text(encoding="utf-8"))
CAPAS = {"en": json.loads((AQUI / "contenido/sitio.en.json").read_text(encoding="utf-8"))}


class Rutas:
    """Los prefijos relativos de la pagina que se esta armando. El castellano
    vive en demo/ y el ingles en demo/en/: los assets (img/, video/, fuente/)
    estan un nivel arriba de demo/, y el CSS y el JS en demo/ mismo. Las
    paginas de un mismo idioma se enlazan entre si sin prefijo, porque estan
    en la misma carpeta."""
    def __init__(self):
        self.poner("")

    def poner(self, carpeta):
        n = carpeta.count("/")
        self.carpeta = carpeta
        self.demo = "../" * n          # estilos.css, guion.js, favicon.png
        self.raiz = "../" * (n + 1)    # img/, video/, fuente/


R = Rutas()


def version(archivo):
    """Ocho caracteres del hash del archivo. Van como `?v=` en el enlace: sin
    esto el navegador sirve el CSS viejo de cache y una correccion no se ve."""
    return hashlib.sha1((AQUI / archivo).read_bytes()).hexdigest()[:8]


def medio(ruta):
    """Lo mismo para los videos y sus posters: si se recorta un video y la URL
    no cambia, el navegador sigue mostrando el de antes. La ruta del JSON es
    relativa a la raiz del repo (`video/x.mp4`); el hash se calcula contra el
    disco y el enlace sale con el prefijo de la pagina."""
    try:
        v = hashlib.sha1((AQUI.parent / ruta).read_bytes()).hexdigest()[:8]
        return f"{R.raiz}{ruta}?v={v}"
    except OSError:
        return R.raiz + ruta


URL = "https://davidtaranto96.github.io/mavenz-web/demo/"
RAIZ = "https://davidtaranto96.github.io/mavenz-web/"


def fundir(base, encima):
    """Mezcla profunda: lo de `encima` pisa a lo de `base`, clave por clave.
    Una lista de diccionarios del mismo largo se funde posicion por posicion,
    asi la capa de idioma lleva solo los textos y no repite fotos, ids ni
    tintas (repetirlos fue lo que pudrio la capa inglesa: se desincronizaba en
    silencio). Cualquier otra lista se reemplaza entera."""
    if isinstance(base, dict) and isinstance(encima, dict):
        salida = dict(base)
        for k, v in encima.items():
            salida[k] = fundir(base.get(k), v) if k in base else v
        return salida
    if (isinstance(base, list) and isinstance(encima, list) and len(base) == len(encima)
            and all(isinstance(x, dict) for x in base + encima)):
        return [fundir(b, c) for b, c in zip(base, encima)]
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
    srcset = ", ".join(f'{R.raiz}{foto["src"]}-{w}.webp {w}w' for w in anchos)
    carga = (' loading="lazy" decoding="async"' if lazy
             else ' fetchpriority="high" decoding="async"')
    c = f' class="{clase}"' if clase else ""
    return (f'<img{c} src="{R.raiz}{foto["src"]}-{anchos[-1]}.webp" srcset="{srcset}" '
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


def enlaces_menu(d, aqui):
    """El menu, desde `paginas`: es la unica fuente y la leen la barra, el pie y
    el flotante. Una entrada con `archivo` es una pagina; una con `ancla` es una
    seccion que vive en la pagina `en` (o en todas, si no dice). Lo que tiene
    `en_menu: false` o `publicar: false` no entra."""
    salida = []
    for k, p in d["paginas"].items():
        if p.get("en_menu") is False or p.get("publicar") is False:
            continue
        if "archivo" in p:
            href = p["archivo"]
            actual = ' aria-current="page"' if k == aqui else ""
        else:
            vive = p.get("en")
            href = ("#" + p["ancla"] if vive in (None, aqui)
                    else d["paginas"][vive]["archivo"] + "#" + p["ancla"])
            actual = ""
        salida.append(f'<a href="{e(href)}"{actual}>{e(p["rotulo"])}</a>')
    return "".join(salida)


def selector_idioma(d, lang, slug):
    """ES · EN · PT. Cada enlace lleva a LA MISMA pagina en el otro idioma. Un
    idioma sin `genera` (el portugues, hasta que llegue el copy) queda como
    texto deshabilitado, no como enlace a una pagina que no existe."""
    ui, archivo = d["interfaz"], d["paginas"][slug]["archivo"]
    piezas = []
    for k, idi in d["idiomas"].items():
        if k.startswith("_"):
            continue
        if k == lang:
            piezas.append(f'<span class="idioma__on" aria-current="true">{e(idi["rotulo"])}</span>')
        elif idi.get("genera"):
            piezas.append(f'<a class="idioma__off" href="{e(R.demo + idi["carpeta"] + archivo)}" '
                          f'lang="{e(idi["lang"])}" hreflang="{e(idi["lang"])}">{e(idi["rotulo"])}</a>')
        else:
            piezas.append(f'<span class="idioma__off idioma__off--pronto" aria-disabled="true" '
                          f'title="{e(ui["idioma_pronto"])}">{e(idi["rotulo"])}</span>')
    sep = '<span class="idioma__sep" aria-hidden="true">·</span>'
    return f'<nav class="idioma" aria-label="{e(ui["idioma"])}">{sep.join(piezas)}</nav>'


def cabecera(d, lang, aqui, tema="claro"):
    """La barra ya no acompana el scroll: queda arriba, casi transparente, y
    se va con la pagina. Por eso su tema es un dato de la pagina (oscuro sobre
    el video del hero, claro sobre la cinta de papel) y no una sonda."""
    m, ui, c = d["marca"], d["interfaz"], d["contacto"]
    enlaces = enlaces_menu(d, aqui)
    return f'''<header class="cabecera" data-cabecera{' data-tema="oscuro"' if tema == "oscuro" else ""}>
  <a class="cabecera__marca" href="index.html" aria-label="{e(m["nombre"])}"><img class="cabecera__logo cabecera__logo--tinta" src="{R.raiz}img/logo-horizontal.webp" alt="{e(m["nombre"])}" width="800" height="216" loading="eager" decoding="async"><img class="cabecera__logo cabecera__logo--papel" src="{R.raiz}img/logo-horizontal-claro.webp" alt="" width="800" height="216" loading="eager" decoding="async" aria-hidden="true"></a>
  <nav class="cabecera__enlaces" aria-label="{e(ui["menu"])}">{enlaces}</nav>
  <div class="cabecera__derecha">
    {selector_idioma(d, lang, aqui)}
    <a class="boton cabecera__contacto" href="#contacto">{e(c["cta_contacto"])}</a>
    <button class="hamburguesa" type="button" data-menu-boton aria-expanded="false" aria-controls="menu-celular" aria-label="{e(ui["menu"])}">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
<div class="panel" id="menu-celular" data-menu-panel>{enlaces}<a class="boton" href="#contacto">{e(c["cta_contacto"])}</a></div>'''


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
        f'<figure class="pieza pieza--grande">'
        f'{img(x["foto"], "(min-width:64rem) 88vw, 100vw")}'
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
    <div class="piezas__par{" piezas__par--sola" if len(q["piezas"]) == 1 else ""}">{piezas}</div>
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
        {f'<p class="espacio__nota">{e(x["nota"])}</p>' if x.get("nota") else ""}
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
    <video class="cardenal__video" data-diferido data-reinicia data-src="{e(medio(v["src"]))}" poster="{e(medio(v["poster"]))}"
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
        f'style="--x:{n["x"]}%;--y:{n["y"]}%;--sangria:{n["sangria"]}px;--i:{i}">'
        f'{e(n["nombre"])}</p>'
        for i, n in enumerate(r["nodos"]))
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
    temas = "".join(
        f'<li class="tema" style="--i:{i}">'
        f'<span class="tema__n" aria-hidden="true">{e(t["n"])}</span>'
        f'<span class="tema__rotulo">{e(t["rotulo"])}</span></li>'
        for i, t in enumerate(m["temas"]))
    return f'''<section class="seccion mirada-seccion" id="mirada"{fx("mirada")}>
  <p class="margen seccion__margen">{e(m["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <p class="cita mirada__cita" data-formar>{e(m["cita"])}</p>
  <ul class="temas">{temas}</ul>
  <p class="mirada__nota">{e(m["hueco"])}</p>
</section>'''


def equipo(d):
    """Retratos grandes en grilla asimetrica: el primero manda y los otros dos
    lo acompanan. Los que faltan quedan a la vista como hueco, no disimulados."""
    q = d["equipo"]
    personas = []
    for i, x in enumerate(q["personas"]):
        pendiente = x["nombre"] == "Pendiente"
        nombre = x["rol"] if pendiente else x["nombre"]
        personas.append(
            f'<article class="persona{" persona--principal" if i == 0 else ""}'
            f'{" persona--pendiente" if pendiente else ""}" style="--i:{i}">'
            f'<div class="persona__marco">'
            f'<div class="hueco persona__hueco"><p class="hueco__rotulo">{e(x["hueco"])}</p></div>'
            f'</div>'
            f'<div class="persona__pie">'
            f'<span class="persona__n" aria-hidden="true">{i + 1:02d}</span>'
            f'<h3 class="persona__nombre">{e(nombre)}</h3>'
            f'<p class="persona__rol">{e("Se suma" if pendiente else x["rol"])}</p>'
            + (f'<p class="persona__linea">{e(x["linea"])}</p>' if x["linea"] else '')
            + '</div></article>')
    return f'''<section class="seccion seccion--ancha equipo-seccion" id="equipo"{fx("equipo")}>
  <p class="margen seccion__margen">{e(q["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["intro"])}</p>
  </div>
  <div class="personas">{"".join(personas)}</div>
</section>'''


def banda(d):
    """Corte panorámico a sangre entre dos bloques. El póster va primero y el
    video entra diferido: sin esto se baja 119 KB que nadie pidió todavía."""
    b = d["banda"]
    return (f'<div class="banda" aria-hidden="true">'
            f'<video class="banda__video" data-diferido data-src="{medio(b["src"])}" '
            f'poster="{medio(b["poster"])}" muted loop playsinline preload="none"></video></div>')


def contacto(d):
    """Movamos algo juntos, con las cuatro opciones del documento del 08/09.
    Un solo formulario: al elegir una opcion cambian la linea de arriba y el
    motivo oculto, no el formulario entero (es lo que hace la referencia y lo
    que mantiene el alto estable). La primera opcion viene activa con el
    formulario a la vista. `?motivo=x` en la URL preselecciona: lo usan los
    paneles de proyectos. Sin clave del servicio, el envio abre WhatsApp."""
    c, cd, f, ui = d["contacto"], d["contacto_datos"], d["contacto"]["formulario"], d["interfaz"]
    correo = (f'<a class="subrayado subrayado--tenue" href="mailto:{e(cd["correo"])}">'
              f'{e(cd["correo"])}</a>' if cd["correo"] else "")
    motivos = c["motivos"]
    solapas = "".join(
        f'<button class="solapa" type="button" role="tab" id="solapa-{m["id"]}" data-solapa="{m["id"]}" '
        f'data-copia="{e(m.get("copy", ""))}" data-wa="{e(wa(d, m["wa"]))}" '
        f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">'
        f'<span class="solapa__texto">{e(m["rotulo"])}</span></button>'
        for i, m in enumerate(motivos))
    primera = motivos[0]
    campos = f["campos"]
    def fila(i, html):
        return f'<div class="formulario__fila" style="--i:{i}">{html}</div>'
    filas = [
        fila(0, f'<label class="campo"><span class="campo__rotulo">{e(campos["nombre"])}</span>'
                f'<input class="campo__entrada" type="text" name="nombre" autocomplete="name" required></label>'),
        fila(1, f'<label class="campo"><span class="campo__rotulo">{e(campos["correo"])}</span>'
                f'<input class="campo__entrada" type="email" name="email" autocomplete="email" required></label>'),
        fila(2, f'<label class="campo"><span class="campo__rotulo">{e(campos["telefono"])}</span>'
                f'<input class="campo__entrada" type="tel" name="telefono" autocomplete="tel"></label>'),
        fila(3, f'<label class="campo"><span class="campo__rotulo">{e(campos["mensaje"])}</span>'
                f'<textarea class="campo__entrada" name="mensaje" rows="4" required></textarea></label>'),
        fila(4, f'<p class="formulario__nota">{e(f["privacidad"])}</p>'),
        fila(5, f'<button class="boton formulario__enviar" type="submit">{e(f["enviar"])}</button>'),
    ]
    return f'''<section class="seccion--ancha contacto" id="contacto"{fx("contacto")}>
  <div class="contacto__caja">
    {cinta([c["palabra"]], tono="marca", continua=True, vertical=True, velocidad=125)}
    <div class="contacto__datos">
      <p class="contacto__apertura">{e(c["apertura"])}</p>
      <h2 class="contacto__titulo" data-letras>{e(c["titulo"])}</h2>
      <p class="margen">{e(c["bloque_datos"])}</p>
      <ul class="contacto__lista">
        <li><a class="subrayado" href="{e(wa(d, c["wa_general"]))}" target="_blank" rel="noopener">WhatsApp</a></li>
        <li>{correo}</li>
      </ul>
    </div>
    <div class="contacto__panel" data-panel-contacto>
      <p class="margen">{e(c["rotulo_motivos"])}</p>
      <div class="solapas" role="tablist" aria-label="{e(c["rotulo_motivos"])}">{solapas}</div>
      <p class="contacto__copia" data-copia-motivo style="--i:0">{e(primera.get("copy", ""))}</p>
      <form class="formulario" data-formulario novalidate action="https://api.web3forms.com/submit" method="post"
            data-clave="{e(f["clave"])}" data-asunto="{e(f["asunto"])}" data-wa-base="{e(wa(d, ""))}"
            data-enviando="{e(f["enviando"])}" data-gracias="{e(f["gracias"])}" data-error="{e(f["error"])}"
            data-falta="{e(f["falta"])}" data-correo-invalido="{e(f["correo_invalido"])}" data-enviar="{e(f["enviar"])}">
        <input type="hidden" name="motivo" value="{e(primera["rotulo"])}">
        <input type="checkbox" name="botcheck" class="formulario__trampa" tabindex="-1" autocomplete="off" aria-hidden="true">
        {"".join(filas)}
        <p class="formulario__estado" aria-live="polite"></p>
      </form>
      <p class="contacto__alternativa">{e(c["alternativa"])} <a class="subrayado subrayado--bordo" href="{e(wa(d, c["wa_general"]))}" target="_blank" rel="noopener">WhatsApp</a>.</p>
    </div>
  </div>
</section>'''


def pie(d, lang, slug):
    """El pie repite el menu definitivo y deja el WhatsApp y el correo a la
    vista (pedido del 08/09). El enlace de cookies nace oculto: consent.js le
    saca el `hidden` solo si hay etiquetas de medicion que consentir."""
    m, cd, c, ck = d["marca"], d["contacto_datos"], d["contacto"], d["cookies"]
    paginas = enlaces_menu(d, None)
    correo = (f'<a href="mailto:{e(cd["correo"])}">{e(cd["correo"])}</a>' if cd["correo"] else "")
    contacto_pie = (f'<a href="{e(wa(d, c["wa_general"]))}" target="_blank" rel="noopener">WhatsApp</a>'
                    f'{correo}')
    redes = "".join(
        (f'<a href="{e(r["href"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>'
         if r["href"] else f'<span>{e(r["nombre"])}</span>')
        for r in d["redes"])
    return f'''<footer class="pie" data-tema="claro">
  <img class="pie__iso" src="{R.raiz}img/isotipo.webp" alt="{e(m["nombre"])}" width="600" height="381" loading="lazy" decoding="async">
  <nav class="pie__redes" aria-label="{e(m["nombre"])}">{redes}</nav>
  <p class="pie__contacto">{contacto_pie}</p>
  <div class="pie__abajo">
    <p class="pie__lugar">{e(m["lugar"])}</p>
    <nav class="pie__paginas" aria-label="{e(d["interfaz"]["menu"])}">{paginas}</nav>
    {selector_idioma(d, lang, slug)}
    <button class="pie__cookies" type="button" data-cookies-abrir hidden>{e(ck["enlace_pie"])}</button>
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
        "url": URL + R.carpeta,
        "description": m["definicion"],
        "logo": f"{RAIZ}img/logo-horizontal.webp",
        "address": {"@type": "PostalAddress", "addressLocality": "Salta",
                    "addressRegion": "Salta", "addressCountry": "AR"},
        "areaServed": {"@type": "AdministrativeArea", "name": "Salta, Argentina"},
    }


# --------------------------------------------------------------------------- #

def cascara(d, lang, slug, cuerpo, tema="claro"):
    """El head, la cabecera y el pie son los mismos en todas las paginas. Se
    escriben una sola vez o se desincronizan: es el bug que mas caro sale."""
    m, ui, pg, idi = d["marca"], d["interfaz"], d["paginas"][slug], d["idiomas"][lang]
    titulo = f'{pg["titulo"]} — {m["nombre"]}' if slug != "inicio" else f'{m["nombre"]} — {m["mensaje"]}'
    archivo = "" if slug == "inicio" else pg["archivo"]
    canonica = URL + idi["carpeta"] + archivo
    # Cada idioma apunta a los otros y x-default al castellano: asi Google no
    # toma las dos versiones como contenido duplicado.
    alternas = "".join(
        f'<link rel="alternate" hreflang="{e(x["lang"])}" href="{URL}{x["carpeta"]}{archivo}">\n'
        for k, x in d["idiomas"].items() if not k.startswith("_") and x.get("genera"))
    alternas += f'<link rel="alternate" hreflang="x-default" href="{URL}{archivo}">\n'
    robots = '<meta name="robots" content="noindex">\n' if pg.get("publicar") is False else ""
    return f'''<!DOCTYPE html>
<html lang="{e(idi["lang"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(m["definicion"])}">
<meta name="theme-color" content="#eeecec">
{robots}<link rel="canonical" href="{canonica}">
{alternas}<meta property="og:type" content="website">
<meta property="og:locale" content="{e(idi["og"])}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(m["definicion"])}">
<meta property="og:image" content="{RAIZ}img/aerea-dia-1600.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{R.demo}favicon.png">
<link rel="preload" href="{R.raiz}fuente/urbanist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R.raiz}img/logo-horizontal-claro.webp" as="image" type="image/webp">
<link rel="stylesheet" href="{R.demo}estilos.css?v={version("estilos.css")}">
<script type="application/ld+json">{json.dumps(datos_estructurados(d), ensure_ascii=False)}</script>
</head>
<body data-pagina="{slug}" data-lang="{e(lang)}">
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cms("cabecera", cabecera(d, lang, slug, tema))}
<main class="contenido" id="contenido">
{cuerpo}
</main>
{cms("pie", pie(d, lang, slug))}
<a class="wa" data-wa href="{e(wa(d, d["contacto"]["wa_general"]))}" target="_blank" rel="noopener" aria-label="{e(ui["whatsapp"])}">
  <span class="wa__punto" aria-hidden="true"></span>{e(ui["whatsapp"])}
</a>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.11/dist/lenis.min.js" defer></script>
<script src="{R.demo}guion.js?v={version("guion.js")}" defer></script>
</body>
</html>
'''


def pagina_inicio(d, lang):
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
    return cascara(d, lang, "inicio", cuerpo, tema="oscuro")


def pagina_nosotros(d, lang):
    """Quienes son. Lo que falta se muestra como hueco, no se disimula."""
    pg = d["paginas"]["nosotros"]
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
    return cascara(d, lang, "nosotros", cuerpo)


def pagina_proyectos(d, lang):
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
    return cascara(d, lang, "proyectos", cuerpo)


def cinta(piezas, tono="tinta", titulo=False, continua=False, vertical=False,
          velocidad=120, imagen=False):
    """Una cinta de piezas repetidas. Dos motores:

    - Por SCROLL (la de siempre): el JS escribe --corrida y sin JS queda quieta
      y legible. Cuatro copias, la primera es el texto real.
    - CONTINUA (pedido del 08/09, `data-fx="marquee"`): corre sola con un
      keyframe infinito, pausado fuera de pantalla y apagado con
      reduced-motion. Es la unica excepcion documentada a "cero infinitas".
      Emite la secuencia DOS veces para que `translate: -50%` cierre el loop
      sin salto, y el JS calcula la duracion para que la velocidad (px/s) sea
      constante sin importar el cuerpo tipografico.

    `piezas` es un texto, o una lista de textos, o una lista de dicts con
    `rotulo` y `href` (enlaces). Con `imagen` son rutas de imagen (el isotipo).
    Con titulo=True la primera pieza es un h2: sin eso un mundo entero queda
    sin encabezado y el lector de pantalla no tiene por donde entrar."""
    if isinstance(piezas, str):
        piezas = [piezas]
    def pieza(p, oculta):
        oc = ' aria-hidden="true"' if oculta else ""
        if imagen:
            return f'<img class="cinta__pieza cinta__pieza--img" src="{R.raiz}{p}" alt=""{oc} loading="lazy" decoding="async">'
        if isinstance(p, dict):
            return f'<a class="cinta__pieza cinta__pieza--enlace" href="{e(p["href"])}"{" tabindex=-1" if oculta else ""}{oc}>{e(p["rotulo"])}</a>'
        et = "h2" if (titulo and not oculta) else "span"
        return f'<{et} class="cinta__pieza"{oc}>{e(p)}</{et}>'
    if continua:
        copias = [pieza(p, i > 0) for i, p in enumerate(piezas)]
        copias += [pieza(p, True) for p in piezas]
        clases = f'cinta cinta--{tono} cinta--continua{" cinta--vertical" if vertical else ""}'
        attrs = f'data-cinta-continua data-fx="marquee" data-velocidad="{velocidad}" data-sangra'
    else:
        copias = [pieza(p, i > 0) for i, p in enumerate(piezas * 4)]
        clases = f'cinta cinta--{tono}'
        attrs = f'data-cinta data-copias="4" data-sangra'
    return (f'<div class="{clases}" {attrs}>'
            f'<div class="cinta__riel" data-cinta-riel>{"".join(copias)}</div></div>')


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


PAGINAS = {"inicio": pagina_inicio, "nosotros": pagina_nosotros, "proyectos": pagina_proyectos}

# Claves que no son texto para leer: no se traducen y no se reclaman.
TECNICAS = {"src", "poster", "href", "id", "tinta", "lang", "og", "archivo", "carpeta", "ancla",
            "en", "whatsapp", "correo", "sitio_espacio", "proporcion", "numero", "n", "x", "y",
            "sangria", "peso", "anchos", "ancho", "alto", "columnas", "solo_visor", "bn",
            "genera", "publicar", "en_menu", "clave", "ga4", "pixel"}


def hojas(o, ruta=(), vacias=False):
    """Todas las hojas de texto de un JSON, con su ruta, salteando lo tecnico.
    Con `vacias` tambien devuelve las claves en blanco: existen como ruta
    aunque no haya nada que traducir."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith("_") or k in TECNICAS:
                continue
            yield from hojas(v, ruta + (k,), vacias)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from hojas(v, ruta + (i,), vacias)
    elif isinstance(o, str) and (vacias or o.strip()):
        yield ruta, o


def chequear_capas(base, capa, nombre):
    """Antes de generar un idioma: la capa no puede apuntar a una ruta que ya no
    existe en el castellano (eso es lo que pudrio la capa inglesa), y se avisa
    de cada texto del castellano que la capa no traduce. Corta solo en el primer
    caso; el segundo es deuda, no error."""
    rutas_base = {r for r, _ in hojas(base, vacias=True)}
    textos_base = dict(hojas(base))
    huerfanas = [r for r, _ in hojas(capa, vacias=True) if r not in rutas_base]
    if huerfanas:
        for r in huerfanas[:12]:
            print(f"  ERROR capa {nombre}: la ruta {'.'.join(map(str, r))} no existe en el castellano")
        raise SystemExit(f"capa {nombre}: {len(huerfanas)} rutas huerfanas. Se corrige la capa o se corre --plantilla {nombre}.")
    traducidas = dict(hojas(capa))
    # Un nombre propio queda igual en los dos idiomas a proposito: la capa lo
    # declara en `_iguales` y deja de figurar como deuda.
    iguales = set(capa.get("_iguales", []))
    faltan = [r for r in textos_base
              if (r not in traducidas or traducidas[r] == textos_base[r])
              and ".".join(map(str, r)) not in iguales]
    if faltan:
        print(f"  capa {nombre}: {len(faltan)} textos sin traducir de {len(textos_base)}"
              f" (los primeros: {', '.join('.'.join(map(str, r)) for r in faltan[:6])})")


def plantilla(base, nombre):
    """La estructura del castellano con solo las hojas de texto, para rellenar."""
    salida = {}
    for ruta, texto in hojas(base):
        nodo = salida
        for i, k in enumerate(ruta[:-1]):
            sig = ruta[i + 1]
            if isinstance(k, int):
                while len(nodo) <= k:
                    nodo.append({} if isinstance(sig, str) else [])
                nodo = nodo[k]
            else:
                nodo = nodo.setdefault(k, {} if isinstance(sig, str) else [])
        k = ruta[-1]
        if isinstance(k, int):
            while len(nodo) <= k:
                nodo.append("")
            nodo[k] = texto
        else:
            nodo[k] = texto
    return json.dumps(salida, ensure_ascii=False, indent=2)


def comprobar_rutas(html, carpeta):
    """Cada src= y href= relativo tiene que existir en disco, resuelto desde la
    carpeta donde queda el HTML. Es lo que atrapa un `../` de mas o de menos
    cuando el ingles baja a en/."""
    import re
    avisos = 0
    for m in re.finditer(r'(?:src|href)="([^"#?]+)', html):
        ruta = m.group(1)
        if ruta.startswith(("http", "mailto:", "tel:", "data:")):
            continue
        if not (carpeta / ruta).exists():
            avisos += 1
            print(f"  RUTA ROTA en {carpeta.name or 'demo'}/: {ruta}")
    return avisos


def auditar_enlaces(html, nombre):
    """FOOT-4: ningun enlace con etiqueta enganosa. Un `wa.me` tiene que decir
    que es WhatsApp o una consulta; un `#ancla` tiene que existir en la misma
    pagina. Devuelve la cantidad de avisos."""
    import re
    avisos = 0
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', html, re.S):
        attrs, texto = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        h = re.search(r'href="([^"]*)"', attrs)
        if not h:
            continue
        href = h.group(1)
        if "wa.me" in href and not re.search(r"whatsapp|consult|escrib", texto, re.I):
            avisos += 1
            print(f'  ENLACE ENGANOSO en {nombre}: "{texto[:40]}" abre WhatsApp')
        if href.startswith("#") and len(href) > 1 and href[1:] not in ids:
            avisos += 1
            print(f'  ANCLA ROTA en {nombre}: "{texto[:40]}" -> {href}')
    return avisos


def main(args):
    if "--plantilla" in args:
        print(plantilla(ES, args[args.index("--plantilla") + 1]))
        return
    escritos = []
    for lang, idi in ES["idiomas"].items():
        if lang.startswith("_") or not idi.get("genera"):
            continue
        if lang == "es":
            d = ES
        else:
            chequear_capas(ES, CAPAS[lang], lang)
            d = fundir(ES, CAPAS[lang])
        R.poner(idi["carpeta"])
        carpeta = AQUI / idi["carpeta"]
        carpeta.mkdir(exist_ok=True)
        for slug, pg in d["paginas"].items():
            if "archivo" not in pg:
                continue
            if slug not in PAGINAS:
                print(f"  (todavia sin funcion: {slug}, no se genera)")
                continue
            html = PAGINAS[slug](d, lang)
            (carpeta / pg["archivo"]).write_text(html, encoding="utf-8")
            escritos.append((html, carpeta))
            auditar_enlaces(html, f"{idi['carpeta']}{pg['archivo']}")
            print(f"{idi['carpeta']}{pg['archivo']} armado")
    # Las rutas se comprueban al final, cuando todas las paginas de todos los
    # idiomas ya existen: si no, index.html reclama nosotros.html por orden.
    rotas = sum(comprobar_rutas(h, c) for h, c in escritos)
    print("rutas: todas existen" if not rotas else f"rutas rotas: {rotas}")


if __name__ == "__main__":
    main(sys.argv[1:])


