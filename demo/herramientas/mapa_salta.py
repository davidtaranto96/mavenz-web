"""Arma el Mapa Mavenz con la geografia real de Salta, desde OpenStreetMap.

    python herramientas/mapa_salta.py <carpeta-con-q2-q3-q4.json>

Entra lo que devolvio Overpass (las consultas estan en herramientas/osm/):
  q2.json  los limites: municipio de Salta (2722832) y de San Lorenzo (7274360)
  q3.json  las calles principales, con sus etiquetas
  q4.json  las calles residenciales, solo la geometria

Sale:
  contenido/mapa-salta.json   el contorno, las rutas y la proyeccion. Lo lee armar.py
                              para dibujar el contorno y ubicar cada territorio por
                              su latitud y longitud (sitio.json). No se edita a mano.
  ../img/mapa-salta-calles.svg  la trama de calles, en el mismo lienzo de 1000 x 407.

Datos (c) colaboradores de OpenStreetMap, licencia ODbL: el credito va en el mapa.
Necesita shapely (pip install shapely)."""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString
from shapely.ops import linemerge, polygonize, unary_union

AQUI = Path(__file__).resolve().parent.parent          # demo/
OSM = Path(sys.argv[1])

W, H, MARGEN = 1000, 407, 16
# La caja de lo que se muestra: los dos municipios, con aire para la salida al sur.
LON_O, LON_E = -65.605, -65.335
LAT_N, LAT_S = -24.640, -24.905
K = math.cos(math.radians((LAT_N + LAT_S) / 2))
ESCALA = (H - 2 * MARGEN) / (LAT_N - LAT_S)
X0 = (W - (LON_E - LON_O) * K * ESCALA) / 2


def xy(lat, lon):
    return (X0 + (lon - LON_O) * K * ESCALA, MARGEN + (LAT_N - lat) * ESCALA)


def trazo(coords, cerrar=False):
    pts = list(coords)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return d + ("Z" if cerrar else "")


# --- El contorno: Salta y San Lorenzo unidos en una sola figura ----------
limites = json.load(open(OSM / "q2.json"))
figuras = []
for rel in limites["elements"]:
    if rel["id"] not in (2722832, 7274360):
        continue
    lineas = [LineString([xy(p["lat"], p["lon"]) for p in m["geometry"]])
              for m in rel["members"] if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
    figuras.extend(polygonize(linemerge(lineas)))
union = unary_union(figuras).buffer(0.8).buffer(-0.8).simplify(0.6)
partes = [union] if union.geom_type == "Polygon" else list(union.geoms)
partes = [p for p in partes if p.area > 200]
contorno = " ".join(trazo(p.exterior.coords, cerrar=True) for p in partes)

# --- Las calles -----------------------------------------------------------
PRINCIPALES = {"motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link", "primary_link", "secondary_link"}
principales, calles, rutas = [], [], []
for e in json.load(open(OSM / "q3.json"))["elements"]:
    geo = e.get("geometry") or []
    if len(geo) < 2:
        continue
    linea = LineString([xy(p["lat"], p["lon"]) for p in geo]).simplify(0.35)
    if linea.length < 1:
        continue
    destino = principales if e["tags"].get("highway") in PRINCIPALES else calles
    destino.append(trazo(linea.coords))
    if e["tags"].get("ref") in ("RN9", "RN68", "RN51", "RP28"):
        rutas.append(trazo(linea.coords))
for e in json.load(open(OSM / "q4.json"))["elements"]:
    geo = e.get("geometry") or []
    if len(geo) < 2:
        continue
    linea = LineString([xy(p["lat"], p["lon"]) for p in geo]).simplify(0.35)
    if linea.length < 1.2:
        continue
    calles.append(trazo(linea.coords))

# El color va en el archivo porque un SVG que entra como imagen no lee los
# tokens: es Timberwolf, el mismo --linea de estilos.css.
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
       f'<path d="{"".join(calles)}" fill="none" stroke="#D3CFC8" stroke-opacity=".30" stroke-width=".45" stroke-linecap="round" stroke-linejoin="round"/>'
       f'<path d="{"".join(principales)}" fill="none" stroke="#D3CFC8" stroke-opacity=".62" stroke-width=".9" stroke-linecap="round" stroke-linejoin="round"/>'
       f'</svg>')
(AQUI.parent / "img" / "mapa-salta-calles.svg").write_text(svg)

json.dump({
    "_dt": ("Generado por herramientas/mapa_salta.py desde OpenStreetMap (ODbL). No se edita a mano: "
            "se vuelve a correr el script. armar.py ubica cada territorio con proyeccion y sus puntos."),
    "caja": [W, H],
    "proyeccion": {"lon_oeste": LON_O, "lat_norte": LAT_N, "k": K, "escala": ESCALA, "x0": X0, "margen": MARGEN},
    "contorno": contorno,
    "rutas": "".join(rutas),
}, open(AQUI / "contenido" / "mapa-salta.json", "w"), ensure_ascii=False)

print(f"contorno: {len(partes)} figura(s), {len(contorno) // 1024} KB")
print(f"calles: {len(calles)} + {len(principales)} principales, svg {len(svg) // 1024} KB")
print(f"rutas nacionales: {len(rutas)} tramos")
