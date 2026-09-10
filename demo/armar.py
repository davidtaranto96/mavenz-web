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
    return f'https://wa.me/{n}?text={quote(texto)}' if n else "contacto.html"


# El trazo de la marca: la M de Mavenz como una sola onda continua.
ONDA = ("M 40 296 C 130 240, 206 96, 302 178 C 382 246, 322 336, 240 302 "
        "C 168 272, 288 196, 516 258 C 642 292, 700 138, 832 158 "
        "C 936 174, 898 298, 1002 314 C 1082 326, 1142 300, 1178 272")


# La dirección con la que entra cada sección. Que no se repita seguida es
# justamente lo que separa un diseño de un plugin.
DIRECCION = {"quienes": "izq", "universo": "escala", "metodo": "der", "espacio": "arriba",
             "proyectos": "izq", "red": "escala", "equipo": "izq", "mirada": "der",
             "contacto": "arriba"}


def fx(seccion):
    return f' data-fx="reveal" data-fx-desde="{DIRECCION[seccion]}"'


def enlaces_menu(d, aqui, rodar=False):
    """El menu, desde `paginas`: es la unica fuente y la leen la barra, el pie y
    el flotante. Una entrada con `archivo` es una pagina; una con `ancla` es una
    seccion que vive en la pagina `en` (o en todas, si no dice). Lo que tiene
    `en_menu: false` o `publicar: false` no entra.

    Con `rodar` cada enlace sale con la palabra DOS veces apiladas (la segunda
    aria-hidden) y su posicion en --i: es el item del flotante, que rueda en
    vertical al pasar el puntero y entra escalonado por --i."""
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
        if rodar:
            i = len(salida)
            salida.append(f'<a class="rodar" href="{e(href)}" style="--i: {i}"{actual}>'
                          f'<span class="rodar__pista"><span class="rodar__cara">{e(p["rotulo"])}</span>'
                          f'<span class="rodar__cara" aria-hidden="true">{e(p["rotulo"])}</span></span></a>')
        else:
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
    # Sin hamburguesa ni panel (09/09): el unico menu desplegable es el
    # flotante de abajo a la derecha, en todos los carriles. En celular la
    # barra lleva solo el logo y el selector de idioma.
    return f'''<header class="cabecera" data-cabecera{' data-tema="oscuro"' if tema == "oscuro" else ""}>
  <a class="cabecera__marca" href="index.html" aria-label="{e(m["nombre"])}"><img class="cabecera__logo cabecera__logo--tinta" src="{R.raiz}img/logo-horizontal.webp" alt="{e(m["nombre"])}" width="800" height="216" loading="eager" decoding="async"><img class="cabecera__logo cabecera__logo--papel" src="{R.raiz}img/logo-horizontal-claro.webp" alt="" width="800" height="216" loading="eager" decoding="async" aria-hidden="true"></a>
  <nav class="cabecera__enlaces" aria-label="{e(ui["menu"])}">{enlaces}</nav>
  <div class="cabecera__derecha">
    {selector_idioma(d, lang, aqui)}
    <a class="boton cabecera__contacto" href="contacto.html">{e(c["cta_contacto"])}</a>
  </div>
</header>'''


def hero(d):
    """La primera pantalla: video aereo de fondo (diferido, solo poster en el
    celular), titulo y bajada centrados como la referencia, y al pie la cinta
    con los mundos del sitio corriendo. Sin el parrafo de relleno y sin el
    trazo: los dos los saco el documento del 08/09."""
    h, v = d["hero"], d["hero"]["video"]
    return f'''<section class="hero" id="inicio" data-tema="oscuro">
  <video class="hero__fondo" data-diferido data-pesado="1" data-src="{e(medio(v["src"]))}" poster="{e(medio(v["poster"]))}"
         muted loop playsinline preload="none" aria-label="{e(v["alt"])}"></video>
  <div class="hero__velo"></div>
  <div class="hero__texto">
    <h1 class="hero__titulo" data-letras>{e(h["titulo"])}</h1>
    <p class="hero__bajada">{e(h["bajada"])}</p>
    <div class="hero__acciones">
      <a class="boton boton--claro" href="{e(h["cta1"]["href"])}">{e(h["cta1"]["rotulo"])}</a>
      <a class="subrayado subrayado--claro" href="{e(h["cta2"]["href"])}">{e(h["cta2"]["rotulo"])}</a>
    </div>
  </div>
  <div class="hero__cinta">{cinta(h["cinta"], tono="hero", continua=True, velocidad=70)}</div>
</section>'''


def quienes(d):
    """Somos Mavenz, como quedo el 08/09 (SOM-1..5): titulo, dos parrafos en
    una columna angosta, y a la derecha dos fotos en circulo, una de fondo y
    otra un poco superpuesta (SOM-4). Sin `circulos` la columna no se emite y
    el texto ocupa el ancho: lo que falta se oculta por dato, no con
    placeholder. Se fueron el rotulo lateral, la cita y la foto de 'Donde
    trabajamos'. Solo vive en Inicio."""
    q = d["quienes"]
    c = q.get("circulos") or {}
    circulos = ""
    if c.get("fondo") and c.get("frente"):
        circulos = (f'<div class="circulos" aria-hidden="false">'
                    f'<figure class="circulo circulo--fondo">{img(c["fondo"], "(min-width:64rem) 28vw, 60vw", clase="circulo__foto")}</figure>'
                    f'<figure class="circulo circulo--frente">{img(c["frente"], "(min-width:64rem) 24vw, 52vw", clase="circulo__foto")}</figure>'
                    f'</div>')
    return f'''<section class="seccion quienes{" quienes--con-circulos" if circulos else ""}" id="quienes"{fx("quienes")}>
  <div class="quienes__texto">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["copy"])}</p>
    <p class="bajada">{e(q["copy2"])}</p>
  </div>
  {circulos}
</section>'''


