# Forensic Compliance Agent

> **Sistema de análisis forense post-incidente de sistemas de IA con múltiples frameworks regulatorios**

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/EU%20AI%20Act-Compliant-green.svg" alt="EU AI Act"/>
  <img src="https://img.shields.io/badge/DPV-2.2-orange.svg" alt="DPV 2.2"/>
</p>

## Tabla de Contenidos

- [Overview](#overview)
- [Arquitectura](#arquitectura)
- [Evidence Planner (Nuevo v1.1)](#evidence-planner-nuevo-v11)
- [Flujo de Inferencia](#flujo-de-inferencia)
- [Quick Start](#quick-start)
- [Instalación](#instalación)
- [Uso de la API](#uso-de-la-api)
- [Configuración](#configuración)
- [Features](#features)
- [Testing](#testing)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Desarrollo](#desarrollo)

---

## Overview

El **Forensic Compliance Agent** realiza análisis automatizado post-incidente de sistemas de IA utilizando:

- **Extracción estructurada con LLM** (Ollama + Llama 3.2)
- **Razonamiento semántico** (SPARQL) sobre la ontología del EU AI Act v0.37.4
- **Análisis multi-framework** (EU AI Act + ISO 42001 + NIST AI RMF + DPV 2.2)
- **Detección automática de gaps** de cumplimiento
- **Evidence Planner** con integración W3C DPV para generación de planes de evidencia
- **Persistencia dual** (MongoDB + Apache Jena Fuseki)

### Capacidades Principales

| Capacidad | Descripción |
|-----------|-------------|
| **Extracción LLM** | Extrae propiedades estructuradas de narrativas de incidentes |
| **Clasificación de Riesgo** | Determina nivel de riesgo según EU AI Act (HighRisk, LimitedRisk, MinimalRisk) |
| **Requisitos Obligatorios** | Identifica requisitos basados en propósito, contexto y datos procesados |
| **ISO 42001** | Mapea a 15 controles de certificación |
| **NIST AI RMF** | Mapea a 18 funciones del framework |
| **DPV 2.2** | Integración con W3C Data Privacy Vocabulary para medidas de compliance |
| **Evidence Planner** | Genera planes de evidencia con 14 requisitos y ~40 items de evidencia |
| **Gap Detection** | Detecta gaps críticos de compliance |
| **Reportes Forenses** | Genera reportes completos en markdown |
| **Persistencia** | Guarda análisis en MongoDB y RDF en Fuseki |

---

## Arquitectura

```mermaid
flowchart TB
    subgraph Frontend["Frontend :5173"]
        FA[ForensicAgentPage<br/>AIAAIC Browser]
    end

    subgraph Agent["Forensic Agent :8002"]
        IE[Incident Extractor<br/>LLM + Ollama]
        AE[Analysis Engine<br/>Multi-Framework]
        EP[Evidence Planner<br/>DPV Integration]
        MC[MCP Client<br/>SPARQL Tools]
        PS[Persistence Service<br/>MongoDB + Fuseki]
    end

    subgraph Data["Data Layer"]
        MG[(MongoDB :27017<br/>Documents)]
        FK[(Fuseki :3030<br/>RDF/SPARQL)]
    end

    subgraph Services["External Services"]
        OL[Ollama :11434<br/>Llama 3.2]
        MCP[MCP Server :8080<br/>FastMCP 2.0]
    end

    FA -->|POST /forensic/analyze| IE
    IE -->|Extract| OL
    IE --> AE
    AE --> EP
    AE --> MC
    MC -->|MCP Protocol| MCP
    MCP -->|SPARQL| FK
    AE --> PS
    PS --> MG
    PS -->|RDF Triples| FK

    style Frontend fill:#3b82f6,color:#fff
    style Agent fill:#8b5cf6,color:#fff
    style Data fill:#f59e0b,color:#fff
    style Services fill:#10b981,color:#fff
```

### Componentes

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| **Forensic Agent** | 8002 | API REST FastAPI |
| **MCP Server** | 8080 | Model Context Protocol (SPARQL tools) |
| **Ollama** | 11434 | Runtime LLM local |
| **MongoDB** | 27017 | Persistencia de documentos |
| **Fuseki** | 3030 | Almacenamiento RDF/SPARQL |

---

## Evidence Planner (Nuevo v1.1)

El **Evidence Planner** es un nuevo servicio que genera planes de evidencia para remediar gaps de compliance identificados durante el análisis forense. Utiliza mappings basados en el **W3C Data Privacy Vocabulary (DPV) 2.2**.

### ¿Qué es DPV?

El [Data Privacy Vocabulary (DPV)](https://w3c.github.io/dpv/) es una especificación W3C que proporciona términos para describir:
- Actividades de procesamiento de datos personales
- Medidas técnicas y organizativas
- Bases legales y propósitos
- Riesgos y evaluaciones de impacto

### Extensiones DPV Utilizadas

| Extensión | Propósito | Uso en SERAMIS |
|-----------|-----------|----------------|
| **dpv:core** | Medidas técnicas y organizativas | Mapeo de requisitos a medidas |
| **dpv:ai** | Sistemas de IA, capacidades, riesgos | Clasificación de sistemas |
| **dpv:risk** | Gestión de riesgos | Evaluación de gaps |
| **dpv:legal/eu/aiact** | Conceptos específicos AI Act | Equivalencias semánticas |

### Tipos de Evidencia

El Evidence Planner define 6 tipos de evidencia:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `PolicyEvidence` | Políticas y procedimientos | Human Oversight Policy |
| `TechnicalEvidence` | Documentación técnica | Model Card, System Architecture |
| `AuditEvidence` | Logs, tests, auditorías | Bias Audit Report |
| `TrainingEvidence` | Registros de formación | Operator Training Records |
| `AssessmentEvidence` | Evaluaciones de impacto | FRIA Report, DPIA |
| `ContractualEvidence` | Contratos y acuerdos | Data Processing Agreement |

### Catálogo de Requisitos

El servicio mapea **14 requisitos del EU AI Act** a **~40 items de evidencia**:

| Requisito | Artículo | Items de Evidencia |
|-----------|----------|-------------------|
| HumanOversightRequirement | Art. 14 | 4 items |
| TransparencyRequirement | Art. 13 | 3 items |
| DataGovernanceRequirement | Art. 10 | 3 items |
| TechnicalDocumentationRequirement | Art. 11 | 4 items |
| BiasAssessmentRequirement | Art. 10 | 3 items |
| FundamentalRightsAssessmentRequirement | Art. 27 | 3 items |
| RiskManagementRequirement | Art. 9 | 4 items |
| ... | ... | ... |

### Ejemplo de Uso

```bash
# Generar plan de evidencia desde gaps
curl -X POST http://localhost:8002/forensic/evidence-plan \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "Facial Recognition System",
    "risk_level": "HighRisk",
    "missing_requirements": [
      "http://ai-act.eu/ai#HumanOversightRequirement",
      "http://ai-act.eu/ai#FundamentalRightsAssessmentRequirement"
    ],
    "critical_gaps": []
  }'
```

**Response:**
```json
{
  "plan_id": "EP-20251214-abc123",
  "system_name": "Facial Recognition System",
  "summary": {
    "total_requirements": 2,
    "total_evidence_items": 7,
    "by_priority": {"critical": 3, "high": 2, "medium": 2},
    "by_evidence_type": {"PolicyEvidence": 2, "TechnicalEvidence": 3, "AuditEvidence": 2}
  },
  "requirement_plans": [
    {
      "requirement_uri": "http://ai-act.eu/ai#HumanOversightRequirement",
      "requirement_label": "Human Oversight Requirement",
      "article_reference": "Article 14",
      "priority": "critical",
      "dpv_measures": ["dpv:HumanInvolvement", "dpv:Review"],
      "evidence_items": [...]
    }
  ],
  "recommendations": [
    "Prioritize critical evidence items for high-risk system",
    "Establish document control procedures"
  ]
}
```

### Análisis Combinado

Para obtener análisis forense + plan de evidencia en una sola llamada:

```bash
curl -X POST http://localhost:8002/forensic/analyze-with-evidence-plan \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Sistema de reconocimiento facial utilizado por la policía...",
    "source": "AIAAIC"
  }'
```

---

## Flujo de Inferencia

### Secuencia de Análisis Completo

```mermaid
sequenceDiagram
    participant U as Frontend
    participant API as FastAPI :8002
    participant IE as IncidentExtractor
    participant LLM as Ollama/Llama3.2
    participant AE as AnalysisEngine
    participant MCP as MCP Server :8080
    participant FK as Fuseki :3030
    participant PS as Persistence
    participant MG as MongoDB

    U->>API: POST /forensic/analyze
    Note over API: {narrative, source, metadata}

    API->>IE: extract(narrative)
    IE->>LLM: Prompt estructurado
    LLM-->>IE: JSON con propiedades extraídas
    IE-->>API: SystemExtraction + confidence

    API->>AE: analyze(extraction)

    par EU AI Act Analysis
        AE->>MCP: call_tool(query_ontology)
        MCP->>FK: SPARQL: criterios por propósito
        FK-->>MCP: Criterios activados
        MCP-->>AE: Results
    and ISO 42001 Analysis
        AE->>MCP: call_tool(query_iso_mappings)
        MCP->>FK: SPARQL: mappings ISO 42001
        FK-->>MCP: 15 controles mapeados
        MCP-->>AE: Results
    and NIST AI RMF Analysis
        AE->>MCP: call_tool(query_nist_mappings)
        MCP->>FK: SPARQL: mappings NIST
        FK-->>MCP: 18 funciones mapeadas
        MCP-->>AE: Results
    end

    AE->>AE: Calcular gaps de compliance
    AE->>AE: Generar reporte forense
    AE-->>API: ForensicAnalysisResult

    API->>PS: persist(result)
    PS->>MG: Guardar documento JSON
    PS->>FK: INSERT RDF triples

    API-->>U: Response completa
```

### Flujo de Extracción LLM

```mermaid
sequenceDiagram
    participant IE as IncidentExtractor
    participant PP as PromptBuilder
    participant LLM as Ollama API
    participant VP as Validator

    IE->>PP: build_prompt(narrative)
    PP->>PP: Construir system prompt
    PP->>PP: Añadir ontology context
    PP->>PP: Definir JSON schema
    PP-->>IE: Prompt completo

    IE->>LLM: POST /api/generate
    Note over LLM: model: llama3.2<br/>temperature: 0.1<br/>format: json

    LLM-->>IE: Raw JSON response

    IE->>VP: validate(response)
    VP->>VP: Parse JSON
    VP->>VP: Validar campos requeridos
    VP->>VP: Normalizar valores ontología
    VP->>VP: Calcular confidence scores

    alt Validación exitosa
        VP-->>IE: SystemExtraction válido
    else Validación fallida
        VP-->>IE: Error + retry hint
        IE->>LLM: Retry con prompt mejorado
    end
```

### Flujo de Clasificación de Riesgo

```mermaid
sequenceDiagram
    participant AE as AnalysisEngine
    participant MCP as MCP Server :8080
    participant FK as Fuseki :3030
    participant CL as Classifier

    AE->>MCP: call_tool(determine_risk_level)
    MCP->>FK: SPARQL: propósitos del sistema
    FK-->>MCP: [BiometricIdentification, ...]
    MCP-->>AE: purposes

    AE->>MCP: call_tool(query_ontology)
    MCP->>FK: SPARQL: contextos de despliegue
    FK-->>MCP: [LawEnforcement, PublicSpaces, ...]
    MCP-->>AE: contexts

    AE->>CL: classify(purposes, contexts, data_types)

    CL->>CL: Evaluar criterios Anexo III
    Note over CL: 8 categorías de alto riesgo

    CL->>CL: Unión de criterios activados

    alt Criterios HighRisk activados
        CL-->>AE: HighRisk + criterios[]
    else Solo transparencia requerida
        CL-->>AE: LimitedRisk
    else Sin criterios especiales
        CL-->>AE: MinimalRisk
    end

    AE->>MCP: call_tool(get_requirements_for_system)
    MCP->>FK: SPARQL: requisitos por nivel
    FK-->>MCP: Requisitos obligatorios
    MCP-->>AE: requirements[]
```

### Flujo de Persistencia Dual

```mermaid
sequenceDiagram
    participant PS as PersistenceService
    participant MG as MongoDB
    participant FK as Fuseki
    participant RDF as RDFBuilder

    PS->>MG: Insert forensic_systems
    Note over MG: Documento completo JSON<br/>con análisis y metadatos
    MG-->>PS: ObjectId confirmado

    PS->>RDF: build_triples(analysis)
    RDF->>RDF: Crear URN sistema
    RDF->>RDF: Añadir propiedades
    RDF->>RDF: Añadir clasificación
    RDF->>RDF: Añadir requisitos
    RDF-->>PS: Turtle string

    PS->>FK: POST /ai-act/data
    Note over FK: INSERT DATA { triples }
    FK-->>PS: Success

    PS-->>PS: Sync confirmado
```

---

## Quick Start

### Requisitos

- Docker y Docker Compose
- 8GB RAM disponible
- ~2GB espacio en disco para el modelo LLM

### Paso 1: Levantar servicios

```bash
# Levantar Fuseki, Ollama y Forensic Agent
docker-compose up -d fuseki ollama forensic_agent

# Ver logs
docker-compose logs -f forensic_agent
```

### Paso 2: Inicializar Ollama

Espera ~30 segundos a que Ollama esté listo, luego descarga el modelo:

```bash
# Hacer el script ejecutable (solo primera vez)
chmod +x forensic_agent/init_ollama.sh

# Descargar modelo Llama 3.2 (~2GB)
bash forensic_agent/init_ollama.sh
```

### Paso 3: Verificar instalación

```bash
curl http://localhost:8002/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "llm_model": "llama3.2",
  "fuseki_connected": true,
  "mongodb_connected": true
}
```

### Paso 4: Analizar incidente de prueba

```bash
curl -X POST http://localhost:8002/forensic/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Amazon Rekognition facial recognition system exhibited racial bias. The system misidentified women and people of color at higher rates. System marketed to law enforcement agencies.",
    "source": "AIAAIC Repository",
    "metadata": {"aiaaic_id": "AIAAIC0042"}
  }'
```

---

## Instalación

### Docker Compose (Recomendado)

```bash
# Build y run
docker-compose up -d fuseki ollama forensic_agent

# Inicializar modelo LLM
bash forensic_agent/init_ollama.sh
```

### Desarrollo Local

```bash
cd forensic_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Asegúrate de tener Fuseki y Ollama corriendo
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## Uso de la API

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| POST | `/forensic/analyze` | Analizar incidente |
| POST | `/forensic/analyze-with-evidence-plan` | Analizar + generar plan de evidencias |
| POST | `/forensic/evidence-plan` | Generar plan de evidencias desde gaps |
| GET | `/forensic/systems` | Listar sistemas analizados |
| GET | `/forensic/systems/{urn}` | Obtener análisis específico |
| DELETE | `/forensic/systems/{urn}` | Eliminar análisis |
| GET | `/forensic/stats` | Estadísticas del servicio |

### POST /forensic/analyze

**Request:**
```json
{
  "narrative": "Descripción del incidente de IA...",
  "source": "AIAAIC Repository",
  "metadata": {
    "aiaaic_id": "AIAAIC0042",
    "headline": "Título del incidente"
  }
}
```

**Response:**
```json
{
  "status": "COMPLETED",
  "urn": "urn:forensic:uuid-here",
  "extraction": {
    "system_name": "Amazon Rekognition",
    "system_type": "vision",
    "primary_purpose": "BiometricIdentification",
    "deployment_context": ["LawEnforcement"],
    "processes_data_types": ["BiometricData"],
    "confidence": {
      "overall": 0.87
    }
  },
  "eu_ai_act": {
    "risk_level": "HighRisk",
    "criteria": ["BiometricIdentificationCriterion"],
    "requirements": [...]
  },
  "iso_42001": {
    "total_mapped": 15,
    "mappings": [...]
  },
  "nist_ai_rmf": {
    "total_mapped": 18,
    "mappings": [...]
  },
  "compliance_gaps": {
    "total_required": 7,
    "implemented": 2,
    "missing": 5,
    "compliance_ratio": 0.29,
    "severity": "CRITICAL"
  }
}
```

---

## Configuración

### Variables de Entorno

```bash
# Puerto del servicio
FORENSIC_PORT=8002

# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Persistencia
MONGODB_URI=mongodb://mongodb:27017
FUSEKI_ENDPOINT=http://fuseki:3030

# Ontología
ONTOLOGY_PATH=/ontologias/versions/0.37.2/ontologia-v0.37.2.ttl
MAPPINGS_PATH=/ontologias/mappings
```

### Modelos Ollama Disponibles

| Modelo | Parámetros | RAM | Velocidad | Calidad |
|--------|------------|-----|-----------|---------|
| **llama3.2** | 3B | 6-8GB | 15-25s | Recomendado |
| llama3.2:1b | 1B | 4-6GB | 8-15s | Básica |
| mistral | 7B | 10-12GB | 30-60s | Alta |

---

## Features

### 1. Extracción Estructurada

- Propiedades del sistema (tipo, propósito, datos, contexto)
- Clasificación del incidente (tipo, severidad, poblaciones afectadas)
- Timeline (descubrimiento, impacto, resolución)
- Respuesta organizacional (acciones, mejoras)
- Confidence scoring en 6 dimensiones

### 2. Análisis EU AI Act

- Clasificación de riesgo automática
- Identificación de criterios Anexo III
- Requisitos obligatorios por nivel de riesgo
- Detección de gaps de compliance

### 3. Cross-Framework Analysis

**ISO 42001 (15 mappings):**
- Secciones 5.1, 8.1-8.7, 9.1-9.2, 10.1
- Confidence levels: High, Medium, Partial

**NIST AI RMF (18 mappings):**
- Funciones: GOVERN, MAP, MEASURE, MANAGE
- Jurisdiction-aware (US/Global/EU)

**DPV 2.2 (14 mappings):**
- Medidas técnicas y organizativas
- 6 tipos de evidencia estandarizados
- Integración con dpv:ai y dpv:legal/eu/aiact

### 4. Evidence Planner

- Genera planes de evidencia basados en gaps de compliance
- 14 requisitos mapeados a ~40 items de evidencia
- Priorización automática (critical/high/medium/low)
- Recomendaciones contextuales por nivel de riesgo
- Output en JSON o Markdown

### 5. Persistencia Dual

- **MongoDB:** Documentos JSON completos
- **Fuseki:** Triples RDF para consultas SPARQL
- Sincronización automática

---

## Performance

### Métricas

| Métrica | Valor |
|---------|-------|
| Tiempo de análisis | 15-30s |
| Confidence extracción | 70-85% |
| Throughput | 3-4 incidentes/min |
| API Availability | >99% |

### Costos

- **Ollama (local):** $0 por incidente
- Único costo: Hardware (8GB RAM recomendado)

---

## Troubleshooting

### Ollama no conecta

```bash
# Verificar estado
docker-compose ps ollama
docker-compose logs ollama

# Reiniciar
docker-compose restart ollama
```

### Modelo no encontrado

```bash
# Listar modelos
curl http://localhost:11434/api/tags

# Reinstalar
bash forensic_agent/init_ollama.sh
```

### Fuseki no responde

```bash
docker-compose restart fuseki
docker-compose logs fuseki
```

---

## Desarrollo

### Estructura del Proyecto

```
forensic_agent/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── models/
│   │   ├── incident.py            # Modelos de extracción
│   │   └── forensic_report.py     # Modelos de análisis
│   └── services/
│       ├── __init__.py            # Exports de servicios
│       ├── incident_extractor.py  # Extracción LLM
│       ├── analysis_engine.py     # Análisis multi-framework
│       ├── evidence_planner.py    # Evidence Planner (DPV) ← NUEVO
│       ├── sparql_queries.py      # Consultas SPARQL via MCP
│       └── persistence.py         # MongoDB + Fuseki
├── tests/
├── init_ollama.sh                 # Script inicialización
├── Dockerfile
├── requirements.txt
└── README.md
```

### Testing

```bash
# Tests unitarios
pytest tests/ -v

# Con coverage
pytest tests/ -v --cov=app --cov-report=html
```

---

## Recursos

- **Ontología EU AI Act:** `/ontologias/versions/0.37.4/`
- **ISO 42001 Mappings:** `/ontologias/mappings/iso-42001-mappings.ttl`
- **NIST AI RMF Mappings:** `/ontologias/mappings/nist-ai-rmf-mappings.ttl`
- **DPV Integration:** `/ontologias/mappings/dpv-integration.ttl`
- **W3C DPV 2.2:** https://w3c.github.io/dpv/
- **Ollama Documentation:** https://ollama.ai/

---

## Agradecimientos

Este proyecto utiliza datos del **AI, Algorithmic, and Automation Incidents and Controversies (AIAAIC) Repository**, una base de datos independiente y de acceso abierto que documenta incidentes relacionados con sistemas de IA a nivel mundial.

Agradecemos a **Charlie Pownall** y al equipo de AIAAIC por su trabajo en la recopilación y mantenimiento de este recurso invaluable para la investigación y el análisis de incidentes de IA.

- **AIAAIC Repository:** https://www.aiaaic.org/aiaaic-repository
- **GitHub:** https://github.com/AIAAIC/AIAAIC-Repository

Este proyecto ha sido desarrollado con la asistencia de **Claude Sonnet** (Anthropic), utilizado como herramienta de desarrollo para la generación de código y documentación.

---

## License

Part of the SERAMIS project - EU AI Act Unified Ontology.
Licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

**Version:** 1.1.0
**Status:** Operacional
**Last Updated:** Diciembre 2025

### Changelog v1.1.0

- Integración W3C Data Privacy Vocabulary (DPV) 2.2
- Nuevo servicio Evidence Planner con 14 requisitos y ~40 items de evidencia
- Nuevos endpoints: `/forensic/evidence-plan`, `/forensic/analyze-with-evidence-plan`
- Fix clasificación GPAI (GenerativeAI → HighRisk)
- Actualizada ontología a v0.37.4
