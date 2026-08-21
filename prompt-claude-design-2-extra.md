# Anexo al prompt de la 2.0 — carácter y movimiento

Se pega después del prompt principal. Este anexo es sobre **cómo se siente**, no sobre qué contiene.

---

## El punto de partida

La clienta es usuaria de Apple y le gusta lo moderno. Y me pidió, textual, algo que rompa con lo
convencional del rubro. Las dos cosas apuntan al mismo lado y conviene decirlo con precisión,
porque "moderno" mal entendido termina en degradados violetas.

**Apple no es un estilo visual, es una forma de responder.** Lo que hace que algo se sienta de esa
familia no son los bordes redondeados ni el vidrio esmerilado: es que la interfaz contesta al
instante, que el movimiento arranca desde donde la cosa está y no desde donde debería estar, y que
todo se puede interrumpir a mitad de camino.

## Contra qué compite

Todas las inmobiliarias y constructoras de Salta usan la misma plantilla comprada, casi siempre el
theme Houzez. Se reconocen por tres cosas:

1. Hero con barra de búsqueda de propiedades encima de una foto.
2. Grilla de tarjetas de propiedad, todas del mismo tamaño.
3. Carrusel de renders con flechitas.

Mavenz tiene que verse distinta desde el primer scroll, y la forma más barata de lograrlo es
**no hacer ninguna de esas tres**. No poner buscador en la home es la declaración de
posicionamiento más fuerte y no cuesta una línea de código: el listado vive en Espacio Mavenz y se
enlaza.

## Movimiento: resortes, no duraciones

Reemplazá las transiciones de duración fija por resortes. Un resorte se puede agarrar a mitad de
camino y redirigir; una transición de 400 ms, no.

| Interacción | Amortiguación | Respuesta |
|---|---|---|
| Mover o reposicionar algo | 1.0 (sin rebote) | 0.4 s |
| Abrir un panel o una ficha | 0.8 | 0.3 s |
| Todo lo demás por defecto | 1.0 | 0.3 a 0.4 s |

Reglas que van con eso:

- **Feedback al apretar, no al soltar.** El botón responde en el `pointerdown`, no en el `click`.
- **La animación arranca del valor actual en pantalla**, nunca del valor lógico. Si alguien
  interrumpe algo a mitad, no puede haber salto.
- **Nada de rebote ni elástico** salvo que el gesto haya traído impulso, como un arrastre soltado.
- **Nada que siga al cursor** sin `@media (hover:hover) and (pointer:fine)`.

## Materiales y profundidad

Acá sí entra lo de Apple, pero con criterio:

- La barra superior puede ser una capa traslúcida con `backdrop-filter`, con el contenido pasando
  por abajo. **Nunca dos superficies traslúcidas una encima de la otra**: se cae la legibilidad.
- El peso del material indica jerarquía: más oscuro y más difuso para lo estructural, más liviano
  para lo interactivo.
- En el borde donde el contenido se mete abajo de la barra fija, va un desvanecido corto en vez de
  una línea de 1px. La línea dura se lee a plantilla.
- Respetá `prefers-reduced-transparency`: ahí la barra pasa a sólida y sin blur.

## Tipografía

Urbanist es la fuente de la marca y no se cambia. Lo que sí hay que hacer es tratarla como se
trata una tipografía variable:

- **El tracking es por tamaño, nunca uno solo para todo.** El display grande va con tracking
  negativo, el cuerpo en cero, y lo micro apenas positivo. Un `letter-spacing` fijo está mal en
  algún lado siempre.
- **El interlineado es inverso al tamaño.** Ajustado en los titulares, holgado en el cuerpo.
- La jerarquía se construye con peso, tamaño e interlineado como conjunto, no estirando el tamaño.
- Techo del titular: 96px. Piso del tracking del display: −0.04em.

## Composición

Lo que más va a diferenciarla del rubro:

- **Romper la grilla en algún lado.** Una imagen que se sale del contenedor, un bloque que arranca
  en la columna 3 y deja el tercio derecho vacío a propósito. La simetría permanente es lo que hace
  que una página se lea a plantilla.
- **Asimetría con intención en los proyectos.** Cardinal está en comercialización y Cafay en
  desarrollo: que se note en cuánto espacio ocupa cada uno, sin tener que explicarlo con texto.
- **Densidad variable.** Secciones que respiran mucho al lado de secciones densas. El ritmo es lo
  que se recuerda.
- Nada de tarjetas iguales repetidas. Si aparece una grilla de cards con ícono, título y bajada,
  está mal.

## El detalle que se va a recordar

Buscá una sola cosa memorable y hacela bien, en vez de diez efectos repartidos.

Candidatos que salen de la propia marca:

- **El trazo del isotipo dibujándose** una vez, al entrar, cruzando el hero. Está en
  `assets/marca/trazo.svg`, es un solo path abierto con `pathLength="1"`.
- **El mapa de territorios** respondiendo con resorte al pasar de uno a otro, con la vista
  desplazándose en vez de saltando.
- **El ciclo del Método** dibujándose como una forma continua que vuelve sobre sí misma, en vez de
  cinco pasos numerados.

Uno alcanza. Tres es demasiado.

## Accesibilidad, que no es opcional

- `prefers-reduced-motion`: los desplazamientos y resortes pasan a fundidos cortos. El contenido
  siempre visible.
- Foco visible en todo lo interactivo.
- Contraste de cuerpo 4.5:1 como mínimo.