def puente():
    """El pliegue entre Somos y el Universo (SOM-6): el papel se difumina en
    el bistre del Universo. Un gradiente quieto y, encima, una capa de bistre
    que crece desde abajo con el scroll (`scale: 1 var(--mezcla)`, solo
    transform, la escribe puente() de guion.js). Sin guion o con menos
    movimiento queda el gradiente, que ya es la transicion. Decorativo: no
    tiene texto y el auditor lo saltea."""
    return ('<div class="puente" data-puente data-decorativo aria-hidden="true">'
            '<div class="puente__tinta"></div></div>')


def orbita(d):
    """El Universo Mavenz del 08/09 (UNI-1..5): fondo bistre, MAVENZ fijo en
    el centro, tres esferas alrededor (12h, 4h, 8h) unidas por lineas que no
    se cortan, y el anillo de Marca y comunicacion rodeandolas. La elegida
    pasa al primer plano (scale) y su descripcion se lee al costado, en un
    bloque aria-live. En celular el diagrama queda chico y las descripciones
    son un carril con una tarjeta por vez, con flechas de 44px (el doc pide
    toque, swipe o botones). El anillo se dibuja al entrar (anillo() en
    guion.js). El componente tolera de 3 a 6 esferas sin tocar CSS."""
    import math
    u = d["universo"]
    n = len(u["esferas"])
    nodos, paneles, puntos = [], [], []
    for i, sf in enumerate(u["esferas"]):
        # Repartidas sobre la circunferencia arrancando arriba, a un 36 % del
        # centro: con tres, quedan a las 12, a las 4 y a las 8.
        ang = -math.pi / 2 + i * 2 * math.pi / n
        x, y = 50 + 36 * math.cos(ang), 50 + 36 * math.sin(ang)
        puntos.append(f"{x:.2f},{y:.2f}")
        nodos.append(
            f'<button class="orbita__nodo" type="button" data-esfera="{sf["id"]}" '
            f'style="--x:{x:.2f}%;--y:{y:.2f}%" '
            f'aria-pressed="{"true" if i == 0 else "false"}">'
            f'<span class="orbita__n" aria-hidden="true">{e(sf["numero"])}</span>'
            f'<span class="orbita__nombre">{e(sf["nombre"])}</span></button>')
        paneles.append(
            f'<div class="orbita__panel" data-panel="{sf["id"]}" '
            f'aria-hidden="{"false" if i == 0 else "true"}">'
            f'<span class="orbita__panel-n" aria-hidden="true">{e(sf["numero"])}</span>'
            f'<h3>{e(sf["nombre"])}</h3><p>{e(sf["copy"])}</p></div>')
    a = u["anillo"]
    ui = d["interfaz"]
    return f'''<section class="seccion universo oscuro" id="universo" data-tema="oscuro"{fx("universo")}>
  <div class="seccion__cabeza universo__cabeza">
    <h2 class="titulo" data-letras>{e(u["titulo"])}</h2>
    <p class="bajada">{e(u["intro"])}</p>
  </div>
  <div class="universo__cuerpo">
    <div class="orbita" data-orbita style="--esferas:{n}">
      <svg class="orbita__dibujo" viewBox="0 0 100 100" aria-hidden="true">
        <circle class="orbita__anillo" data-anillo cx="50" cy="50" r="46" fill="none"
                stroke="currentColor" stroke-width="1.2" vector-effect="non-scaling-stroke"/>
        <polygon class="orbita__lineas" points="{" ".join(puntos)}" fill="none"
                 stroke="currentColor" stroke-width="1" vector-effect="non-scaling-stroke"/>
      </svg>
      <p class="orbita__rotulo-anillo" aria-hidden="true">{e(a["nombre"])}</p>
      <p class="orbita__centro" aria-hidden="true">{e(u["centro"])}</p>
      {"".join(nodos)}
    </div>
    <div class="orbita__detalle">
      <div class="orbita__paneles" data-carril-esferas aria-live="polite">{"".join(paneles)}</div>
      <div class="orbita__flechas">
        <button class="orbita__flecha" type="button" data-carril-ant aria-label="{e(ui["anterior"])}"><span aria-hidden="true">&larr;</span></button>
        <button class="orbita__flecha" type="button" data-carril-sig aria-label="{e(ui["siguiente"])}"><span aria-hidden="true">&rarr;</span></button>
      </div>
      <p class="orbita__ayuda">{e(u["ayuda"])}</p>
    </div>
  </div>
  <p class="orbita__anillo-copy"><strong>{e(a["nombre"])}.</strong> {e(a["copy"])}</p>
  <p class="universo__cierre">{e(u["cierre"])}</p>
</section>'''


def mapa(d):
    """Los seis territorios del Mapa Mavenz. Es contenido de la clienta y está
    construido desde agosto. Desde el 08/09 vive en Mirada Mavenz (el Universo
    quedo para las tres esferas), asi que lee de `mirada.mapa`."""
    mp = d["mirada"]["mapa"]
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


