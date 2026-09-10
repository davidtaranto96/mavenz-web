# Mavenz: cinco páginas en dos idiomas

`https://davidtaranto96.github.io/mavenz-web/demo/`

Rediseño del 08 al 10/09/2026, a partir del documento que Vero mandó el 08/09 después de ver
la demo de tres páginas. La reemplaza entera. Vive en la rama `rediseno-0909` (un commit por
fase) y se publica con el merge a `main` cuando David apruebe las capturas. Las tres
referencias que ella eligió están medidas en el código: realevate.agency (la ficha de proyecto y
el menú flotante), rogo.ai (la cabecera y el hero) y era-residence.com (el aviso de cookies).

**La idea, en una línea:** papel quieto, tres bloques de tinta (el Universo en bistre, Espacio
en wenge, la ficha y la red en bordó) y un solo gesto de marca, el trazo de la M, que se dibuja
con el scroll en Cómo trabajamos y corre como cinta en el hero y en la ficha de Cardinal. Lo que
no está aprobado no se muestra: se apaga por dato en el generador, nunca con un placeholder.

---

## Las páginas

| Archivo | Cabecera | Qué tiene, en orden, con su `id` |
|---|---|---|
| `index.html` | oscura, sobre el video | hero con video y la cinta de los cinco mundos (`#inicio`) · Somos Mavenz (`#quienes`) · el puente, decorativo · El Universo Mavenz, en bistre (`#universo`) · Cómo trabajamos (`#metodo`) · Proyectos en movimiento (`#mundos`) · Mirada Mavenz con el mapa de seis territorios adentro (`#mirada`) · Movamos algo juntos (`#contacto`) |
| `proyectos.html` | clara | cinta por scroll "Proyectos" · intro · Cardinal resumido (`#cardinal`) · Otros proyectos (`#otros`, hoy no se emite) · Oportunidades de inversión (`#oportunidades`) · contacto (`#contacto`) |
| `cardinal.html` | oscura, sobre bordó | hero que se abre con el scroll, con la cinta de isotipos detrás (`#inicio`) · título con marcador, datos y aclaración (`#proyecto`) · galería escalonada (`#galeria`) · el cardenal que se dibuja · sub-items (`#detalles`, hoy no se emite) · franja de video a sangre · Unidades (`#unidades`) · Financiación, en bordó (`#financiacion`) · cierre (`#cierre`) · contacto (`#contacto`) · el visor `<dialog>` |
| `espacio.html` | clara | cinta "Espacio Mavenz" · el bloque plano en wenge (`#espacio-bloque`) · contacto (`#contacto`) |
| `nosotros.html` | clara | cinta "Nosotros" · Las personas detrás de Mavenz (`#equipo`) · La red, en bordó (`#red`) · contacto (`#contacto`) |
| `en/` | | las mismas cinco en inglés: `<html lang="en">`, canónica propia y `hreflang` es-AR / en / x-default en las diez páginas |

El menú sale de `paginas` del JSON y hoy tiene cinco entradas: Inicio · Universo Mavenz
(`#universo`, o `index.html#universo` desde otra página) · Proyectos · Espacio Mavenz ·
Contactanos (`#contacto`, que existe en todas). Lo leen la barra, el pie y el flotante desde la
misma función, `enlaces_menu()`.

**Nosotros tiene `publicar: false`**: se genera igual, con `<meta name="robots"
content="noindex">`, pero no entra al menú hasta que el equipo esté completo. **Cardinal tiene
`en_menu: false`**: no va en el menú; se llega desde la cinta del hero, desde el panel de
Proyectos en movimiento y desde el resumen de `proyectos.html`.

---

## Cómo se edita

Un dato vive en un solo lugar: `contenido/sitio.json`.

```bash
python3 armar.py                        # arma las diez páginas: ES en demo/, EN en demo/en/
python3 armar.py --plantilla en         # vuelca la estructura de textos del castellano, para rellenar
python3 armar.py --palabra movimiento   # lista cada texto que contiene la palabra, con su clave
```

**El HTML no se toca a mano.** Cada región que sale del JSON queda envuelta en
`<!--cms:nombre--> … <!--/cms:nombre-->` para que el panel de `web-editable` la pueda regenerar
sola más adelante. El CSS, el JS, los videos y sus pósters salen enlazados con `?v=` y ocho
caracteres del hash del archivo: sin eso el navegador sirve la versión vieja y una corrección no
se ve.

