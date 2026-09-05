#!/usr/bin/env python3
"""
armar.py — genera index.html (castellano) y en.html (inglés) desde contenido/.

    python3 armar.py

La regla de la casa: un dato vive en un solo lugar. El HTML que queda en el
repo es el HTML final (se abre y se ve lo que ve la persona), pero nunca se
edita a mano: se toca el JSON y se vuelve a correr esto. Cada región que sale
del JSON queda envuelta en <!--cms:nombre--> ... <!--/cms:nombre--> para que
el panel de edición de web-editable pueda regenerarla sola más adelante.

Sin dependencias. Python 3.8+.
"""
import json
import html as H
from pathlib import Path

AQUI = Path(__file__).parent
ES = json.loads((AQUI / "contenido/sitio.json").read_text(encoding="utf-8"))
EN = json.loads((AQUI / "contenido/sitio.en.json").read_text(encoding="utf-8"))

URL_BASE = "https://davidtaranto96.github.io/mavenz-web/v3/"


def fundir(base, encima):
    """Mezcla profunda: lo que está en `encima` pisa a `base`, clave por clave.
    Las listas se reemplazan enteras (un menú traducido es un menú entero)."""
    if isinstance(base, dict) and isinstance(encima, dict):
        salida = dict(base)
        for k, v in encima.items():
            salida[k] = fundir(base.get(k), v) if k in base else v
        return salida
    return encima if encima is not None else base


def e(texto):
    return H.escape(str(texto), quote=True)


def cms(nombre, contenido):
    return f"<!--cms:{nombre}-->\n{contenido}\n<!--/cms:{nombre}-->"


def img(foto, sizes, clase="", lazy=True, extra=""):
    """<img> con srcset por los anchos que existen en img/. El alto y el ancho
    reales van en los atributos para que el navegador reserve el lugar."""
    anchos = foto["anchos"]
    srcset = ", ".join(f'{foto["src"]}-{w}.webp {w}w' for w in anchos)
    mayor = anchos[-1]
    carga = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    return (f'<img class="{clase}" src="{foto["src"]}-{mayor}.webp" srcset="{srcset}" '
            f'sizes="{sizes}" alt="{e(foto["alt"])}" width="{foto["ancho"]}" height="{foto["alto"]}"{carga}{extra}>')


# El trazo de la marca: la M como un solo trazo (assets/marca/trazo.svg).
TRAZO = ('<svg viewBox="0 0 1200 400" preserveAspectRatio="none" aria-hidden="true">'
         '<path pathLength="1" fill="none" d="M 40 296 C 44 148, 206 96, 302 178 '
         'C 382 246, 322 336, 240 302 C 168 272, 288 196, 516 258 C 642 292, 700 138, 832 158 '
         'C 936 174, 898 298, 1002 314 C 1082 326, 1142 300, 1178 272"/></svg>')

# El isotipo como SVG con currentColor, para el centro de la rueda (el PNG
# queda para el pie: ninguna imagen repetida).
ISOTIPO = (AQUI / "../assets/marca/isotipo.svg").read_text(encoding="utf-8").strip().replace('<svg ', '<svg class="rueda__iso" ', 1)

FLECHA = ('<svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">'
          '<path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" '
          'stroke-linecap="round" stroke-linejoin="round"/></svg>')

WA_ICONO = ('<svg viewBox="0 0 24 24" aria-hidden="true" width="26" height="26" fill="currentColor">'
            '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 0 1 0 16.4c-1.5 0-3-.4-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zm-3.2 4.4c-.2 0-.5 0-.7.3-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2 3.2 5 4.4 2.5 1 3 .8 3.5.7.5 0 1.7-.7 2-1.4.2-.7.2-1.3.1-1.4l-.5-.3-1.9-.9c-.3-.1-.5-.2-.7.2l-.9 1.1c-.2.2-.3.2-.6.1a6.7 6.7 0 0 1-3.4-3c-.2-.4 0-.5.2-.7l.5-.6.3-.5c.1-.2 0-.4 0-.5l-.9-2.1c-.2-.6-.5-.5-.7-.5h-.5z"/></svg>')