def puntos_onda(fracciones, pasos=120):
    """Puntos sobre ONDA a ciertas fracciones de su LONGITUD (no del parametro
    t de cada curva, que no es uniforme). Aplana las seis cubicas en
    segmentos, arma la tabla de longitud de arco y busca ahi. Devuelve
    (x%, y%) sobre la caja 1200x400 del trazo."""
    import re
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", ONDA)]
    p0 = (nums[0], nums[1])
    puntos, largo = [p0], [0.0]
    i = 2
    while i + 5 < len(nums):
        c1, c2, p3 = (nums[i], nums[i + 1]), (nums[i + 2], nums[i + 3]), (nums[i + 4], nums[i + 5])
        for k in range(1, pasos + 1):
            t = k / pasos
            u = 1 - t
            x = u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p3[0]
            y = u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p3[1]
            ax, ay = puntos[-1]
            largo.append(largo[-1] + ((x - ax) ** 2 + (y - ay) ** 2) ** .5)
            puntos.append((x, y))
        p0 = p3
        i += 6
    total = largo[-1]
    salida = []
    for f in fracciones:
        objetivo = f * total
        j = next(k for k, l in enumerate(largo) if l >= objetivo)
        x, y = puntos[j]
        salida.append((x / 12, y / 4))     # a porcentaje de 1200 x 400
    return salida


def metodo(d):
    """Como trabajamos (MET-1..4, 08/09): el trazo de la M se dibuja con el
    scroll y los cinco pasos se despliegan desde su cola, uno tras otro, a
    medida que se baja. Sin pin: la seccion mide lo que mide y el trazo se
    completa en una pantalla de scroll. Fondo papel, trazo y palabras en
    bordo. El isotipo arranca el trazo. Sin guion: trazo entero y pasos a la
    vista; con menos movimiento, igual. En celular el trazo queda de adorno
    arriba y los pasos son una lista con filete, cada uno entra al verse.
    Los pasos se muestrean sobre la longitud del trazo (puntos_onda)."""
    m = d["metodo"]
    fr = [.14, .32, .52, .72, .92][:len(m["pasos"])]
    nodos = []
    for i, (p, (x, y)) in enumerate(zip(m["pasos"], puntos_onda(fr))):
        arriba = ' data-arriba' if i % 2 == 0 else ''
        nodos.append(
            f'<li class="trazo__nodo" data-t="{fr[i]}" style="--x:{x:.2f}%;--y:{y:.2f}%"{arriba}>'
            f'<span class="trazo__punto" aria-hidden="true"></span>'
            f'<span class="trazo__rotulo"><span class="trazo__n" aria-hidden="true">{e(p["numero"])}</span>'
            f'<strong class="trazo__nombre">{e(p["nombre"])}</strong> '
            f'<span class="trazo__copy">{e(p["copy"])}</span></span></li>')
    return f'''<section class="seccion metodo" id="metodo"{fx("metodo")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <div class="trazo" data-trazo>
    <div class="trazo__caja">
      <img class="trazo__iso" src="{R.raiz}img/isotipo.webp" alt="" width="600" height="381" loading="lazy" decoding="async">
      <svg class="trazo__dibujo" viewBox="0 0 1200 400" preserveAspectRatio="none" aria-hidden="true">
        <path class="trazo__onda" pathLength="1" d="{ONDA}" fill="none" stroke="currentColor"
              stroke-width="1.6" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
      </svg>
      <ol class="trazo__nodos">{"".join(nodos)}</ol>
    </div>
  </div>
  <p class="metodo__cierre">{e(m["cierre"])}</p>
</section>'''


def espacio(d):
    """Espacio Mavenz (ESP-1..7, 08/09): pagina propia, un bloque plano en
    wenge con texto en papel, titulo, bajada, copy y el CTA al sitio externo
    (con "(sitio externo)" solo para lectores de pantalla). Sin foto aprobada
    no hay foto: el bloque "Todavia no hay material" se fue. Cuando `foto`
    traiga un dict, entra como columna al lado del texto."""
    x = d["espacio"]
    f = x.get("foto")
    columna = f'<figure class="espacio__foto">{img(f, "(min-width:64rem) 44vw, 100vw")}</figure>' if f else ""
    return f'''<section class="sangre oscuro espacio{" espacio--con-foto" if f else ""}" id="espacio-bloque" data-tinta="wenge" data-tema="oscuro"{fx("espacio")}>
  <div class="sangre__interior espacio__interior">
    <div class="espacio__texto">
      <h2 class="titulo" data-letras>{e(x["titulo"])}</h2>
      <p class="espacio__bajada">{e(x["bajada"])}</p>
      <p class="bajada">{e(x["copy"])}</p>
      <a class="boton boton--claro espacio__cta" href="{e(x["cta"]["href"])}" target="_blank" rel="noopener">{e(x["cta"]["rotulo"])}<span class="visualmente-oculto"> {e(x["cta"]["externo"])}</span></a>
    </div>
    {columna}
  </div>
</section>'''


def datos_chips(datos):
    return '<ul class="datos">' + "".join(f'<li class="dato">{e(x)}</li>' for x in datos) + '</ul>'


def cardinal_resumen(d):
    """Cardinal en proyectos.html (PROY-2): titulo, texto, los seis datos, la
    aclaracion de roles y dos CTAs con destinos distintos: la principal a la
    ficha propia, la comercial a WhatsApp con su rotulo honesto. Ningun boton
    dice 'Ver el proyecto' y lleva a WhatsApp."""
    c = d["proyectos"]["cardinal"]
    return f'''<section class="seccion resumen" id="cardinal"{fx("proyectos")}>
  <div class="resumen__foto">{img(c["hero_foto"], "(min-width:64rem) 46vw, 100vw")}</div>
  <div class="resumen__texto">
    <p class="margen">{e(c["nombre"])} · {e(c["meta"])} · {e(c["estado"])}</p>
    <h2 class="titulo titulo--chico" data-letras>{e(c["titulo"])}</h2>
    <p class="bajada">{e(c["texto"])}</p>
    {datos_chips(c["datos"])}
    <p class="resumen__aclaracion">{e(c["aclaracion"])}</p>
    <div class="resumen__acciones">
      <a class="boton" href="cardinal.html">{e(c["cta_principal"])}</a>
      <a class="subrayado" href="{e(wa(d, c["wa"]))}" target="_blank" rel="noopener">{e(c["cta_comercial"])}</a>
    </div>
  </div>
</section>'''