| Archivo | Qué es |
|---|---|
| `contenido/sitio.json` | todo: textos, fotos, videos, datos de contacto, el mapa de páginas, los idiomas, la medición |
| `contenido/sitio.en.json` | la capa en inglés: sólo textos |
| `armar.py` | el generador, sin dependencias. Una función por sección y una cáscara compartida (`cascara()`) para las diez páginas |
| `estilos.css` | tokens en `:root` y todo lo demás. Siete hex, todos en `:root`; los tres que aparecen más abajo están en comentarios |
| `guion.js` | motor de reveal, títulos letra por letra, videos diferidos, tema del flotante, visor, Lenis + GSAP, órbita, puente, trazo del método, tilt, hero de la ficha, marcadores, carrusel, cintas, formulario y el módulo del flotante |
| `consent.js` | el aviso de cookies, con su cola de eventos |
| `auditar.sh` | el auditor de siete carriles sobre las diez URLs |
| `../img/` | fotos en WebP, dos anchos cada una |
| `../video/` | `hero.mp4`, `cardinal.mp4` y `cardenal.mp4`, con póster cada uno |
| `../fuente/urbanist.woff2` | Urbanist variable, 100 a 900, 24 KB |

### La capa en inglés

`sitio.en.json` es una capa sobre `sitio.json`: **lleva sólo lo que cambia**, que son textos.
`fundir()` la mezcla clave por clave; una lista de fichas del mismo largo se funde posición por
posición, así la capa no repite fotos, ids ni tintas (repetirlos fue lo que pudrió la capa
inglesa anterior: se desincronizaba en silencio). Una lista de textos sueltos, como los `datos`
de Cardinal, se reemplaza entera. Una lista de fichas más larga que en castellano corta el
generador por ruta huérfana; una más corta ya no se funde posición por posición, se reemplaza
entera, y el generador se cae porque le faltan las fotos.

Lo que no es texto para leer no se traduce ni se reclama. Es la lista `TECNICAS` de `armar.py`:
`src`, `poster`, `href`, `id`, `tinta`, `lang`, `og`, `archivo`, `carpeta`, `ancla`, `en`,
`whatsapp`, `correo`, `sitio_espacio`, `proporcion`, `numero`, `n`, `x`, `y`, `sangria`, `peso`,
`anchos`, `ancho`, `alto`, `columnas`, `solo_visor`, `bn`, `genera`, `publicar`, `en_menu`,
`clave`, `ga4`, `pixel`, `otros_publicar`, `servicio`, `motivo`. Las claves que empiezan con `_`
tampoco.

Un nombre propio que queda igual en los dos idiomas (Cardinal, Espacio Mavenz, Salta) se declara
en `_iguales` de la capa y deja de contar como deuda.

`chequear_capas()` corre antes de generar cada idioma: **corta** si la capa tiene una ruta que no
existe en el castellano (se corrige la capa, o se corre `--plantilla en` y se rearma), y
**avisa** por cada texto del castellano que la capa no traduce. Hoy no avisa nada: la capa está
completa, con 28 entradas en `_iguales`. Completa no quiere decir aprobada: la tradujo DT System
y Mavenz la tiene que revisar (está anotado en `_revisar`).

El portugués existe en `idiomas` con `genera: false`: entra al selector como texto deshabilitado
con el título "Próximamente" y no se genera nada hasta que haya un `sitio.pt.json`.

Además, en cada corrida: `auditar_enlaces()` avisa si un `wa.me` tiene un rótulo que no dice
WhatsApp ni consulta, y si un `#ancla` no existe en su página; `comprobar_rutas()` resuelve cada
`src` y `href` relativo contra la carpeta de salida, que es lo que atrapa un `../` de más cuando
el inglés baja a `en/`.

### Lo que se apaga por dato

Cada bloque que depende de material de la clienta tiene una clave. Vacía, el generador emite
`""` y no hay placeholder.

| Clave | Qué prende |
|---|---|
| `quienes.circulos` con `fondo` y `frente` | la columna de los dos círculos de Somos Mavenz; sin ella el texto ocupa el ancho |
| `proyectos.otros_publicar` y `proyectos.otros` | la sección Otros proyectos de `proyectos.html` (hoy `false`) |
| `proyectos.cardinal.sub_items[]`, con `foto` **y** `copy` | cada sub-item de la ficha; sin ninguno completo la sección `#detalles` no existe (hoy) |
| `proyectos.cardinal.unidades.foto` | la columna de foto de Unidades |
| `proyectos.cardinal.financiacion.copy` | el párrafo de la franja de Financiación (hoy sólo título y CTA) |
| `proyectos.cardinal.cierre.titulo` | la frase del cierre de la ficha (hoy sólo el botón) |
| `espacio.foto` | la columna de foto de Espacio Mavenz (hoy `null`) |
| `equipo.personas[]` con `foto`, `nombre`, `apellido`, `rol` y `linea` | cada persona de Nosotros; un perfil incompleto no se publica, y sin ninguno la sección queda con título y texto |
| `paginas.nosotros.publicar` | Nosotros en el menú y sin `noindex` |
| `medicion.ga4` o `medicion.pixel` | el aviso de cookies y el botón "Cookies" del pie; sin IDs no aparece nada |
| `contacto.formulario.clave` | el envío por Web3Forms; vacía, el formulario abre WhatsApp con el mensaje armado |
| `contacto_datos.whatsapp` | los enlaces a `wa.me`; vacío, van a `#contacto` |
| `contacto_datos.correo` | el correo en el pie, en el contacto y en el flotante |
| `redes[].href` | cada red como enlace; vacío, queda el nombre en texto |
| `contacto.motivos[].copy` | la línea sobre el formulario de esa opción (`:empty` la esconde) |

