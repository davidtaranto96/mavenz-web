# Mavenz — tres páginas

`https://davidtaranto96.github.io/mavenz-web/demo/`

Rediseño del 08/09/2026, después de la reunión con Vero del 07/09. Reemplaza la página única
anterior. Las referencias que ella eligió: `edificiolatorre.com` (nuestra), `realevate.agency`
y `akaru.fr`.

**La idea, en una línea:** el trazo de la M es el hilo. Se dibuja en el hero, se cierra en la
órbita de las esferas, se aprieta en el círculo del método, se estira como riel de los
proyectos y se apaga en el pie. Un gesto en todo el sitio, no un efecto por sección.

**Tres páginas**, castellano. El inglés lo debe la clienta; `fundir()` y `sitio.en.json`
siguen en pie para cuando llegue.

| Página | Qué cuenta |
|---|---|
| `index.html` | el relato: hero, quiénes, las 4 esferas en órbita, el método en ciclo, los 4 mundos, contacto |
| `about.html` | quiénes son, el equipo, la mirada, la red |
| `proyectos.html` | cada proyecto es un mundo de color entero, con su cinta y su "Siguiente". Del último se vuelve al primero |

**Las cuatro esferas** son textuales del WhatsApp de Vero del 07/09. **"Marca y comunicación"
no es una esfera: es el anillo que las rodea** — decisión de David del 08/09. El componente
tolera de 4 a 6 esferas sin tocar CSS.

**Las cuatro tintas de los mundos** salen del manual de Fractura. No hay un hex nuevo en toda
la hoja de estilos.

---


## Cómo se edita

Un dato vive en un solo lugar: `contenido/sitio.json`.

```bash
python3 armar.py
```

Eso reescribe `index.html`, `about.html` y `proyectos.html`. **El HTML no se toca a mano.** Cada región que sale del JSON queda
envuelta en `<!--cms:nombre--> … <!--/cms:nombre-->` para que el panel de `web-editable` la
pueda regenerar sola más adelante.

| Archivo | Qué es |
|---|---|
| `contenido/sitio.json` | todo el texto, las fotos, los datos de contacto |
| `contenido/sitio.en.json` | la capa en inglés: sólo lo que cambia. Las listas van enteras |
| `armar.py` | genera las tres páginas desde una cáscara compartida |
| `estilos.css` | tokens y los cuatro carriles |
| `guion.js` | Lenis+GSAP, órbita, ciclo, cintas por scroll, riel fijado, solapas, cabecera, menú, entrada de los títulos y de las secciones, trazo con el scroll, visor de fotos, índice lateral |
| `../img/` | fotos en WebP, dos anchos cada una |
| `../fuente/urbanist.woff2` | Urbanist variable, 100–900, 24 KB |

---

## Lo que pidió Vero y dónde está

| Respuesta del tablero | Cómo se resolvió |
|---|---|
| Fondo: papel con tinta bordó | El bordó es tinta, nunca fondo de sección |
| Direcciones: al margen · un solo trazo · dossier · el pliegue · ondas | Las cinco comparten papel y trazo: se fusionaron en una |
| Títulos ExtraBold gigante, en mayúscula (audio) | `--t-hero` y `--t-titulo`, peso 800, versalita sólo en títulos de display |
| Un solo efecto: los títulos entran letra por letra | Es el único movimiento de scroll de toda la página |
| Movimiento suave | `cubic-bezier(.22,.61,.36,1)`, 0 animaciones en bucle |
| Botones: píldora rellena y texto subrayado | `.boton` y `.subrayado` |
| Sólo CARDINAL | La cuarta ficha del estante está vacía, y se ve que lo está |
| Fotos: color, blanco y negro, con velo y texto | Las tres, una por ficha |
| Universo: rueda conectada, se apilan como cartas | Heptagrama + tres capas de papel |
| Menú siempre a la vista | Cabecera pegada arriba |
| Entrada: que pida una reunión | Es el botón principal en la cabecera y en el cierre |
| Redes: Instagram, LinkedIn, Facebook | En el pie, sin enlace hasta que pase las URL |
| **Grilla de tarjetas** y **estante que se desliza** | Las dos: estante en el celular, grilla de cuatro columnas de notebook para arriba |
| **Las dos versiones completas de idioma** | `index.html` y `en.html`, con selector real, `hreflang` y `lang` |
| Los tres públicos del audio | Cuatro motivos en el cierre, cada uno abre WhatsApp con su propio mensaje |

---

## Lo que se agregó el 06/09 (pasada de subir-nivel)

De las catorce opciones del menú, David tildó doce. Todas salen de la receta editorial de
SAURIUM, que es la única web que elogió espontáneamente, del auditor de efectos o del detector
de genérico.