def ficha_hero(d):
    """La primera pantalla de cardinal.html (FICHA-1, FICHA-2): una seccion
    de 220svh con el contenido sticky a 100svh. Detras corre la cinta
    continua del isotipo; en el centro una tarjeta cuadrada con la foto, que
    se abre a pantalla completa con el scroll (fichaHero() en guion.js
    escribe --w y --h por separado, con clip-path: inset(): el encuadre se
    revela en vez de deformarse, que es lo que se midio en la referencia). El
    bajada se va en el primer cuarto; "(Scroll)" mas lento. La cinta dice el
    nombre del proyecto (David, 10/09: antes era el isotipo) y el h1 queda
    solo para lectores de pantalla. Sin
    GSAP o con menos movimiento: foto entera y sin recorrido."""
    c = d["proyectos"]["cardinal"]
    return f'''<section class="ficha-hero oscuro" id="inicio" data-ficha-hero data-tema="oscuro">
  <div class="ficha-hero__pin">
    <div class="ficha-hero__cinta" data-ficha-cinta aria-hidden="true">{cinta([c["marquee"]] * 3, tono="nombre", continua=True, velocidad=120, decorativa=True)}</div>
    <div class="ficha-hero__foto" data-ficha-foto>{img(c["hero_foto"], "100vw", lazy=False)}</div>
    <div class="ficha-hero__copia" data-ficha-copia>
      <h1 class="visualmente-oculto">{e(c["nombre"])}</h1>
      <p class="margen margen--claro">{e(c["meta"])} · {e(c["estado"])}</p>
      <p class="ficha-hero__bajada">{e(c["titulo"])}</p>
    </div>
    <p class="ficha-hero__scroll" data-ficha-scroll aria-hidden="true">{e(c["scroll"])}</p>
  </div>
</section>'''


def marcador():
    """La linea vertical fina que entra 200 ms antes que el bloque (motor 3
    de la referencia). marcadores() en guion.js le escribe data-visto."""
    return '<span class="marcador" data-marcador aria-hidden="true"></span>'


def ficha_titulo(d):
    c = d["proyectos"]["cardinal"]
    return f'''<section class="seccion ficha-titulo" id="proyecto"{fx("proyectos")}>
  {marcador()}
  <h2 class="titulo ficha-titulo__titulo" data-letras>{e(c["titulo"])}</h2>
  <p class="bajada ficha-titulo__texto">{e(c["texto"])}</p>
  {datos_chips(c["datos"])}
  <p class="resumen__aclaracion">{e(c["aclaracion"])}</p>
  <a class="subrayado" href="{e(wa(d, c["wa"]))}" target="_blank" rel="noopener">{e(c["cta_comercial"])}</a>
</section>'''


def galeria(d):
    """La galeria en cascada (David, 10/09: antes era un carril arrastrable):
    una grilla de tres columnas con escalera, cada foto entra sola al llegar
    con el scroll y las columnas se deslizan a velocidades distintas
    (cascada() en guion.js, solo transform). Nada que arrastrar. La misma
    lista alimenta el visor: data-foto es el indice en `galeria`."""
    c, ui = d["proyectos"]["cardinal"], d["interfaz"]
    fotos = "".join(
        f'<figure class="lamina lamina--{x["ancho"]}" style="--i:{i};--col:{i % 3}">'
        f'<button class="lamina__abrir" type="button" data-foto="{i}" aria-label="{e(ui["abrir_foto"])}: {e(x["epigrafe"])}">'
        f'{img(x["foto"], "(min-width:64rem) 30vw, 90vw")}</button>'
        f'<figcaption class="lamina__epigrafe">{e(x["epigrafe"])}</figcaption></figure>'
        for i, x in enumerate(c["galeria"]))
    return f'''<section class="seccion galeria-seccion" id="galeria">
  <h2 class="visualmente-oculto">{e(c["galeria_titulo"])}</h2>
  <div class="galeria" data-cascada>{fotos}</div>
</section>'''


def sub_items(d):
    """Los sub-items de Cardinal (FICHA-4, FICHA-5): foto 3:4 y texto, los
    pares espejados, el tercero alineado abajo. Solo se emite el que tiene
    foto Y copy: hoy ninguno, asi que la seccion no existe hasta que Vero
    mande el material. Sin placeholder."""
    c = d["proyectos"]["cardinal"]
    completos = [x for x in c["sub_items"] if x.get("foto") and x.get("copy")]
    if not completos:
        return ""
    bloques = "".join(
        f'<article class="subitem{" subitem--espejo" if i % 2 else ""}{" subitem--abajo" if i % 3 == 2 else ""}" id="sub-{e(x["id"])}">'
        f'<figure class="subitem__foto">{img(x["foto"], "(min-width:64rem) 30vw, 100vw")}</figure>'
        f'<div class="subitem__texto"><h3 class="subitem__nombre">{e(x["nombre"])}</h3><p>{e(x["copy"])}</p></div>'
        f'</article>'
        for i, x in enumerate(completos))
    return f'<section class="seccion subitems" id="detalles"{fx("proyectos")}>{bloques}</section>'


def franja_video(d):
    """Foto o video a sangre, sin texto (el ritmo de la referencia: bloques
    de solo imagen entre bloques de aire). Video diferido con poster."""
    v = d["proyectos"]["cardinal"]["franja"]
    return (f'<div class="franja-video" aria-label="{e(v["alt"])}" role="img">'
            f'<video class="franja-video__video" data-diferido data-pesado="1" data-src="{e(medio(v["src"]))}" '
            f'poster="{e(medio(v["poster"]))}" muted loop playsinline preload="none" aria-hidden="true"></video></div>')