---

## Las decisiones del 08 al 10/09, con David

- **Formulario sin backend.** Un solo `<form>` que manda a Web3Forms con la clave pública en
  `contacto.formulario.clave`. Sin clave, el `submit` arma el mensaje con motivo, nombre,
  teléfono, correo y texto, y abre WhatsApp: el sitio nunca queda con un botón que no hace nada.
  Sin checkbox de privacidad: una nota inline (`formulario.privacidad`).
- **Cookies con Aceptar y Rechazar, del mismo peso.** Es una excepción a la regla de la casa (un
  solo botón, Entendido), decidida por David para este proyecto el 10/09. El aviso existe sólo si
  hay un ID de GA4 o de pixel en `medicion`; hoy no hay y no se muestra nada.
- **El marquee continuo es la única excepción documentada a "cero animaciones infinitas".**
  `@keyframes mvCinta` (y `mvCintaY` para la vertical) con `infinite`, pero con
  `animation-play-state: paused` hasta que un IntersectionObserver marca `data-vivo` en la cinta,
  y con `animation: none` bajo `prefers-reduced-motion`. El auditor las reconoce por
  `data-fx="marquee"` y las lista aparte como `cintas: N` en vez de contarlas como infinitas.
- **ES y EN ahora, PT deshabilitado con aviso.** Selector ES · EN · PT en la cabecera, en el pie
  y en el flotante; cada enlace lleva a la misma página en el otro idioma.
- **El mapa de páginas**: menú de seis (Inicio, Universo Mavenz, Proyectos, Espacio Mavenz,
  Nosotros, Contactanos), que hoy son cinco porque Nosotros espera al equipo. La ficha
  `cardinal.html` fuera del menú. **Mirada Mavenz es una sección de Inicio**, no una página.
- **Los paneles 2 y 3 van al contacto.** Otros proyectos y Oportunidades de inversión
  (`mundos.lista`) llevan a `#contacto` con `data-motivo`, que preselecciona la opción del
  formulario ("Tengo un proyecto", "Busco una oportunidad de inversión"). Su copy es el que ya
  existía en las opciones del contacto. En `proyectos.html`, la sección Oportunidades hace lo
  mismo.
- **La cinta del hero son los mundos del sitio**: Cardinal · Universo Mavenz · Espacio Mavenz ·
  Mirada Mavenz · Cómo trabajamos, cada uno enlazado a su página o su sección (`hero.cinta`).
- **La cortina se fue.** El hero deja de ser `sticky`. Con un `<video>` de fondo, un hero pegado
  sigue "en pantalla" para el observador de videos diferidos y corría tapado toda la página; el
  documento pide además que nunca se vea el fondo del inicio al bajar; y sin cabecera pegajosa la
  cortina no tenía con qué dialogar.
- **Un solo menú, el flotante.** Se fueron la hamburguesa, el panel de celular a pantalla
  completa y el globo `.wa` suelto. La cabecera es `position: relative`, casi transparente (alfa
  .10 sobre un RGB de la paleta, **sin blur**: el blur de 18 px la convertía en placa) y se va con
  la página. Su tema lo escribe el generador por página (`data-tema="oscuro"` en Inicio y en la
  ficha), no una sonda.
- **`.oscuro` es el único bloque de legibilidad.** Reasigna de una vez todos los tonos de texto,
  filetes y enlaces de lo que va sobre tinta. Lo usan el Universo (bistre), Espacio (wenge), la
  franja de Financiación y el hero de la ficha (bordó).
- **Dos excepciones a "sólo transform, opacity y filter"**: los keyframes del marquee y
  `clip-path: inset()` en el hero de la ficha, porque el efecto medido en la referencia (el ancho
  y el alto abren por separado y la foto revela encuadre en vez de deformarse) no existe con
  `scale`, y `clip-path` no dispara layout. Ya venía de antes y queda: la transición de
  `grid-template-rows` (`0fr` a `1fr`) del acordeón del mapa, la receta del vault para no
  inventar un `max-height`.

---

## Cómo funciona cada pieza

**El hero** (`hero()`). Sección de `100svh` con `margin-top` negativo para meterse debajo de la
cabecera. El video es de fondo y diferido: no tiene `src` hasta que entra en pantalla, y con
`data-pesado="1"` bajo 64rem no se baja nunca, queda el póster. Título y bajada centrados, el
título con `data-letras`. Al pie, la cinta continua de los cinco mundos (`cinta(..., continua=True,
velocidad=70)`), con `mask-image` lateral al 14 y al 86 % para que las piezas entren difuminadas,
y `filter: blur(var(--foco))` por pieza: `cintasContinuas()` escribe `--foco` según la distancia
al centro (hasta 3 px, cuantizado a medio píxel), sólo con puntero fino.

