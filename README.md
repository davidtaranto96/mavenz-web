# Mavenz — plataforma web

Assets y brief para construir la plataforma de Mavenz. Todo lo de acá salió del material que
mandó la clienta: kit de marca, videos de sus posteos y fotos de sus proyectos.

Una vez publicado con GitHub Pages, cada archivo tiene URL directa:

```
https://davidtaranto96.github.io/mavenz-web/assets/<carpeta>/<archivo>
```

---

## Qué es Mavenz

Comercializadora de real estate de Salta. **No es una inmobiliaria más: es la marca madre que
contiene a todos sus proyectos.** Esa es la idea central de la plataforma.

- Claim: **Generamos movimiento.**
- Posicionamiento: *"Somos el partner estratégico que mueve el Real Estate. Detectamos
  oportunidades, diseñamos estrategias y potenciamos la comercialización."*
- Se define por negación: *"No somos una inmobiliaria tradicional. No somos solamente una
  comercializadora. No somos una agencia."*
- Personalidad: estratégica, curiosa, cercana, elegante, colaborativa, visionaria, con criterio.

### Lo que tiene que contener la plataforma

| Nivel | Qué es |
|---|---|
| **Mavenz** | La marca madre. Quiénes son, el Método, el Mapa Mavenz |
| **Espacio Mavenz** | El canal de comercialización, con el listado de propiedades. Hoy vive en `espaciomavenz.com.ar` |
| **Proyectos** | CARDINAL, CAFAY, WA y los que vengan. Cada uno con su página y su link propio para pautar |

### Universo Mavenz — las cuatro áreas
Estrategia · Desarrollo de Negocios · Comercialización · Gestión y Evolución

### Método Mavenz — el ciclo de cinco pasos
Descubrir → Diseñar → Conectar → Activar → Generar Movimiento → y vuelve a empezar

### Mapa Mavenz — los seis territorios
Su gran diferencial. Cada territorio se lee con las mismas cuatro preguntas: qué está cambiando,
quién lo elige, qué oportunidades aparecen, qué ve Mavenz.

1. **Micro y Macrocentro** — Donde el patrimonio comienza a transformarse
2. **Zona Norte** — La ciudad crece hacia la naturaleza
3. **San Lorenzo** — Dos territorios, dos formas distintas de vivir
4. **Zona Aeropuerto y San Luis** — Conectividad que impulsa crecimiento
5. **Cafayate y Cachi** — Invertir también es elegir una forma de vivir
6. **Vaqueros** — Una respuesta eco-cultural

---

## Marca

### Color

| Token | Hex | Uso |
|---|---|---|
| Marrón principal | `#342223` | Fondo oscuro dominante |
| Marrón elevado | `#3d2729` | Superficie un escalón más clara |
| Marrón medio | `#5b484a` | Texto secundario sobre claro |
| Arena | `#b7a18a` | Acento |
| Arena oscuro | `#9c8976` | Hover del acento |
| Gris | `#a1a7a8` | Texto secundario sobre oscuro |
| Blanco | `#ffffff` | Fondo claro |

### Tipografía

**Urbanist**, variable, licencia OFL. Está en `assets/marca/Urbanist-Variable.ttf` y también en
Google Fonts. Es la tipografía oficial del kit de marca.

### Logo

| Archivo | Cuándo usarlo |
|---|---|
| `marca/logo-horizontal-claro.png` | Sobre fondo marrón. **Es el que se usa casi siempre** |
| `marca/logo-horizontal-oscuro.png` | Sobre fondo blanco |
| `marca/logo-vertical-claro.png` | Formatos verticales |
| `marca/isotipo-claro.png` · `isotipo-oscuro.png` | Solo el símbolo, sin texto |
| `marca/Identidad.ai` | El vectorial original de Fractura Studio |
| `marca/trazo.svg` | El gesto del isotipo como una sola línea abierta, `pathLength="1"`, listo para animar con `stroke-dashoffset` |

El isotipo es un gesto caligráfico continuo: un lazo, un barrido y un arco. `trazo.svg` es ese
mismo gesto reducido a una línea de un solo trazo, pensado para dibujarse con animación.

---

## Assets

### `assets/video/` — lo mejor que hay

| Archivo | Qué muestra | Medidas | Peso |
|---|---|---|---|
| `banda-aerea-1.mp4` | Dron sobre San Lorenzo Chico, montañas de fondo, 5,8 s | 1600×360 | 0,27 MB |
| `banda-aerea-2.mp4` | Dron, plano más abierto del valle, 7,8 s | 1600×360 | 0,38 MB |

Sin audio, listos para `autoplay muted loop playsinline`.

