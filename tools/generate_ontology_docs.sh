#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------
# Script para generar documentación HTML de la ontología con Widoco
# Levanta un servidor local para usar -ontURI y lo apaga al terminar
# Post-procesa los HTML para añadir autores y casos de uso
# ----------------------------------------------------------------

WIDOCO_JAR="widoco/Widoco-1.4.25-jar-with-dependencies_JDK-17.jar"

# Cargar versión actual desde entorno
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/ontologias.env"
echo "${SCRIPT_DIR}/ontologias.env cargado."
VERSION="$CURRENT_RELEASE"
ONTOLOGY_DIR="../ontologias/versions/${VERSION}"
TTL_FILE="ontologia-v${VERSION}.ttl"
HTTP_PORT="8080"
TTL_URI="http://localhost:${HTTP_PORT}/${TTL_FILE}"
OUT_FOLDER="../ontologias/docs"
LANGUAGES="es-en"

# ================================================================
# Contenido personalizado para la documentación
# ================================================================

# Abstract en español
ABSTRACT_ES='La <strong>Ontología Unificada del EU AI Act</strong> proporciona un modelo semántico formal para la representación, clasificación y evaluación de sistemas de Inteligencia Artificial bajo el marco regulatorio del Reglamento Europeo de Inteligencia Artificial (EU AI Act - Regulation 2024/1689).

<h3>Autores</h3>
<ul>
<li><strong>Mariano Ortega de Mues</strong> - Universidad Internacional de La Rioja (UNIR)</li>
<li><strong>David Fernández González</strong> - Universidad Internacional de La Rioja (UNIR)</li>
<li>Máster en Inteligencia Artificial - Curso 2024-2025</li>
<li>Trabajo Fin de Máster: SERAMIS - Sistema de Evaluación de Riesgos y Análisis de Mitigaciones de IA Semántico</li>
</ul>

<h3>Casos de Uso Soportados</h3>
<ol>
<li><strong>Clasificación Automática de Riesgo</strong>: Inferencia semántica del nivel de riesgo (Inaceptable, Alto, Limitado, Mínimo) basada en propósitos, contextos de despliegue y criterios normativos del AI Act.</li>
<li><strong>Detección de Prácticas Prohibidas (Art. 5)</strong>: Identificación automática de sistemas que emplean manipulación subliminal, explotación de vulnerabilidades, social scoring, predictive policing o identificación biométrica remota en tiempo real.</li>
<li><strong>Gestión de Excepciones Art. 5.2</strong>: Soporte para excepciones legales de identificación biométrica con autorización judicial (búsqueda de víctimas, amenazas terroristas, delitos graves).</li>
<li><strong>Análisis de Ámbito de Aplicación (Art. 2)</strong>: Determinación de exclusiones de scope para sistemas militares, I+D, uso personal no profesional, y acuerdos internacionales.</li>
<li><strong>Derivación de Requisitos de Cumplimiento</strong>: Inferencia automática de obligaciones según Títulos III (Alto Riesgo) y IV (Transparencia), incluyendo requisitos técnicos y documentales.</li>
<li><strong>Clasificación de Modelos GPAI (Art. 51-55)</strong>: Identificación de modelos de IA de propósito general y evaluación de riesgo sistémico.</li>
<li><strong>Análisis Forense Post-Incidente</strong>: Extracción estructurada de información de narrativas de incidentes para evaluación retrospectiva de cumplimiento.</li>
<li><strong>Mapeo Multi-Framework</strong>: Alineamiento semántico con ISO/IEC 42001, NIST AI RMF 1.0, y W3C Data Privacy Vocabulary (DPV).</li>
</ol>'

# Abstract en inglés
ABSTRACT_EN='The <strong>EU AI Act Unified Ontology</strong> provides a formal semantic model for the representation, classification, and assessment of Artificial Intelligence systems under the European AI Act regulatory framework (Regulation 2024/1689).

<h3>Authors</h3>
<ul>
<li><strong>Mariano Ortega de Mues</strong> - Universidad Internacional de La Rioja (UNIR)</li>
<li><strong>David Fernández González</strong> - Universidad Internacional de La Rioja (UNIR)</li>
<li>Master in Artificial Intelligence - Academic Year 2024-2025</li>
<li>Master Thesis: SERAMIS - Semantic AI Risk Evaluation and Mitigation Analysis System</li>
</ul>