def cabecera(d, lang):
    m = d["marca"]; ui = d["interfaz"]; idi = d["idiomas"]
    items = "".join(f'<li><a href="#{i["id"]}">{e(i["rotulo"])}</a></li>' for i in d["menu"])
    otro = "en" if lang == "es" else "es"
    return f'''<header class="cabecera" data-cabecera>
  <a class="marca" href="#inicio" aria-label="{e(m["nombre"])}">
    <img src="../assets/marca/logo-horizontal-oscuro.png" alt="{e(m["nombre"])}" width="132" height="36" loading="eager" decoding="async">
  </a>
  <button class="abrir-menu" type="button" aria-expanded="false" aria-controls="menu" data-abrir data-cerrar="{e(ui["cerrar"])}">{e(ui["menu"])}</button>
  <nav id="menu" class="menu" aria-label="Principal" data-menu>
    {cms("menu", f"<ul>{items}</ul>")}
    <div class="menu__pie">
      <a class="boton" href="#contacto">{e(m["cta_reunion"])}</a>
      <a class="idioma" href="{e(idi[otro]["href"])}" hreflang="{otro}" lang="{otro}" aria-label="{e(ui["idioma"])}: {e(idi[otro]["rotulo"])}">{e(idi[otro]["rotulo"])}</a>
    </div>
  </nav>
</header>'''


def hero(d):
    h = d["hero"]; m = d["marca"]; ui = d["interfaz"]
    return f'''<section class="hero" id="inicio">
  <div class="hero__medio" data-onda>
    <img class="hero__poster" src="{h["poster"]}" alt="" width="1600" height="900" loading="eager" fetchpriority="high" decoding="async">
    <video class="hero__video" data-video-dif data-src="{h["video"]}" muted playsinline preload="none" width="1600" height="900" tabindex="-1" aria-hidden="true"></video>
    <div class="trazo trazo--hero" aria-hidden="true">{TRAZO}</div>
    <button class="hero__otra" type="button" data-otra-onda hidden>{e(ui["ver_onda"])}</button>
  </div>
  <div class="hero__papel">
    {cms("hero", f"""<h1 data-fx="letras">{e(h["titulo"])}</h1>
    <p class="hero__bajada">{e(h["bajada"])}</p>
    <p class="hero__apoyo">{e(h["apoyo"])}</p>
    <div class="acciones">
      <a class="boton" href="{e(h["cta1"]["href"])}">{e(h["cta1"]["rotulo"])}</a>
      <a class="enlace" href="{e(h["cta2"]["href"])}">{e(h["cta2"]["rotulo"])} {FLECHA}</a>
    </div>""")}
    {cms("hero-margen", f"""<p class="margen">
      <span>{e(m["lugar"])}</span>
      <span lang="en">{e(m["claim_en"])}</span>
    </p>""")}
  </div>
</section>'''


def quienes(d):
    q = d["quienes"]; ui = d["interfaz"]
    indice = "".join(f'<li><a href="#universo">{e(s["corto"])}</a></li>' for s in d["universo"]["esferas"])
    return f'''<section class="articulo" id="quienes" data-entra="izq">
  <div class="envase articulo__grilla">
    {cms("quienes", f"""<h2 class="titulo reveal" data-fx="letras">{e(q["titulo"])}</h2>
    <div class="articulo__cuerpo">
      <p class="prosa reveal">{e(q["copy"])}</p>
      <p class="cita reveal">{e(q["cierre"])}</p>
    </div>""")}
    <aside class="articulo__margen reveal">
      {cms("quienes-margen", f"""<p>{e(d["marca"]["lugar"])}</p>
      <p>{e(ui["capacidades_indice"])}</p>
      <ol>{indice}</ol>""")}
    </aside>
    <figure class="foto foto--bn articulo__foto" class="reveal">
      {cms("quienes-foto", img(q["foto"], "(min-width: 64rem) 44vw, 100vw", "foto__img"))}
    </figure>
  </div>
</section>'''


def banda(n):
    # El reveal va en el envase y el recorte en la imagen hija: el observer
    # no dispara sobre un elemento cuyo clip-path lo deja en cero de ancho.
    return (f'<div class="banda reveal" aria-hidden="true" data-entra="cortina">'
            f'<img src="img/banda-{n}.webp" alt="" width="1600" height="466" loading="lazy" decoding="async"></div>')