**El flotante** (`flotante()` en `armar.py`; módulo Flotante al final de `guion.js`). WhatsApp y
el botón del menú abajo a la derecha, `fixed` con `z-index: 30`. En escritorio nace escondido y
aparece cuando un IntersectionObserver ve que la cabecera salió de la pantalla
(`body[data-lejos]`); bajo 64rem está siempre, porque ahí la barra lleva sólo el logo y el
idioma. Sobre `#contacto` se esconde (`data-oculto`). `mirarTema` sondea qué bloque hay a 60 px
del borde inferior y le escribe `data-tema="oscuro"` para invertir tinta y fondo. El panel abre
en dos tiempos sólo con `scale` (alto y después ancho), los ítems entran escalonados por `--i` y
ruedan en vertical al pasar el puntero (`.rodar`); adentro van WhatsApp, correo y el selector de
idioma. Al abrir: `aria-expanded`, foco al primer enlace a los 430 ms y `lenis.stop()`; al cerrar
(botón, Escape, clic afuera o clic en un enlace), `lenis.start()`. Para probar desde la consola:
`window.__flotante.abrir()`.

**Cookies** (`cookies()` en `armar.py`; `consent.js`). El generador escribe un
`<template id="cookies">` inerte y pone los IDs en `<body data-ga4 data-pixel>`. `consent.js` los
lee; sin IDs corta ahí y no muestra nada. Con IDs y sin decisión guardada clona la tarjeta y la
cuelga de `<body>`, nunca de un bloque con transform. Aceptar carga GA4 y el pixel como
`<script async>` y vacía la cola de `window.mavenzEvento` (tope de 40 eventos); Rechazar no carga
nada y tira la cola; Escape cierra sin decidir. La decisión queda en `localStorage` con la clave
`mavenz.cookies`, con nombre propio porque GitHub Pages sirve todos los sitios de David desde el
mismo origen. El botón "Cookies" del pie nace con `hidden` y `consent.js` se lo saca sólo con
IDs: la reabre. La tarjeta va abajo a la izquierda, con la palabra "Cookies" gigante, rotada 12
grados y cortada por el `overflow: clip`, y las dos acciones son `.barajar`: dos copias del
rótulo partidas por letra (`letras()`), que se intercambian con un retraso de 30 ms por letra.

**Somos Mavenz** (`quienes()`). Título y dos párrafos en una columna de 34ch y, a la derecha, dos
fotos en círculo posicionadas por porcentaje dentro de una caja cuadrada: la de fondo al 58 %
arriba a la derecha, la de frente al 50 % abajo a la izquierda, pisándola. En celular la columna
va abajo. Sólo vive en Inicio.

**El puente** (`puente()` en los dos archivos). Un `div` decorativo entre Somos y el Universo:
gradiente quieto de papel a bistre y, encima, una capa de bistre con `scale: 1 var(--mezcla)`
que crece desde abajo con el scroll. Sin guion o con menos movimiento queda el gradiente. Lleva
`data-decorativo` para que el auditor no le mida tinta.

**El Universo** (`orbita()`; `circular()`, `anillo()` y `carrilEsferas()`). Sección `.oscuro` en
bistre. `orbita()` reparte las esferas sobre una circunferencia al 36 % del centro arrancando
arriba (con tres: a las 12, a las 4 y a las 8) y las une con un `<polygon>`; MAVENZ fijo en el
centro y el anillo de Marca y comunicación afuera, con su rótulo abajo. Tolera de 3 a 6 esferas
sin tocar CSS. `circular()` activa una esfera por clic, por foco o por `pointerenter` con mouse,
y hasta que alguien toca avanza sola según la posición de la sección en la pantalla; la activa
sube a `scale: 1.3` y su descripción se lee al costado, en un bloque `aria-live`. `anillo()`
dibuja el anillo en 900 ms al entrar en vista (`--dibujo`). Bajo 64rem el diagrama queda chico y
las descripciones son un carril con `scroll-snap`, una tarjeta por vez y flechas de 44 px:
`carrilEsferas()` lo sincroniza en los dos sentidos por el evento `mv:activar`.

**Cómo trabajamos** (`metodo()` y `puntos_onda()`; `trazoMetodo()`). El trazo es `ONDA`, un solo
path de la M con `pathLength="1"`, que se dibuja con `stroke-dashoffset: calc(1 - var(--trazo))`.
Los cinco pasos se posicionan sobre el trazo a las fracciones .14, .32, .52, .72 y .92 **de su
longitud**, no del parámetro de cada curva: `puntos_onda()` aplana las seis cúbicas en 120
segmentos cada una y busca en la tabla de longitud de arco. Rótulos alternados arriba y abajo.
`trazoMetodo()` escribe `--trazo` con el scroll (0 cuando la caja asoma por abajo, 1 cuando su
base llega al 40 % de la pantalla) y marca `data-visto` en cada paso cuando el trazo pasó por su
`data-t`; los dos son acumulativos, al subir no se deshacen. Sin pin. En celular el trazo queda de
adorno arriba y los pasos son una lista con filete, cada uno entra por IntersectionObserver. Sin
guion o con menos movimiento todo está a la vista.

