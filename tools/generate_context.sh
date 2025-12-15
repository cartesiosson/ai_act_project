#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------
# Script para generar context.jsonld desde la ontología TTL
# Extrae todas las propiedades ai: y genera el contexto JSON-LD
# ----------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/ontologias.env"

VERSION="$CURRENT_RELEASE"
TTL_FILE="${SCRIPT_DIR}/../ontologias/versions/${VERSION}/ontologia-v${VERSION}.ttl"
DPV_FILE="${SCRIPT_DIR}/../ontologias/mappings/dpv-integration.ttl"
CONTEXT_OUT="${SCRIPT_DIR}/../ontologias/docs/context.jsonld"
CONTEXT_ROOT="${SCRIPT_DIR}/../ontologias/json-ld-context.json"

echo "📄 Generando context.jsonld desde ontología v${VERSION}..."

# Función para extraer propiedades de un archivo TTL
extract_properties() {
    local file="$1"
    local prefix="$2"

    if [[ -f "$file" ]]; then
        # Extraer propiedades que son ObjectProperty o DatatypeProperty
        grep -E "^${prefix}:[a-zA-Z]+" "$file" 2>/dev/null | \
            grep -E "(ObjectProperty|DatatypeProperty)" | \
            sed -E "s/^(${prefix}:[a-zA-Z]+).*/\1/" | \
            sort -u
    fi
}

# Función para determinar el tipo de una propiedad
get_property_type() {
    local prop="$1"
    local name="${prop#*:}"

    # Propiedades booleanas
    if [[ "$name" =~ ^(requires|mandatory|is)[A-Z] ]] && [[ "$name" =~ (Compliance|Governance|Assessment|Notification|Explainability|Review)$ ]]; then
        echo "xsd:boolean"
        return
    fi

    # Propiedades de texto
    if [[ "$name" =~ (Description|Reference|Scope|Note|Name|Version|Type|Priority|Deadline|Role|Frequency|Iri)$ ]]; then
        echo "xsd:string"
        return
    fi

    # Por defecto, las propiedades son referencias a otros recursos
    echo "@id"
}