def universo(d):
    u = d["universo"]; ui = d["interfaz"]
    cartas = ""
    for i, s in enumerate(u["esferas"]):
        clase = "carta carta--destacada" if s.get("destacada") else "carta"
        cartas += (f'<li class="{clase}" data-corto="{e(s["corto"])}" style="--i:{i}">'
                   f'<span class="carta__n">{i + 1} {e(ui["de"])} {len(u["esferas"])}</span>'
                   f'<h3>{e(s["nombre"])}</h3><p>{e(s["copy"])}</p></li>')
    return f'''<section class="universo" id="universo">
  <div class="envase">
    <div class="cabecera-seccion">
      {cms("universo", f"""<h2 class="titulo reveal" data-fx="letras">{e(u["titulo"])}</h2>
      <p class="entrada reveal">{e(u["intro"])}</p>""")}
    </div>

    <div class="rueda-marco" data-rueda-marco>
      <div class="rueda" data-rueda role="tablist" aria-label="{e(u["titulo"])}">
        <svg class="rueda__pista" viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="46" pathLength="100"/>
          <circle class="rueda__arco" cx="50" cy="50" r="46" pathLength="100" stroke-dasharray="0 100" transform="rotate(-90 50 50)"/>
        </svg>
        <div class="rueda__centro" aria-hidden="true">
          {ISOTIPO}
          <span class="rueda__corto" data-corto-activo></span>
        </div>
      </div>
      <div class="rueda__detalle" data-detalle>
        <span class="rueda__cuenta" data-cuenta></span>
        <div class="rueda__cuerpo"><h3></h3><p></p></div>
        <div class="rueda__mandos">
          <button type="button" class="mando" data-anterior aria-label="{e(ui["anterior"])}">{FLECHA}</button>
          <button type="button" class="mando" data-siguiente aria-label="{e(ui["siguiente"])}">{FLECHA}</button>
        </div>
      </div>
    </div>

    {cms("universo-esferas", f'<ol class="cartas" data-cartas>{cartas}</ol>')}

    <p class="acciones acciones--seccion" class="reveal">
      {cms("universo-cta", f'<a class="boton" href="{e(u["cta"]["href"])}">{e(u["cta"]["rotulo"])}</a>')}
    </p>
  </div>
</section>'''


def metodo(d):
    m = d["metodo"]; ui = d["interfaz"]
    pasos = "".join(
        f'<li class="paso reveal" style="--i:{i};--fila:{i // 2};--col:{i % 2 + 1}"><span class="paso__n" data-nodo aria-label="{e(ui["paso"])} {e(p["n"])}">{e(p["n"])}</span>'
        f'<h3>{e(p["nombre"])}</h3><p>{e(p["copy"])}</p></li>'
        for i, p in enumerate(m["pasos"]))
    return f'''<section class="metodo" id="metodo">
  <div class="envase">
    <div class="cabecera-seccion">
      {cms("metodo", f"""<h2 class="titulo reveal" data-fx="letras">{e(m["titulo"])}</h2>
      <p class="entrada reveal">{e(m["intro"])}</p>""")}
    </div>
    <div class="hilo" data-hilo>
      <svg class="hilo__trazo" aria-hidden="true"><path pathLength="1" fill="none"/></svg>
      {cms("metodo-pasos", f'<ol class="pasos">{pasos}</ol>')}
    </div>
  </div>
</section>'''


def espacio(d):
    s = d["espacio"]; ui = d["interfaz"]
    usos = "".join(f'<div class="uso reveal"><h3>{e(u["nombre"])}</h3><p>{e(u["copy"])}</p></div>' for u in s["usos"])
    pend = s["pendientes"]
    return f'''<section class="espacio" id="espacio" data-entra="der">
  <div class="envase espacio__grilla">
    <div class="espacio__texto">
      {cms("espacio", f"""<h2 class="titulo reveal" data-fx="letras">{e(s["titulo"])}</h2>
      <p class="prosa reveal">{e(s["copy"])}</p>
      {usos}
      <p class="acciones reveal"><a class="boton" href="{e(s["cta"]["href"])}" rel="noopener">{e(s["cta"]["rotulo"])}</a></p>""")}
    </div>
    <div class="espacio__lugar">
      <div class="falta falta--foto" class="reveal"><span class="pendiente">{e(pend[0])}: {e(ui["pendiente"])}</span></div>
      <div class="falta falta--lista" class="reveal"><span class="pendiente">{e(pend[1])}: {e(ui["pendiente"])}</span></div>
    </div>
  </div>
</section>'''


