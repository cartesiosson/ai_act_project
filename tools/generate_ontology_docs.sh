#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------
# Script para generar documentación HTML de la ontología con Widoco
# Levanta un servidor local para usar -ontURI y lo apaga al terminar
# ----------------------------------------------------------------

WIDOCO_JAR="widoco/Widoco-1.4.25-jar-with-dependencies_JDK-17.jar"

# Cargar versión actual desde entorno
source "../tools/ontologias.env"
VERSION="$CURRENT_RELEASE"
ONTOLOGY_DIR="../ontologias/versions/${VERSION}"
TTL_FILE="ai-act-v${VERSION}.ttl"
TTL_URI="http://localhost:8080/${TTL_FILE}"
OUT_FOLDER="../docs/ontology"
LANGUAGES="es-en"

# Lanzar servidor HTTP en segundo plano
cd "$ONTOLOGY_DIR"
echo "🌐 Lanzando servidor local para servir ${TTL_FILE}..."
python3 -m http.server 8080 > /dev/null 2>&1 &
SERVER_PID=$!

# Esperar unos segundos a que arranque el servidor
sleep 3

# Volver al directorio original del script
cd - > /dev/null

echo "📄 Generando documentación desde $TTL_URI ..."
java -jar "${WIDOCO_JAR}" \
  -ontURI "$TTL_URI" \
  -outFolder "${OUT_FOLDER}" \
  -lang "${LANGUAGES}" \
  -rewriteAll \
  -includeImportedOntologies \
  -uniteSections \
  -oops

# Detener servidor local
echo "🛑 Apagando servidor local (PID $SERVER_PID)..."
kill "$SERVER_PID"

echo "✅ ¡Documentación generada en ${OUT_FOLDER}/index.html!"
