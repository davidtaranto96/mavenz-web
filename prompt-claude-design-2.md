# Prompt para la segunda pasada en Claude Design

Pegar de acá para abajo.

---

Estoy rehaciendo la home de **Mavenz**, una comercializadora de real estate de Salta, Argentina.
Ya hay una primera versión tuya y funciona, pero quedó demasiado oscura y quiero subirle el nivel
con criterio de diseñador senior.

## El diagnóstico de la v1

Medí la superficie de la página renderizada: **65% en marrón oscuro, 18% en claro**. Está dos
tercios en modo noche y se lee pesada. El problema no es el marrón, que es de la marca: es la
proporción.

## Lo que quiero de la v2

**Invertir la relación: que domine el claro y que el marrón oscuro pase a ser el anclaje.**

Y una trampa que quiero evitar de entrada: *claro no significa crema, arena, beige ni papel*.
Ese fondo cálido casi blanco es el default de todas las webs generadas hoy y se reconoce a
kilómetros. El blanco tiene que ser **blanco puro o un neutro con un toque mínimo del propio marrón
de la marca**, no un beige de plantilla. La calidez la aporta la tipografía en marrón, el acento
arena y las fotos, no el fondo.

Concretamente:

- **Blanco como base dominante**, con el marrón `#342223` reservado para tres o cuatro momentos de
  anclaje: el hero, una sección de método o manifiesto, y el cierre con el footer.
- El texto sobre blanco va en marrón, no en gris. Gris sobre blanco cálido es lo que hace que estas
  páginas se lean lavadas.
- Verificá contraste: cuerpo mínimo 4.5:1, titulares grandes 3:1.

## La marca

| Token | Hex | Rol propuesto para la v2 |
|---|---|---|
| Marrón principal | `#342223` | Anclaje: hero, una sección, footer. Y el color del texto sobre blanco |
| Marrón elevado | `#3d2729` | Una superficie apenas separada del anterior |
| Marrón medio | `#5b484a` | Texto secundario sobre claro |
| Arena | `#b7a18a` | Acento único, con moderación |
| Gris | `#a1a7a8` | Texto secundario sobre oscuro |
| Blanco | `#ffffff` | **La base nueva** |

Tipografía: **Urbanist** variable. Ya está en `assets/marca/Urbanist-Variable.ttf`.

Techo de tamaño para el titular: no pasar de 96px. Tracking del display: no bajar de −0.04em.

## Qué tiene que contener

Mavenz no es una inmobiliaria: **es la marca madre que contiene a todos sus proyectos.** Esa es la
idea que tiene que quedar clara en el primer scroll.

1. **Hero** — Claim "Generamos movimiento". Video aéreo de fondo o banda.
2. **Manifiesto** — Lo que Mavenz no es, y lo que sí: "Somos el partner estratégico que mueve el
   Real Estate".
3. **Universo Mavenz** — Las cuatro áreas: Estrategia, Desarrollo de Negocios, Comercialización,
   Gestión y Evolución.
4. **El Método** — El ciclo de cinco pasos que vuelve a empezar: Descubrir, Diseñar, Conectar,
   Activar, Generar Movimiento.
5. **Mapa Mavenz** — Los seis territorios de Salta. **El mapa Leaflet de la v1 funciona muy bien,
   conservalo**: tiles teñidos con la paleta, marcadores por territorio, y las cuatro preguntas
   fijas (qué está cambiando, quién lo elige, qué oportunidades aparecen, qué ve Mavenz).
6. **Proyectos** — CARDINAL (San Lorenzo Chico, 35 hogares, en comercialización) y CAFAY
   (Cafayate, en desarrollo). Más un lugar visible para los que vengan: la plataforma tiene que
   verse hecha para crecer.
7. **Espacio Mavenz** — El canal de comercialización, que vive en `espaciomavenz.com.ar`. Se
   enlaza, no se replica.
8. **Footer**.

## Assets

Todos en el repo, con URL directa:

```
https://davidtaranto96.github.io/mavenz-web/assets/<carpeta>/<archivo>
```

| Carpeta | Qué hay |
|---|---|
| `video/` | `banda-aerea-1.mp4` y `banda-aerea-2.mp4`. Dron sobre San Lorenzo Chico, ultrawide 1600×360, sin audio, 0,5 MB |
| `aereas/` | `aerea-dia`, `aerea-amplia`, `aerea-verde`. Fotos reales de dron, 1600×738 |
| `renders/` | `casas`, `amenities`, `comercial`, `interior`. **Son renders de CARDINAL, no fotos** |
| `proyectos/` | `porto-01..04`, `wa-storages-01/02`, `wa-cocheras`, `cardinal-cardenal`, `cardinal-post` |
| `planos/` | `cocheras-disponibles`, `storages-disponibles` |
| `marca/` | Logos claro y oscuro, isotipo, `trazo.svg`, `Urbanist-Variable.ttf` |

`trazo.svg` es el gesto del isotipo reducido a una sola línea abierta con `pathLength="1"`. Se
dibuja solo animando `stroke-dashoffset`. Es lo más de la marca que se puede animar.

**Decir que un render es un render.** En los pies de foto. Ninguna plantilla del rubro lo hace y es
el gesto de criterio más barato que existe acá.

## Movimiento

La v1 ya tiene reveal al scroll, header reactivo y carga diferida. Mantener eso y sumar con
criterio, no por cantidad.

- Curvas de salida exponenciales. Sin rebote, sin elástico.
- Bloque de `prefers-reduced-motion` obligatorio, con el contenido siempre visible.
- **El reveal nunca puede ser lo que hace visible al contenido.** Que la sección se vea por defecto
  y la animación la mejore. Si no, en un render sin scroll la página sale en blanco.
- Escalonar los ítems dentro de una lista está bien. Que todas las secciones entren igual, no.

## Lo que no quiero

Eyebrows en mayúscula arriba de cada sección · numerales 01/02/03 como andamiaje · fila de
estadísticas inventadas en el hero · fondo crema, arena o beige · Inter, Poppins o Roboto ·
texto con degradado · glassmorphism decorativo · grillas de tarjetas todas iguales · cursor
personalizado o partículas que siguen al mouse · titular animado letra por letra en el hero.

## La referencia contra la que se compara

`davidtaranto96.github.io/Aires-SanLorenzo` es del mismo barrio y del mismo rubro, y está bien
hecha. Mavenz tiene que estar a esa altura y **verse claramente distinta**: Aires vende un
proyecto, Mavenz lee el territorio y contiene muchos. Si alguien en Salta las pone al lado, la
diferencia tiene que ser evidente.

## Copy

Voseo argentino. Sin signos de exclamación. Sin emojis. CTAs en infinitivo. Todo el copy sale del
material de la marca, nada inventado.