| Qué | De dónde sale |
|---|---|
| **La cortina**: el hero queda fijo y el dossier sube encima con radio y sombra invertida | SAURIUM. Es el gesto grande, una sola vez en toda la página |
| **El solape**: la grilla de proyectos cruza el corte y su pie vive en la sección siguiente | SAURIUM. El margen negativo y el padding salen del mismo token |
| **Cada sección entra con su gesto** (izquierda, derecha, escala) | Auditor 8/10 + anti-slop. En celular todo entra desde abajo: un desplazamiento lateral abre scroll horizontal en un teléfono |
| **El nav se invierte** según el bloque de abajo, con los dos logos | SAURIUM. Sondea `offsetTop`, no una lista de ids |
| **Grilla asimétrica** de proyectos: 7/5 y 5/7, cuatro proporciones distintas | Anti-slop: la grilla de tarjetas iguales es el tell número uno de web hecha con IA |
| **Visor de fotos** con swipe nativo dentro de un `<dialog>` | SAURIUM. La inercia la pone el sistema |
| **Barrido de luz** al cambiar de capacidad en la rueda | SAURIUM: sin el barrido el visitante duda de si el clic hizo algo |
| **El método cuenta qué pasa**: los cinco verbos se abren | SAURIUM. Copy del documento de Vero |
| **Vuelve el Mapa Mavenz**, adentro del Universo | Del vault: está construido y pago dentro de los USD 300 |
| **Índice lateral de rayas** desde 1180 px | SAURIUM. `scaleX` desde la izquierda, que se lee como progreso |
| **El trazo se dibuja con el scroll** en vez de solo al cargar | El gesto de la marca atado al del visitante |
| **Pie de foto catalogada**: leyenda y las siete muestras del manual | SAURIUM. La aérea deja de ser un banner de stock |

Quedaron sin tildar el wordmark gigante de fondo y el corte duro de entrada de la foto.

Y tres arreglos de celular que no eran gusto sino QA: **el menú ocupa la pantalla y bloquea el
scroll de atrás**, **el globo de WhatsApp se esconde donde ya hay WhatsApp a la vista** (el hero
y el cierre), y **el CSS y el JS llevan `?v=` con el hash del archivo**, sin lo cual el
navegador sirve la versión vieja y una corrección no se ve.

---

## Segunda pasada de subir-nivel (06/09, noche)

De catorce opciones entraron doce, y quedaron afuera las dos del hero que sumaban una capa
decorativa. Lo que cambió:

| Qué | De dónde sale |
|---|---|
| **Dos secciones a sangre**: Espacio Mavenz sobre la aérea con velo bordó, y La red en tinta bordó maciza | El pedido de que los bloques no fueran todos iguales |
| **Banda de video** panorámica entre el método y Espacio | `banda-aerea-1.mp4`, de 1,4 MB a 119 KB |
| **El método en horizontal**: la sección se clava y las cinco cartas pasan de costado | El scroll lateral que pidió David |
| **El cardenal que se dibuja** | `assets/video/cardinal-trazo.mp4`, pieza de Fractura, 65 KB. El ave se dibuja, se posa sobre la M del isotipo y cierra con *"Y esto recién se pone en movimiento"* |
| **El film de CARDINAL** de fondo en la ficha del proyecto | `cardinal-film.mp4`, de 17 MB a 3 MB |
| **Palabras que se forman con el scroll** en la cita de Somos Mavenz | Pedido de David |
| **El mapa en grilla** de seis territorios numerados, la ficha abierta ocupa el ancho | Antes eran seis renglones idénticos |
| **Las piezas de marca** de Fractura (agenda y carpeta) en Somos Mavenz | Estaban en el repo sin usar |
| **Tres proyectos**: CARDINAL en profundidad, más Porto y WA | Pendiente de confirmar con Vero |
| **Sección de ellas**, con los huecos de los retratos a la vista | Pedido de David |
| **Las capas de la rueda y las píldoras tenues** dejan de verse apagadas | Lo que marcó David en la captura |

**Videos, todos diferidos**: `preload="none"` no alcanza, con `autoplay` el navegador se baja el
archivo igual. Ninguno tiene `src` hasta que entra en pantalla.

**Tres bugs de esta pasada, anotados porque son de los que se repiten:**

1. El `position: fixed` del fondo de Espacio **no queda contenido por el `overflow` de su
   sección** y terminaba pintando la foto sobre toda la página. Va con `translate` desde el guion.
2. El hero queda `sticky` toda la página: **todo bloque que venga después tiene que ser opaco y
   estar posicionado**, o se ve la foto por atrás.
3. El signo `+` del acordeón se salía 28 px del ancho cuando el nombre del territorio era largo.
   La fila necesita `flex-wrap` y `min-width: 0`.

---

## Medido, no estimado