**Proyectos en movimiento** (`mundos()`; `tilt()`). Tres paneles con aire entre sí, cada uno con
su tinta por `data-tinta` (bordó, bistre, wenge), la foto abajo (el 30 % en escritorio) y el
nombre en vertical desde 64rem. Cada tarjeta es un `<a>` con `data-fx="tilt" data-fx-grados="5"`:
`tilt()` escribe `--fx-rx` y `--fx-ry` por `pointermove` y el CSS los aplica con
`perspective(900px)`, sólo con puntero fino. Los paneles con `data-motivo` eligen esa opción del
contacto al hacer clic.

**Mirada Mavenz** (`mirada()` y `mapa()`). Las cinco categorías como lista numerada y, debajo, el
mapa de seis territorios como acordeón `<details name="territorio">` (uno abierto por vez, sin
JS); en escritorio en dos columnas, y el abierto ocupa el ancho.

**El contacto** (`contacto()`; `formulario()`). Cuatro opciones como solapas (`role="tab"`) y un
solo formulario: al elegir cambian la línea de arriba y el `<input type="hidden" name="motivo">`,
no el formulario. La primera opción viene activa con el formulario a la vista; `?motivo=x` en la
URL y un clic en `a[data-motivo]` preseleccionan. El cambio es en tres tiempos, medido en el video
de Vero: fade-out del bloque en 170 ms, 150 ms vacío, y las filas entrando de arriba abajo cada
65 ms por `--i`. El indicador de la solapa crece desde el centro (`scale`), un tercio en hover.
Validación propia con `novalidate`, `aria-invalid` y errores por `aria-live`; honeypot
`botcheck`. El envío es un `fetch` JSON a `api.web3forms.com/submit`; sin clave, WhatsApp. A la
izquierda, desde 64rem, la cinta vertical "Contacto" (`cinta(..., vertical=True, velocidad=125,
decorativa=True)`): color con `color-mix` al 12 % y nunca `opacity`, absoluta para no darle alto
a la caja, oculta en celular.

**La ficha de Cardinal** (`pagina_cardinal()`):

- `ficha_hero()` y `fichaHero()`: una sección de `100svh` más `120svh` de recorrido
  (`--recorrido`, sólo con `data-vivo`), con el contenido `sticky` a `100svh`. La foto es un
  bloque a pantalla completa recortado con `clip-path: inset()` a una ventana de `--w` por
  `--h`, que arranca en una tarjeta cuadrada (`--tarjeta`, `clamp(9rem, 12.5vw, 15rem)`). Un
  ScrollTrigger con `scrub` y sin pin escribe `--w` con `power1.out` y `--h` con
  `power1.inOut`: el ancho abre más rápido y la ventana pasa de 1:1 a 16:9. Detrás corre la
  cinta continua de cuatro isotipos al 18 % de opacidad, que sube a 1,5 veces el scroll; el
  nombre y la bajada se van en el primer cuarto, y "(Scroll)" a 0,4. Sin GSAP o con menos
  movimiento: foto abierta, sin recorrido.
- `marcador()` y `marcadores()`: la línea vertical de 1 por 72 px que escala de 0 a 1 en .6 s
  cuando un IntersectionObserver la ve (margen inferior del 10 %). Va antes del título, de
  Financiación y del cierre.
- `carrusel()` y `arrastrar()`: un carril con `scroll-snap-type: x proximity`, cada lámina un
  escalón más arriba que la anterior (`translate: 0 calc(var(--i) * -4.5svh)`) y anchos
  alternados (`ancha` a 3:2, `angosta` a 3:4), a sangre por los dos lados. `arrastrar()` suma el
  arrastre con el mouse, inercia con factor .92 por fotograma, un umbral de 6 px para que un clic
  siga abriendo el visor, y un `click` en captura que se come el arrastre. Las flechas mueven una
  lámina. La misma lista `galeria` alimenta el carrusel y el visor: `data-foto` es el índice.
- `sub_items()`: foto 3:4 y texto, los pares espejados, el tercero alineado abajo. Sólo se emite
  el que tiene foto y copy.
- `franja_video()`: `cardinal.mp4` a sangre, diferido y pesado (en celular sólo el póster).
- `unidades()`: rótulo, título, texto y la foto si hay.
- `financiacion()`: franja `.oscuro` en bordó de `50svh` mínimo, con marcador, título, el copy
  si hay y el CTA a WhatsApp.
