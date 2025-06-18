#!/bin/bash

# Rutas
ONTOLOGY_TTL="../ontologias/ai-act-master.ttl"
ONTOLOGY_RDF="./ai-act-master.rdf"
REPORT_FILE="validation_result.html"
OOPS_CONTAINER_NAME="oops-validator"
OOPS_IMAGE="mpovedavillalon/oops:v2"
OOPS_PORT=80

# Verifica que el archivo TTL existe
if [ ! -f "$ONTOLOGY_TTL" ]; then
  echo "❌ Archivo '$ONTOLOGY_TTL' no encontrado."
  exit 1
fi

# Verifica que rapper está instalado
if ! command -v rapper &> /dev/null; then
  echo "❌ El comando 'rapper' no está instalado. Instálalo con:"
  echo "    sudo apt install raptor2-utils"
  exit 1
fi

# Convierte Turtle a RDF/XML
echo "🔄 Convirtiendo '$ONTOLOGY_TTL' a RDF/XML..."
rapper -i turtle "$ONTOLOGY_TTL" -o rdfxml-abbrev > "$ONTOLOGY_RDF"

if [ $? -ne 0 ]; then
  echo "❌ Error al convertir el archivo TTL a RDF/XML."
  exit 1
fi

# Inicia el contenedor si no está corriendo
if [ ! "$(docker ps -q -f name=$OOPS_CONTAINER_NAME)" ]; then
  if [ "$(docker ps -aq -f name=$OOPS_CONTAINER_NAME)" ]; then
    echo "🧹 Eliminando contenedor detenido '$OOPS_CONTAINER_NAME'..."
    docker rm -f $OOPS_CONTAINER_NAME
  fi

  echo "🚀 Iniciando contenedor OOPS!..."
  docker run -d --name $OOPS_CONTAINER_NAME -p $OOPS_PORT:8080 $OOPS_IMAGE
  echo "⏳ Esperando a que OOPS! esté listo (15s)..."
  sleep 15
fi

# Codifica en base64 el RDF/XML
echo "📦 Codificando '$ONTOLOGY_RDF' en base64..."
BASE64_ONTOLOGY=$(base64 "$ONTOLOGY_RDF")

# Envía la ontología a OOPS!
echo "📤 Enviando ontología a OOPS!..."
RESPONSE=$(curl -s -X POST "http://localhost/OOPS/rest" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "ontologyContent": "$BASE64_ONTOLOGY",
  "contentType": "base64",
  "outputFormat": "html"
}
EOF
)

# Guarda el resultado
echo "$RESPONSE" > "$REPORT_FILE"
echo "✅ Validación completada. Revisa el archivo 'tools/$REPORT_FILE'."

# Limpieza opcional
rm "$ONTOLOGY_RDF"

# Puedes también apagar y borrar el contenedor si deseas:
# docker stop $OOPS_CONTAINER_NAME && docker rm $OOPS_CONTAINER_NAME