| | Demo vieja (`v1/`) | Esta |
|---|---|---|
| Pantallas en celular (390×844) | 23,6 | **11,7** |
| Pantallas en notebook (1366×657) | 26,2 | **16,3** |
| Animaciones en bucle en el celular | 17 | **0** |
| Peso de la primera carga | 10 MB | **260 KB** |
| Peso de la página entera | — | **1,0 MB** |
| `@keyframes` | 22 | **4** |
| Videos, con su póster y diferidos | 1 sin diferir, 10 MB | **3**, 3,2 MB |
| Colores fuera de `:root` | 109 | **0** |
| Hex en toda la hoja | — | **7** (los del manual de Fractura, ni uno más) |
| Tamaños de texto renderizados | 26 | **13** |
| Áreas táctiles por debajo de 44 px | — | **0** |
| Imágenes repetidas | hasta 5 veces | **0** |

Los cuatro tonos de papel (pie, huecos, capas de la ficha) **no son colores nuevos**: salen de
mezclar Anti-flash white con Timberwolf por `color-mix`. La paleta sigue siendo de siete.

---

## Los tres carriles

| Carril | Medida | Qué cambia |
|---|---|---|
| Celular | 390×844 | Rueda de puntos, verbos del método en línea, red apilada |
| Notebook horizontal | 1366×657 | **Todo lo que ocupa alto se mide contra `svh`**: el ritmo entre secciones, la rueda, el hero, el trazo del método |
| Escritorio | ≥1512 | La rueda con las píldoras, la red como nube, la marginalia al margen |

Y un cuarto que no se rompe aunque no esté en la lista: **celular acostado** (812×375), que cae
por una consulta de **alto** con tope de ancho, para que no se lleve puesta a la notebook.

---

## Decisiones que tomé y conviene revisar

1. **No hay formulario, hay motivos.** El diseño no trae formulario y Vero marcó que lo que
   quiere es que pidan una reunión. En el cierre hay cuatro motivos —presentar un proyecto,
   buscar una oportunidad, proponer una alianza, conocer Espacio Mavenz— y cada uno abre
   WhatsApp con su propio mensaje. Eso recupera lo que hacía el formulario de la demo vieja:
   saber quién escribe. Son los tres públicos que nombró en el audio del 04/09
   —desarrollador, consumidor final e inversor— más los partners.
2. **El copy en inglés lo escribí yo**, traduciendo el de Vero. Mavenz lo tiene que revisar, y
   sobre todo confirmar el claim del hero: *Mavenz creates momentum* es la traducción fiel de
   *Mavenz genera movimiento*, pero un claim de marca lo decide la marca. La alternativa que ya
   usaba el kit es *Moving things forward*. Está anotado en `sitio.en.json`.
3. **El WhatsApp y el correo hay que confirmarlos.** El número viene de la demo vieja y
   `hola@mavenz.com.ar` salió del diseño. Están en `contacto_datos` del JSON.
4. **Sin banner de cookies**, porque todavía no hay etiquetas de medición configuradas. Cuando
   entren, va el de la convención: una línea, un botón *Entendido*, abajo a la izquierda.
5. **Cuatro pesos tipográficos** (300, 400, 600, 800) en vez de tres. Vero pidió en el audio
   "el grueso y gigante, y después los subtítulos más finitos": ese contraste necesita los dos
   extremos, y el peso 400 es el de la interfaz.
6. **El `backdrop-filter` de la cabecera y del botón de WhatsApp se queda.** No es
   glassmorphism decorativo: es una barra translúcida sobre una foto, que es lo que resuelve la
   legibilidad del menú sobre el hero.
7. **El dossier da 79/100.** Sus tres primeras recomendaciones son sumar efectos —reveal por
   sección, parallax, entrada de títulos— y las tres están descartadas a propósito: Vero marcó
   **un solo efecto** de diez.

## Lo que falta y hay que pedirle a Vero

Está construido con marcadores a la vista, no con relleno disimulado, así ella ve qué debe:

- **Foto de Espacio Mavenz.** Cero material y es una sección entera.
- **Fotos del equipo y de la red.**
- **Qué otros proyectos entran y con qué fotos.** Hoy sólo CARDINAL tiene material.
- **Los textos reales de "Contenido y mirada".**
- **Las URL de Instagram, LinkedIn y Facebook.**
- **Confirmar el WhatsApp y el correo.**
- **Que Mavenz revise el inglés**, en especial el claim del hero.

Aparte, en mensaje separado: **rotar la credencial de Gmail** que vino en texto plano en el
archivo de 2 Clics.

---

## Verificado y lo que no

Verificado con medición en vivo y captura: los tres carriles más el celular acostado, cero
desborde horizontal en los cuatro, las anclas del menú no quedan tapadas por la cabecera, la
rueda cambia de capacidad, el menú de celular abre y cierra, el selector ES/EN va y vuelve
entre las dos versiones, ninguna palabra en castellano se coló en `en.html`,
`prefers-reduced-motion` deja la página completa y legible, consola sin errores en las dos.