**Por qué son ultrawide y no cuadro completo.** Los videos originales son posteos de Instagram ya
terminados, con el subtitulado quemado **en el centro del cuadro**, no abajo. No hay forma de
sacarlo recortando por abajo. Lo que sí funciona es quedarse con el 40% superior del cuadro y solo en la ventana donde
tampoco hay rótulos arriba a la derecha (1 a 6,8 s en el primero, 1 a 8,8 s en el segundo): da cielo, montaña y barrio, en una banda cinematográfica de 4,4:1 sin una
sola letra encima. Es el formato que mejor le sienta a un hero de plataforma.

**Si hace falta el cuadro completo en movimiento, hay que pedirle a Vero el metraje original sin
subtitular.** Quien editó esos videos lo tiene. Sería el mejor upgrade posible de todo el paquete:
hay tomas de dron muy buenas debajo de esos carteles.

### `assets/aereas/` — tomas reales de dron

| Archivo | Qué muestra |
|---|---|
| `aerea-dia.jpg` | San Lorenzo Chico de día, con las montañas de fondo |
| `aerea-amplia.jpg` | Plano abierto del valle |
| `aerea-verde.jpg` | Zona verde con la avenida principal |

Todas 1600×738. Son **fotos reales**, no renders.

### `assets/renders/` — renders de CARDINAL

| Archivo | Qué muestra |
|---|---|
| `casas.jpg` | Casas con familias, calle arbolada |
| `amenities.jpg` | Pileta y quincho de piedra |
| `comercial.jpg` | Esquina comercial, toldos bordó, guirnaldas |
| `interior.jpg` | Cocina y living con hogar a leña |

**Son renders, no fotos.** Conviene decirlo en el pie de foto: es un gesto de criterio que
ninguna plantilla del rubro hace.

### `assets/proyectos/` — fotos reales de producto

| Archivo | Qué muestra |
|---|---|
| `porto-01..04.jpg` | Oficina vacía con ventanal, baño, palier con ascensor, cocina con mesada de granito |
| `wa-storages-01.jpg` · `02.jpg` | Pasillos de storages numerados, iluminación lineal |
| `wa-cocheras.jpg` | Cochera cubierta, tomas largas |
| `cardinal-cardenal.jpg` | Pieza de marca: el cardenal, *"¿Sabías que el cardenal siempre vuelve a su hogar?"* |
| `cardinal-post.jpg` | Pieza de marca: *"Es un ave que representa pertenencia. Movimiento. Identidad."* |

Ojo: el material de **WA** (Porto, storages, cocheras) es de Grupo MDay. En los documentos que
mandó la clienta, Mavenz no aparece nombrada junto a WA ni una vez. Antes de publicarlo hay que
confirmar que Mavenz lo comercializa.

### `assets/planos/` — inventario

| Archivo | Qué muestra |
|---|---|
| `cocheras-disponibles.jpg` | Plano del subsuelo con las cocheras disponibles en verde |
| `storages-disponibles.jpg` | Plano de storages con la tabla de superficies por unidad |

Los storages disponibles son las unidades 9, 10, 11, 12, 21, 22, 23, 24 y 26, con superficies de
4,86 a 24,84 m². **La unidad 9, de 14,09 m², es la misma que está publicada en
espaciomavenz.com.ar como `MAV-226174` a USD 35.000**, así que los datos del plano y del CRM
coinciden. Sirven para un plano interactivo de disponibilidad.

---

## Lo que pidió la clienta

Textual: **algo que rompa con lo convencional del rubro.** Dijo que las webs inmobiliarias que
mira le parecen todas iguales, y tiene razón: casi todas salen de la misma plantilla comprada
(theme Houzez y similares). Su propio sitio actual, `espaciomavenz.com.ar`, es uno de esos.

Quiere movimiento, efectos y color. No quiere un catálogo.

### Lo que hay que evitar

Eyebrows en mayúscula arriba de cada sección · estadísticas inventadas en el hero · fondos crema
o beige genéricos · Inter, Poppins o Roboto · numerales 01/02/03 por sección · glassmorphism
decorativo · texto con degradado · grillas de tarjetas todas iguales · copy que serviría para
cualquier marca.

### La referencia a superar

`davidtaranto96.github.io/Aires-SanLorenzo` es del mismo barrio y del mismo rubro. La plataforma
de Mavenz tiene que estar a esa altura y verse claramente distinta: Aires vende **un** proyecto,
Mavenz **lee el territorio y contiene muchos**.

---

## Contexto técnico

- El listado de propiedades vive en `espaciomavenz.com.ar`, un WordPress con theme Houzez que
  provee el CRM **Negocios de 2 Clics**, que Mavenz ya paga. Desde la plataforma se enlaza, no se
  reemplaza.
- Dominios: `mavenz.com.ar` y `espaciomavenz.com.ar` ya están registrados a nombre de ellas.
  `mavenz.ar` está libre. `mavenz.com` es de una empresa del exterior.
- Ninguno de los dos sitios publicados tiene analítica ni píxel instalado.