def unidades(d):
    u = d["proyectos"]["cardinal"]["unidades"]
    f = f'<figure class="unidades__foto">{img(u["foto"], "(min-width:64rem) 50vw, 100vw")}</figure>' if u.get("foto") else ""
    return f'''<section class="seccion unidades" id="unidades"{fx("proyectos")}>
  <div class="unidades__texto">
    <p class="margen">{e(u["rotulo"])}</p>
    <h2 class="titulo titulo--chico" data-letras>{e(u["titulo"])}</h2>
    <p class="bajada">{e(u["texto"])}</p>
  </div>
  {f}
</section>'''


def financiacion(d):
    """El remate de la ficha (FICHA-7 y FICHA-8 juntos, David 10/09: la web
    termina aca y el contacto va aparte): titulo, el copy cuando llegue,
    Consulta disponibilidad a WhatsApp y Contactanos a la pagina de contacto."""
    c = d["proyectos"]["cardinal"]
    fi = c["financiacion"]
    copia = f'<p class="franja__copy">{e(fi["copy"])}</p>' if fi.get("copy") else ""
    return f'''<section class="franja oscuro" id="financiacion" data-tema="oscuro"{fx("espacio")}>
  {marcador()}
  <h2 class="franja__titulo" data-letras>{e(fi["titulo"])}</h2>
  {copia}
  <div class="franja__acciones">
    <a class="boton boton--claro" href="{e(wa(d, c["wa"]))}" target="_blank" rel="noopener">{e(fi["cta"])}</a>
    <a class="subrayado subrayado--claro" href="contacto.html">{e(fi["cta2"])}</a>
  </div>
</section>'''


def oportunidades(d):
    o = d["proyectos"]["oportunidades"]
    return f'''<section class="seccion oportunidades" id="oportunidades"{fx("proyectos")}>
  <div class="seccion__cabeza">
    <h2 class="titulo titulo--chico" data-letras>{e(o["rotulo"])}</h2>
    <div>
      <p class="bajada">{e(o["bajada"])}</p>
      <a class="boton oportunidades__cta" href="{e(o["href"])}">{e(o["cta"])}</a>
    </div>
  </div>
</section>'''


def cardenal(d):
    """La pieza animada de Fractura: el ave se dibuja, se posa sobre la M del
    isotipo y cierra con la frase de ellos. Arranca al entrar en vista, una vez."""
    v = d["proyectos"]["cardinal"]["cardenal"]
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
    """Otros proyectos (PROY-3): solo proyectos confirmados y con informacion
    suficiente. Porto y WA son de Grupo MDay y Vero no los confirmo:
    `otros_publicar` en false y la seccion no se emite."""
    p = d["proyectos"]
    if not p.get("otros_publicar") or not p.get("otros"):
        return ""
    fichas = "".join(
        f'<article class="otro">'
        f'<div class="otro__marco">{img(x["foto"], "(min-width:64rem) 34rem, 90vw")}</div>'
        f'<h3 class="otro__nombre">{e(x["nombre"])}</h3>'
        f'<p class="otro__meta">{e(x["meta"])}</p>'
        f'<p class="otro__copy">{e(x["copy"])}</p></article>'
        for x in p["otros"])
    return f'''<section class="seccion otros" id="otros"{fx("proyectos")}>
  <div class="seccion__cabeza">
    <h2 class="titulo titulo--chico" data-letras>{e(p["otros_rotulo"])}</h2>
    <p class="bajada">{e(p["otros_intro"])}</p>
  </div>
  <div class="otros__par">{fichas}</div>
</section>'''


def visor(d):
    """Lightbox de la galeria de Cardinal. El swipe lo hace el navegador dentro
    de un carril con scroll-snap. Una sola lista (`galeria`) alimenta el
    carrusel y el visor: data-foto es el indice y no se desincroniza."""
    c, ui = d["proyectos"]["cardinal"], d["interfaz"]
    laminas = "".join(
        f'<figure class="visor__lamina" data-lamina="{i}">'
        f'{img(x["foto"], "100vw")}'
        f'<figcaption>{e(x["epigrafe"])}</figcaption></figure>'
        for i, x in enumerate(c["galeria"]))
    return f'''<dialog class="visor" data-visor aria-label="{e(c["nombre"])}">
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
    """Mirada Mavenz (documento del 08/09): la seccion editorial que reemplaza
    a Territorio, con las cinco categorias y el mapa como contenido editorial.
    Vive en Inicio, entre Proyectos en movimiento y Contacto."""
    m = d["mirada"]
    temas = "".join(
        f'<li class="tema" style="--i:{i}">'
        f'<span class="tema__n" aria-hidden="true">{e(t["n"])}</span>'
        f'<span class="tema__rotulo">{e(t["rotulo"])}</span></li>'
        for i, t in enumerate(m["temas"]))
    return f'''<section class="seccion mirada-seccion" id="mirada"{fx("mirada")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <ul class="temas">{temas}</ul>
  {mapa(d)}
</section>'''


def equipo(d):
    """Las personas detras de Mavenz (NOS-1..4). Se publica cada integrante
    que tenga nombre y rol (David, 10/09); el apellido, la foto y la linea
    entran cuando Vero los mande. Sin foto, la tarjeta lleva el isotipo."""
    q = d["equipo"]
    con = [x for x in q["personas"] if x.get("nombre") and x.get("rol")]
    def tarjeta(i, x):
        foto = (f'<figure class="persona__marco">{img(x["foto"], "(min-width:64rem) 30vw, 100vw")}</figure>' if x.get("foto")
                else f'<figure class="persona__marco persona__marco--sin-foto" aria-hidden="true"><img src="{R.raiz}img/isotipo.webp" alt="" width="600" height="381" loading="lazy" decoding="async"></figure>')
        nombre = f'{x["nombre"]} {x.get("apellido", "")}'.strip()
        linea = f'<p class="persona__linea">{e(x["linea"])}</p>' if x.get("linea") else ""
        return (f'<article class="persona" style="--i:{i}">{foto}'
                f'<div class="persona__pie"><h3 class="persona__nombre">{e(nombre)}</h3>'
                f'<p class="persona__rol">{e(x["rol"])}</p>{linea}</div></article>')
    grilla = f'<div class="personas">{"".join(tarjeta(i, x) for i, x in enumerate(con))}</div>' if con else ""
    return f'''<section class="seccion equipo-seccion" id="equipo"{fx("equipo")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["intro"])}</p>
  </div>
  {grilla}
