# Cambios Importantes en la Ontología: v0.40.0 → v0.41.0

## Resumen Ejecutivo

La ontología ha evolucionado de la versión **v0.40.0** (31 diciembre 2025) a la versión **v0.41.0** (4 enero 2026), introduciendo una **taxonomía completa de incidentes graves** según el Artículo 3(49) del EU AI Act.

---

## 1. CAMBIO PRINCIPAL: Taxonomía de Incidentes Graves (v0.41.0)

### 1.1. Nueva Jerarquía de Clases

Se añadió una jerarquía completa para clasificar incidentes graves según el **Artículo 3(49)** del EU AI Act:

```turtle
ai:SeriousIncident (clase base)
  ├── ai:DeathOrHealthHarm             [Art. 3(49)(a)]
  ├── ai:CriticalInfrastructureDisruption [Art. 3(49)(b)]
  ├── ai:FundamentalRightsInfringement   [Art. 3(49)(c)]
  └── ai:PropertyOrEnvironmentHarm       [Art. 3(49)(d)]
```

### 1.2. Propiedades Nuevas

| Propiedad | Dominio | Rango | Propósito |
|-----------|---------|-------|-----------|
| `ai:hasSeriousIncidentType` | `IntelligentSystem` | `SeriousIncident` | Vincula sistema con tipo de incidente |
| `ai:indicatorKeywords` | `SeriousIncident` | `xsd:string` | Keywords para extracción por LLM |
| `ai:mapsToAIAAICType` | `SeriousIncident` | `xsd:string` | Mapeo a taxonomía AIAAIC (ground truth) |
| `ai:triggersArticle73` | `SeriousIncident` | `xsd:boolean` | Indica si activa reporte obligatorio |

### 1.3. Detalles de Cada Tipo de Incidente Grave

#### (a) Death or Health Harm - `ai:DeathOrHealthHarm`
- **Artículo**: 3(49)(a)
- **Definición**: Muerte de persona o daño grave a la salud
- **Keywords**: death, died, killed, fatal, suicide, injury, hospitalized, serious harm, trauma, casualties
- **Mapea a AIAAIC**: `safety_failure`
- **Ejemplos**:
  - Fatalidad de vehículo autónomo
  - Sobredosis por medicación recomendada por IA
  - Suicidio de adolescente influenciado por algoritmo de recomendación

#### (b) Critical Infrastructure Disruption - `ai:CriticalInfrastructureDisruption`
- **Artículo**: 3(49)(b)
- **Definición**: Interrupción grave e irreversible de infraestructura crítica
- **Keywords**: infrastructure failure, blackout, power grid, transport disruption, water supply, emergency services
- **Mapea a AIAAIC**: `safety_failure` (cuando afecta infraestructura)
- **Sectores**: energía, transporte, agua, salud, comunicaciones

#### (c) Fundamental Rights Infringement - `ai:FundamentalRightsInfringement`
- **Artículo**: 3(49)(c)
- **Definición**: Violación de derechos fundamentales de la UE
- **Keywords**: discrimination, wrongful arrest, privacy breach, GDPR violation, bias, profiling, surveillance
- **Mapea a AIAAIC**: `bias`, `privacy_violation`, `discrimination`
- **Integración**: `skos:closeMatch` con `dpv-risk:RightsImpact`

#### (d) Property or Environment Harm - `ai:PropertyOrEnvironmentHarm`
- **Artículo**: 3(49)(d)
- **Definición**: Daño grave a propiedad o medio ambiente
- **Keywords**: property damage, environmental damage, financial loss, infrastructure damage
- **Mapea a AIAAIC**: (no tiene equivalente directo)

### 1.4. Beneficios de esta Adición

1. **Clasificación ontológica de incidentes**: Elimina necesidad de lista hardcoded de `incident_type`
2. **Alineación con EU AI Act**: Taxonomía oficial del Artículo 3(49)
3. **Soporte para benchmarking**: Mapeo explícito a taxonomía AIAAIC para ground truth
4. **Extracción guiada por LLM**: Keywords semánticos para clasificación automática
5. **Reporte obligatorio**: Identifica incidentes que activan Artículo 73
6. **Integración con DPV**: Enlaces a Data Privacy Vocabulary Risk concepts

---

## 2. CONTEXTO PREVIO: Evolución v0.38.0 → v0.40.0

### 2.1. v0.40.0 (31 dic 2025) - Migración a Determinación Semántica de Scope

