# 🧠 AI Act SWRL Reasoner Service

## Descripción General

Este servicio implementa un **motor de razonamiento semántico híbrido** que combina **RDFLib** para el parsing de ontologías con **inferencia manual de reglas SWRL** para evaluar el cumplimiento del EU AI Act en sistemas de inteligencia artificial.

## 🎯 Arquitectura del Reasoner

### Componentes Principales

1. **Parser RDFLib**: Carga y procesa archivos TTL (ontologías + datos del sistema)
2. **Motor SWRL Manual**: Aplica reglas de inferencia basadas en el EU AI Act
3. **Generador de Inferencias**: Produce nuevos triples RDF basados en las reglas
4. **Serializador**: Convierte el grafo resultante a TTL y JSON estructurado

### Flujo de Procesamiento

```mermaid
graph LR
    A[Sistema IA] --> B[Generación TTL]
    B --> C[Carga Ontología Base]
    C --> D[Aplicación Reglas SWRL]
    D --> E[Inferencias Generadas]
    E --> F[Respuesta JSON + TTL]
```

## 📋 Reglas SWRL Implementadas

### 1. **Reglas por Propósito (Purpose-based Rules)**

#### 1.1 Regla de Protección Educativa
```swrl
hasPurpose(system, EducationAccess) → hasNormativeCriterion(system, ProtectionOfMinors)
```
**Justificación**: Anexo III, punto 3 del EU AI Act - Sistemas de evaluación educativa requieren protección especial de menores.

**Implementación**:
```python
if (system, AI.hasPurpose, AI.EducationAccess) in combined_graph:
    combined_graph.add((system, AI.hasNormativeCriterion, AI.ProtectionOfMinors))
```

#### 1.2 Regla de No Discriminación en Empleo
```swrl
hasPurpose(system, Employment) → hasNormativeCriterion(system, NonDiscrimination)
```
**Justificación**: Anexo III, punto 4 del EU AI Act - Sistemas de reclutamiento y empleo deben prevenir discriminación.

#### 1.3 Regla de Seguridad Biométrica
```swrl
hasPurpose(system, BiometricIdentification) → hasContextualCriterion(system, BiometricSecurity)
```
**Justificación**: Anexo III, punto 1 del EU AI Act - Identificación biométrica requiere medidas de seguridad específicas.

### 2. **Reglas por Contexto de Despliegue (Context-based Rules)**

#### 2.1 Regla de Contexto Educativo
```swrl
hasDeploymentContext(system, Education) → hasNormativeCriterion(system, ProtectionOfMinors)
```
**Justificación**: Cualquier sistema desplegado en entorno educativo requiere protección de menores independientemente del propósito.

#### 2.2 Regla de Servicios de Salud
```swrl
hasDeploymentContext(system, Healthcare) → hasNormativeCriterion(system, EssentialServicesAccessCriterion)
```
**Justificación**: Sistemas en entornos sanitarios afectan el acceso a servicios esenciales.

#### 2.3 Regla de Servicios Públicos
```swrl
hasDeploymentContext(system, PublicServices) → hasNormativeCriterion(system, EssentialServicesAccessCriterion)
```
**Justificación**: Sistemas en servicios públicos pueden limitar el acceso ciudadano a servicios fundamentales.

#### 2.4 Regla de Procesamiento en Tiempo Real
```swrl
hasDeploymentContext(system, RealTimeProcessing) → hasTechnicalCriterion(system, PerformanceRequirements)
```
**Justificación**: Sistemas de tiempo real requieren garantías de rendimiento específicas.

#### 2.5 Regla de Alto Volumen
```swrl
hasDeploymentContext(system, HighVolumeProcessing) → hasTechnicalCriterion(system, ScalabilityRequirements)
```
**Justificación**: Sistemas de alto volumen necesitan requisitos de escalabilidad.

### 3. **Reglas en Cadena (Chain Rules)**

#### 3.1 Cadena de Protección de Menores
```swrl
hasNormativeCriterion(system, ProtectionOfMinors) → hasRequirement(system, ParentalConsent)
```
**Justificación**: Artículo 29 del EU AI Act - Protección de menores requiere consentimiento parental.

#### 3.2 Cadena de No Discriminación
```swrl
hasNormativeCriterion(system, NonDiscrimination) → hasRequirement(system, Auditability)
```
**Justificación**: Sistemas anti-discriminación deben ser auditables para verificar cumplimiento.

#### 3.3 Cadena de Seguridad Biométrica
```swrl
hasContextualCriterion(system, BiometricSecurity) → hasTechnicalRequirement(system, DataEncryption)
```
**Justificación**: Datos biométricos requieren cifrado por su naturaleza sensible.