</section>'''


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
    {cinta([c["palabra"]], tono="marca", continua=True, vertical=True, velocidad=125, decorativa=True)}
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
    """El pie rehecho el 10/09: cuatro columnas en escritorio (la marca con su
    mensaje, las secciones, el contacto, las redes) y una fila de abajo con
    los derechos, el idioma y el enlace de cookies, que nace oculto y solo
    aparece si hay etiquetas de medicion (consent.js le saca el hidden)."""
    m, cd, c, ck, pf, ui = d["marca"], d["contacto_datos"], d["contacto"], d["cookies"], d["pie"], d["interfaz"]
    paginas = enlaces_menu(d, slug)
    correo = (f'<a href="mailto:{e(cd["correo"])}">{e(cd["correo"])}</a>' if cd["correo"] else "")
    href_wa = wa(d, c["wa_general"])
    afuera = ' target="_blank" rel="noopener"' if href_wa.startswith("http") else ""
    redes = "".join(
        (f'<a href="{e(r["href"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>'
         if r["href"] else f'<span class="pie__pronto" title="{e(ui["idioma_pronto"])}">{e(r["nombre"])}</span>')
        for r in d["redes"])
    return f'''<footer class="pie" data-tema="claro">
  <div class="pie__arriba">
    <div class="pie__marca">
      <a class="pie__logo" href="index.html" aria-label="{e(m["nombre"])}"><img class="pie__iso" src="{R.raiz}img/isotipo.webp" alt="" width="600" height="381" loading="lazy" decoding="async"></a>
      <p class="pie__mensaje">{e(m["mensaje"])}</p>
      <p class="pie__definicion">{e(m["definicion"])}</p>
    </div>
    <nav class="pie__col" aria-label="{e(ui["menu"])}">
      <p class="pie__rotulo">{e(pf["rotulo_paginas"])}</p>
      <div class="pie__paginas">{paginas}</div>
    </nav>
    <div class="pie__col">
      <p class="pie__rotulo">{e(pf["rotulo_contacto"])}</p>
      <div class="pie__contacto"><a href="{e(href_wa)}"{afuera}>{e(ui["whatsapp"])}</a>{correo}<span class="pie__lugar">{e(m["lugar"])}</span></div>
    </div>
    <div class="pie__col">
      <p class="pie__rotulo">{e(pf["rotulo_redes"])}</p>
      <nav class="pie__redes" aria-label="{e(pf["rotulo_redes"])}">{redes}</nav>
    </div>
  </div>
  <div class="pie__abajo">
    <p class="pie__derechos">&copy; {e(pf["derechos"])}</p>
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

def flotante(d, lang, aqui):
    """El menu y el WhatsApp juntos, abajo a la derecha (pedido del 08/09,
    mecanica de realevate.agency medida cuadro a cuadro). Reemplaza al globo
    `.wa` suelto, a la hamburguesa y al panel de celular: un solo menu
    desplegable en todos los carriles. En escritorio aparece cuando la
    cabecera salio de la pantalla; bajo 64rem esta siempre. Lo abre y cierra
    el modulo "Flotante" de guion.js; el tema se lo escribe mirarTema.

    Sin numero de WhatsApp el enlace va a #contacto y sin target=_blank: un
    ancla en otra pestana es un error clasico."""
    ui, cd = d["interfaz"], d["contacto_datos"]
    href = wa(d, d["contacto"]["wa_general"])
    afuera = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    icono = lambda ruta: (f'<svg class="flotante__icono" viewBox="0 0 16 16" width="14" height="14" fill="none" '
                          f'stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ruta}</svg>')
    correo = (f'<a class="flotante__dato" href="mailto:{e(cd["correo"])}">'
              f'{icono("<path d=\"M2 4.5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1z\"/><path d=\"M2.5 5l5.5 4 5.5-4\"/>")}{e(ui["correo"])}</a>'
              if cd.get("correo") else "")
    return f'''<div class="flotante" data-flotante>
  <a class="flotante__wa" href="{e(href)}"{afuera}><span class="flotante__wa-texto">{e(ui["whatsapp"])}</span></a>
  <button class="flotante__boton" type="button" data-menu-boton aria-expanded="false" aria-controls="menu-flotante" aria-label="{e(ui["menu"])}">
    <span class="flotante__raya flotante__raya--larga" aria-hidden="true"></span><span class="flotante__raya flotante__raya--corta" aria-hidden="true"></span>
  </button>
  <div class="flotante__panel" id="menu-flotante" data-menu-panel data-lenis-prevent>
    <div class="flotante__fondo-y" aria-hidden="true"><div class="flotante__fondo-x"></div></div>
    <nav class="flotante__enlaces" aria-label="{e(ui["menu"])}">{enlaces_menu(d, aqui, rodar=True)}</nav>
    <div class="flotante__pie">
      <a class="flotante__dato" href="{e(href)}"{afuera}>{icono('<path d="M2.5 4.5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H7.5l-3 2.5v-2.5h-1a1 1 0 0 1-1-1z"/><path d="M5.5 7h5"/>')}{e(ui["whatsapp"])}</a>
      {correo}
    </div>
    {selector_idioma(d, lang, aqui)}
  </div>
</div>'''


