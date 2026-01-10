# Diagrama de Flujo - Agente Forense de Cumplimiento

## Parte 1: Extracción y Análisis Ontológico (Fases 1-3)

```mermaid
flowchart TB
    %% Entrada
    Start([API POST /forensic/analyze<br/>Narrative + Metadata]) --> Phase1

    %% Fase 1: Extracción
    Phase1{{Fase 1: Extracción LLM}}
    Phase1 --> Extract[LLM Extraction<br/>incident_extractor.py]
    Extract --> ParseJSON[Parse JSON<br/>system, incident, timeline]
    ParseJSON --> Confidence{Confidence<br/> ≥ 0.6?}

    Confidence -->|No| LowConf[LOW_CONFIDENCE<br/>requires_human_review]
    Confidence -->|Yes| Phase2

    %% Fase 2: Ontología EU AI Act
    Phase2{{Fase 2: Análisis EU AI Act}}
    Phase2 --> SPARQL1[Query SPARQL<br/>mandatory_requirements]

    SPARQL1 --> Scope{EU AI Act<br/>scope?}

    Scope -->|Sí| RiskCalc[Calcular Risk Level]
    Scope -->|No| ScopeExcl[Verificar Exclusions<br/>Art. 2]

    ScopeExcl --> Override{Scope<br/>Override?}
    Override -->|Sí| RiskCalc
    Override -->|No| OutOfScope[OutOfScope]

    RiskCalc --> RiskLevel{Risk Level}
    RiskLevel -->|HighRisk| HighReqs[Requisitos Título III<br/>Art. 8-15]
    RiskLevel -->|LimitedRisk| LimitedReqs[Requisitos Art. 50-52]
    RiskLevel -->|MinimalRisk| MinimalReqs[Transparency Art. 50]

    HighReqs --> Phase3
    LimitedReqs --> Phase3
    MinimalReqs --> Phase3
    OutOfScope --> Phase3

    %% Fase 3: Multi-framework
    Phase3{{Fase 3: Mapeo Multi-framework}}
    Phase3 --> ISO[ISO 42001<br/>Controls]
    Phase3 --> NIST[NIST AI RMF<br/>Functions]

    ISO --> Continue[Continúa en Parte 2]
    NIST --> Continue
    LowConf --> EndPart1([Fin Parte 1])
    Continue --> EndPart1

    %% Estilos
    classDef phaseStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:3px,color:#000
    classDef decisionStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000
    classDef processStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000
    classDef errorStyle fill:#FFEBEE,stroke:#C62828,stroke-width:2px,color:#000
    classDef continueStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000

    class Phase1,Phase2,Phase3 phaseStyle
    class Confidence,Scope,Override,RiskLevel decisionStyle
    class Extract,ParseJSON,SPARQL1,RiskCalc,ISO,NIST processStyle
    class LowConf errorStyle
    class Continue,EndPart1 continueStyle
```

## Parte 2: Análisis de Gaps y Persistencia (Fases 4-6)

```mermaid
flowchart TB
    %% Continuación
    Start([Continúa de Parte 1<br/>Requirements + Mappings]) --> Phase4

    %% Fase 4: Análisis de Gaps
    Phase4{{Fase 4: Análisis de Gaps}}
    Phase4 --> GapAnalysis[analyze_compliance_gaps<br/>compliance_ratio]

    GapAnalysis --> CriticalGaps[Detectar Critical Gaps<br/>CRITICAL, MAJOR, MINOR]
    CriticalGaps --> InferenceRules[Query SWRL Rules<br/>Navigation Rules]

    InferenceRules --> Phase5

    %% Fase 5: Generación Reporte
    Phase5{{Fase 5: Generación Reporte}}
    Phase5 --> BuildReport[Construir ForensicReport<br/>extraction + frameworks + gaps]

    BuildReport --> SeriousIncident{Incidente Grave<br/>Art. 3 49?}

    SeriousIncident -->|Sí| ClassifyType[Clasificar tipo:<br/>DeathOrHealthHarm<br/>CriticalInfrastructure<br/>FundamentalRights<br/>PropertyOrEnvironment]
    SeriousIncident -->|No| SkipSerious[No aplica Art. 3 49]

    ClassifyType --> Article73{triggers<br/>Article73?}
    Article73 -->|Sí| Notification[Notificación obligatoria<br/>15 días Art. 73]
    Article73 -->|No| NoNotification[No requiere notificación]

    SkipSerious --> Phase6
    Notification --> Phase6
    NoNotification --> Phase6

    %% Fase 6: Persistencia
    Phase6{{Fase 6: Persistencia}}
    Phase6 --> MongoDB[MongoDB<br/>analyzed_systems]
    Phase6 --> Fuseki[Fuseki<br/>RDF triples + URN]

    MongoDB --> Success[COMPLETED<br/>persisted: true]
    Fuseki --> Success

    Success --> End([Return ForensicAnalysisResult])

    %% Estilos
    classDef phaseStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:3px,color:#000
    classDef decisionStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000
    classDef processStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000
    classDef successStyle fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px,color:#000
    classDef continueStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000

    class Phase4,Phase5,Phase6 phaseStyle
    class SeriousIncident,Article73 decisionStyle
    class GapAnalysis,CriticalGaps,InferenceRules,BuildReport,ClassifyType,MongoDB,Fuseki processStyle
    class Success successStyle
    class Start continueStyle
```