- `cierre_ficha()`: marcador, la frase si hay y el botón a `#contacto`.
- `cardenal()`: la pieza de Fractura, diferida y con `data-reinicia`: al salir de pantalla vuelve
  a cero, porque lo que importa es el trazo dibujándose y no un logo ya hecho.

**Espacio Mavenz** (`espacio()`). Un bloque `.sangre.oscuro` en wenge con título, bajada, copy y
el botón claro al sitio externo (con "(sitio externo)" sólo para lectores de pantalla). Cuando
`espacio.foto` traiga un dict, entra como columna al lado.

**Nosotros** (`equipo()` y `red()`; `nubeRed()`). Sólo perfiles completos; hoy ninguno lo es y
la sección queda con título y texto. La red es la sección a sangre en bordó: los nodos entran
escalonados cuando la nube aparece y después derivan apenas con el scroll (`--deriva`), sin
keyframe.

**Videos diferidos** (bloque de `guion.js`). `preload="none"` no alcanza: con `autoplay` el
navegador baja el archivo igual. Ninguno tiene `src` hasta que entra en pantalla, con red de
seguridad por scroll y por reloj para cuando el observador no dispara.

---

## Medido, no estimado

`auditar.sh`, siete carriles por URL, el 10/09. Pantallas de alto por carril:

| URL | 390×844 | 390×660 | 812×375 | 1366×657 | 1512×982 | 1705×900 | 1920×1080 | cintas |
|---|---|---|---|---|---|---|---|---|
| `index.html` | 10,8 | 13,1 | 19,4 | 9,4 | 7,5 | 7,9 | 7,1 | 2 |
| `proyectos.html` | 4,2 | 5,2 | 9,1 | 4,0 | 2,8 | 2,9 | 2,5 | 1 |
| `cardinal.html` | 8,8 | 10,3 | 16,0 | 9,4 | 7,7 | 8,1 | 7,5 | 2 |
| `espacio.html` | 2,9 | 3,6 | 6,2 | 3,2 | 2,2 | 2,3 | 2,0 | 1 |
| `nosotros.html` | 3,7 | 4,6 | 7,9 | 4,1 | 2,9 | 3,0 | 2,6 | 1 |
| `en/index.html` | 10,6 | 12,9 | 19,3 | 9,4 | 7,4 | 7,9 | 7,1 | 2 |
| `en/proyectos.html` | 4,2 | 5,2 | 9,0 | 3,9 | 2,7 | 2,8 | 2,5 | 1 |
| `en/cardinal.html` | 8,8 | 10,2 | 16,1 | 9,4 | 7,7 | 8,1 | 7,5 | 2 |
| `en/espacio.html` | 2,9 | 3,6 | 6,2 | 3,2 | 2,2 | 2,3 | 2,0 | 1 |
| `en/nosotros.html` | 3,6 | 4,4 | 7,9 | 4,0 | 2,8 | 3,0 | 2,6 | 1 |

En las setenta corridas: **cero** desborde horizontal, **cero** contenido recortado, **cero**
toques por debajo de 44 px (también en escritorio), **cero** contrastes por debajo de 4,5 y
**cero** animaciones infinitas fuera de las cintas.

**`cintas: N` es a propósito**: son las cintas continuas (`data-fx="marquee"`), dos en Inicio
(hero y contacto), dos en la ficha (isotipos y contacto) y una en las demás (contacto). El
auditor las lista aparte en vez de contarlas como infinitas. Lo marcado con `data-sangra` (las
cintas se pasan del recorte adrede) no cuenta como recortado, y lo marcado con `data-decorativo`
(el puente) no cuenta como pantalla sin tinta.

Las diez URLs dan `ok` en los siete carriles. El auditor exceptúa el pie de la cuenta de
paradas casi vacías (en el celular acostado la última pantalla es solo el pie, que a propósito
no cuenta como tinta) y la cabecera flotante del contraste (su fondo real es el video).

Los videos, con póster y diferidos:

| Video | Peso | Póster | Dónde |
|---|---|---|---|
| `hero.mp4` | 707 KB | 112 KB | el hero de Inicio: recorte de 2,9 s del post de Cardinal, en ida y vuelta, sin el subtítulo quemado. En celular sólo el póster |
| `cardinal.mp4` | 3,0 MB | 72 KB | la franja de la ficha. En celular sólo el póster |
| `cardenal.mp4` | 22 KB | 4 KB | el cardenal, en la ficha. Se baja en todos los carriles |

`@keyframes` en la hoja: siete (`mvLetra`, `mvEntra`, `mvCinta`, `mvCintaY`, `cookiesEntrar`,
`cookiesAparecer`, `flotante-pliegue`). Una sola con `infinite`: la cinta.

---

## Trampas

Las que costaron una vuelta, viejas y nuevas.

- **El motor de reveal compara `data-fx="reveal"` por igualdad exacta.** Un
  `data-fx="reveal tilt"` no es una sección de reveal. Por eso el tilt va en la tarjeta
  (`.mundo`) y nunca en una sección: `tilt()` busca `[data-fx~="tilt"]`, el motor busca
  `[data-fx="reveal"]`, y son dos elementos distintos.