<h3>Supported Use Cases</h3>
<ol>
<li><strong>Automatic Risk Classification</strong>: Semantic inference of risk level (Unacceptable, High, Limited, Minimal) based on purposes, deployment contexts, and AI Act normative criteria.</li>
<li><strong>Prohibited Practices Detection (Art. 5)</strong>: Automatic identification of systems employing subliminal manipulation, vulnerability exploitation, social scoring, predictive policing, or real-time remote biometric identification.</li>
<li><strong>Art. 5.2 Exception Management</strong>: Support for legal exceptions for biometric identification with judicial authorization (victim search, terrorist threats, serious crimes).</li>
<li><strong>Scope Analysis (Art. 2)</strong>: Determination of scope exclusions for military systems, R&amp;D, non-professional personal use, and international agreements.</li>
<li><strong>Compliance Requirements Derivation</strong>: Automatic inference of obligations under Titles III (High Risk) and IV (Transparency), including technical and documentary requirements.</li>
<li><strong>GPAI Model Classification (Art. 51-55)</strong>: Identification of general-purpose AI models and systemic risk assessment.</li>
<li><strong>Post-Incident Forensic Analysis</strong>: Structured extraction of information from incident narratives for retrospective compliance evaluation.</li>
<li><strong>Multi-Framework Mapping</strong>: Semantic alignment with ISO/IEC 42001, NIST AI RMF 1.0, and W3C Data Privacy Vocabulary (DPV).</li>
</ol>'

# Introducción en español
INTRO_ES='Esta ontología forma parte del proyecto <strong>SERAMIS</strong> (Sistema de Evaluación de Riesgos y Análisis de Mitigaciones de IA Semántico), desarrollado como Trabajo Fin de Máster en la Universidad Internacional de La Rioja.

<h3>Motivación</h3>
<p>El EU AI Act (Reglamento 2024/1689) establece un marco regulatorio complejo con múltiples categorías de riesgo, requisitos técnicos y obligaciones documentales. La evaluación manual de cumplimiento es propensa a errores y difícil de escalar. Esta ontología permite automatizar la clasificación mediante razonamiento semántico.</p>

<h3>Arquitectura</h3>
<p>La ontología sigue un enfoque <em>ontology-first</em> donde:</p>
<ul>
<li>Los conceptos del AI Act se modelan como clases OWL</li>
<li>Las relaciones regulatorias se expresan como object/data properties</li>
<li>Las reglas de inferencia se implementan en SWRL (externalizadas en /rules)</li>
<li>Las restricciones de validación se definen en SHACL (externalizadas en /shacl)</li>
</ul>