## Leyenda de Componentes

### Fases del Análisis

1. **Fase 1: Recepción y Extracción**
   - Entrada: Narrative (texto libre)
   - Procesador: LLM (llama3.2 via Ollama o Claude Sonnet)
   - Salida: ExtractedIncident (JSON estructurado)
   - Validación: Threshold de confianza ≥ 0.6

2. **Fase 2: Consulta Ontología EU AI Act**
   - Determina Risk Level usando clasificación ontológica
   - Verifica Scope Exclusions (Art. 2) y Scope Overrides (v0.39.0)
   - Identifica criterios activados y requisitos mandatorios
   - Consulta vía MCP SPARQL Service

3. **Fase 3: Mapeo Multi-framework**
   - ISO 42001: Controls de AIMS (AI Management System)
   - NIST AI RMF: Functions y Subcategories del Risk Management Framework
   - Mapeo semántico mediante propiedades `ai:mapsToISO42001` y `ai:mapsToNISTAIRMF`

4. **Fase 4: Análisis de Compliance Gaps**
   - Compara requisitos mandatorios vs. evidencia del incidente
   - Calcula `compliance_ratio` (0.0 - 1.0)
   - Clasifica gaps por severidad: CRITICAL, MAJOR, MINOR
   - Identifica reglas SWRL aplicables para inferencias

5. **Fase 5: Generación de Reporte Forense**
   - Construcción de `ForensicAnalysisResult`
   - Clasificación de Serious Incidents (Art. 3(49)) - v0.41.0
   - Determinación de obligaciones de notificación (Art. 73)
   - Validación de completitud del análisis

6. **Fase 6: Persistencia**
   - MongoDB: Almacenamiento de análisis completo en JSON
   - Fuseki: Persistencia en RDF con URN único
   - Integración con Knowledge Graph para consultas posteriores

### Decisiones Críticas

- **Confidence Threshold**: Si < 0.6, el análisis se detiene con `LOW_CONFIDENCE`
- **Scope Determination**: Art. 2 exclusions pueden ser overridden por contextos críticos
- **Risk Level**: Determina conjunto de requisitos aplicables (Título III vs. Art. 50-52)
- **Serious Incidents**: Activa obligaciones de notificación según Art. 73

### Nuevas Características (v0.41.0)

- **Taxonomía Art. 3(49)**: Clasificación de incidentes graves en 4 categorías
- **Article 73 Triggers**: Detección automática de obligación de reporte (15 días)
- **DPV-Risk Integration**: Mapeo a Data Privacy Vocabulary Risk concepts
- **SWRL Inference Rules**: Navegación semántica de requisitos relacionados

## Tecnologías Utilizadas

- **LLM**: Ollama (llama3.2) o Claude Sonnet 4.5
- **Ontología**: OWL 2 DL (v0.41.0)
- **Query Engine**: Apache Jena Fuseki + MCP SPARQL Service
- **Persistencia**: MongoDB + RDF triples
- **Framework**: FastAPI (async/await)
- **Inference**: SWRL rules + Pellet reasoner