def letras(palabra):
    """Un <span> por caracter, con su posicion en --i y sin espacios entre
    spans (un espacio entre spans es un hueco visible en la palabra). El
    espacio del rotulo va como &nbsp; para que su span no se colapse. Lo usa
    el efecto .barajar del aviso de cookies: la palabra se apaga y vuelve
    letra por letra, y el CSS escalona cada una por su --i."""
    return "".join(
        f'<span class="barajar__letra" style="--i:{i}">{"&nbsp;" if c == " " else e(c)}</span>'
        for i, c in enumerate(palabra))


def cookies(d):
    """El <template> del aviso de cookies. Es inerte: consent.js lo clona y lo
    cuelga de <body> solo si hay un ID de GA4 o de pixel en `medicion` y
    todavia no hay decision. Sin IDs no se muestra nada, que es la regla de
    la casa. Dos acciones con el mismo peso, Aceptar / Rechazar, decision de
    David del 10/09 para este proyecto (la regla general es un solo boton).
    El rotulo va en aria-label porque un lector de pantalla deletrea los
    spans inline-block, igual que pasa con los titulos [data-letras]."""
    ck = d["cookies"]
    def boton(clave):
        return (f'<button type="button" class="barajar" data-cookies="{clave}" aria-label="{e(ck[clave])}">'
                f'<span class="barajar__copia barajar__copia--sale">{letras(ck[clave])}</span>'
                f'<span class="barajar__copia barajar__copia--entra" aria-hidden="true">{letras(ck[clave])}</span>'
                f'</button>')
    return f"""<template id="cookies">
<div class="cookies" role="region" aria-labelledby="cookies-titulo" aria-live="polite">
  <p class="cookies__titulo" id="cookies-titulo">{e(ck["titulo"])}</p>
  <p class="cookies__texto">{e(ck["texto"])}</p>
  <div class="cookies__acciones">
    {boton("aceptar")}
    <span class="cookies__barra" aria-hidden="true">/</span>
    {boton("rechazar")}
  </div>
</div>
</template>"""