#### 3.4 Cadena de Servicios Esenciales
```swrl
hasNormativeCriterion(system, EssentialServicesAccessCriterion) →
    hasRequirement(system, HumanOversightRequirement) ∧
    hasRequirement(system, DataGovernanceRequirement) ∧
    hasRequirement(system, FundamentalRightsAssessmentRequirement)
```
**Justificación**: Servicios esenciales requieren supervisión humana, gobernanza de datos y evaluación de derechos fundamentales.

### 4. **Reglas de Prácticas Prohibidas (Art. 5)**

#### 4.1 Regla de Práctica Prohibida → Criterio
```swrl
hasProhibitedPractice(system, ?practice) → hasCriteria(system, ?practice)
```
**Justificación**: Artículo 5 del EU AI Act - Las prácticas prohibidas se convierten en criterios activados para permitir la inferencia de nivel de riesgo.

#### 4.2 Regla de Criterio → Nivel de Riesgo Inaceptable
```swrl
hasCriteria(system, ?criterion) ∧ assignsRiskLevel(?criterion, ?riskLevel) → hasRiskLevel(system, ?riskLevel)
```
**Justificación**: Si un criterio (incluyendo prácticas prohibidas) asigna un nivel de riesgo, el sistema hereda ese nivel. Las prácticas prohibidas del Art. 5 asignan `UnacceptableRisk`.

#### 4.3 Regla de Override de Niveles de Riesgo (REGLA 5.5)
```swrl
hasRiskLevel(system, UnacceptableRisk) → ¬hasRiskLevel(system, HighRisk) ∧ ¬hasRiskLevel(system, LimitedRisk) ∧ ¬hasRiskLevel(system, MinimalRisk)
```
**Justificación**: Cuando un sistema tiene múltiples niveles de riesgo inferidos de diferentes criterios, el nivel más restrictivo prevalece. La jerarquía es:
- **UnacceptableRisk** > HighRisk > LimitedRisk > MinimalRisk

**Comportamiento**:
- Si `UnacceptableRisk` está presente → elimina `HighRisk`, `LimitedRisk`, `MinimalRisk`
- Si `HighRisk` está presente (sin Unacceptable) → elimina `LimitedRisk`, `MinimalRisk`
- Si `LimitedRisk` está presente (sin High ni Unacceptable) → elimina `MinimalRisk`

**Ejemplo**:
Un sistema con `BiometricIdentification` (infiere `HighRisk`) y `PredictivePolicingProfilingCriterion` (infiere `UnacceptableRisk`) solo mostrará `UnacceptableRisk` como nivel de riesgo final.

**Prácticas prohibidas definidas (Art. 5):**
| Criterio | Artículo | Nivel de Riesgo |
|----------|----------|-----------------|
| `ai:SubliminalManipulationCriterion` | Art. 5(1)(a) | UnacceptableRisk |
| `ai:VulnerabilityExploitationCriterion` | Art. 5(1)(b) | UnacceptableRisk |
| `ai:SocialScoringCriterion` | Art. 5(1)(c) | UnacceptableRisk |
| `ai:PredictivePolicingProfilingCriterion` | Art. 5(1)(d) | UnacceptableRisk |
| `ai:RealTimeBiometricIdentificationCriterion` | Art. 5(1)(h) | UnacceptableRisk |

**Implementación**:
```python
# En backend/swrl_rules.py
ai:ProhibitedPracticeToCriteriaRule rdf:type swrl:Rule ;
    swrl:body [ hasProhibitedPractice(?system, ?practice) ] ;
    swrl:head [ hasCriteria(?system, ?practice) ] .

# La regla CriterionRiskLevelRule existente infiere:
ai:CriterionRiskLevelRule rdf:type swrl:Rule ;
    swrl:body [ hasCriteria(?system, ?criterion) ∧ assignsRiskLevel(?criterion, ?riskLevel) ] ;
    swrl:head [ hasRiskLevel(?system, ?riskLevel) ] .
```

#### 4.4 Regla de Excepciones Art. 5.2 (REGLA 5.5a)
```swrl
hasProhibitedPractice(system, RealTimeBiometricIdentificationCriterion) ∧
hasLegalException(system, ?exception) ∧
hasJudicialAuthorization(system, true) →
    ¬hasRiskLevel(system, UnacceptableRisk) ∧
    hasRiskLevel(system, HighRisk) ∧
    hasArticle5Exception(system, true)
```
**Justificación**: Artículo 5(2) del EU AI Act permite excepciones **únicamente** para la identificación biométrica remota en tiempo real cuando se cumplen **todas** las condiciones:
1. El sistema utiliza identificación biométrica remota en tiempo real (Art. 5.1.h)
2. Existe una excepción legal válida del Art. 5.2
3. Se ha obtenido autorización judicial previa