def proyectos(d):
    p = d["proyectos"]; r = p["rotulos"]; ui = d["interfaz"]
    salida = ""
    for it in p["items"]:
        sueltas = "".join(
            f'<figure class="foto suelta suelta--{i + 1}" class="reveal">{img(f, "(min-width: 64rem) 34vw, 72vw", "foto__img")}</figure>'
            for i, f in enumerate(it["fotos"]))
        salida += f'''<article class="dossier" data-entra="escala">
      <figure class="foto foto--velo dossier__portada" class="reveal">
        {img(it["portada"], "(min-width: 64rem) 62vw, 100vw", "foto__img")}
        <figcaption class="dossier__nombre"><span>{e(it["nombre"])}</span><span>{e(it["ubicacion"])}</span></figcaption>
      </figure>
      <div class="dossier__ficha" class="reveal">
        <p class="cita">{e(it["frase"])}</p>
        <dl class="ficha">
          <div><dt>{e(r["rol"])}</dt><dd>{e(it["rol"])}</dd></div>
          <div><dt>{e(r["estado"])}</dt><dd>{e(it["estado"])}</dd></div>
        </dl>
        <a class="enlace" href="{e(it["href"])}">{e(it["cta"])} {FLECHA}</a>
      </div>
      <div class="mesa estante" data-estante aria-label="{e(r["fotos"])}: {e(it["nombre"])}">{sueltas}</div>
    </article>'''
    return f'''<section class="proyectos" id="proyectos">
  <div class="envase">
    <div class="cabecera-seccion">
      {cms("proyectos", f"""<h2 class="titulo reveal" data-fx="letras">{e(p["titulo"])}</h2>
      <p class="entrada reveal">{e(p["intro"])}</p>""")}
    </div>
    {cms("proyectos-items", salida)}
    <p class="falta falta--linea" class="reveal"><span class="pendiente">{e(p["pendiente"])}</span></p>
  </div>
</section>'''


def red(d):
    r = d["red"]; ui = d["interfaz"]
    return f'''<section class="articulo red" id="red" data-entra="izq">
  <div class="envase articulo__grilla">
    {cms("red", f"""<h2 class="titulo reveal" data-fx="letras">{e(r["titulo"])}</h2>
    <div class="articulo__cuerpo">
      <p class="prosa reveal">{e(r["copy"])}</p>
      <p class="cita reveal">{e(r["cierre"])}</p>
    </div>""")}
    <div class="falta falta--foto articulo__foto" class="reveal"><span class="pendiente">{e(r["pendiente"])}: {e(ui["pendiente"])}</span></div>
  </div>
</section>'''


def mirada(d):
    m = d["mirada"]
    notas = "".join(
        f'<li class="nota reveal"><span class="nota__meta">{e(n["meta"])}</span>'
        f'<h3>{e(n["titulo"])}</h3><p>{e(n["bajada"])}</p></li>' for n in m["notas"])
    cta = m["cta"]
    href = cta["href"] or "#contacto"
    return f'''<section class="mirada" id="mirada">
  <div class="envase">
    <div class="cabecera-seccion">
      {cms("mirada", f"""<h2 class="titulo reveal" data-fx="letras">{e(m["titulo"])}</h2>
      <p class="entrada reveal">{e(m["intro"])}</p>""")}
    </div>
    {cms("mirada-notas", f'<ol class="notas">{notas}</ol>')}
    <p class="acciones acciones--seccion" class="reveal">
      <a class="enlace" href="{e(href)}">{e(cta["rotulo"])} {FLECHA}</a>
      <span class="pendiente">{e(m["pendiente"])}</span>
    </p>
  </div>
</section>'''


def contacto(d):
    c = d["contacto"]; f = c["form"]; cd = d["contacto_datos"]
    opciones = "".join(f'<option value="{e(o["rotulo"])}">{e(o["rotulo"])}</option>' for o in c["opciones"])
    return f'''<section class="contacto" id="contacto" data-entra="der">
  <div class="envase contacto__grilla">
    <div>
      {cms("contacto", f"""<h2 class="titulo reveal" data-fx="letras">{e(c["titulo"])}</h2>
      <p class="prosa reveal">{e(c["cierre"])}</p>""")}
    </div>
    <form class="formulario reveal" data-formulario data-whatsapp="{e(cd["whatsapp"])}" data-falta="{e(f["falta"])}" data-listo="{e(f["listo"])}" data-sin-numero="{e(f["sin_numero"])}" novalidate>
      {cms("contacto-form", f"""<label><span>{e(f["motivo"])}</span>
        <select name="motivo" id="motivo">{opciones}</select></label>
      <label><span>{e(f["nombre"])}</span><input type="text" name="nombre" autocomplete="name" required></label>
      <label><span>{e(f["contacto"])}</span><input type="text" name="contacto" autocomplete="tel" inputmode="email" required></label>
      <label><span>{e(f["mensaje"])}</span><textarea name="mensaje" rows="3"></textarea></label>
      <button class="boton" type="submit">{e(f["enviar"])}</button>""")}
      <p class="aviso" data-aviso aria-live="polite"></p>
    </form>
  </div>
</section>'''