def cascara(d, lang, slug, cuerpo, tema="claro"):
    """El head, la cabecera y el pie son los mismos en todas las paginas. Se
    escriben una sola vez o se desincronizan: es el bug que mas caro sale."""
    m, ui, pg, idi = d["marca"], d["interfaz"], d["paginas"][slug], d["idiomas"][lang]
    md = d.get("medicion", {})
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
<meta property="og:image" content="{RAIZ}video/hero-poster.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{R.demo}favicon.png">
<link rel="preload" href="{R.raiz}fuente/urbanist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R.raiz}img/logo-horizontal-claro.webp" as="image" type="image/webp">
<link rel="stylesheet" href="{R.demo}estilos.css?v={version("estilos.css")}">
<script type="application/ld+json">{json.dumps(datos_estructurados(d), ensure_ascii=False)}</script>
</head>
<body data-pagina="{slug}" data-lang="{e(lang)}" data-ga4="{e(md.get("ga4", ""))}" data-pixel="{e(md.get("pixel", ""))}">
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cms("cabecera", cabecera(d, lang, slug, tema))}
<main class="contenido" id="contenido">
{cuerpo}
</main>
{cms("pie", pie(d, lang, slug))}
{flotante(d, lang, slug)}
{cookies(d)}
<script src="{R.demo}consent.js?v={version("consent.js")}" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.11/dist/lenis.min.js" defer></script>
<script src="{R.demo}guion.js?v={version("guion.js")}" defer></script>
</body>
</html>
'''


def pagina_inicio(d, lang):
    """El relato del 08/09: hero con video, Somos, el pliegue al bistre del
    Universo, Como trabajamos, Proyectos en movimiento, Mirada y Contacto.
    La cortina (hero sticky con el dossier subiendo encima) se fue: con un
    video de fondo seguia corriendo tapado toda la pagina y MET-5 pide que
    nunca se vea el fondo del inicio al bajar."""
    cuerpo = f'''{cms("hero", hero(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("quienes", quienes(d))}
</div></div>
{puente()}
{cms("universo", orbita(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("metodo", metodo(d))}
{cms("mundos", mundos(d))}
{cms("mirada", mirada(d))}
</div></div>'''
    return cascara(d, lang, "inicio", cuerpo, tema="oscuro")


def pagina_nosotros(d, lang):
    """Las personas detras de Mavenz. Se genera con noindex y fuera del menu
    hasta que el equipo este completo (paginas.nosotros.publicar)."""
    pg = d["paginas"]["nosotros"]
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("equipo", equipo(d))}
</div></div>
{cms("red", red(d))}'''
    return cascara(d, lang, "nosotros", cuerpo)


def pagina_proyectos(d, lang):
    """El indice liviano (PROY-1..3): cinta, intro, Cardinal resumido con su
    CTA a la ficha, otros proyectos (solo si hay confirmados) y las
    oportunidades de inversion, que llevan al formulario. Espacio Mavenz y
    Territorio ya no viven aca: no son proyectos."""
    pg, p = d["paginas"]["proyectos"], d["proyectos"]
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
<section class="seccion proyectos-intro"{fx("proyectos")}>
  <p class="bajada bajada--angosta proyectos-intro__texto">{e(p["intro"])}</p>
</section>
{cms("cardinal", cardinal_resumen(d))}
{cms("otros", otros(d))}
{cms("oportunidades", oportunidades(d))}
</div></div>'''
    return cascara(d, lang, "proyectos", cuerpo)


def pagina_espacio(d, lang):
    """Espacio Mavenz, con seccion propia en el menu (ESP-1)."""
    pg = d["paginas"]["espacio"]
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
{cms("espacio", espacio(d))}'''
    return cascara(d, lang, "espacio", cuerpo)


def pagina_cardinal(d, lang):
    """La ficha de Cardinal (FICHA-1..8, PROY-2), en el orden del documento:
    hero que se abre, titulo con marcador, galeria escalonada, el cardenal,
    sub-items (cuando haya material), franja de video, unidades,
    financiacion en oscuro, cierre al contacto."""
    cuerpo = f'''{cms("hero", ficha_hero(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("titulo", ficha_titulo(d))}
{cms("galeria", galeria(d))}
{cms("cardenal", cardenal(d))}
{cms("detalles", sub_items(d))}
</div></div>
{cms("franja", franja_video(d))}
<div class="dossier" data-tema="claro"><div class="dossier__interior">
{cms("unidades", unidades(d))}
</div></div>
{cms("financiacion", financiacion(d))}
{visor(d)}'''
    return cascara(d, lang, "cardinal", cuerpo, tema="oscuro")


def pagina_contacto(d, lang):
    """La ventana de contacto, sola (David, 10/09): cinta, la seccion entera
    con la palabra corriendo en vertical, las cuatro opciones y el
    formulario. `?motivo=` en la URL abre la solapa elegida."""
    pg = d["paginas"]["contacto"]
    cuerpo = f'''{cinta(pg["cinta"], titulo=True)}
<div class="dossier dossier--contacto" data-tema="claro"><div class="dossier__interior">
{cms("contacto", contacto(d))}
</div></div>'''
    return cascara(d, lang, "contacto", cuerpo)


def cinta(piezas, tono="tinta", titulo=False, continua=False, vertical=False,
          velocidad=120, imagen=False, decorativa=False):
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
    Con `decorativa` TODAS las copias van aria-hidden: es una marca de agua, el
    texto real esta en otro lado (el h2 del contacto) y el lector de pantalla
    no tiene por que leerla ni el auditor medirle el contraste.
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
        # La primera secuencia es la real entera (cinco enlaces distintos en el
        # hero); solo la segunda, que existe para cerrar el loop, va oculta.
        copias = [pieza(p, decorativa) for p in piezas]
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
    """Proyectos en movimiento (PROY-1, 3, 4, 5): tres paneles con aire entre
    si, cada uno con su tinta, la foto en el tercio de abajo y el nombre en
    vertical (la mecanica de realevate que pidio el documento). Tilt al pasar
    el puntero fino (data-fx="tilt" en la tarjeta y NUNCA en una seccion de
    reveal: el motor propio compara data-fx="reveal" por igualdad exacta).
    Un panel con `motivo` lleva al contacto con esa opcion preseleccionada."""
    w = d["mundos"]
    def panel(i, x):
        return (f'<a class="mundo" href="{e(x["href"])}" data-tinta="{e(x["tinta"])}" data-fx="tilt" data-fx-grados="5" '
        f'style="--i:{i}">'
        f'<span class="mundo__cuerpo">'
        f'<span class="mundo__marca" aria-hidden="true"><img src="{R.raiz}img/isotipo.webp" alt="" width="600" height="381" loading="lazy" decoding="async"></span>'
        f'<span class="mundo__nombre">{e(x["nombre"])}</span>'
        f'<span class="mundo__bajada">{e(x["bajada"])}</span>'
        f'<span class="mundo__cierre">{e(x["cierre"])}<span aria-hidden="true"> &#8594;</span></span>'
        f'</span>'
        f'{img(x["foto"], "(min-width:64rem) 30vw, 100vw", clase="mundo__foto") if x.get("foto") else ""}'
        f'</a>')
    paneles = "".join(panel(i, x) for i, x in enumerate(w["lista"]))
    return f'''<section class="seccion mundos-seccion" id="mundos"{fx("proyectos")}>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(w["rotulo"])}</h2>
    <p class="bajada">{e(w["intro"])}</p>
  </div>
  <div class="mundos">{paneles}</div>
</section>'''


PAGINAS = {"inicio": pagina_inicio, "nosotros": pagina_nosotros, "proyectos": pagina_proyectos,
           "espacio": pagina_espacio, "cardinal": pagina_cardinal, "contacto": pagina_contacto}

# Claves que no son texto para leer: no se traducen y no se reclaman.
TECNICAS = {"src", "poster", "href", "id", "tinta", "lang", "og", "archivo", "carpeta", "ancla",
            "en", "whatsapp", "correo", "sitio_espacio", "proporcion", "numero", "n", "x", "y",
            "sangria", "peso", "anchos", "ancho", "alto", "columnas", "solo_visor", "bn",
            "genera", "publicar", "en_menu", "clave", "ga4", "pixel", "otros_publicar",
            "servicio", "motivo"}


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


def buscar_palabra(d, palabra):
    """`--palabra movimiento` (PRIO-5 del 08/09): Vero pidio no repetir tanto
    'movimiento'. Lista cada texto que la contiene con su clave, para que ella
    decida cual cambia. No se reescribe nada sin ella."""
    import unicodedata
    def plano(t):
        return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
    hits = [(".".join(map(str, r)), t) for r, t in hojas(d) if plano(palabra) in plano(t)]
    print(f'"{palabra}" aparece en {len(hits)} textos:')
    for clave, texto in hits:
        print(f"  {clave}\n      {texto}")
    return hits


def main(args):
    if "--plantilla" in args:
        print(plantilla(ES, args[args.index("--plantilla") + 1]))
        return
    if "--palabra" in args:
        buscar_palabra(ES, args[args.index("--palabra") + 1])
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