**Cambio arquitectónico crítico**: Migración de clasificación basada en keywords a clasificación semántica.

#### Antes (keywords hardcoded):
```python
OUT_OF_SCOPE_KEYWORDS = [
    "game", "gaming", "video game", "entertainment", ...
]  # ~150 keywords
```

#### Después (validación ontológica):
```python
# LLM extrae conceptos semánticos
scope_override_contexts = ["CausesRealWorldHarmContext", "VictimImpactContext"]

# Python valida contra ontología
if ai:CausesRealWorldHarmContext in ontology:
    system_in_scope = True
```

**Beneficios**:
- ✓ Eliminados ~150 keywords hardcoded del código Python
- ✓ Aproximación "ontology-first"
- ✓ Escalable y auditable
- ✓ Benchmark: 100% success rate mantenido (5/5 casos)

### 2.2. v0.39.0 (31 dic 2025) - Scope Override Detection

**Añadidos**:
- `ai:MinorsAffectedContext` - override para sistemas que afectan menores
- `ai:ContentRecommendation` - propósito para algoritmos de recomendación
- `ai:ContentRecommendationCriterion` - criterio para redes sociales, feeds de noticias

**Propiedades nuevas**:
- `ai:hasScopeOverride` - marca contextos que anulan exclusiones
- `ai:isInEUAIActScope` - indica si sistema está dentro del scope
- `ai:requiresFRIA` - indica si requiere FRIA según Artículo 27

**Casos validados**:
- Chase Nasca (TikTok For You algorithm)
- Deepfakes en entretenimiento
- Casos de psicosis inducidos por recomendaciones

### 2.3. v0.38.0 (30 dic 2025) - Article 2 Scope Exclusions

**Jerarquía de exclusiones**:
```turtle
ai:ScopeExclusion
  ├── ai:PersonalNonProfessionalUse    [Art. 2.10]
  ├── ai:PureScientificResearch        [Art. 2.6]
  ├── ai:MilitaryDefenseUse            [Art. 2.3]
  ├── ai:EntertainmentWithoutRightsImpact [Recital 12]
  └── ai:ThirdCountryExclusion         [Art. 2.7]
```

**Propiedades**:
- `ai:mayBeExcludedBy` - vincula Purpose → ScopeExclusion
- `ai:overridesExclusion` - contexto que anula la exclusión

**Contextos override añadidos**:
- `ai:AffectsFundamentalRightsContext`
- `ai:CausesRealWorldHarmContext`
- `ai:LegalConsequencesContext`

---

## 3. Cambios en el Forensic Agent (Código)

### 3.1. Extractor de Incidentes (`incident_extractor.py`)

**Cambios en el prompt**:

```python
# ANTES (v0.40.0):
"incident_type": "discrimination|bias|safety_failure|..."  # Lista fija

# DESPUÉS (v0.41.0):
"serious_incident_type": [
    "DeathOrHealthHarm",
    "CriticalInfrastructureDisruption",
    "FundamentalRightsInfringement",
    "PropertyOrEnvironmentHarm"
]  # Taxonomía EU AI Act
```

**Mejoras recientes** (enero 2026):
- Definiciones de `incident_type` optimizadas para reducir confusión accuracy_failure ↔ privacy_violation
- Regla explícita: "Focus on WHAT WENT WRONG, not data type"
- Mejora medida: 0/5 → 3/5 casos correctos (60% accuracy_failure recall)

### 3.2. Ground Truth Mapper (`ground_truth_mapper.py`)

**Añadido**:
```python
def map_to_serious_incident_types(
    issues_str, sector_str, individual_harms_str, societal_harms_str
) -> Dict:
    """
    Maps AIAAIC data to EU AI Act Article 3(49) serious incident types.
    """
    # Mapeo de AIAAIC harms → EU AI Act serious incidents
    HARM_TO_SERIOUS_INCIDENT = {
        "Loss of life": ["DeathOrHealthHarm"],
        "Discrimination": ["FundamentalRightsInfringement"],
        "Financial harm": ["PropertyOrEnvironmentHarm"],
        ...
    }
```

**Función de evaluación**:
```python
def evaluate_serious_incident_type(predicted: List[str], ground_truth: Dict) -> Dict:
    """
    Multi-label evaluation: strict_match, primary_match, precision, recall, F1
    """
```

---

## 4. Impacto en el TFM

### 4.1. Secciones Afectadas