def pie(d, lang):
    m = d["marca"]; ui = d["interfaz"]; idi = d["idiomas"]
    redes = ""
    for r in d["redes"]:
        if r["href"]:
            redes += f'<li><a href="{e(r["href"])}" rel="noopener">{e(r["nombre"])}</a></li>'
        else:
            redes += f'<li><span>{e(r["nombre"])}</span> <span class="pendiente">{e(ui["pendiente"])}</span></li>'
    idiomas = "".join(
        f'<li><a href="{e(v["href"])}" hreflang="{k}" lang="{k}"{" aria-current=\"true\"" if k == lang else ""}>{e(v["rotulo"])}</a></li>'
        for k, v in idi.items() if not k.startswith("_"))
    return f'''<footer class="pie">
  <div class="trazo trazo--pie" aria-hidden="true">{TRAZO}</div>
  <div class="envase pie__grilla">
    <img class="pie__iso" src="../assets/marca/isotipo-oscuro.png" alt="{e(m["nombre"])}" width="600" height="381" loading="lazy" decoding="async">
    {cms("pie", f"""<p class="pie__claim" lang="en">{e(m["claim_en"])}</p>
    <ul class="pie__redes">{redes}</ul>
    <p class="pie__lugar">{e(m["nombre"])} · {e(m["lugar"])}</p>""")}
    <ul class="pie__idiomas" aria-label="{e(ui["idioma"])}">{idiomas}</ul>
  </div>
</footer>'''


def pagina(d, lang):
    m = d["marca"]; ui = d["interfaz"]; cd = d["contacto_datos"]
    titulo = f'{m["nombre"]} — {m["mensaje"].rstrip(".")}'
    otro = "en" if lang == "es" else "es"
    aviso_en = ""
    if d.get("_pendiente"):
        aviso_en = f'<p class="aviso-idioma" role="status"><span class="pendiente">{e(d["_aviso"])}</span></p>'
    wa_href = f'https://wa.me/{cd["whatsapp"]}' if cd["whatsapp"] else "#contacto"
    wa_extra = ' target="_blank" rel="noopener"' if cd["whatsapp"] else ""
    return f'''<!DOCTYPE html>
<html lang="{"es-AR" if lang == "es" else "en"}" class="sin-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(m["definicion"])} {e(d["hero"]["apoyo"])}">
<meta name="theme-color" content="#eeecec">
<link rel="canonical" href="{URL_BASE}{"" if lang == "es" else "en.html"}">
<link rel="alternate" hreflang="es" href="{URL_BASE}">
<link rel="alternate" hreflang="en" href="{URL_BASE}en.html">
<meta property="og:type" content="website">
<meta property="og:locale" content="{"es_AR" if lang == "es" else "en"}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(m["definicion"])}">
<meta property="og:image" content="https://davidtaranto96.github.io/mavenz-web/assets/video/ondas.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../demo/favicon.png">
<link rel="preload" href="../assets/marca/Urbanist-Variable.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="estilos.css">
<noscript><style>.reveal,[data-fx~="letras"] span{{opacity:1!important;translate:none!important;scale:none!important;clip-path:none!important}} .rueda-marco{{display:none!important}} .cartas{{display:grid!important}}</style></noscript>
<script>
/* El estado oculto del reveal se marca antes del primer pintado, para que no
   parpadee. El seguro lo saca si el guion nunca arrancó: mejor sin
   animación que con la página en blanco. */
(function(d){{
  d.classList.remove('sin-js'); d.classList.add('js');
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  d.classList.add('fx-on');
  setTimeout(function(){{ if (!d.dataset.fxVivo) d.classList.remove('fx-on') }}, 3000);
}})(document.documentElement);
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"ProfessionalService","name":"{e(m["nombre"])}","description":"{e(m["definicion"])}","areaServed":{{"@type":"State","name":"{e(m["lugar"])}"}},"address":{{"@type":"PostalAddress","addressLocality":"Salta","addressCountry":"AR"}},"url":"{URL_BASE}","slogan":"{e(m["mensaje"])}"}}
</script>
</head>
<body>
<a class="saltar" href="#contenido">{e(ui["saltar"])}</a>
{cabecera(d, lang)}
{aviso_en}
<main id="contenido">
{hero(d)}
{quienes(d)}
{banda(1)}
{universo(d)}
{metodo(d)}
{espacio(d)}
{banda(2)}
{proyectos(d)}
{red(d)}
{mirada(d)}
{contacto(d)}
</main>
{pie(d, lang)}
<a class="wa" href="{wa_href}"{wa_extra} aria-label="{e(ui["whatsapp"])}">{WA_ICONO}</a>
<script src="guion.js" defer></script>
</body>
</html>
'''


def main():
    (AQUI / "index.html").write_text(pagina(ES, "es"), encoding="utf-8")
    (AQUI / "en.html").write_text(pagina(fundir(ES, EN), "en"), encoding="utf-8")
    print("listo: index.html y en.html")


if __name__ == "__main__":
    main()