<h3>Namespaces</h3>
<ul>
<li><code>ai:</code> - Namespace principal unificado (http://ai-act.eu/ai#)</li>
<li><code>airo:</code> - AI Risk Ontology (https://w3id.org/airo#)</li>
<li><code>dpv:</code> - W3C Data Privacy Vocabulary</li>
<li><code>eli:</code> - European Legislation Identifier</li>
</ul>'

# Introducción en inglés
INTRO_EN='This ontology is part of the <strong>SERAMIS</strong> project (Semantic AI Risk Evaluation and Mitigation Analysis System), developed as a Master Thesis at Universidad Internacional de La Rioja.

<h3>Motivation</h3>
<p>The EU AI Act (Regulation 2024/1689) establishes a complex regulatory framework with multiple risk categories, technical requirements, and documentary obligations. Manual compliance assessment is error-prone and difficult to scale. This ontology enables automated classification through semantic reasoning.</p>

<h3>Architecture</h3>
<p>The ontology follows an <em>ontology-first</em> approach where:</p>
<ul>
<li>AI Act concepts are modeled as OWL classes</li>
<li>Regulatory relationships are expressed as object/data properties</li>
<li>Inference rules are implemented in SWRL (externalized in /rules)</li>
<li>Validation constraints are defined in SHACL (externalized in /shacl)</li>
</ul>

<h3>Namespaces</h3>
<ul>
<li><code>ai:</code> - Main unified namespace (http://ai-act.eu/ai#)</li>
<li><code>airo:</code> - AI Risk Ontology (https://w3id.org/airo#)</li>
<li><code>dpv:</code> - W3C Data Privacy Vocabulary</li>
<li><code>eli:</code> - European Legislation Identifier</li>
</ul>'

# Lanzar servidor HTTP en segundo plano
cd "$ONTOLOGY_DIR"
echo "📂 Usando directorio de ontología: ${ONTOLOGY_DIR}"
echo "🌐 Lanzando servidor local en puerto ${HTTP_PORT} para servir ${TTL_FILE}..."
python3 -m http.server ${HTTP_PORT} > /dev/null 2>&1 &
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
echo "🛑 Apagando servidor local (puerto ${HTTP_PORT})..."
kill "$SERVER_PID"


echo "✅ ¡Documentación generada en ${OUT_FOLDER}/index.html!"

# ================================================================
# Post-procesamiento: Insertar contenido personalizado en los HTML
# ================================================================
echo "📝 Insertando contenido personalizado en la documentación..."

# Función para escapar caracteres especiales para sed
escape_for_sed() {
    echo "$1" | sed 's/[&/\]/\\&/g' | sed ':a;N;$!ba;s/\n/\\n/g'
}

# Guardar contenido en archivos temporales para evitar problemas con caracteres especiales
TEMP_DIR=$(mktemp -d)
echo "$ABSTRACT_ES" > "$TEMP_DIR/abstract_es.html"
echo "$ABSTRACT_EN" > "$TEMP_DIR/abstract_en.html"
echo "$INTRO_ES" > "$TEMP_DIR/intro_es.html"
echo "$INTRO_EN" > "$TEMP_DIR/intro_en.html"

# Procesar index-es.html
if [ -f "${OUT_FOLDER}/index-es.html" ]; then
    echo "  → Procesando index-es.html..."

    # Usar Python para reemplazo más robusto
    python3 << PYTHON_SCRIPT
import re

# Leer archivos
with open("${OUT_FOLDER}/index-es.html", "r", encoding="utf-8") as f:
    content = f.read()

with open("$TEMP_DIR/abstract_es.html", "r", encoding="utf-8") as f:
    abstract_es = f.read()

with open("$TEMP_DIR/intro_es.html", "r", encoding="utf-8") as f:
    intro_es = f.read()

# Reemplazar abstract (español)
abstract_pattern = r'(<div id="abstract"><h2>S&iacute;ntesis</h2><span class="markdown">)[^<]*(</span>)'
abstract_replacement = r'\1' + abstract_es + r'\2'
content = re.sub(abstract_pattern, abstract_replacement, content, flags=re.DOTALL)

# Reemplazar introducción (español)
intro_pattern = r'(<div id="introduction"><h2 id="intro" class="list">Introducci&oacute;n <span class="backlink"> volver a <a href="#toc">&iacute;ndice</a></span></h2>\s*<span class="markdown">)[^<]*(</span>)'
intro_replacement = r'\1' + intro_es + r'\2'
content = re.sub(intro_pattern, intro_replacement, content, flags=re.DOTALL)

# Escribir resultado
with open("${OUT_FOLDER}/index-es.html", "w", encoding="utf-8") as f:
    f.write(content)

print("    ✓ Abstract y Introducción actualizados en español")
PYTHON_SCRIPT
fi

# Procesar index-en.html
if [ -f "${OUT_FOLDER}/index-en.html" ]; then
    echo "  → Procesando index-en.html..."

    python3 << PYTHON_SCRIPT
import re

# Leer archivos
with open("${OUT_FOLDER}/index-en.html", "r", encoding="utf-8") as f:
    content = f.read()

with open("$TEMP_DIR/abstract_en.html", "r", encoding="utf-8") as f:
    abstract_en = f.read()

with open("$TEMP_DIR/intro_en.html", "r", encoding="utf-8") as f:
    intro_en = f.read()

# Reemplazar abstract (inglés)
abstract_pattern = r'(<div id="abstract"><h2>Abstract</h2><span class="markdown">)[^<]*(</span>)'
abstract_replacement = r'\1' + abstract_en + r'\2'
content = re.sub(abstract_pattern, abstract_replacement, content, flags=re.DOTALL)

# Reemplazar introducción (inglés)
intro_pattern = r'(<div id="introduction"><h2 id="intro" class="list">Introduction <span class="backlink"> back to <a href="#toc">ToC</a></span></h2>\s*<span class="markdown">)[^<]*(</span>)'
intro_replacement = r'\1' + intro_en + r'\2'
content = re.sub(intro_pattern, intro_replacement, content, flags=re.DOTALL)

# Escribir resultado
with open("${OUT_FOLDER}/index-en.html", "w", encoding="utf-8") as f:
    f.write(content)

print("    ✓ Abstract and Introduction updated in English")
PYTHON_SCRIPT
fi

# Limpiar archivos temporales
rm -rf "$TEMP_DIR"

echo "✅ Contenido personalizado insertado correctamente"

# Generar context.jsonld
echo "📄 Generando context.jsonld..."
"${SCRIPT_DIR}/generate_context.sh"

echo "🎉 ¡Proceso completo!"