- **La cinta nunca es hija directa de una sección de reveal.** El motor le escribe `opacity` y
  un transform a cada hijo directo: a la cinta le pisaría la opacidad, y el transform la
  convertiría en bloque contenedor. En el contacto vive adentro de `.contacto__caja`, y su tinte
  es color con `color-mix`, no `opacity`: un elemento, una sola cosa que lo controle.
- **El observador de una cinta continua va sobre el ancestro quieto, nunca sobre el riel.** Un
  riel en movimiento entra y sale del umbral solo y apaga lo que tiene que prender.
  `cintasContinuas()` observa `[data-cinta-continua]`, no `[data-cinta-riel]`.
- **`translate: 0px` no es `none`.** `@keyframes mvEntra { to { translate: none } }` interpola a
  `0px`, y un `translate` distinto de `none` convierte al elemento en bloque contenedor de todo
  `position: fixed` que tenga adentro, y además le crea un contexto de apilamiento que sus hijos
  con `z-index` negativo pueden estar usando sin que nadie lo sepa. Por eso, cuando la entrada
  termina, `animationend` marca `data-entrado` y el CSS saca el transform del todo. Y por eso la
  tarjeta de cookies cuelga de `<body>` y de nada más.
- **`lenis.stop()` con el menú abierto.** Lenis mueve el scroll a mano, así que el
  `overflow: hidden` del `body` no lo frena. El flotante lo para al abrir y lo arranca al cerrar;
  y como `guion.js` intercepta los `href="#ancla"` y los manda a `lenis.scrollTo`, que Lenis
  parado ignora, el clic en un enlace del panel cierra **en captura**, antes de que el enlace haga
  lo suyo.
- **`min-width: 0` en los hijos de la grilla del contacto.** Un item de grilla es
  `minmax(auto, 1fr)`: no encoge por debajo de su contenido, y una solapa larga estiraba la
  columna y rompía el 4fr / 6fr. Lo mismo en la fila del acordeón: `flex-wrap` y `min-width: 0`
  para que el signo no se salga cuando el nombre del territorio es largo.
- **El snap alinea contra el borde del scrollport, no del padding.** Un carril a sangre con
  `padding-inline` para alinearse con el texto necesita el mismo valor en
  `scroll-padding-inline` (el carril de esferas y el carrusel lo llevan), y `carrilEsferas()`
  descuenta ese padding al calcular a qué tarjeta ir.
- **Una lista de selectores huérfana se pega a la regla siguiente.** Al borrar un bloque de CSS
  y dejar sus selectores sin llaves, el parser los une con coma a la regla de abajo, y esa regla
  pasa a aplicarse a lo que uno creía borrado. Pasó en este rediseño al sacar los bloques viejos;
  con `grep -c` a cero antes y el auditor después se atrapa.
- **El `h2` de la cinta no puede heredar el cuerpo.** La primera pieza de una cinta con
  `titulo=True` es un `h2`; `h2.cinta__pieza` resetea sólo el margen, porque con `font: inherit`
  tomaba el cuerpo del `body` y la primera pieza salía chica.
- **El pie va con `flex-wrap`.** En 390 la fila de abajo lleva lugar, páginas, idioma y el botón
  de cookies; sin wrap el último se salía y el celular hacía zoom out (`innerWidth` 425 en vez de
  390).
- **`.oscuro` se rompe de dos maneras.** Un descendiente con `color` propio no hereda (pintar el
  `summary` no alcanzaba para el `span` del nombre), y uno con fondo propio claro no puede
  recibir el tono claro (el botón `.boton--claro` necesita su propia regla, más específica).
- **El título del contacto se mide contra la columna, no contra el viewport.** `var(--t-hero)` a
  1512 daba 96 px y la palabra pisaba el botón de al lado; ahora es
  `clamp(2.25rem, 15cqi, var(--t-hero))` con `container-type: inline-size` en la columna.
- **Dos clases para la cinta del hero y la de la ficha.** La base `.cinta` (papel, filete,
  padding) está más abajo en la hoja y con una sola clase le ganaba: texto papel sobre fondo
  papel, una banda vacía.

---

## Lo que debe Vero

Cada cosa tiene su clave y, mientras falta, el sitio se ve así.