**Excepciones válidas del Art. 5.2:**
| Excepción | Artículo | Descripción |
|-----------|----------|-------------|
| `ai:VictimSearchException` | Art. 5.2(a) | Búsqueda de víctimas de secuestro, trata de personas, explotación sexual |
| `ai:TerroristThreatException` | Art. 5.2(b) | Prevención de amenaza terrorista específica e inminente |
| `ai:SeriousCrimeException` | Art. 5.2(c) | Localización/identificación de sospechoso de delito grave (Anexo II) |

**Comportamiento**:
- Si el sistema cumple las 3 condiciones → `UnacceptableRisk` se convierte en `HighRisk`
- El sistema puede desplegarse, pero sigue siendo de **alto riesgo** con todas las obligaciones del Título III
- Se añade `hasArticle5Exception: true` para indicar que opera bajo excepción

**IMPORTANTE**: Las demás prácticas prohibidas (manipulación subliminal, explotación de vulnerabilidades, social scoring, predictive policing) **NO tienen excepciones** y siempre resultan en `UnacceptableRisk`.

**Ejemplo**:
```ttl
<urn:uuid:system-biometric> a ai:IntelligentSystem ;
    ai:hasName "Sistema Policial de Búsqueda" ;
    ai:hasProhibitedPractice ai:RealTimeBiometricIdentificationCriterion ;
    ai:hasLegalException ai:VictimSearchException ;
    ai:hasJudicialAuthorization true .

# Resultado del razonamiento:
# hasRiskLevel: HighRisk (no UnacceptableRisk)
# hasArticle5Exception: true
```

### 5. **Reglas de Ámbito de Aplicación (Art. 2)**

#### 5.1 Regla de Exclusión de Scope
```swrl
hasPurpose(system, ?purpose) ∧ mayBeExcludedBy(?purpose, ?exclusion) →
    hasPotentialScopeExclusion(system, ?exclusion)
```
**Justificación**: Artículo 2 del EU AI Act - Ciertos propósitos pueden estar excluidos del ámbito de aplicación.

#### 5.2 Regla de Override de Exclusión
```swrl
hasPotentialScopeExclusion(system, ?exclusion) ∧
hasDeploymentContext(system, ?context) ∧
overridesExclusion(?context, ?exclusion) →
    isInEUAIActScope(system, true)
```
**Justificación**: Contextos con impacto real (víctimas, consecuencias legales, derechos fundamentales) anulan las exclusiones y traen el sistema de vuelta al ámbito del reglamento.

**Contextos Override definidos:**
- `ai:CausesRealWorldHarmContext` - Daño real a personas
- `ai:VictimImpactContext` - Víctimas identificables
- `ai:AffectsFundamentalRightsContext` - Afecta derechos fundamentales
- `ai:LegalConsequencesContext` - Consecuencias legales
- `ai:MinorsAffectedContext` - Menores afectados

### 6. **Reglas de Incidentes Graves (Art. 3(49))**

#### 6.1 Regla de Clasificación de Incidente Grave
```swrl
hasIncidentType(system, ?type) ∧ SeriousIncident(?type) →
    hasSeriousIncidentType(system, ?type)
```
**Justificación**: Artículo 3(49) del EU AI Act - Clasificación de incidentes graves según taxonomía.

#### 6.2 Regla de Notificación Obligatoria (Art. 73)
```swrl
hasSeriousIncidentType(system, ?type) ∧ triggersArticle73(?type, true) →
    requiresIncidentNotification(system, true) ∧
    notificationDeadlineDays(system, 15)
```
**Justificación**: Artículo 73 del EU AI Act - Incidentes graves requieren notificación a la autoridad competente en 15 días.

**Tipos de incidente grave (Art. 3(49)):**
| Tipo | Artículo | Trigger Art. 73 |
|------|----------|-----------------|
| `ai:DeathOrHealthHarm` | Art. 3(49)(a) | ✓ |
| `ai:CriticalInfrastructureDisruption` | Art. 3(49)(b) | ✓ |
| `ai:FundamentalRightsInfringement` | Art. 3(49)(c) | ✓ |
| `ai:PropertyOrEnvironmentHarm` | Art. 3(49)(d) | ✓ |

### 7. **Reglas de Affected Persons (Art. 86)**

