#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------
# Script para generar documentación HTML de la ontología con Widoco
# ----------------------------------------------------------------

# Ruta al JAR de Widoco (asegúrate de que coincida con el nombre real)
WIDOCO_JAR="tools/widoco/Widoco-1.4.25-jar-with-dependencies_JDK-17.jar"

# Fichero “master” que importa todos tus TTL
MASTER_TTL="ontologias/ai-act-master.ttl"

# Carpeta donde se volcará la doc generada
OUT_FOLDER="docs/ontology"

# Idiomas de la documentación (en Widoco se separan con “-”)
LANGUAGES="es-en"

# Opciones extra de Widoco:
#  -rewriteAll: fuerza regeneración completa
#  -includeImportedOntologies: documenta también cada ontología importada
#  -uniteSections: (opcional) genera un único HTML con todas las secciones
EXTRA_OPTS=(
  "-rewriteAll"
  "-includeImportedOntologies"
  "-uniteSections"
  "-oops"
)

echo "Generando documentación de la ontología a partir de ${MASTER_TTL}..."
java -jar "${WIDOCO_JAR}" \
  -ontFile "${MASTER_TTL}" \
  -outFolder "${OUT_FOLDER}" \
  -lang "${LANGUAGES}" \
  "${EXTRA_OPTS[@]}"

echo "¡Documentación generada en ${OUT_FOLDER}/index.html!"
