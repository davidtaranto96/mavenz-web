# demo — home de Mavenz

Base generada en Claude Design, extraída del lienzo y con efectos aplicados.

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

- Desktop 1280 y mobile 375, scrolleando de verdad: 0 de 7 elementos quedan ocultos.
- Con `prefers-reduced-motion: reduce`: 0 ocultos, todo el contenido visible.
- Sin scroll horizontal en ninguno de los dos anchos.

## Pendiente para la 2.0

El 65% de la superficie es marrón oscuro y solo el 18% clara. Hay que subir la proporción de claro.
El prompt para la segunda pasada está en `../prompt-claude-design-2.md`.
