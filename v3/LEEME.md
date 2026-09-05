# Mavenz — demo v3

Construida el 2026-09-04 sobre las respuestas de Vero en el tablero de decisiones
(link con `#r=` del 04/09) y sus tres audios del mismo día. HTML, CSS y JS planos,
sin frameworks ni build. Se publica en `davidtaranto96.github.io/mavenz-web/v3/`.

## Cómo se edita

El copy vive en un solo lugar: `contenido/sitio.json` (castellano) y
`contenido/sitio.en.json` (inglés, sólo lo que reemplaza al castellano). El HTML
**no se edita a mano**: se toca el JSON y se corre

```bash
python3 armar.py
```

que regenera `index.html` y `en.html`. Cada región que sale del JSON queda entre
marcas `<!--cms:nombre-->…<!--/cms:nombre-->`, así el panel de `web-editable` puede
regenerarla sola más adelante.

Lo que la clienta debe todavía está marcado en pantalla con la píldora **pendiente**
(foto y proyectos de Espacio Mavenz, fotos del equipo y la red, más proyectos con sus
fotos, las notas reales de Contenido y mirada, el WhatsApp y el correo, los enlaces de
las redes, y el copy en inglés). Los datos vacíos están en `contacto_datos` y `redes`
del JSON; en cuanto se cargan, el formulario abre WhatsApp con el mensaje escrito y el
botón flotante apunta directo.

## Qué eligió Vero y dónde está

| Elección (tablero / audio) | Dónde se ve |
|---|---|
| Papel con tinta bordó | `:root` de `estilos.css`: paleta oficial de Fractura, sin `#fff` |
| Títulos ExtraBold gigantes en mayúscula (audio 04/09) | `h1` y los ocho `h2` |
| El pliegue + las ondas del kit + el trazo dibujándose | Hero: agua a dos tercios, el título cruza el pliegue, la M se dibuja una vez |
| Al margen | Quiénes somos y La red: columna de texto, datos chicos al costado, foto que se va de largo |
| Ondas entre secciones | Las dos bandas de agua: se abren una vez y quedan quietas |
| Rueda conectada / se apilan como cartas | Universo: rueda en escritorio (quieta hasta que la tocás), cartas sticky en celular |
| Cinco capacidades destacadas | `destacada: true` en el JSON; las otras dos en segundo plano |
| Un solo trazo | Cómo trabajamos: el hilo pasa por los cinco pasos y se dibuja con el scroll |
| Dossier / estante | Proyectos: fotos sueltas a distintas alturas en escritorio, estante con swipe en celular |
| Sólo CARDINAL | Único proyecto; marcador para los que faltan |
| Color natural, blanco y negro, velo con texto | CARDINAL en color, la foto de Salta en B/N, la portada del proyecto con velo y nombre |
| Píldora rellena + texto subrayado | `.boton` y `.enlace` |
| Los títulos entran letra por letra | `data-fx="letras"`, una vez por sección |
| Movimiento suave | Reveal de 0,9 s con dirección por sección; cero animaciones infinitas, cero `@keyframes` |
| Que pida una reunión + WhatsApp siempre disponible (audio) | "Pedir una reunión" fijo en el menú y botón flotante de WhatsApp |
| Menú siempre a la vista | Cabecera sticky |
| Las dos versiones completas | `en.html` con el selector ES/EN; el copy en inglés queda pendiente de Mavenz |
| Instagram, LinkedIn, Facebook | Pie, a la espera de los enlaces |
| Espacio Mavenz es donde viven los proyectos | Sección con enlace a espaciomavenz.com.ar y marcador del listado |
| Mapa Mavenz afuera | No se muestra; `contenido/mapa.json` queda guardado por si vuelve |

## Verificación (04/09)

Capturas en 375×812, 1366×657, 1512×982 y 812×375 sin desborde horizontal.
Pantallas: 11,0 en celular · 10,3 en notebook · 8,3 en escritorio (objetivo del traspaso: 11 y 10). Primera carga
883 KB decodificados. Siete tamaños de texto, tres pesos. Cero HEX fuera de `:root`.
Auditor de efectos 97/100 sin bloqueantes. Reveal probado con salto directo por ancla
y `scrollBehavior='auto'`. Con `prefers-reduced-motion` la página queda completa.
