# Mappings Multi-Framework del EU AI Act

> Mappings bidireccionales entre los requisitos de cumplimiento del EU AI Act y frameworks internacionales de gobernanza de IA

## Descripción General

Este directorio contiene mappings formales RDF/OWL entre:
- **EU AI Act**: Requisitos de cumplimiento (Artículos 9-15, 27, 43, 72-73, Anexo III)
- **ISO/IEC 42001:2023**: Controles del Sistema de Gestión de IA (Secciones 5-10)
- **NIST AI RMF 1.0**: Funciones y categorías del Risk Management Framework
- **W3C DPV 2.2**: Data Privacy Vocabulary para medidas técnicas y organizativas
- **ELI**: European Legislation Identifier para enlaces a EUR-Lex

**Propósito**: Habilitar análisis de cumplimiento multi-framework, investigación forense de incidentes, integración con auditorías corporativas y análisis de incidentes transjurisdiccionales.

---

## Ficheros

| Fichero | Descripción | Estado |
|---------|-------------|--------|
| `iso-42001-mappings.ttl` | 15 mappings ISO esenciales (Fase 2) | ✅ Activo |
| `nist-ai-rmf-mappings.ttl` | 16 mappings NIST AI RMF (Fase 3) | ✅ Activo |
| `dpv-integration.ttl` | Integración W3C DPV 2.2 + URIs ELI (v0.2.0) | ✅ Activo |

---

## Integración ELI

Todos los requisitos de esta ontología incluyen URIs del **European Legislation Identifier (ELI)** para enlaces directos a EUR-Lex. Esto permite:

- **URIs desreferenciables**: Acceso directo al texto legislativo oficial
- **Identificadores persistentes**: Referencias estables a través de consolidaciones legislativas
- **Referencias legibles por máquina**: Conformidad con la Web Semántica

**URI Base ELI**: `http://data.europa.eu/eli/reg/2024/1689`

**Ejemplo**:
```turtle
ai:HumanOversightRequirement
    ai:articleReference "Article 14" ;
    eli:cites <http://data.europa.eu/eli/reg/2024/1689/art_14/oj> .
```

**Estándares de referencia**:
- Council Conclusions 2012/C 325/02
- Decision (EU) 2017/1191

---

## Integración W3C DPV 2.2