| Sección TFM | Cambio | Acción Requerida |
|-------------|--------|------------------|
| **Metodología - Ontología** | v0.40.0 → v0.41.0 | Actualizar versión y describir taxonomía Art. 3(49) |
| **Implementación - Extractor** | Nuevas definiciones incident_type | Documentar mejoras en clasificación |
| **Evaluación - Ground Truth** | Mapeo a serious incidents | Añadir métricas de evaluación multi-label |
| **Resultados - Benchmark** | Mejora accuracy_failure | Actualizar matrices de confusión |

### 4.2. Figuras a Actualizar

1. **Diagrama de Ontología**: Añadir jerarquía `ai:SeriousIncident`
2. **Flujo del Sistema**: Incluir paso de clasificación de serious incidents
3. **Matriz de Confusión**: Nueva versión con definiciones mejoradas
4. **Tabla de Métricas**: Comparación v0.41 antes/después de fix

---

## 5. Estadísticas de Evolución

### Líneas de Tiempo

| Versión | Fecha | Clases Nuevas | Propiedades Nuevas | Foco Principal |
|---------|-------|---------------|-------------------|----------------|
| v0.38.0 | 30 dic 2025 | 5 (ScopeExclusion) | 2 | Article 2 Exclusions |
| v0.39.0 | 31 dic 2025 | 3 (Contexts) | 5 | Scope Override Detection |
| v0.40.0 | 31 dic 2025 | 0 | 0 | Migración Semántica (código) |
| **v0.41.0** | **4 ene 2026** | **5 (SeriousIncident)** | **4** | **Art. 3(49) Taxonomy** |

### Tamaño de la Ontología

- **Conceptos totales**: ~250+ clases
- **Propiedades**: ~80+
- **Instancias Purpose**: 20+
- **Criteria**: 30+
- **Requirements**: 50+

---

## 6. Referencias Legales

### Enlaces EUR-Lex (ELI)

La v0.41.0 mantiene los enlaces ELI introducidos en v0.37.5:

```turtle
eli:cites <http://data.europa.eu/eli/reg/2024/1689/art_3/par_49/oj>
eli:cites <http://data.europa.eu/eli/reg/2024/1689/art_3/par_49/pnt_a/oj>
eli:cites <http://data.europa.eu/eli/reg/2024/1689/art_73/oj>
```

### Integración con Vocabularios

- **DPV (Data Privacy Vocabulary)**: `skos:closeMatch` con `dpv-risk:PhysicalHarm`, `dpv-risk:RightsImpact`
- **AIRO**: Mapeo a `airo:AISystem`, `airo:DataSource`
- **AIAAIC**: Propiedad `ai:mapsToAIAAICType` para ground truth

---

## 7. Trabajo Futuro (Fuera del scope v0.41.0)

Posibles extensiones para versiones futuras:

1. **Ontología de Controles**: ISO 42001 controls detallados
2. **NIST AI RMF**: Mapeo completo a Risk Management Framework
3. **Temporal Reasoning**: Modelado de líneas de tiempo de incidentes
4. **Causalidad**: Relaciones causales sistema → incidente
5. **Severidad Cuantitativa**: Escalas numéricas de impacto

---

## 8. Conclusiones

### Cambios Críticos para el TFM:

1. ✅ **Taxonomía oficial de incidentes graves** (Art. 3(49))
2. ✅ **Mapeo AIAAIC → EU AI Act** para ground truth
3. ✅ **Eliminación de keywords hardcoded** (aproximación semántica)
4. ✅ **Mejoras en clasificación** (accuracy_failure: 0% → 60%)

### Alineación con Objetivos del TFM:

- ✓ **Clasificación semántica**: Ontología como fuente de verdad
- ✓ **Benchmarking riguroso**: Mapeo explícito AIAAIC-EU AI Act
- ✓ **Trazabilidad legal**: Enlaces ELI a legislación consolidada
- ✓ **Extensibilidad**: Arquitectura preparada para futuras extensiones

### Impacto en Resultados:

- **Antes (v0.40.0)**: accuracy_failure recall = 4.7% (1/21)
- **Después (v0.41.0 + fix)**: accuracy_failure recall = 60%+ (estimado en nuevo benchmark)
- **Serious Incidents**: Nueva métrica multi-label para evaluar clasificación Art. 3(49)

---

**Documento generado**: 8 enero 2026
**Versiones comparadas**: v0.40.0 (31 dic 2025) → v0.41.0 (4 ene 2026)
**Autor**: Sistema Forensic Agent + Análisis Claude
**Propósito**: Actualización documentación TFM