# Iniciar el JSON con los namespaces
cat > "$CONTEXT_OUT" << 'HEADER'
{
  "@context": {
    "ai": "http://ai-act.eu/ai#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dpv": "https://w3id.org/dpv#",
    "dpv-ai": "https://w3id.org/dpv/ai#",
    "dpv-risk": "https://w3id.org/dpv/risk#",
    "dpv-tech": "https://w3id.org/dpv/tech#",
    "dpv-legal-eu-aiact": "https://w3id.org/dpv/legal/eu/aiact#",
    "dpv-legal-eu-gdpr": "https://w3id.org/dpv/legal/eu/gdpr#",
    "airo": "https://w3id.org/airo#"
HEADER

# Extraer propiedades del archivo TTL principal
# Buscar líneas que definen propiedades (ObjectProperty o DatatypeProperty)
properties=$(grep -E "^ai:[a-zA-Z]+ a owl:(Object|Datatype)Property" "$TTL_FILE" 2>/dev/null | \
    sed -E 's/^(ai:[a-zA-Z]+).*/\1/' | sort -u || true)

# También buscar propiedades usadas en el archivo
additional_props=$(grep -oE "ai:[a-zA-Z]+" "$TTL_FILE" 2>/dev/null | \
    grep -vE "^ai:(a|type)$" | sort -u || true)

# Combinar y deduplicar
all_props=$(echo -e "${properties}\n${additional_props}" | sort -u | grep -E "^ai:[a-z]" || true)

# Si existe el archivo DPV, agregar sus propiedades
if [[ -f "$DPV_FILE" ]]; then
    dpv_props=$(grep -oE "ai:[a-zA-Z]+" "$DPV_FILE" 2>/dev/null | sort -u || true)
    all_props=$(echo -e "${all_props}\n${dpv_props}" | sort -u | grep -E "^ai:[a-z]" || true)
fi

# Propiedades conocidas con sus tipos (basadas en el context.jsonld existente)
declare -A known_types=(
    # Object Properties (@id)
    ["ai:activatesCriterion"]="@id"
    ["ai:activatesRequirement"]="@id"
    ["ai:assessedSystem"]="@id"
    ["ai:assignedRiskLevel"]="@id"
    ["ai:assignsRiskLevel"]="@id"
    ["ai:considersCriterion"]="@id"
    ["ai:deploysSystem"]="@id"
    ["ai:distributesSystem"]="@id"
    ["ai:expectedRiskLevel"]="@id"
    ["ai:generatesEvidence"]="@id"
    ["ai:hasActivatedCriterion"]="@id"
    ["ai:hasAlgorithmType"]="@id"
    ["ai:hasCapabilityMetric"]="@id"
    ["ai:hasDeployer"]="@id"
    ["ai:hasDeploymentContext"]="@id"
    ["ai:hasDeveloper"]="@id"
    ["ai:hasEvidenceItem"]="@id"
    ["ai:hasException"]="@id"
    ["ai:hasGap"]="@id"
    ["ai:hasManuallyIdentifiedCriterion"]="@id"
    ["ai:hasModelScale"]="@id"
    ["ai:hasNormativeCriterion"]="@id"
    ["ai:hasOversightBody"]="@id"
    ["ai:hasProhibitedPractice"]="@id"
    ["ai:hasProvider"]="@id"
    ["ai:hasPurpose"]="@id"
    ["ai:hasRequirement"]="@id"
    ["ai:hasRiskLevel"]="@id"
    ["ai:hasSubRequirement"]="@id"
    ["ai:hasSubject"]="@id"
    ["ai:hasTechnicalCriterion"]="@id"
    ["ai:hasTechnicalRequirement"]="@id"
    ["ai:hasTrainingDataOrigin"]="@id"
    ["ai:hasUrn"]="@id"
    ["ai:hasUser"]="@id"
    ["ai:importsSystem"]="@id"
    ["ai:isAssessmentOfSystem"]="@id"
    ["ai:isAssignedRiskLevelOf"]="@id"
    ["ai:isComplianceRequiredBy"]="@id"
    ["ai:isCriterionConsideredBy"]="@id"
    ["ai:isDeploymentContextOf"]="@id"
    ["ai:isEvidenceForRequirement"]="@id"
    ["ai:isEvidenceGeneratedBy"]="@id"
    ["ai:isExpectedRiskLevelFor"]="@id"
    ["ai:isMonitoredBy"]="@id"
    ["ai:isNormativeCriterionOf"]="@id"
    ["ai:isPurposeOfSystem"]="@id"
    ["ai:isRequirementActivatedBy"]="@id"
    ["ai:isRequirementOfSystem"]="@id"
    ["ai:isRiskLevelAssignedBy"]="@id"
    ["ai:isRiskLevelOfSystem"]="@id"
    ["ai:isSystemDeployedBy"]="@id"
    ["ai:isSystemDistributedBy"]="@id"
    ["ai:isSystemImportedBy"]="@id"
    ["ai:isSystemProvidedBy"]="@id"
    ["ai:isSystemUsedBy"]="@id"
    ["ai:isTechnicalCriterionOfSystem"]="@id"
    ["ai:isTechnicalRequirementOf"]="@id"
    ["ai:isTrainingDataOriginOf"]="@id"
    ["ai:isTriggeredBy"]="@id"
    ["ai:justifiedByCriterion"]="@id"
    ["ai:mapsToDPVMeasure"]="@id"
    ["ai:monitorsSystem"]="@id"
    ["ai:providesEvidenceFor"]="@id"
    ["ai:providesSystem"]="@id"
    ["ai:requiresCompliance"]="@id"
    ["ai:requiresEvidence"]="@id"
    ["ai:triggersComplianceRequirement"]="@id"
    ["ai:triggersCriterion"]="@id"
    ["ai:usesSystem"]="@id"
    # Datatype Properties (xsd:string)
    ["ai:articleReference"]="xsd:string"
    ["ai:evidenceDescription"]="xsd:string"
    ["ai:evidenceFrequency"]="xsd:string"
    ["ai:evidencePriority"]="xsd:string"
    ["ai:hasDocumentationType"]="xsd:string"
    ["ai:hasHttpIri"]="xsd:string"
    ["ai:hasName"]="xsd:string"
    ["ai:hasVersion"]="xsd:string"
    ["ai:justificationNote"]="xsd:string"
    ["ai:planDeadline"]="xsd:string"
    ["ai:planPriority"]="xsd:string"
    ["ai:prohibitionScope"]="xsd:string"
    ["ai:responsibleRole"]="xsd:string"
    # Boolean Properties (xsd:boolean)
    ["ai:mandatoryCompliance"]="xsd:boolean"
    ["ai:requiresAffectedPersonNotification"]="xsd:boolean"
    ["ai:requiresDataGovernance"]="xsd:boolean"
    ["ai:requiresExplainability"]="xsd:boolean"
    ["ai:requiresFundamentalRightsAssessment"]="xsd:boolean"
    ["ai:requiresProhibitionReview"]="xsd:boolean"
)

# Generar las entradas de propiedades
first=true
for prop in $(echo "$all_props" | grep -E "^ai:[a-z]" | sort -u); do
    # Ignorar clases y términos que no son propiedades
    if [[ "$prop" =~ ^ai:[A-Z] ]]; then
        continue
    fi

    # Determinar el tipo
    if [[ -v "known_types[$prop]" ]]; then
        type="${known_types[$prop]}"
    else
        type=$(get_property_type "$prop")
    fi

    # Agregar coma y salto de línea
    if $first; then
        first=false
        # Primera propiedad: agregar coma después del último namespace
        printf ',\n' >> "$CONTEXT_OUT"
    else
        printf ',\n' >> "$CONTEXT_OUT"
    fi

    # Escribir la entrada
    printf '    "%s": {\n      "@type": "%s"\n    }' "$prop" "$type" >> "$CONTEXT_OUT"
done

# Cerrar el JSON
cat >> "$CONTEXT_OUT" << 'EOF'

  }
}
EOF

# Copiar a la ubicación raíz de ontologías
cp "$CONTEXT_OUT" "$CONTEXT_ROOT"

echo "✅ context.jsonld generado en: ${CONTEXT_OUT}"
echo "✅ Sincronizado con: ${CONTEXT_ROOT}"
