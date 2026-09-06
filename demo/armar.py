#!/usr/bin/env python3
"""
armar.py — genera index.html desde contenido/sitio.json.

    python3 armar.py

La regla de la casa: un dato vive en un solo lugar. El index.html que queda en
el repo es el HTML final —se abre y se ve lo que ve la persona—, pero nunca se
edita a mano: se toca el JSON y se vuelve a correr esto. Cada región que sale
del JSON queda envuelta en <!--cms:nombre--> ... <!--/cms:nombre--> para que el
panel de edición de web-editable la pueda regenerar sola más adelante.

Sin dependencias. Python 3.8+.
"""
import json
import html as H
from pathlib import Path

AQUI = Path(__file__).parent
D = json.loads((AQUI / "contenido/sitio.json").read_text(encoding="utf-8"))
URL = "https://davidtaranto96.github.io/mavenz-web/demo/"


def e(t):
    return H.escape(str(t), quote=True)


def cms(nombre, contenido):
    return f"<!--cms:{nombre}-->{contenido}<!--/cms:{nombre}-->"


def img(foto, sizes, clase="", lazy=True, extra=""):
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
            f'width="{foto["ancho"]}" height="{foto["alto"]}"{carga}{extra}>')


def wa(texto):
    n = D["contacto_datos"]["whatsapp"]
    from urllib.parse import quote
    return f'https://wa.me/{n}?text={quote(texto)}' if n else "#contacto"


# El trazo de la marca: la M de Mavenz como una sola onda continua.
ONDA = ("M 40 296 C 44 148, 206 96, 302 178 C 382 246, 322 336, 240 302 "
        "C 168 272, 288 196, 516 258 C 642 292, 700 138, 832 158 "
        "C 936 174, 898 298, 1002 314 C 1082 326, 1142 300, 1178 272")

# Los siete vértices del heptagrama, en porcentaje de la caja de la rueda.
# Radio 42 % desde el centro; el primero arriba y de ahí cada 360/7 grados.
VERTICES = [(50.00, 8.00), (82.84, 23.81), (90.95, 59.35), (68.22, 87.84),
            (31.78, 87.84), (9.05, 59.35), (17.16, 23.81)]


def poligono(orden, opacidad):
    pts = " ".join(f"{VERTICES[i][0]},{VERTICES[i][1]}" for i in orden)
    return (f'<polygon points="{pts}" fill="none" stroke="var(--linea-acento)" '
            f'stroke-width="1" vector-effect="non-scaling-stroke" opacity="{opacidad}"/>')


# --------------------------------------------------------------------------- #
# Secciones
# --------------------------------------------------------------------------- #

def cabecera():
    m, ui, idi = D["marca"], D["interfaz"], D["idiomas"]
    enlaces = "".join(f'<a href="#{s["id"]}">{e(s["rotulo"])}</a>' for s in D["menu"])
    idioma = (f'<span class="idioma"><span class="idioma__on">{e(idi["es"]["rotulo"])}</span>'
              f'<span class="idioma__sep" aria-hidden="true">/</span>'
              f'<span class="idioma__off" title="{e(ui["en_pendiente"])}">{e(idi["en"]["rotulo"])}</span></span>')
    return f'''<header class="cabecera" data-cabecera>
  <a class="cabecera__marca" href="#contenido" aria-label="{e(m["nombre"])}"><img class="cabecera__logo" src="../img/logo-horizontal.webp" alt="{e(m["nombre"])}" width="800" height="216"></a>
  <nav class="cabecera__enlaces" aria-label="Secciones">{enlaces}</nav>
  <div class="cabecera__derecha">
    {idioma}
    <a class="boton cabecera__reunion" href="{e(wa(D["contacto"]["wa_reunion"]))}" target="_blank" rel="noopener">{e(D["contacto"]["cta_reunion"])}</a>
    <button class="hamburguesa" type="button" data-menu-boton aria-expanded="false" aria-controls="menu-celular" aria-label="{e(ui["menu"])}">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
<div class="panel" id="menu-celular" data-menu-panel>{enlaces}<a class="boton" href="{e(wa(D["contacto"]["wa_reunion"]))}" target="_blank" rel="noopener">{e(D["contacto"]["cta_reunion"])}</a></div>'''


