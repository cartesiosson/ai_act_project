# 🔍 Catálogo de Queries SPARQL Forenses

Este documento describe las queries SPARQL disponibles para el análisis forense de cumplimiento del EU AI Act.

## Descripción General

El fichero `forensic-queries.sparql` contiene un catálogo de **15 queries SPARQL** diseñadas para:

- Reconstruir la clasificación correcta de sistemas de IA
- Identificar requisitos obligatorios de cumplimiento
- Detectar brechas de cumplimiento (gaps)
- Evaluar severidad de incidentes
- Determinar el ámbito de aplicación del EU AI Act (Art. 2)

---

## Índice de Queries

| # | Query | Propósito |
|---|-------|-----------|
| 1 | [PROPER_CLASSIFICATION](#query-1-proper_classification) | Reconstruir clasificación correcta |
| 2 | [MANDATORY_REQUIREMENTS](#query-2-mandatory_requirements) | Identificar requisitos obligatorios |
| 3 | [COMPLIANCE_GAPS](#query-3-compliance_gaps) | Encontrar requisitos no implementados |
| 4 | [MISSING_SECURITY_REQUIREMENTS](#query-4-missing_security_requirements) | Gaps de seguridad específicos |
| 5 | [ARTICLE_6_3_HIDDEN_REQUIREMENTS](#query-5-article_6_3_hidden_requirements) | Requisitos ocultos Art. 6(3) |
| 6 | [DATA_HANDLING_VIOLATIONS](#query-6-data_handling_violations) | Violaciones de gobernanza de datos |
| 7 | [HUMAN_OVERSIGHT_VIOLATIONS](#query-7-human_oversight_violations) | Falta de supervisión humana |
| 8 | [HISTORICAL_COMPLIANCE_STATE](#query-8-historical_compliance_state) | Estado de cumplimiento histórico |
| 9 | [SIMILAR_VULNERABILITY_PATTERNS](#query-9-similar_vulnerability_patterns) | Patrones de vulnerabilidad similares |
| 10 | [ENFORCEMENT_SEVERITY](#query-10-enforcement_severity) | Evaluación de severidad de sanción |
| 11 | [DETERMINE_SCOPE](#query-11-determine_scope) | Determinar ámbito Art. 2 |
| 12 | [IS_IN_SCOPE_ASK](#query-12-is_in_scope_ask) | Verificación rápida de ámbito |
| 13 | [LIST_SCOPE_EXCLUSIONS](#query-13-list_scope_exclusions) | Listar exclusiones de ámbito |
| 14 | [LIST_OVERRIDE_CONTEXTS](#query-14-list_override_contexts) | Contextos que anulan exclusiones |
| 15 | [POTENTIALLY_EXCLUDED_PURPOSES](#query-15-potentially_excluded_purposes) | Propósitos potencialmente excluidos |

---

## Descripción Detallada

### Query 1: PROPER_CLASSIFICATION

**Propósito**: Reconstruir la clasificación correcta de un sistema de IA basándose en su propósito y contexto de despliegue.

**Uso forense**: Identificar si un sistema fue incorrectamente clasificado en el momento del incidente.

**Variables de salida**:
- `?system` - URI del sistema
- `?purpose` - Propósito declarado
- `?context` - Contexto de despliegue
- `?activatedCriterion` - Criterio que debería activarse
- `?criterionLabel` - Etiqueta del criterio

---

### Query 2: MANDATORY_REQUIREMENTS

**Propósito**: Identificar TODOS los requisitos de cumplimiento obligatorios para un sistema dado su clasificación.

**Uso forense**: Determinar qué controles DEBERÍAN haberse implementado.

**Variables de salida**:
- `?system` - URI del sistema
- `?criterion` - Criterio activado
- `?requirement` - Requisito obligatorio
- `?requirementLabel` - Nombre del requisito
- `?requirementType` - Tipo de requisito

---

### Query 3: COMPLIANCE_GAPS

**Propósito**: Encontrar requisitos obligatorios que NO están implementados en el sistema.

**Uso forense**: Identificar violaciones específicas y su impacto potencial.

**Lógica**: Usa `MINUS` para encontrar requisitos que deberían existir pero no están declarados como implementados.

**Variables de salida**:
- `?system` - URI del sistema
- `?missingRequirement` - Requisito faltante
- `?requirementLabel` - Nombre del requisito
- `?requirementType` - Tipo de requisito

---

### Query 4: MISSING_SECURITY_REQUIREMENTS

**Propósito**: Identificar específicamente los requisitos de SEGURIDAD que no fueron implementados.

**Uso forense**: Focalizar en controles que podrían haber prevenido el incidente.

**Filtro**: Solo requisitos de tipo `ai:SecurityRequirement`.

---

### Query 5: ARTICLE_6_3_HIDDEN_REQUIREMENTS

**Propósito**: Descubrir requisitos "ocultos" que solo se activan por criterios del Artículo 6(3).

**Uso forense**: Identificar requisitos de "riesgo residual" que el Anexo III no activa automáticamente.

**Contexto legal**: El Art. 6(3) permite clasificación manual de sistemas como alto riesgo cuando presentan riesgos significativos no cubiertos por el Anexo III.

---

### Query 6: DATA_HANDLING_VIOLATIONS

**Propósito**: Detectar sistemas que procesan datos personales/sensibles sin los requisitos de gobernanza de datos correspondientes.

**Tipos de datos monitorizados**:
- `ai:PersonalData`
- `ai:SensitivePersonalData`
- `ai:BiometricData`

---

### Query 7: HUMAN_OVERSIGHT_VIOLATIONS

**Propósito**: Identificar sistemas de alto riesgo que deberían tener supervisión humana pero no la tienen implementada.

**Contexto legal**: Art. 14 del EU AI Act requiere supervisión humana para sistemas de alto riesgo.

---

### Query 8: HISTORICAL_COMPLIANCE_STATE

**Propósito**: Reconstruir el estado de cumplimiento que debería haber tenido un sistema en la fecha del incidente.

**Uso forense**: Análisis temporal para determinar negligencia.

**Requiere**: Datos temporales (`ai:effectiveDate`, `ai:modificationDate`).

**Período de gracia**: Asume 6 meses desde el despliegue para cumplimiento.

---

### Query 9: SIMILAR_VULNERABILITY_PATTERNS

**Propósito**: Identificar otros sistemas con el mismo gap de cumplimiento que causó el incidente.

**Uso forense**: Remediación proactiva en sistemas similares.

**Lógica**: Busca sistemas con mismo propósito/contexto que tienen los mismos requisitos faltantes.

---

### Query 10: ENFORCEMENT_SEVERITY

**Propósito**: Determinar la severidad del incumplimiento y estimar la categoría de sanción.

**Categorías de sanción**:
| Categoría | Condición | Rango estimado |
|-----------|-----------|----------------|
| **A** | ≥10 violaciones + HighRisk | €10M+ |
| **B** | ≥5 violaciones | €5M-10M |
| **C** | <5 violaciones | <€5M |

---

### Query 11: DETERMINE_SCOPE

**Propósito**: Determinar si un sistema de IA cae dentro del ámbito de aplicación del EU AI Act según el Artículo 2.

**Lógica de ámbito**:
1. **EN ÁMBITO** si el propósito no tiene exclusión
2. **EN ÁMBITO** si la exclusión es anulada por el contexto
3. **FUERA DE ÁMBITO** solo si existe exclusión Y no hay override

**Variables de salida**:
- `?inScope` - Booleano indicando si está regulado
- `?scopeReason` - Explicación legible del resultado

---

### Query 12: IS_IN_SCOPE_ASK

**Propósito**: Verificación rápida (ASK) de si un sistema está dentro del ámbito.

**Tipo**: Query ASK (retorna true/false).

**Uso**: Primera comprobación rápida antes de análisis detallado.

---

### Query 13: LIST_SCOPE_EXCLUSIONS

**Propósito**: Listar todas las exclusiones de ámbito definidas en la ontología.

**Información retornada**:
- URI de la exclusión
- Etiqueta
- Referencia al artículo
- Comentario explicativo

---

### Query 14: LIST_OVERRIDE_CONTEXTS

**Propósito**: Listar todos los contextos de despliegue que pueden anular exclusiones de ámbito.

**Contextos override definidos**:
- `ai:CausesRealWorldHarmContext` - Daño real a personas
- `ai:VictimImpactContext` - Víctimas identificables
- `ai:AffectsFundamentalRightsContext` - Afecta derechos fundamentales
- `ai:LegalConsequencesContext` - Consecuencias legales
- `ai:MinorsAffectedContext` - Menores afectados

---

### Query 15: POTENTIALLY_EXCLUDED_PURPOSES

**Propósito**: Listar todos los propósitos que pueden estar excluidos del ámbito del EU AI Act.

**Ejemplos**:
- `ai:Entertainment` → `EntertainmentWithoutRightsImpact`
- `ai:PersonalAssistant` → `PersonalNonProfessionalUse`
- `ai:ScientificResearch` → `PureScientificResearch`

---

## Flujos de Trabajo Recomendados

### Flujo 1: Análisis Forense Completo

```
1. DETERMINE_SCOPE → ¿Está el sistema regulado?
   ↓ (si IN SCOPE)
2. PROPER_CLASSIFICATION → Clasificación correcta
   ↓
3. MANDATORY_REQUIREMENTS → Lista completa de requisitos
   ↓
4. COMPLIANCE_GAPS → Identificar violaciones
   ↓
5. MISSING_SECURITY_REQUIREMENTS → Foco en seguridad
   ↓
6. ENFORCEMENT_SEVERITY → Estimar sanción
```

### Flujo 2: Detección Proactiva de Vulnerabilidades

```
1. SIMILAR_VULNERABILITY_PATTERNS → Sistemas en riesgo
   ↓
2. MISSING_SECURITY_REQUIREMENTS → Priorizar por riesgo
   ↓
3. HUMAN_OVERSIGHT_VIOLATIONS → Remediación manual
```

### Flujo 3: Reconstrucción Histórica

```
1. HISTORICAL_COMPLIANCE_STATE → Estado en fecha del incidente
   ↓
2. ARTICLE_6_3_HIDDEN_REQUIREMENTS → Requisitos pasados por alto
   ↓
3. ENFORCEMENT_SEVERITY → Determinar negligencia intencional
```

---

## Notas de Implementación

### Estado Actual

Estas queries están documentadas como **referencia conceptual**. El Agente Forense actualmente construye queries SPARQL dinámicamente en código Python ([sparql_queries.py](../../forensic_agent/app/services/sparql_queries.py)) en lugar de cargar este fichero directamente.

### Prefijos Requeridos

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
```

### Compatibilidad

- **Ontología**: v0.41.0+
- **Endpoint**: Apache Jena Fuseki (SPARQL 1.1)
- **Servidor MCP**: `mcp_sparql:8080`

---

## Referencias

- [EU AI Act Regulation (EU) 2024/1689](http://data.europa.eu/eli/reg/2024/1689)
- [Ontología SERAMIS v0.41.0](../versions/0.41.0/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)

---

**Versión**: 1.0
**Última Actualización**: Enero 2026
**Compatibilidad**: EU AI Act Ontology v0.41.0