#### 7.1 Regla de Explicabilidad
```swrl
hasSubject(system, ?person) ∧ hasRiskLevel(system, HighRisk) →
    requiresExplainability(system, true)
```
**Justificación**: Artículo 86 del EU AI Act - Sistemas de alto riesgo con personas afectadas requieren explicabilidad.

#### 7.2 Regla de FRIA para Grupos Vulnerables
```swrl
hasSubject(system, ?person) ∧ VulnerableGroup(?person) →
    requiresFundamentalRightsAssessment(system, true)
```
**Justificación**: Artículo 27 del EU AI Act - Sistemas que afectan a grupos vulnerables requieren evaluación de impacto en derechos fundamentales (FRIA).

**Grupos vulnerables detectados:**
- Menores (Minor/Child)
- Personas mayores (Elderly)
- Personas con discapacidad (Disabled)
- Migrantes y solicitantes de asilo (Migrant/Asylum)

## 🔧 Modo de Evaluación

### Endpoint Principal
```
POST http://localhost:8001/reason
```

### Estructura de Entrada
```json
{
    "system_ttl": "...",     // TTL del sistema a evaluar
    "rules_ttl": "..."       // Reglas SWRL en formato TTL
}
```

### Estructura de Salida
```json
{
    "system_id": "urn:uuid:...",
    "system_name": "Ejemplo_1",
    "reasoning_completed": true,
    "inferred_relationships": {
        "hasNormativeCriterion": ["http://ai-act.eu/ai#EssentialServicesAccessCriterion"],
        "hasTechnicalCriterion": [],
        "hasContextualCriterion": ["http://ai-act.eu/ai#BiometricSecurity"],
        "hasRequirement": [
            "http://ai-act.eu/ai#DataGovernanceRequirement",
            "http://ai-act.eu/ai#FundamentalRightsAssessmentRequirement",
            "http://ai-act.eu/ai#HumanOversightRequirement"
        ],
        "hasTechnicalRequirement": ["http://ai-act.eu/ai#DataEncryption"]
    },
    "raw_ttl": "..."  // Grafo completo con inferencias
}
```

## 🧪 Casos de Prueba

### Caso 1: Sistema Educativo
**Input**:
```ttl
<urn:uuid:system1> a ai:IntelligentSystem ;
    ai:hasPurpose ai:EducationAccess ;
    ai:hasDeploymentContext ai:Education .
```

**Inferencias Esperadas**:
- `hasNormativeCriterion: ProtectionOfMinors` (por propósito + contexto)
- `hasRequirement: ParentalConsent` (regla en cadena)

### Caso 2: Sistema Biométrico en Servicios Públicos
**Input**:
```ttl
<urn:uuid:system2> a ai:IntelligentSystem ;
    ai:hasPurpose ai:BiometricIdentification ;
    ai:hasDeploymentContext ai:PublicServices .
```

**Inferencias Esperadas**:
- `hasContextualCriterion: BiometricSecurity` (por propósito)
- `hasTechnicalRequirement: DataEncryption` (regla en cadena)
- `hasNormativeCriterion: EssentialServicesAccessCriterion` (por contexto)
- `hasRequirement: HumanOversightRequirement, DataGovernanceRequirement, FundamentalRightsAssessmentRequirement` (regla en cadena)

### Caso 3: Sistema con Incidente Grave (Art. 3(49))
**Input**:
```ttl
<urn:uuid:system3> a ai:IntelligentSystem ;
    ai:hasPurpose ai:LawEnforcementSupport ;
    ai:hasIncidentType ai:FundamentalRightsInfringement .
```

**Inferencias Esperadas**:
- `hasSeriousIncidentType: FundamentalRightsInfringement` (Art. 3(49)(c))
- `requiresIncidentNotification: true` (Art. 73)
- `notificationDeadlineDays: 15` (Art. 73)

### Caso 4: Sistema con Práctica Prohibida (Art. 5)
**Input**:
```ttl
<urn:uuid:system4> a ai:IntelligentSystem ;
    ai:hasName "Paco" ;
    ai:hasPurpose ai:BiometricIdentification ;
    ai:hasDeploymentContext ai:WorkplaceMonitoringContext ;
    ai:hasProhibitedPractice ai:PredictivePolicingProfilingCriterion .
```

**Inferencias Esperadas**:
- `hasCriteria: PredictivePolicingProfilingCriterion` (por regla ProhibitedPracticeToCriteriaRule)
- `hasRiskLevel: UnacceptableRisk` (por regla CriterionRiskLevelRule, ya que PredictivePolicingProfilingCriterion tiene assignsRiskLevel UnacceptableRisk)

