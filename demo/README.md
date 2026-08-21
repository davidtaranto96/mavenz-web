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