def hero():
    h = D["hero"]
    ecos = "".join(
        f'<path d="{ONDA}" fill="none" stroke="var(--linea-acento)" stroke-width="1" '
        f'vector-effect="non-scaling-stroke" opacity="{op}" transform="translate(0,{dy})"/>'
        for op, dy in ((".45", 54), (".28", 104)))
    return f'''<section class="hero">
  {img(h["foto"], "100vw", "hero__foto", lazy=False)}
  <div class="hero__velo"></div>
  <div class="hero__trazos" aria-hidden="true">
    <svg class="eco" viewBox="0 0 1200 400" preserveAspectRatio="none">{ecos}</svg>
    <svg viewBox="0 0 1200 400" preserveAspectRatio="none">
      <path class="trazo-vivo" pathLength="1" d="{ONDA}" fill="none" stroke="var(--sobre-foto)" stroke-width="2.4" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    </svg>
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


def quienes():
    q = D["quienes"]
    return f'''<section class="seccion" id="quienes">
  <p class="margen seccion__margen">{e(q["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(q["titulo"])}</h2>
    <p class="bajada">{e(q["copy"])}</p>
  </div>
  <div class="quienes__cierre"><p class="cita">{e(q["cierre"])}</p></div>
</section>'''


def universo():
    u = D["universo"]
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
    return f'''<section class="seccion" id="universo">
  <h2 class="titulo titulo--bordo" data-letras>{e(u["titulo"])}</h2>
  <p class="bajada" style="max-width:42ch;margin-top:1.25rem">{e(u["intro"])}</p>
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
</section>'''


def metodo():
    m = D["metodo"]
    nodos = "".join(
        f'<div class="metodo__nodo" style="--x:{p["x"]}%;--y:{p["y"]}%"'
        f'{" data-arriba" if p["arriba"] else ""}><span>{e(p["nombre"])}</span></div>'
        for p in m["pasos"])
    lista = '<span class="metodo__punto" aria-hidden="true"></span>'.join(
        f'<span class="metodo__paso">{e(p["nombre"])}</span>' for p in m["pasos"])
    return f'''<section class="seccion" id="metodo">
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
  <div class="metodo__lista">{lista}</div>
</section>'''


def espacio():
    s = D["espacio"]
    return f'''<section class="seccion" id="espacio">
  <p class="margen seccion__margen">{e(s["margen"])}</p>
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(s["titulo"])}</h2>
    <div>
      <p class="bajada">{e(s["copy"])}</p>
      <p class="espacio__nota">{e(s["nota"])}</p>
      <a class="subrayado subrayado--bordo espacio__cta" href="{e(s["cta"]["href"])}" target="_blank" rel="noopener">{e(s["cta"]["rotulo"])}</a>
    </div>
  </div>
  <div class="hueco espacio__hueco">
    <p class="hueco__rotulo">{e(s["hueco"]["rotulo"])}</p>
    <p class="hueco__texto">{e(s["hueco"]["texto"])}</p>
  </div>
</section>'''


def proyectos():
    p = D["proyectos"]
    d = p["destacado"]
    fichas = []
    for f in p["estante"]:
        velo = ""
        if f.get("velo"):
            velo = ('<div class="ficha__velo"></div>'
                    f'<p class="ficha__sobretexto">{e(f["velo"])}</p>')
        fichas.append(
            f'<figure class="ficha{" ficha--bn" if f.get("bn") else ""}">'
            f'<div class="ficha__marco">{img(f["foto"], "(min-width:64rem) 22rem, 15rem")}{velo}</div>'
            f'<figcaption class="ficha__epigrafe">{e(f["epigrafe"])}</figcaption></figure>')
    fichas.append(
        f'<figure class="ficha"><div class="hueco ficha__hueco">'
        f'<p class="hueco__texto">{e(p["hueco"]["texto"])}</p></div>'
        f'<figcaption class="ficha__epigrafe">{e(p["hueco"]["epigrafe"])}</figcaption></figure>')
    return f'''<section class="seccion" id="proyectos">
  <p class="margen seccion__margen">{e(p["margen"])}</p>
  <div class="seccion__cabeza seccion__cabeza--pie">
    <h2 class="titulo" data-letras>{e(p["titulo"])}</h2>
    <p class="bajada">{e(p["intro"])}</p>
  </div>
  <article class="proyecto">
    {img(d["foto"], "(min-width:64rem) 76vw, 100vw", "proyecto__foto")}
    <div class="proyecto__velo"></div>
    <p class="proyecto__rotulo">{e(d["rotulo_foto"])}</p>
    <div class="proyecto__pie">
      <h3 class="proyecto__nombre">{e(d["nombre"])}</h3>
      <p class="proyecto__meta">{e(d["meta"])}</p>
      <a class="subrayado subrayado--claro" href="{e(d["href"])}">{e(d["cta"])}</a>
    </div>
  </article>
  <div class="estante">{"".join(fichas)}</div>
</section>'''


def red():
    r = D["red"]
    nodos = "".join(
        f'<p class="red__nodo" data-peso="{n["peso"]}" '
        f'style="--x:{n["x"]}%;--y:{n["y"]}%;--sangria:{n["sangria"]}px">{e(n["nombre"])}</p>'
        for n in r["nodos"])
    return f'''<section class="seccion red" id="red">
  <h2 class="titulo" data-letras>{e(r["titulo"])}</h2>
  <p class="bajada" style="max-width:44ch;margin-top:1.25rem">{e(r["copy"])}</p>
  <div class="red__nube">{nodos}</div>
  <p class="cita red__cierre">{e(r["cierre"])}</p>
</section>'''


def mirada():
    m = D["mirada"]
    return f'''<section class="seccion" id="mirada">
  <div class="seccion__cabeza">
    <h2 class="titulo" data-letras>{e(m["titulo"])}</h2>
    <p class="bajada">{e(m["intro"])}</p>
  </div>
  <div class="mirada__hueco"><p>{e(m["hueco"])}</p></div>
</section>'''


def contacto():
    c = D["contacto"]
    cd = D["contacto_datos"]
    correo = (f'<a class="subrayado subrayado--tenue" href="mailto:{e(cd["correo"])}">{e(cd["correo"])}</a>'
              if cd["correo"] else "")
    return f'''<section class="seccion contacto" id="contacto">
  <p class="contacto__apertura">{e(c["apertura"])}</p>
  <h2 class="contacto__titulo" data-letras>{e(c["titulo"])}</h2>
  <div class="contacto__acciones">
    <a class="boton" href="{e(wa(c["wa_reunion"]))}" target="_blank" rel="noopener">{e(c["cta_reunion"])}</a>
    <a class="subrayado" href="{e(wa(c["wa_general"]))}" target="_blank" rel="noopener">{e(c["cta_wa"])}</a>
    {correo}
  </div>
</section>'''


def pie():
    m, idi = D["marca"], D["idiomas"]
    redes = "".join(
        (f'<a href="{e(r["href"])}" target="_blank" rel="noopener">{e(r["nombre"])}</a>'
         if r["href"] else f'<span>{e(r["nombre"])}</span>')
        for r in D["redes"])
    return f'''<footer class="pie">
  <img class="pie__iso" src="../img/isotipo.webp" alt="{e(m["nombre"])}" width="600" height="381" loading="lazy" decoding="async">
  <nav class="pie__redes" aria-label="Redes">{redes}</nav>
  <div class="pie__abajo">
    <p class="pie__lugar">{e(m["lugar"])}</p>
    <span class="idioma"><span class="idioma__on">{e(idi["es"]["rotulo"])}</span><span class="idioma__sep" aria-hidden="true">/</span><span class="idioma__off" title="{e(D["interfaz"]["en_pendiente"])}">{e(idi["en"]["rotulo"])}</span></span>
  </div>
</footer>'''


# --------------------------------------------------------------------------- #

def datos_estructurados():
    """Ficha de la organización para Google. Sólo lo que está confirmado: el
    correo y el WhatsApp quedan afuera hasta que Vero los confirme."""
    m = D["marca"]
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": m["nombre"],
        "url": URL,
        "description": m["definicion"],
        "logo": "https://davidtaranto96.github.io/mavenz-web/img/logo-horizontal.webp",
        "address": {"@type": "PostalAddress", "addressLocality": "Salta",
                    "addressRegion": "Salta", "addressCountry": "AR"},
        "areaServed": {"@type": "AdministrativeArea", "name": "Salta, Argentina"},
    }


def pagina():
    m, ui, c = D["marca"], D["interfaz"], D["contacto"]
    titulo = f'{m["nombre"]} — {m["mensaje"]}'
    return f'''<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(m["definicion"])} {e(D["hero"]["apoyo"])}">
<meta name="theme-color" content="#eeecec">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_AR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(m["definicion"])}">
<meta property="og:image" content="https://davidtaranto96.github.io/mavenz-web/img/aerea-dia-1600.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.png">
<link rel="preload" href="../fuente/urbanist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="estilos.css">
<script type="application/ld+json">{json.dumps(datos_estructurados(), ensure_ascii=False)}</script>
</head>
<body>
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cms("cabecera", cabecera())}
<main class="contenido" id="contenido">
{cms("hero", hero())}
<div class="dossier"><div class="dossier__interior">
{cms("quienes", quienes())}
{cms("universo", universo())}
{cms("metodo", metodo())}
{cms("espacio", espacio())}
{cms("proyectos", proyectos())}
{cms("red", red())}
{cms("mirada", mirada())}
{cms("contacto", contacto())}
</div></div>
</main>
{cms("pie", pie())}
<a class="wa" href="{e(wa(c["wa_general"]))}" target="_blank" rel="noopener" aria-label="{e(ui["whatsapp"])}">
  <span class="wa__punto" aria-hidden="true"></span>{e(ui["whatsapp"])}
</a>
<script src="guion.js" defer></script>
</body>
</html>
'''


def main():
    (AQUI / "index.html").write_text(pagina(), encoding="utf-8")
    print("index.html armado desde contenido/sitio.json")


if __name__ == "__main__":
    main()