**Sobre el largo, que es lo que hay que mirar**: la notebook pasó de 10,5 a 16,3 pantallas en las
dos pasadas. Sigue por debajo de la demo vieja (26,2) y con muchísimo más adentro —tres
proyectos, seis territorios, el método con contenido, la sección de ellas, tres videos—, pero es
lo contrario de lo que pidió Vero cuando dijo que la anterior era muy larga.

Lo que ya se hizo para contenerlo: tres de las nueve fotos de CARDINAL viven **sólo en el visor**
(el contenido está, el scroll no crece), las fichas de la grilla no pasan de `46svh` de alto, y
el pin del método mide lo que miden las cartas y no la pantalla entera.

Lo que queda como palanca, a una variable: `--ritmo` en el bloque de la notebook, hoy en
`8.5svh`. Y la decisión más grande, si Vero insiste con el largo: **el pin del método cuesta
cerca de una pantalla y media**; sin él los cinco pasos siguen siendo un estante que se desliza.

**No verificado:** el toque real en un teléfono. El panel del navegador corre oculto en esta
máquina y no completa los clicks; las áreas táctiles están medidas (44 px, ninguna por debajo)
pero el gesto hay que probarlo en el teléfono.

**Una trampa del método, anotada porque costó caro:** `--window-size` de Chrome headless **no
baja de 500 px**. Si le pedís 390 maqueta a 500 y recorta la imagen a 390, así que la captura
muestra textos cortados y botones fuera de pantalla en una web que no desborda. Las capturas de
celular de este LEEME salen del capturador por DevTools
(`~/.claude/skills/visual-verify/scripts/capturar-celular.py`), que usa
`Emulation.setDeviceMetricsOverride` y lo reaplica después de navegar.

---

## Medido el 08/09, contra el sitio publicado

| | Inicio | Nosotras | Proyectos |
|---|---|---|---|
| Pantallas en celular (390×844) | 7,3 | 5,3 | 8,2 |
| Pantallas en notebook (1366×657) | 7,4 | 6,2 | 11,0 |
| Primera carga, celular | 348 KB | 242 KB | 663 KB |

**Cero scroll lateral** en los cinco carriles (390×844, 390×660, 1366×657, 1512×982 y 812×375
acostado), probado moviendo la página de costado de verdad y no leyendo `scrollWidth` — el
`pin-spacer` de GSAP infla ese número 28 px sin que se vea ni se pueda scrollear.

**Cero** `@keyframes` infinitos, **cero** hex fuera de `:root`, **cero** errores de consola,
**cero** toques por debajo de 44 px en los carriles de celular.

Con `prefers-reduced-motion` y con salto directo al fondo, **ningún bloque queda invisible** en
las tres páginas.

### Dos cosas que el auditor marca y quedan así a propósito

- **`transition: grid-template-rows`** en el acordeón. Es una propiedad de layout, sí, pero es
  la receta `0fr↔1fr` del vault, que existe justamente para no inventar un `max-height: 1000px`
  ni medir con JS. Se anima una fila de un elemento chico.
- **El puntaje del auditor de efectos es 73/100.** Este sitio tiene motor propio de reveal;
  encimarle un segundo motor sobre los mismos elementos es el error ya documentado (dos
  animaciones de opacidad sobre el mismo nodo lo dejan invisible) y ningún puntaje lo compensa.
  Lo que el auditor marcaba **y era real** ya se arregló: los cuatro mundos no tenían encabezado
  ni entrada propia, y faltaba `scroll-padding-top`.

## Trampas que costaron una vuelta cada una

- **Un item de grilla es `minmax(auto, 1fr)`: no encoge.** `#proyectos-bloque` empujaba 1675 px
  dentro de un viewport de 812. Va `min-width: 0`.
- **El motor de reveal escribe `opacity` a los hijos de la sección**, así que el `opacity: .07`
  de la palabra gigante de contacto se lo comía y la palabra tapaba el texto. Se resolvió con
  color tintado en vez de opacidad: un elemento, una sola cosa que lo controle.
- **La órbita no entra en 390 px.** Cuatro rótulos a radio 38 % más un panel al centro se
  cruzan entre sí y con el anillo. En celular el arco se desenrolla y queda una lista vertical.
- **Las secciones traen sus colores de papel.** Adentro de un mundo el fondo es la tinta y el
  bordó sobre bordó desaparece. Hay un bloque de legibilidad que reasigna todos los tonos de
  una vez, en lugar de parchear sección por sección.
- **El video de fondo de Cardinal son 3 MB.** En celular no se baja: el póster ya cuenta la
  escena. La página pasó de 3679 KB a 663 KB.
