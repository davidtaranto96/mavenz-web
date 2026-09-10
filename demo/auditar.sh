#!/bin/sh
# Corre el auditor de siete carriles sobre las diez URLs de la demo (ES y EN).
# Antes: `python3 -m http.server 8899` en mavenz-web/ (sirve /demo/...).
# Necesita el venv con websocket-client: ~/.claude/skills/visual-verify/scripts/auditar.py lo explica.
B=${1:-http://localhost:8899/demo}
exec python3 ~/.claude/skills/visual-verify/scripts/auditar.py \
  "$B/index.html" "$B/proyectos.html" "$B/cardinal.html" "$B/espacio.html" "$B/nosotros.html" \
  "$B/contacto.html" "$B/en/index.html" "$B/en/proyectos.html" "$B/en/cardinal.html" "$B/en/espacio.html" "$B/en/nosotros.html" "$B/en/contacto.html"