| Qué falta | Clave | Cómo queda mientras |
|---|---|---|
| Metraje de dron limpio, sin subtítulos | `hero.video` | el recorte de 2,9 s del post de Cardinal |
| Las dos fotos en círculo de Somos Mavenz | `quienes.circulos` | dos aéreas reales, provisorias, para que se vea la composición |
| Proyectos confirmados para Otros proyectos (Porto y WA son de Grupo MDay y no los confirmó) | `proyectos.otros_publicar`, `proyectos.otros`, `mundos.lista[1].foto` | la sección no se emite; el panel de Inicio lleva al formulario, con una aérea provisoria |
| Fotos y copy de jardines, cochera, SUM y espacios verdes; copy de la pileta | `proyectos.cardinal.sub_items` | los sub-items no se emiten |
| Plano o foto de tipologías | `proyectos.cardinal.unidades.foto` | el render interior |
| Copy de financiación (plazos, anticipo, cuotas) | `proyectos.cardinal.financiacion.copy` | título y CTA |
| La frase de cierre de la ficha | `proyectos.cardinal.cierre.titulo` | el botón solo |
| Confirmar los epígrafes reescritos sin "casas" y la grafía de GRIFIL | `proyectos.cardinal.galeria[].epigrafe`, `proyectos.cardinal.aclaracion` | neutros, como vinieron |
| Foto aprobada de Espacio Mavenz | `espacio.foto` | sin foto |
| El equipo completo: foto, nombre y apellido, rol y una línea por persona | `equipo.personas`, `paginas.nosotros.publicar` | la página se genera con `noindex` y fuera del menú |
| Copy de las opciones "Quiero generar una alianza" y "Quiero conocer Espacio Mavenz" | `contacto.motivos[2].copy`, `contacto.motivos[3].copy` | sin línea sobre el formulario |
| Aprobar la nota de privacidad y el texto de cookies, que propuso DT | `contacto.formulario.privacidad`, `cookies.texto` | la propuesta |
| La clave pública de Web3Forms (se crea con el mail de Mavenz) | `contacto.formulario.clave` | el formulario abre WhatsApp |
| Las URL de Instagram, LinkedIn y Facebook | `redes[].href` | los nombres en texto |
| Confirmar el WhatsApp y el correo (el número viene de la demo vieja, el correo del diseño) | `contacto_datos` | los datos actuales; quedan fuera de los datos estructurados hasta que confirme |
| IDs de GA4 y de pixel | `medicion` | sin aviso de cookies |
| Revisar el inglés, en especial el claim del hero (*Mavenz creates momentum* o *Moving things forward*) | `sitio.en.json` | la traducción de DT |
| El copy en portugués | `sitio.pt.json` | PT deshabilitado en el selector |
| Confirmar que Gestión & Evolución desaparece del Universo (el documento fija tres esferas) | `universo.esferas` | tres esferas y el anillo |
| Decidir qué "movimiento" cambia: hoy aparece en 10 textos, `python3 armar.py --palabra movimiento` los lista | varias | no se reescribe nada sin ella |

Aparte, y viene del LEEME anterior sin novedad conocida: **rotar la credencial de Gmail** que
vino en texto plano en el archivo de 2 Clics.

---

## Verificación

```bash
cd mavenz-web && python3 -m http.server 8899    # sirve /demo/...
demo/auditar.sh                                   # las diez URLs, siete carriles
```

`auditar.sh` corre `~/.claude/skills/visual-verify/scripts/auditar.py` (necesita el venv con
`websocket-client`) sobre `index`, `proyectos`, `cardinal`, `espacio` y `nosotros`, en ES y en
`en/`. Los siete carriles: celular 390×844, celular bajo 390×660, acostado 812×375, notebook
1366×657, escritorio 1512×982, el ancho de David 1705×900 y 1920×1080. Pregunta lo que una
captura no contesta: pantallas sin tinta scrolleando de verdad, desborde moviendo la página de
costado, contenido recortado por un ancestro con `overflow: clip`, toques de 44 px en todos los
carriles, contraste compuesto contra el primer fondo opaco e infinitas fuera de las cintas.

Lo que el auditor no mide y hay que probar con la pestaña al frente o en el teléfono: la
apertura de la tarjeta de Cardinal (con `?sinlenis` en la URL para depurar sin scroll suave), el
trazo del método dibujándose, hover y toque en la órbita, el carril con swipe, el flotante con
teclado (Tab, Enter, Escape, foco de vuelta), el envío real con una clave de Web3Forms (hoy no
hay: sólo existe el fallback a WhatsApp), el aviso de cookies con un ID de prueba y recarga,
`prefers-reduced-motion` forzado con salto directo al fondo, y el toque real en un teléfono.
**Una trampa del método**: `--window-size` de Chrome headless no baja de 500 px; las capturas de
celular salen del capturador por DevTools
(`~/.claude/skills/visual-verify/scripts/capturar-celular.py`), que usa
`Emulation.setDeviceMetricsOverride`.

La limpieza final ya pasó: el CSS de la versión anterior se podó con un parser de reglas
(103 reglas, de 132 a 120 KB; `scratchpad/podar_css.py` en la sesión del 10/09 tiene el
método: una clase que no aparece en ningún HTML generado ni en el JS es muerta, salvo los
bloques que el generador emite solo con dato), el guion perdió la rueda, el método horizontal,
la foto quieta y las palabras que se forman, y `video/banda.mp4` con su póster salieron del
repo. Siguen en el historial de git.
