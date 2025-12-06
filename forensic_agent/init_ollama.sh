#!/bin/bash

# Script para inicializar Ollama con el modelo Llama 3.2

set -e

echo "=================================="
echo "Inicializando Ollama"
echo "=================================="

OLLAMA_ENDPOINT="${OLLAMA_ENDPOINT:-http://localhost:11434}"
MODEL="${OLLAMA_MODEL:-llama3.2}"

echo ""
echo "Esperando a que Ollama esté disponible..."
until curl -s "${OLLAMA_ENDPOINT}/api/tags" > /dev/null 2>&1; do
    echo "  Esperando Ollama en ${OLLAMA_ENDPOINT}..."
    sleep 2
done

echo "✓ Ollama está disponible"
echo ""

echo "Verificando si el modelo ${MODEL} está instalado..."
if curl -s "${OLLAMA_ENDPOINT}/api/tags" | grep -q "\"name\":\"${MODEL}\""; then
    echo "✓ Modelo ${MODEL} ya está instalado"
else
    echo "Descargando modelo ${MODEL}..."
    echo "  (esto puede tardar varios minutos dependiendo de tu conexión)"
    echo ""

    curl -X POST "${OLLAMA_ENDPOINT}/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"${MODEL}\"}" \
        --no-buffer

    echo ""
    echo "✓ Modelo ${MODEL} descargado exitosamente"
fi

echo ""
echo "=================================="
echo "Ollama configurado correctamente"
echo "=================================="
echo ""
echo "Modelos disponibles:"
curl -s "${OLLAMA_ENDPOINT}/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4
echo ""
echo "Para probar el modelo:"
echo "  curl ${OLLAMA_ENDPOINT}/api/generate -d '{\"model\": \"${MODEL}\", \"prompt\": \"Hello\"}'"