La ontología integra el **[W3C Data Privacy Vocabulary (DPV) 2.2](https://w3c.github.io/dpv/)** para la generación de planes de evidencia de cumplimiento.

### Extensiones DPV Utilizadas

| Extensión DPV | Propósito | Uso en SERAMIS |
|---------------|-----------|----------------|
| **dpv:core** | Medidas técnicas y organizativas | Mapeo de requisitos a medidas |
| **dpv:ai** | Sistemas de IA, capacidades, riesgos | Clasificación de sistemas |
| **dpv:risk** | Gestión de riesgos | Evaluación de gaps |
| **dpv:legal** | Bases legales y obligaciones | Cumplimiento normativo |

### Propiedades de Integración DPV

```turtle
ai:mapsToDPVMeasure         # Requisito → Medida DPV
ai:requiresEvidence         # Requisito → Evidencia requerida
ai:dpvRiskLevel            # Sistema → Nivel de riesgo DPV
```

### Evidence Planner

El módulo Evidence Planner utiliza DPV para generar planes de evidencia con:
- **14 requisitos** EU AI Act mapeados a medidas DPV
- **~40 items de evidencia** específicos por requisito
- **Categorización** por tipo de medida (técnica/organizativa)

---

## Requisitos Específicos de la UE (Sin Mapping)

Los siguientes requisitos del EU AI Act **no se mapean intencionalmente** a ISO 42001 o NIST AI RMF por ser prohibiciones regulatorias específicas de la UE sin equivalentes directos en estándares internacionales:

### Artículo 5: Prácticas Prohibidas (Riesgo Inaceptable)

**Estado:** ⚠️ Sin mapping a ISO/NIST (prohibiciones absolutas específicas de la UE)

**Razón:** Las prohibiciones del Artículo 5 son **prohibiciones legales absolutas** específicas del derecho de la UE sin equivalente en ISO 42001 (estándar de sistema de gestión) o NIST AI RMF (framework voluntario de riesgos). Son líneas rojas regulatorias, no riesgos gestionables.

**Prácticas Prohibidas:**
1. **SubliminalManipulationCriterion** (Art. 5.1.a) - Manipulación subliminal
2. **VulnerabilityExploitationCriterion** (Art. 5.1.b) - Explotación de vulnerabilidades
3. **SocialScoringCriterion** (Art. 5.1.c) - Social scoring por autoridades públicas
4. **PredictivePolicingProfilingCriterion** (Art. 5.1.d) - Policía predictiva mediante profiling
5. **RealTimeBiometricIdentificationCriterion** (Art. 5.1.h) - Identificación biométrica en tiempo real en espacios públicos

**Sanción:** Los sistemas con estas prácticas NO PUEDEN desplegarse en la UE. Multas máximas: €35M o 7% de la facturación anual global.

**Excepción:** Solo la identificación biométrica en tiempo real tiene excepciones limitadas bajo el Artículo 5.2 (búsqueda de víctimas, amenaza terrorista, delitos graves) requiriendo autorización judicial previa.

---

## Mappings ISO 42001 (v1.0.0)

### Cobertura

**Total de Mappings:** 15 controles esenciales
**Distribución de Confianza:**
- HIGH: 13 mappings (87%)
- MEDIUM: 2 mappings (13%)

**Secciones ISO Cubiertas:**
- 5.1 - Liderazgo y compromiso
- 8.1 - Evaluación y tratamiento de riesgos
- 8.2 - Evaluación del rendimiento
- 8.3 - Gobernanza de datos
- 8.4 - Documentación y registros
- 8.5 - Seguridad de la información
- 8.6 - Supervisión humana
- 8.7 - Transparencia y explicabilidad
- 9.1 - Monitorización y medición
- 9.2 - Auditoría interna
- 10.1 - Gestión de incidentes

---

## Tabla de Mappings Principales

| Requisito EU AI Act | Control ISO 42001 | Sección | Confianza |
|---------------------|-------------------|---------|-----------|
| DataGovernanceRequirement | Data governance | 8.3 | HIGH |
| BiometricSecurityRequirement | Information security - Biometric | 8.5 | HIGH |
| HumanOversightRequirement | Human oversight | 8.6 | HIGH |
| TransparencyRequirement | Transparency and explainability | 8.7 | HIGH |
| AccuracyRequirement | Performance evaluation | 8.2 | HIGH |
| RiskAssessmentRequirement | Risk assessment and treatment | 8.1 | HIGH |
| DocumentationRequirement | Documentation and records | 8.4 | HIGH |
| RobustnessRequirement | Robustness testing | 8.2.2 | HIGH |
| NonDiscriminationRequirement | Bias detection and mitigation | 8.3.3 | HIGH |
| FundamentalRightsAssessmentRequirement | Leadership and commitment | 5.1 | MEDIUM |
| CybersecurityRequirement | AI system security | 8.5.1 | HIGH |
| MonitoringRequirement | Monitoring and measurement | 9.1 | HIGH |
| IncidentResponseRequirement | Incident management | 10.1 | HIGH |
| AuditTrailRequirement | Logging and traceability | 8.4.2 | HIGH |
| ConformityAssessmentRequirement | Internal audit | 9.2 | HIGH |

---

## Mappings NIST AI RMF (v1.0.0)

### Cobertura

**Total de Mappings:** 16 mappings (4 funciones NIST, 12 categorías)
**Distribución de Confianza:**
- HIGH: 16 mappings (100%)
- MEDIUM: 0 mappings (0%)

**Funciones NIST Cubiertas:**
- **GOVERN** (3 mappings)
  - GOVERN-1.1 - Requisitos legales y regulatorios
  - GOVERN-1.2 - Estructuras de responsabilidad
  - GOVERN-1.3 - Procesos de transparencia
- **MAP** (4 mappings)
  - MAP-2.1 - Contexto de uso
  - MAP-2.2 - Categorización de riesgos
  - MAP-2.3 - Calidad de datos y equidad
- **MEASURE** (4 mappings)
  - MEASURE-3.1 - Métricas de rendimiento
  - MEASURE-3.2 - Testing y validación
  - MEASURE-3.3 - Monitorización de sesgos
- **MANAGE** (5 mappings)
  - MANAGE-4.1 - Supervisión humana
  - MANAGE-4.2 - Monitorización y respuesta a incidentes
  - MANAGE-4.3 - Transparencia y responsabilidad
  - MANAGE-4.4 - Controles de seguridad

**Contextos de Aplicabilidad:**
- GLOBAL_INCIDENTS: 13 mappings (81%)
- US_INCIDENTS: 8 mappings (50%)
- COMPARATIVE_ANALYSIS: 7 mappings (44%)
- VOLUNTARY_COMPLIANCE: 5 mappings (31%)

### Tabla de Mappings NIST

| Requisito EU AI Act | Función NIST | Categoría | Aplicabilidad | Confianza |
|---------------------|--------------|-----------|---------------|-----------|
| FundamentalRightsAssessmentRequirement | GOVERN | 1.1 | US/Comparativo | HIGH |
| RiskAssessmentRequirement | GOVERN/MAP | 1.2/2.2 | Global | HIGH |
| DocumentationRequirement | GOVERN | 1.3 | Global/Voluntario | HIGH |
| HighRiskClassificationCriterion | MAP | 2.1 | Global/Comparativo | HIGH |
| DataGovernanceRequirement | MAP | 2.3 | Global/Voluntario | HIGH |
| NonDiscriminationRequirement | MAP/MEASURE | 2.3/3.3 | Global/US | HIGH |
| AccuracyRequirement | MEASURE | 3.1 | Global/Comparativo | HIGH |
| RobustnessRequirement | MEASURE | 3.1 | Global/Voluntario | HIGH |
| ConformityAssessmentRequirement | MEASURE | 3.2 | Comparativo/Voluntario | HIGH |
| HumanOversightRequirement | MANAGE | 4.1 | Global/Comparativo | HIGH |
| MonitoringRequirement | MANAGE | 4.2 | Global/US | HIGH |
| IncidentResponseRequirement | MANAGE | 4.2 | Global/US | HIGH |
| TransparencyRequirement | MANAGE | 4.3 | Global/Comparativo | HIGH |
| AuditTrailRequirement | MANAGE | 4.3 | Global/US | HIGH |
| CybersecurityRequirement | MANAGE | 4.4 | Global/US | HIGH |
| BiometricSecurityRequirement | MANAGE | 4.4 | Global/US | HIGH |

### Diferencias Clave: ISO 42001 vs NIST AI RMF

| Aspecto | ISO 42001 | NIST AI RMF |
|---------|-----------|-------------|
| **Naturaleza** | Estándar de certificación obligatorio | Framework de orientación voluntario |
| **Alcance** | Sistema de gestión de IA (corporativo) | Gestión de riesgos de IA (a nivel de sistema) |
| **Destinatario** | Organizaciones que buscan certificación | Todos los desarrolladores/desplegadores de IA |
| **Aplicación** | Auditorías de terceros, certificación | Autoevaluación, sin aplicación coercitiva |
| **Caso de Uso** | Cumplimiento corporativo UE | Mejores prácticas US/globales |
| **Valor Forense** | Detectar gaps de certificación | Línea base para adopción voluntaria |

---

## Uso

### Para Análisis Forense

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Query: Encontrar controles ISO que deberían haber prevenido un incidente
SELECT ?euRequirement ?isoControl ?isoSection
WHERE {
  # El requisito EU AI Act fue violado
  ?euRequirement a ai:ComplianceRequirement ;
                 ai:equivalentToISOControl ?isoControl ;
                 ai:isoSection ?isoSection .

  # Obtener descripción del control ISO
  ?euRequirement ai:isoControlDescription ?description .
}
```

**Ejemplo de Salida:**
```
Si BiometricSecurityRequirement fue violado:
→ Control ISO 42001 8.5 (Information security) debería haber sido implementado
→ Conclusión forense: La certificación ISO puede ser inválida
```

---

### Para Detección de Gaps

```sparql
PREFIX ai: <http://ai-act.eu/ai#>

# Query: Sistemas con certificación ISO pero sin requisitos EU AI Act
SELECT ?system ?missingRequirement ?isoControl
WHERE {
  # El sistema afirma tener certificación ISO 42001
  ?system ai:hasCertification ai:ISO42001Certified .

  # Pero le faltan requisitos EU AI Act
  ?system ai:hasPurpose ?purpose .
  ?purpose ai:activatesCriterion ?criterion .
  ?criterion ai:activatesRequirement ?missingRequirement .

  # El requisito NO fue implementado
  MINUS {
    ?system ai:hasComplianceRequirement ?missingRequirement .
  }

  # Mapear al control ISO
  ?missingRequirement ai:equivalentToISOControl ?isoControl .
}
```

**Ejemplo de Salida:**
```
Sistema: urn:uuid:abc-123
Faltante: ai:BiometricSecurityRequirement
Control ISO: iso:Control_8_5
→ Sistema certificado ISO 42001 pero falló en implementar sección 8.5
→ Gap de certificación detectado
```

---

### Para Informes Multi-Framework

Los mappings permiten informes forenses mostrando cumplimiento tanto UE como ISO:

```
INFORME DE AUDITORÍA DE CUMPLIMIENTO FORENSE

Sistema: FacialRecognitionAirport
Incidente: Brecha de datos (50K registros)

VIOLACIONES EU AI ACT:
❌ BiometricSecurityRequirement (Artículo 15 + Anexo III)
❌ DataGovernanceRequirement (Artículo 10)

FALLOS ISO 42001:
❌ Control 8.5 - Seguridad de la información (debería haber prevenido la brecha)
❌ Control 8.3 - Gobernanza de datos (protección de datos inadecuada)

ANÁLISIS DE CAUSA RAÍZ:
El sistema fue certificado ISO 42001 en 2023 pero falló en implementar
correctamente las secciones 8.3 y 8.5. Esto resultó en:
1. Protección inadecuada de plantillas biométricas
2. Controles de acceso débiles
3. Requisitos de cifrado faltantes

La auditoría ISO no detectó estos gaps, sugiriendo:
- Alcance de auditoría incompleto
- Experiencia insuficiente del auditor en sistemas biométricos
- Certificación obtenida antes de implementación adecuada

RECOMENDACIÓN DE APLICACIÓN:
1. Revocar o suspender certificación ISO 42001
2. Multa EU AI Act: €8-12M (violaciones Artículo 15 + Anexo III)
3. Re-auditoría obligatoria por auditor cualificado en seguridad biométrica
4. Desactivación del sistema hasta verificar cumplimiento
```

---

### Para Análisis Comparativo NIST AI RMF

```sparql
PREFIX ai: <http://ai-act.eu/ai#>
PREFIX nist: <http://nist.gov/ai-rmf#>

# Query: Encontrar funciones NIST que se alinean con requisitos EU AI Act violados
SELECT ?euRequirement ?nistFunction ?nistCategory ?applicability
WHERE {
  # El requisito EU AI Act fue violado
  ?euRequirement a ai:ComplianceRequirement ;
                 ai:equivalentToNISTFunction ?nistFunction ;
                 ai:nistCategory ?nistCategory ;
                 ai:nistApplicabilityContext ?applicability .

  # Filtrar para incidentes US/Globales
  FILTER(CONTAINS(?applicability, "US_INCIDENTS") || CONTAINS(?applicability, "GLOBAL_INCIDENTS"))
}
```

**Ejemplo de Salida:**
```
Si BiometricSecurityRequirement fue violado en incidente US:
→ Función NIST AI RMF: MANAGE-4.4 (Security controls)
→ Aplicabilidad: GLOBAL_INCIDENTS, US_INCIDENTS
→ Conclusión forense: Sistema falló en orientación voluntaria NIST Y requisitos obligatorios UE
→ Recomendación: Sistema debería adoptar controles de seguridad NIST incluso si no se despliega en UE
```

---

### Para Análisis de Incidentes Históricos (Pre-EU AI Act)

Los mappings NIST permiten análisis retrospectivo de incidentes que ocurrieron antes de la aplicación del EU AI Act:

```
ANÁLISIS FORENSE: Incidente de Reconocimiento Facial 2023 (Pre-EU AI Act)

Fecha del Incidente: 2023-08-15 (Antes de aplicación EU AI Act)
Sistema: Airport Security Facial Recognition
Jurisdicción: Despliegues tanto en US como UE

ANÁLISIS RETROSPECTIVO EU AI ACT:
❌ BiometricSecurityRequirement (Artículo 15 + Anexo III) - NO implementado
❌ DataGovernanceRequirement (Artículo 10) - Inadecuado
❌ HumanOversightRequirement (Artículo 14) - Faltante

ANÁLISIS NIST AI RMF (Orientación voluntaria disponible en 2023):
❌ MANAGE-4.4 (Security controls) - Sistema ignoró orientación disponible
❌ MAP-2.3 (Data quality and fairness) - Documentación de dataset inadecuada
❌ MANAGE-4.1 (Human oversight) - Sin mecanismos de supervisión

ANÁLISIS ISO 42001:
⚠️  Estándar publicado octubre 2023 - Puede no haber sido adoptado todavía

CONCLUSIONES FORENSES:
1. Sistema habría violado EU AI Act si hubiera estado vigente (ahora sujeto a sanciones)
2. Sistema ignoró orientación voluntaria NIST que estaba disponible
3. El fallo era prevenible usando mejores prácticas de la industria (NIST) disponibles en el momento
4. Demuestra negligencia: frameworks voluntarios existían pero no se siguieron

IMPLICACIONES DE APLICACIÓN:
- Si el sistema sigue operando: Cumplimiento EU AI Act requerido inmediatamente
- Si desplegado en US: Debería adoptar NIST AI RMF retroactivamente
- Si certificado ISO 42001 después del incidente: La certificación puede ser inválida
```

---

## Propiedades Definidas

Los mappings introducen 9 nuevas propiedades entre ambos frameworks:

### Propiedades ISO 42001

#### ai:equivalentToISOControl
- **Tipo:** owl:ObjectProperty
- **Dominio:** ai:ComplianceRequirement
- **Rango:** iso:Control
- **Propósito:** Enlaza requisito EU AI Act con control ISO equivalente

#### ai:isoSection
- **Tipo:** owl:DatatypeProperty
- **Dominio:** ai:ComplianceRequirement
- **Rango:** xsd:string
- **Propósito:** Número de sección ISO (ej., "8.3.2")

#### ai:isoControlDescription
- **Tipo:** owl:DatatypeProperty
- **Propósito:** Descripción legible del control ISO

#### ai:mappingConfidence
- **Tipo:** owl:DatatypeProperty
- **Rango:** "HIGH" | "MEDIUM" | "LOW"
- **Propósito:** Nivel de confianza del mapping ISO

### Propiedades NIST AI RMF

#### ai:equivalentToNISTFunction
- **Tipo:** owl:ObjectProperty
- **Dominio:** ai:ComplianceRequirement
- **Rango:** nist:Function
- **Propósito:** Enlaza requisito EU AI Act con función NIST AI RMF equivalente

#### ai:nistCategory
- **Tipo:** owl:DatatypeProperty
- **Dominio:** ai:ComplianceRequirement
- **Rango:** xsd:string
- **Propósito:** Identificador de categoría NIST AI RMF (ej., "GOVERN-1.1", "MAP-2.3")

#### ai:nistCategoryDescription
- **Tipo:** owl:DatatypeProperty
- **Propósito:** Descripción legible de la categoría NIST

#### ai:nistMappingConfidence
- **Tipo:** owl:DatatypeProperty
- **Rango:** "HIGH" | "MEDIUM" | "LOW"
- **Propósito:** Nivel de confianza del mapping NIST

#### ai:nistApplicabilityContext
- **Tipo:** owl:DatatypeProperty
- **Rango:** "US_INCIDENTS" | "GLOBAL_INCIDENTS" | "COMPARATIVE_ANALYSIS" | "VOLUNTARY_COMPLIANCE"
- **Propósito:** Contexto donde el mapping NIST es más relevante

---

## Carga de Mappings

### Carga Automática (Docker)

Los mappings se montan automáticamente en contenedores vía `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./ontologias/mappings:/ontologias/mappings:ro

reasoner:
  volumes:
    - ./ontologias/mappings:/ontologias/mappings:ro
```

### Carga Manual (Python)

```python
from rdflib import Graph

# Cargar ontología + todos los mappings
g = Graph()
g.parse("ontologias/versions/0.41.0/ontologia-v0.41.0.ttl", format="turtle")
g.parse("ontologias/mappings/iso-42001-mappings.ttl", format="turtle")
g.parse("ontologias/mappings/nist-ai-rmf-mappings.ttl", format="turtle")
g.parse("ontologias/mappings/dpv-integration.ttl", format="turtle")

# Query mappings ISO
iso_query = """
PREFIX ai: <http://ai-act.eu/ai#>
SELECT ?req ?iso WHERE {
  ?req ai:equivalentToISOControl ?iso .
}
"""
iso_results = g.query(iso_query)

# Query mappings NIST
nist_query = """
PREFIX ai: <http://ai-act.eu/ai#>
SELECT ?req ?nist ?category ?context WHERE {
  ?req ai:equivalentToNISTFunction ?nist ;
       ai:nistCategory ?category ;
       ai:nistApplicabilityContext ?context .
}
"""
nist_results = g.query(nist_query)
```

---

## Puntos de Integración

### Agente de Análisis Forense (Fases 2 y 3)

El agente forense utiliza estos mappings para:

**Integración ISO 42001 (Fase 2):**
1. **Identificar controles ISO fallidos** durante análisis de incidentes
2. **Generar informes multi-framework** (EU + ISO)
3. **Detectar gaps de certificación** (certificado ISO pero no cumple EU)
4. **Proporcionar pistas de evidencia** para acciones de aplicación

**Integración NIST AI RMF (Fase 3):**
1. **Analizar incidentes US/globales** usando framework voluntario NIST
2. **Análisis retrospectivo** de incidentes pre-EU AI Act
3. **Cumplimiento comparativo** (obligatorio EU vs voluntario US)
4. **Informes transjurisdiccionales** para despliegues multinacionales
5. **Detectar negligencia** (orientación voluntaria ignorada)

### API Backend (Implementado)

Endpoints disponibles:
```
# Endpoints ISO 42001
GET /mappings/iso-42001                      # Listar todos los mappings ISO
GET /mappings/iso-42001/{requirement}        # Obtener control ISO para requisito EU

# Endpoints NIST AI RMF
GET /mappings/nist-ai-rmf                    # Listar todos los mappings NIST
GET /mappings/nist-ai-rmf/{requirement}      # Obtener función NIST para requisito EU

# Endpoints Multi-Framework
GET /mappings/frameworks                     # Listar todos los frameworks soportados
```

---

## Mantenimiento

### Añadir Nuevos Mappings ISO 42001

1. Editar `iso-42001-mappings.ttl`
2. Añadir mapping siguiendo el patrón existente:

```turtle
ai:NewRequirement
    ai:equivalentToISOControl iso:Control_X_Y ;
    ai:isoSection "X.Y" ;
    ai:isoControlDescription "Descripción aquí" ;
    ai:mappingConfidence "HIGH" ;
    rdfs:comment "Explicación en español"@es,
        "Explanation in English"@en .
```

3. Actualizar estadísticas al final del fichero
4. Reiniciar contenedores para recargar

### Añadir Nuevos Mappings NIST AI RMF

1. Editar `nist-ai-rmf-mappings.ttl`
2. Añadir mapping siguiendo el patrón existente:

```turtle
ai:NewRequirement
    ai:equivalentToNISTFunction nist:FUNCTION_X_Y ;
    ai:nistCategory "FUNCTION-X.Y" ;
    ai:nistCategoryDescription "Descripción aquí" ;
    ai:nistMappingConfidence "HIGH" ;
    ai:nistApplicabilityContext "GLOBAL_INCIDENTS, US_INCIDENTS" ;
    rdfs:comment "Explicación en español"@es,
        "Explanation in English"@en .
```

3. Actualizar estadísticas al final del fichero
4. Reiniciar contenedores para recargar

### Validación

```bash
# Validar sintaxis Turtle
rapper -i turtle -o ntriples iso-42001-mappings.ttl > /dev/null
rapper -i turtle -o ntriples nist-ai-rmf-mappings.ttl > /dev/null
rapper -i turtle -o ntriples dpv-integration.ttl > /dev/null

# Comprobar completitud
grep -c "ai:equivalentToISOControl" iso-42001-mappings.ttl
# Debería mostrar: 15

grep -c "ai:equivalentToNISTFunction" nist-ai-rmf-mappings.ttl
# Debería mostrar: 16
```

---

## Referencias

- **EU AI Act:** [Texto oficial EUR-Lex](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)
- **ISO/IEC 42001:2023:** [Página oficial ISO](https://www.iso.org/standard/81230.html)
- **NIST AI RMF 1.0:** [Publicación oficial NIST](https://www.nist.gov/itl/ai-risk-management-framework)
- **W3C DPV 2.2:** [Data Privacy Vocabulary](https://w3c.github.io/dpv/)
- **Metodología de Mapping:** Basada en análisis comparativo de textos legales, requisitos técnicos y objetivos de los frameworks

---

## Historial de Versiones

| Versión | Fecha | Framework | Cambios |
|---------|-------|-----------|---------|
| 1.0.0 | 2025-12-05 | ISO 42001 | 15 mappings ISO iniciales para Fase 2 |
| 1.0.0 | 2025-12-05 | NIST AI RMF | 16 mappings NIST iniciales para Fase 3 |
| 0.2.0 | 2026-01-10 | DPV 2.2 | Integración W3C DPV + URIs ELI |

---

## Resumen de Estadísticas

| Framework | Mappings | Confianza | Estado |
|-----------|----------|-----------|--------|
| **ISO 42001** | 15 | 87% HIGH, 13% MEDIUM | ✅ Activo |
| **NIST AI RMF** | 16 | 100% HIGH | ✅ Activo |
| **DPV 2.2** | 14 | - | ✅ Activo |
| **Total** | **45** | **94% HIGH** | **Fases 2 y 3 Completadas** |

---

## Licencia

Los mappings se proporcionan bajo Creative Commons Attribution 4.0 International (CC BY 4.0), consistente con la licencia de la ontología EU AI Act.

---

**Última Actualización:** Enero 2026
**Estado:** Activo (Fases 2 y 3 Completadas)
**Compatibilidad:** Ontología EU AI Act v0.41.0