**Nota**: Los sistemas con nivel de riesgo `UnacceptableRisk` no pueden desplegarse en la UE.

### Caso 5: Sistema Excluido con Override (Art. 2)
**Input**:
```ttl
<urn:uuid:system5> a ai:IntelligentSystem ;
    ai:hasPurpose ai:Entertainment ;
    ai:hasDeploymentContext ai:VictimImpactContext .
```

**Inferencias Esperadas**:
- `hasPotentialScopeExclusion: EntertainmentWithoutRightsImpact` (Art. 2)
- `isInEUAIActScope: true` (override por VictimImpactContext)
- `requiresFRIA: true` (Art. 27)

## 🔍 Debugging y Logs

### Activación de Logs Detallados
Los logs están habilitados por defecto y muestran:
```
DEBUG: Procesando sistema: urn:uuid:...
DEBUG: Verificando BiometricIdentification para urn:uuid:...
DEBUG: ¿Tiene propósito BiometricIdentification? True
DEBUG: ✅ Inferencia aplicada: urn:uuid:... -> hasContextualCriterion -> BiometricSecurity (por propósito)
DEBUG: *** RAZONAMIENTO COMPLETADO: 6 inferencias aplicadas ***
```

### Verificación de Reglas
Para verificar qué reglas se están aplicando:
1. Revisar logs del container: `docker-compose logs reasoner`
2. Contar inferencias aplicadas en la respuesta
3. Validar coherencia con la ontología base

## 🚀 Extensión del Sistema

### Agregar Nueva Regla SWRL

1. **Definir la regla** en `backend/swrl_rules.py`:
```ttl
ai:NewRule rdf:type swrl:Rule ;
    swrl:body [ /* condición */ ] ;
    swrl:head [ /* inferencia */ ] .
```

2. **Implementar lógica** en `reasoner_service/app/main.py`:
```python
# NUEVA REGLA: Condición -> Inferencia
if (system, AI.hasProperty, AI.Value) in combined_graph:
    combined_graph.add((system, AI.hasNewProperty, AI.NewValue))
    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNewProperty -> NewValue")
    inferences_count += 1
```

3. **Reconstruir container**:
```bash
docker-compose up -d --build reasoner
```

### Consideraciones de Rendimiento
- Las reglas se evalúan secuencialmente
- El grafo combinado se mantiene en memoria
- Para sistemas complejos, considerar optimización de consultas SPARQL

## 📚 Referencias

- **EU AI Act**: Regulation (EU) 2024/1689
- **SWRL Specification**: https://www.w3.org/Submission/SWRL/
- **RDFLib Documentation**: https://rdflib.readthedocs.io/
- **Ontología AI Act**: `/ontologias/versions/1.0.0/ontologia-v1.0.0.ttl`

## 🤝 Contribución

Para contribuir nuevas reglas SWRL:
1. Identificar el artículo/anexo del EU AI Act aplicable
2. Definir la regla en sintaxis SWRL formal
3. Implementar la lógica de inferencia
4. Agregar casos de prueba
5. Documentar la justificación legal

---

**Versión**: 1.3
**Última Actualización**: Enero 2026
**Compatibilidad**: EU AI Act Ontology v1.0.0

---

### Changelog

#### v1.3 (Enero 2026)
- Nueva regla 4.4 (REGLA 5.5a): Excepciones Art. 5.2 para identificación biométrica remota
- Soporte para `hasLegalException` y `hasJudicialAuthorization` en TTL
- Sistemas con excepción válida + autorización judicial pasan de UnacceptableRisk a HighRisk
- Añadida propiedad `hasArticle5Exception` para indicar operación bajo excepción
- Fix: Bug de cierre de conexión MongoDB en errores de duplicado

#### v1.2 (Enero 2026)
- Nueva regla 4.3 (REGLA 5.5): Override de niveles de riesgo - el más restrictivo prevalece
- Jerarquía implementada: UnacceptableRisk > HighRisk > LimitedRisk > MinimalRisk
- Fix: Sistemas con múltiples criterios de riesgo ahora muestran solo el nivel más alto

#### v1.1 (Enero 2026)
- Añadida sección 4: Reglas de Prácticas Prohibidas (Art. 5)
- Nueva regla `ProhibitedPracticeToCriteriaRule`: convierte prácticas prohibidas en criterios
- Soporte para inferencia automática de `UnacceptableRisk` desde prácticas prohibidas
- Añadido Caso de Prueba 4: Sistema con práctica prohibida
- Renumeración de secciones 5-7