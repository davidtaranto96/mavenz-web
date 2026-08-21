# demo — home de Mavenz

Base generada en Claude Design, extraída del lienzo y con efectos aplicados.

## Directivas de Claude Design que hubo que resolver

El `.dc.html` es un documento de lienzo, no una página publicable. Trae directivas de plantilla que
solo entiende `support.js`. Al sacarlo, cada una rompe de una forma distinta:

| Directiva | Qué pasaba sin `support.js` | Cómo se resolvió |
|---|---|---|
| `<sc-if value="{{ x }}">` | **Se renderizaban las dos ramas.** Por eso aparecían el video y la foto aérea uno abajo del otro | Se resolvieron los 12 estáticamente, según su `hint-placeholder-val` |
| `<x-import from="./mapa-mavenz.js">` | El mapa nunca cargaba | Reemplazado por `<mapa-mavenz>` más su `<script>` |
| `<x-dc><helmet>` | Los `<link>` y `<script>` quedaban dentro del `<body>` | Movidos al `<head>` y desarmados los envoltorios |
| `autoPlay="{{ true }}"` | Atributos estilo React. **Sin `muted` real el navegador bloquea la reproducción** | Pasados a atributos HTML |
| `onClick="{{ sel.micro }}"` | Los seis botones del Mapa no hacían nada, y `color:{{ c.micro }}` era un color inválido | Cableados con `data-terr` a los eventos `mavenz:flyto` y `mavenz:territory` |

## Qué se hizo sobre la salida de Claude Design

1. **Se sacó `support.js`.** Es el runtime del lienzo de Claude Design: envuelve todo en un
   `<div overflow-y:auto>` y por eso los reveals no disparaban. Sin él la página scrollea normal.
2. **Se separaron los tres heroes.** El `.dc.html` traía tres variantes con el mismo `id="inicio"`.
   Quedó el cinematográfico; los otros dos están en `variantes-hero.html` para comparar.
3. **Efectos** con `dt-efectos`: reveal alternando dirección por sección, header reactivo al scroll,
   foco visible, `scroll-padding-top`, y carga diferida de imágenes.
4. **Bloque de `prefers-reduced-motion`**, que no estaba.

## Puntaje de vida

47/100 → **95/100** (`efectos-web/scripts/auditar_efectos.py`)

## Verificado

En 1280 y en 375, scrolleando de verdad:

| Chequeo | Resultado |
|---|---|
| Errores de consola | 0 |
| Recursos que fallan | 0 |
| Imágenes rotas | 0 |
| Marcadores de plantilla sin resolver | 0 |
| Elementos que quedan ocultos | 0 de 7 |
| Scroll horizontal | no |
| Video | reproduciendo, `muted`, `loop` |
| Mapa Leaflet | vivo, 8 marcadores, 6 botones cableados |

Con `prefers-reduced-motion: reduce`: 0 ocultos, todo el contenido visible.

## Pendiente para la 2.0

El 65% de la superficie es marrón oscuro y solo el 18% clara. Hay que subir la proporción de claro.
El prompt para la segunda pasada está en `../prompt-claude-design-2.md`.

---

## Dos pasadas de mejora (21/08/2026)

### Pasada 1 — luz y contraste

La página era **61% marrón oscuro y 23% clara**. Se invirtió: el hero, el Mapa y el footer quedan
como anclajes oscuros; el Manifiesto, el Método, los Proyectos, Espacio Mavenz y el Contacto pasan
a blanco.

Al voltear los fondos aparecieron 15 fallas de contraste, incluidas algunas que introdujo el propio
cambio: texto oscurecido que vivía sobre tarjetas oscuras dentro de secciones claras. Se corrigió
por superficie, no por elemento.

| | Antes | Después |
|---|---|---|
| Superficie oscura | 61% | **29%** |
| Superficie clara | 23% | **57%** |
| Fallas de contraste WCAG | 15 | **0** |

### Pasada 2 — funciones y oficio

Del dossier de `subir-nivel` faltaban once funciones. Se sumaron las de mayor impacto:

- **Botón de WhatsApp flotante**, que aparece pasado el hero. En Argentina es el canal que convierte.
- **Formulario de contacto** con validación real y salida a WhatsApp con el mensaje armado.
- **`og:image`**, para que el link no salga gris al compartirlo. Ahí se juega media conversión.
- **Favicon** desde el isotipo.
- **JSON-LD `RealEstateAgent`** con los territorios que cubren.
- **Lightbox** en renders, fotos de proyecto y planos, accesible por teclado.
- **Header reactivo** al scroll y entrada palabra por palabra en un solo titular, el del cierre.
- **Tracking por tamaño**: negativo en display, cero en cuerpo. Un `letter-spacing` único está mal
  en algún lado siempre.

## Verificación final

| Chequeo | 1280px | 375px |
|---|---|---|
| Fallas de contraste | 0 | 0 |
| Errores de consola | 0 | 0 |
| Recursos que fallan | 0 | 0 |
| Imágenes rotas | 0 | 0 |
| Scroll horizontal | no | no |
| Elementos que quedan ocultos | 0 | 0 |
| Video | reproduciendo | reproduciendo |
| Mapa Leaflet | 8 marcadores | 8 marcadores |

Puntaje de vida: **88/100** (`efectos-web`). Con `prefers-reduced-motion`, todo el contenido visible.

---

## 3.0 — los efectos

