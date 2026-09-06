# Mavenz — demo

`https://davidtaranto96.github.io/mavenz-web/demo/`

Implementación del diseño aprobado en Claude Design (proyecto *Universo interactivo: Mavenz
Home*, 06/09/2026), que se armó sobre el documento `Estructura_Web_Mavenz.docx` de Vero y sus
respuestas al tablero del 04/09.

**La idea, en una línea:** un dossier de papel donde lo único que se mueve es el trazo de la
marca.

HTML/CSS/JS estático, sin framework. La demo anterior quedó intacta en `../v1/`.

---

## Cómo se edita

Un dato vive en un solo lugar: `contenido/sitio.json`.

```bash
python3 armar.py
```

Eso reescribe `index.html`. **El HTML no se toca a mano.** Cada región que sale del JSON queda
envuelta en `<!--cms:nombre--> … <!--/cms:nombre-->` para que el panel de `web-editable` la
pueda regenerar sola más adelante.

| Archivo | Qué es |
|---|---|
| `contenido/sitio.json` | todo el texto, las fotos, los datos de contacto |
| `armar.py` | genera `index.html` |
| `estilos.css` | tokens y los tres carriles |
| `guion.js` | cabecera, menú, rueda del universo, entrada de los títulos |
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
| Proyectos: grilla de tarjetas y estante que se desliza | Destacado + estante horizontal |
| Sólo CARDINAL | La cuarta ficha del estante está vacía, y se ve que lo está |
| Fotos: color, blanco y negro, con velo y texto | Las tres, una por ficha |
| Universo: rueda conectada, se apilan como cartas | Heptagrama + tres capas de papel |
| Menú siempre a la vista | Cabecera pegada arriba |
| Entrada: que pida una reunión | Es el botón principal en la cabecera y en el cierre |
| Redes: Instagram, LinkedIn, Facebook | En el pie, sin enlace hasta que pase las URL |

---

## Medido, no estimado

| | Demo vieja (`v1/`) | Esta |
|---|---|---|
| Pantallas en celular (390×844) | 23,6 | **7,2** |
| Pantallas en notebook (1366×657) | 26,2 | **10,5** |
| Animaciones en bucle en el celular | 17 | **0** |
| Peso de la primera carga | 10 MB | **257 KB** |
| Peso de la página entera | — | **1,0 MB** |
| `@keyframes` | 22 | **2** |
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

1. **No hay formulario.** El diseño no lo trae y Vero marcó que lo que quiere es que pidan una
   reunión. Sin servidor, el botón abre WhatsApp con el mensaje ya escrito. Un formulario de
   verdad necesita destino y se cotiza aparte.
2. **El WhatsApp y el correo hay que confirmarlos.** El número viene de la demo vieja y
   `hola@mavenz.com.ar` salió del diseño. Están en `contacto_datos` del JSON.
3. **La versión en inglés no está.** El selector ES/EN queda en su lugar, apagado, con un
   `title` que lo aclara. Vero pidió las dos versiones completas y eso no entra en los USD 300.
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

---

## Lo que falta y hay que pedirle a Vero

Está construido con marcadores a la vista, no con relleno disimulado, así ella ve qué debe:

- **Foto de Espacio Mavenz.** Cero material y es una sección entera.
- **Fotos del equipo y de la red.**
- **Qué otros proyectos entran y con qué fotos.** Hoy sólo CARDINAL tiene material.
- **Los textos reales de "Contenido y mirada".**
- **Las URL de Instagram, LinkedIn y Facebook.**
- **Confirmar el WhatsApp y el correo.**

Aparte, en mensaje separado: **rotar la credencial de Gmail** que vino en texto plano en el
archivo de 2 Clics.

---

## Verificado y lo que no

Verificado con medición en vivo y captura: los tres carriles más el celular acostado, cero
desborde horizontal en los cuatro, las anclas del menú no quedan tapadas por la cabecera, la
rueda cambia de capacidad, el menú de celular abre y cierra, `prefers-reduced-motion` deja la
página completa y legible, consola sin errores.

**No verificado:** el toque real en un teléfono. El panel del navegador corre oculto en esta
máquina y no completa los clicks; las áreas táctiles están medidas (44 px, ninguna por debajo)
pero el gesto hay que probarlo en el teléfono.
