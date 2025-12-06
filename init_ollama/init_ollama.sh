#!/bin/sh

# Script para inicializar Ollama con el modelo configurado
# Se ejecuta una sola vez - el modelo se guarda en volumen persistente

set -e

echo "=================================="
echo "Inicializando Ollama"
echo "=================================="

OLLAMA_ENDPOINT="${OLLAMA_ENDPOINT:-http://ollama:11434}"
MODEL="${OLLAMA_MODEL:-llama3.2}"

echo ""
echo "Esperando a que Ollama este disponible..."
MAX_RETRIES=60
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "${OLLAMA_ENDPOINT}/api/tags" > /dev/null 2>&1; then
        echo "Ollama esta disponible"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Esperando Ollama en ${OLLAMA_ENDPOINT}... (intento ${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Ollama no responde despues de ${MAX_RETRIES} intentos"
    exit 1
fi

echo ""
echo "Verificando si el modelo ${MODEL} esta instalado..."

# Verificar si el modelo ya existe
if curl -s "${OLLAMA_ENDPOINT}/api/tags" | grep -q "\"name\":\"${MODEL}"; then
    echo "Modelo ${MODEL} ya esta instalado"
    echo ""
    echo "Modelos disponibles:"
    curl -s "${OLLAMA_ENDPOINT}/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4
    echo ""
    echo "=================================="
    echo "Ollama listo - modelo ya disponible"
    echo "=================================="
    exit 0
fi

echo "Descargando modelo ${MODEL}..."
echo "  (esto puede tardar varios minutos la primera vez)"
echo ""

# Descargar el modelo
curl -X POST "${OLLAMA_ENDPOINT}/api/pull" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${MODEL}\"}" \
    --no-buffer

echo ""
echo "Modelo ${MODEL} descargado exitosamente"
echo ""
echo "=================================="
echo "Ollama configurado correctamente"
echo "=================================="
echo ""
echo "Modelos disponibles:"
curl -s "${OLLAMA_ENDPOINT}/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4
echo ""