Todo lo de abajo vive en `mavenz-fx.css` + `mavenz-fx.js`. **HTML/CSS/JS puro, cero
dependencias, cero build.** Se copian los dos archivos y andan.

### Por qué no se instaló React Bits ni KokonutUI

Las dos son librerías de componentes **React**. Meterlas acá implicaba rehacer la demo
como app Next.js, y esta es una estática en GitHub Pages. Va contra la regla de la casa
(*nunca un framework para una web estática*) y contra el propio deploy.

Hay además un tema de licencia concreto: **React Bits es MIT + Commons Clause**. Deja
usar sus componentes en una web de cliente, pero prohíbe redistribuirlos —y el texto
aclara *"ni siquiera en versión porteada"*. Este repo es **público**, así que publicar
acá un port de su código sí sería redistribución.

Lo que se hizo: **escribir cada efecto de cero, en vanilla**, tomando la idea y el ajuste
fino de curvas y duraciones. Las tres que pidió David están las tres.

| React Bits | Acá | Qué hace |
|---|---|---|
| Specular Button | `.fx-esp` | Filo de luz en el borde, con el ángulo mandado por el puntero |
| Depth Carousel | `.fx-prof` | Fichas que retroceden en Z, no de costado |
| Flowing Menu | `.fx-flu` | Panel que entra por el canto por donde entró el puntero |
| Scroll Velocity | `.fx-cinta` | Cinta que corre sola y acelera con el scroll |
| — | `.fx-cortina` | Revelado por cortina (`clip-path`) |
| Magnet | `.fx-iman` | El botón se corre hacia el cursor |

### Cómo se usa cada uno

**Filo especular** — `class="fx-esp"` en cualquier cosa con `border-radius`. Sobre fondo
claro, sumar `fx-esp--claro` para que la luz sea la tinta y no el blanco. Un solo listener
para toda la página, con las medidas cacheadas y el trabajo dentro de un `rAF`. Radio de
activación 300px. En táctil no se monta.

**Carrusel en profundidad** — `data-fx-prof` en el contenedor, `.fx-prof__t` en cada ficha.
Se ajusta con `data-fx-z` (profundidad), `data-fx-spread` (separación), `data-fx-tilt`
(giro) y `data-fx-vis` (cuántas se ven). Arrastre, rueda **horizontal** (nunca secuestra el
scroll vertical), flechas, puntos y teclado. La posición se persigue con amortiguado
crítico: se puede agarrar a mitad de camino.

**Menú fluido** — `.fx-flu__i` por fila, con `.fx-flu__m > .fx-flu__mw > .fx-flu__in`
adentro. El panel calcula el canto más cercano al punto por donde entró el puntero y entra
por ahí; al salir, se va por el canto por donde salió. Esa es toda la diferencia entre que
se lea como una dirección o como un fundido.

**Cinta** — `.fx-cinta` con dos `.fx-cinta__g` idénticos (el segundo con `aria-hidden`).
`data-fx-vel` en px/s. Pausada mientras no se la ve.

### Reglas que se respetaron

- **Nada de bucles infinitos gratis.** Un módulo (`pausar()`) busca todo lo que tenga
  iteración infinita y lo duerme al salir del viewport. La cinta del menú fluido arranca
  pausada y solo corre con el panel abierto.
- **Solo `transform`, `opacity` y `filter`.** Los puntos del carrusel se estiran con
  `scaleX`, no con `width`: animar `width` dispara reflow en cada cuadro.
- **`prefers-reduced-motion` es bloqueante** y nunca deja contenido invisible.
- **Sin JS la página no se rompe**: el carrusel pasa a ser una fila que se scrollea, la
  cinta una fila quieta, el menú una lista. Nada desaparece.
- Nada que siga al cursor sin `@media (hover:hover) and (pointer:fine)`.

Puntaje del auditor de `efectos-web`: **82/100** (los 3 bloqueantes que quedan son
transiciones sobre layout dentro del CSS de Leaflet, no del nuestro).

---

## El isotipo como material gráfico

`assets/marca/isotipo.svg` es el isotipo trazado a un `<path>` desde el PNG del kit
(máscara alfa → contorno → Douglas-Peucker → Bézier). En la página entra una sola vez como
`<symbol id="mv-iso">` y se reusa con `<use>`.

**No es una decoración inventada.** Es exactamente lo que hace la marca en sus propias
portadas de LinkedIn y Facebook: el isotipo enorme y recortado, en dos tonos planos. De ahí
salieron también los seis pares de color oficiales.

## Material nuevo

| Archivo | De dónde salió |
|---|---|
| `video/cardinal-film.mp4` | `POST 2.mp4`, recorte superior 1920×830 entre 15,5s y 27,8s: el único tramo sin subtítulo ni marca de agua (ambos viven abajo de los 840px) |
| `video/ondas.mp4` · `agua.mp4` · `onda.mp4` | **De su propio kit**, carpeta `5. Multimedia`. Ondas que se propagan, sobre una marca que se llama Generamos movimiento |
| `vida/*.jpg` | Cuadros del mismo film: la calle, el interior con gente, la pileta, la esquina, el aéreo y el atardecer |
| `marca/carpeta.jpg` · `agenda.jpg` | Aplicaciones del kit |

**La tarjeta personal quedó afuera a propósito:** tiene teléfono y mail directos de una
persona, legibles, y este repo es público.
