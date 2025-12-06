# Forensic Compliance Agent

> **Sistema de análisis forense post-incidente de sistemas de IA con múltiples frameworks**

## Tabla de Contenidos

- [Overview](#overview)
- [Arquitectura](#arquitectura)
- [Quick Start](#quick-start)
  - [Opción 1: Ollama (Local, Gratis)](#opción-1-ollama-local-gratis)
  - [Opción 2: Anthropic Claude (Cloud)](#opción-2-anthropic-claude-cloud)
- [Instalación](#instalación)
- [Uso de la API](#uso-de-la-api)
- [Configuración](#configuración)
- [Features](#features)
- [Testing](#testing)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Desarrollo](#desarrollo)
- [Roadmap](#roadmap)

---

## Overview

El **Forensic Compliance Agent** realiza análisis automatizado post-incidente de sistemas de IA utilizando:

- **Extracción estructurada con LLM** (Claude Sonnet 4.5 o Llama 3.2)
- **Razonamiento semántico** (SPARQL) sobre la ontología del EU AI Act
- **Análisis multi-framework** (EU AI Act + ISO 42001 + NIST AI RMF)
- **Detección automática de gaps** de cumplimiento
- **Reportes listos para enforcement** con flags de revisión experta

### Capacidades Principales

✅ Extrae propiedades estructuradas de narrativas de incidentes
✅ Determina nivel de riesgo según EU AI Act (HighRisk, LimitedRisk, MinimalRisk)
✅ Identifica requisitos obligatorios basados en propósito, contexto y datos procesados
✅ Mapea a controles ISO 42001 (15 mappings)
✅ Mapea a funciones NIST AI RMF (16 mappings)
✅ Detecta gaps críticos de compliance
✅ Genera reportes forenses completos en markdown
✅ Scoring de confianza en la extracción
✅ **Soporte para modelos locales (Ollama) y cloud (Anthropic)**

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              FORENSIC COMPLIANCE AGENT                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ [1] Incident Extractor (LLM)                    │  │
│  │     • Claude Sonnet 4.5 o Llama 3.2             │  │
│  │     • Extrae propiedades estructuradas          │  │
│  │     • Confidence scoring (6 dimensiones)        │  │
│  └─────────────────────────────────────────────────┘  │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ [2] SPARQL Query Service                        │  │
│  │     • Consulta ontología EU AI Act v0.37.2     │  │
│  │     • Determina requisitos obligatorios         │  │
│  │     • Mapea a ISO 42001 + NIST AI RMF          │  │
│  └─────────────────────────────────────────────────┘  │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ [3] Multi-Framework Analysis Engine             │  │
│  │     • Análisis de compliance gaps               │  │
│  │     • Generación de reportes forenses           │  │
│  │     • Recomendaciones de enforcement            │  │
│  └─────────────────────────────────────────────────┘  │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ [4] FastAPI REST API                            │  │
│  │     • POST /forensic/analyze                    │  │
│  │     • GET /health                               │  │
│  │     • GET /forensic/stats                       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │                                  │
         ▼                                  ▼
   ┌──────────┐                      ┌──────────┐
   │  Ollama  │  or                  │  Fuseki  │
   │ (Llama)  │                      │ (SPARQL) │
   └──────────┘                      └──────────┘
```

---

## Quick Start

### Opción 1: Ollama (Local, Gratis)

**Ideal para:** Desarrollo, testing, privacidad, uso offline

**Ventajas:**
- ✅ **Gratis**: Sin costos de API
- ✅ **Privado**: Los datos no salen de tu máquina
- ✅ **Offline**: Funciona sin conexión a internet
- ✅ **Rápido setup**: Listo en ~5 minutos

**Requisitos:**
- Docker y Docker Compose
- 8GB RAM disponible
- ~2GB espacio en disco para el modelo

#### Paso 1: Levantar servicios

```bash
# Levantar Fuseki, Ollama y Forensic Agent
docker-compose up -d fuseki ollama forensic_agent

# Ver logs
docker-compose logs -f forensic_agent
```

#### Paso 2: Inicializar Ollama

Espera ~30 segundos a que Ollama esté listo, luego descarga el modelo:

```bash
# Hacer el script ejecutable (solo primera vez)
chmod +x forensic_agent/init_ollama.sh

# Descargar modelo Llama 3.2 (primera vez ~2GB)
bash forensic_agent/init_ollama.sh
```

La descarga puede tardar 2-5 minutos dependiendo de tu conexión.

#### Paso 3: Verificar instalación

```bash
# Health check
curl http://localhost:8002/health

# Respuesta esperada:
# {
#   "status": "healthy",
#   "llm_provider": "ollama",
#   "llm_model": "llama3.2",
#   "ontology_loaded": true
# }
```

#### Paso 4: Analizar incidente de prueba

```bash
curl -X POST http://localhost:8002/forensic/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Amazon Rekognition facial recognition system exhibited racial bias in 2019. The system misidentified women and people of color at much higher rates than white males. Error rates up to 34% for dark-skinned women. System marketed to law enforcement. Amazon placed moratorium on police use after criticism.",
    "source": "Test",
    "metadata": {"test": true}
  }'
```

El análisis debería completarse en 10-30 segundos (primera vez puede tardar más).

---

### Opción 2: Anthropic Claude (Cloud)

**Ideal para:** Producción, mayor precisión, menor latencia

**Ventajas:**
- ✅ **Alta calidad**: 90-95% precisión en extracción
- ✅ **Rápido**: 5-15 segundos por análisis
- ✅ **Confiable**: Infraestructura managed

**Requisitos:**
- API Key de Anthropic
- Conexión a internet

#### Configuración

```bash
# 1. Editar .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=tu_api_key_aqui

# 2. Levantar servicios
docker-compose up -d fuseki forensic_agent

# 3. Verificar
curl http://localhost:8002/health
```

---

## Instalación

### Desarrollo Local (sin Docker)

#### 1. Clonar y configurar

```bash
cd forensic_agent
cp .env.example .env
# Editar .env con tu configuración
```

#### 2. Instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Ejecutar

```bash
# Asegúrate de tener Fuseki corriendo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker (Recomendado)

```bash
# Build
docker build -t forensic-agent .

# Run
docker run -p 8000:8000 --env-file .env forensic-agent
```

### Docker Compose (Producción)

Ver [Quick Start](#quick-start) arriba.

---

## Uso de la API

### Endpoints

#### `GET /health`

Verificar estado del servicio.

```bash
curl http://localhost:8002/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "llm_model": "llama3.2",
  "ontology_loaded": true
}
```

#### `POST /forensic/analyze`

Analizar un incidente de IA.

**Request:**
```bash
curl -X POST http://localhost:8002/forensic/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Facebook DeepFace facial recognition system generated racially biased alt text, identifying Black individuals as primates in 2015. Incident discovered through user reports. Facebook response: apology + removed alt text generation feature. No systemic changes to training data or bias detection.",
    "source": "AIAAIC",
    "metadata": {
      "incident_id": "AIAAIC-2015-FB-001"
    }
  }'
```

**Response:**
```json
{
  "status": "COMPLETED",
  "analysis_timestamp": "2025-12-05T15:30:00Z",
  "extraction": {
    "system": {
      "system_name": "Facebook DeepFace",
      "system_type": "vision",
      "primary_purpose": "BiometricIdentification",
      "processes_data_types": ["BiometricData", "PersonalData"],
      "deployment_context": ["PublicSpaces", "HighVolume"],
      "is_automated_decision": true,
      "has_human_oversight": false,
      "model_scale": "Large",
      "organization": "Facebook (Meta)",
      "jurisdiction": "Global"
    },
    "incident": {
      "incident_type": "discrimination",
      "severity": "critical",
      "affected_populations": ["Black users", "Minorities"],
      "public_disclosure": true
    },
    "timeline": {
      "discovery_date": "2015",
      "resolution_date": "2015"
    },
    "response": {
      "acknowledged": true,
      "actions_taken": ["Removed alt text generation feature"],
      "public_apology": true,
      "compensation_provided": false
    },
    "confidence": {
      "system_type": 0.95,
      "purpose": 0.92,
      "data_types": 0.88,
      "incident_classification": 0.96,
      "affected_populations": 0.94,
      "timeline": 0.80,
      "overall": 0.91
    }
  },
  "eu_ai_act": {
    "risk_level": "HighRisk",
    "criteria": ["BiometricIdentificationCriterion", "PublicSpacesCriterion"],
    "total_requirements": 7,
    "requirements": [...]
  },
  "iso_42001": {
    "total_mapped": 5,
    "certification_gap_detected": true,
    "mappings": {...}
  },
  "nist_ai_rmf": {
    "total_mapped": 6,
    "jurisdiction_applicable": true,
    "voluntary_guidance_ignored": true,
    "mappings": {...}
  },
  "compliance_gaps": {
    "total_required": 7,
    "implemented": 2,
    "missing": 5,
    "compliance_ratio": 0.29,
    "missing_requirements": [...],
    "severity": "CRITICAL"
  },
  "report": "# FORENSIC COMPLIANCE AUDIT REPORT\n\n## EXECUTIVE SUMMARY\n...",
  "requires_expert_review": true
}
```

#### `GET /forensic/stats`

Estadísticas del servicio.

```bash
curl http://localhost:8002/forensic/stats
```

---

## Configuración

### Variables de Entorno

El archivo `.env` en la raíz del proyecto contiene:

```bash
# ============================================================================
# FORENSIC AGENT CONFIGURATION
# ============================================================================
FORENSIC_PORT=8002

# LLM Provider: "ollama" (local) or "anthropic" (cloud)
LLM_PROVIDER=ollama

# For Anthropic Claude (opcional):
ANTHROPIC_API_KEY=your_api_key_here

# For Ollama (local):
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Ontology paths (auto-configured with Docker)
ONTOLOGY_PATH=/ontologias/ontologia-v0.37.2.ttl
MAPPINGS_PATH=/ontologias/mappings
```

### Comparación de LLM Providers

| Característica | Ollama (Llama 3.2) | Anthropic Claude |
|----------------|-------------------|------------------|
| **Costo** | Gratis | ~$0.015/incidente |
| **Privacidad** | Total (local) | Datos van a API |
| **Velocidad** | 10-30s | 5-15s |
| **Calidad extracción** | 70-85% | 90-95% |
| **Requisitos** | 8GB RAM | API key + internet |
| **Offline** | ✅ Sí | ❌ No |
| **Ideal para** | Desarrollo, testing, privacidad | Producción, precisión |

### Modelos Ollama Recomendados

**llama3.2** (3B params) - **Recomendado**
- Buena calidad para tareas estructuradas
- Velocidad: ~15-25s por análisis
- RAM: 6-8GB

**llama3.2:1b** (1B params)
- Más rápido pero menor precisión
- Velocidad: ~8-15s por análisis
- RAM: 4-6GB

**mistral** (7B params)
- Mejor calidad, más lento
- Velocidad: ~30-60s por análisis
- RAM: 10-12GB

Para cambiar de modelo:

```bash
# Editar .env
OLLAMA_MODEL=mistral

# Descargar modelo
docker exec -it $(docker ps -q -f name=ollama) ollama pull mistral

# Reiniciar servicio
docker-compose restart forensic_agent
```

---

## Features

### 1. Incident Extraction (LLM)

**Tecnología:** Claude Sonnet 4.5 o Llama 3.2

**Extrae:**
- Propiedades del sistema (tipo, propósito, datos procesados, contexto de despliegue)
- Clasificación del incidente (tipo, severidad, poblaciones afectadas)
- Timeline (fechas de descubrimiento, impacto, resolución)
- Respuesta de la organización (acciones tomadas, mejoras sistémicas)

**Características:**
- Confidence scoring en 6 dimensiones
- Umbral de confianza: 60% (rechaza extracciones de baja calidad)
- Mapeo automático a términos de la ontología EU AI Act
- Temperatura baja (0.0/0.1) para determinismo

### 2. EU AI Act Compliance Analysis

**Consulta la ontología para determinar:**
- Criterios activados (ej. BiometricIdentificationCriterion)
- Requisitos obligatorios según propósito, contexto y datos
- Nivel de riesgo (HighRisk, LimitedRisk, MinimalRisk)

**Identifica gaps:**
- Compara requisitos obligatorios vs implementados
- Calcula ratio de compliance
- Determina severidad del gap (CRITICAL, HIGH, MEDIUM, LOW)

### 3. ISO 42001 Cross-Framework Analysis

**15 mappings bidireccionales** a controles ISO 42001:
- Secciones: 5.1, 8.1-8.7, 9.1-9.2, 10.1
- Confidence levels: High, Medium, Partial
- Detecta "ISO certified but EU non-compliant"
- Trail de evidencia para enforcement

### 4. NIST AI RMF Analysis

**16 mappings** a funciones NIST AI RMF:
- GOVERN, MAP, MEASURE, MANAGE
- Jurisdiction-aware (US/Global/EU)
- Detecta si voluntary guidance fue ignorada
- Análisis histórico (pre/post regulación)

### 5. Multi-Framework Report Generation

**Reporte forense completo** en markdown con:
- Executive summary
- System classification
- EU AI Act compliance analysis
- ISO 42001 cross-framework analysis
- NIST AI RMF analysis
- Root cause analysis
- Enforcement recommendations
- Organization response evaluation
- Expert review checklist

**Características:**
- Temporal awareness (pre/post EU AI Act)
- Siempre requiere expert review
- Formato enforcement-ready

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests unitarios
pytest tests/ -v

# Solo tests de extracción
pytest tests/test_extraction.py -v

# Solo tests de SPARQL
pytest tests/test_sparql.py -v

# Solo tests de análisis
pytest tests/test_analysis.py -v

# Con coverage
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

### Tests de Integración (requiere API key)

```bash
# Con Anthropic Claude
export ANTHROPIC_API_KEY='tu_key_aqui'
pytest tests/test_integration.py::TestLiveIntegration -v

# Con Ollama (requiere Ollama corriendo)
pytest tests/test_integration.py::TestIntegrationWithMocks -v
```

### Incidentes de Prueba

El proyecto incluye 5 incidentes reales de AIAAIC:

1. **Facebook DeepFace 2015** - Bias racial en reconocimiento facial
2. **Amazon Rekognition 2019** - Bias de género y raza
3. **COMPAS 2016** - Discriminación en predicción de reincidencia
4. **Clearview AI 2020** - Violación de privacidad masiva
5. **ChatGPT 2023** - Data breach con exposición de datos personales

Ubicación: [`tests/sample_incidents.py`](tests/sample_incidents.py)

---

## Performance

### Métricas (Phase 1 MVP)

| Métrica | Target | Actual |
|---------|--------|--------|
| Tiempo de análisis | <60s | 15-30s |
| Confidence extracción | >85% | 70-95% (depende del modelo) |
| Accuracy req. ID | >90% | Pendiente validación |
| API Availability | >99% | Operacional |

### Throughput

- **Sequential:** ~3-4 incidentes/minuto (Ollama)
- **Parallel:** ~10-15 incidentes/minuto (con async)
- **Claude:** ~4-6 incidentes/minuto

### Costos

**Ollama (local):**
- Costo por incidente: $0
- 100 incidentes: $0
- 1000 incidentes: $0
- Único costo: Hardware (8GB RAM recomendado)

**Anthropic Claude:**
- Costo por incidente: ~$0.015 (4K input, 2K output)
- 100 incidentes: ~$1.50
- 1000 incidentes: ~$15.00

---

## Troubleshooting

### Ollama: "Cannot connect to Ollama"

```bash
# Verificar que Ollama está corriendo
docker-compose ps

# Ver logs
docker-compose logs ollama

# Reiniciar
docker-compose restart ollama
```

### Ollama: "Model not found"

```bash
# Listar modelos instalados
curl http://localhost:11434/api/tags

# Reinstalar modelo
bash forensic_agent/init_ollama.sh
```

### Ollama: Respuestas de baja calidad

- Llama 3.2 puede tener menor precisión que Claude (~70-85% vs 90-95%)
- Considera usar `mistral` para mejor calidad
- Para producción, usa Anthropic Claude

### Ollama: Muy lento

- Asegúrate de tener suficiente RAM (8GB+)
- Prueba modelo más pequeño: `llama3.2:1b`
- Cierra otras aplicaciones para liberar RAM

### Claude: API errors

```bash
# Verificar API key
echo $ANTHROPIC_API_KEY

# Verificar límites de rate
# Claude Sonnet 4.5: 4,000 requests/min
```

### Fuseki: Connection refused

```bash
# Verificar Fuseki está corriendo
docker-compose ps fuseki

# Reiniciar Fuseki
docker-compose restart fuseki

# Ver logs
docker-compose logs fuseki
```

---

## Desarrollo

### Estructura del Proyecto

```
forensic_agent/
├── app/
│   ├── main.py                     # FastAPI application
│   ├── models/
│   │   ├── incident.py             # Extraction models (Pydantic)
│   │   └── forensic_report.py      # Analysis result models
│   ├── services/
│   │   ├── incident_extractor.py   # LLM extraction (Claude/Llama)
│   │   ├── sparql_queries.py       # SPARQL query service
│   │   └── analysis_engine.py      # Multi-framework analysis
│   └── utils/
├── tests/
│   ├── test_extraction.py          # Unit tests: extraction
│   ├── test_sparql.py              # Unit tests: SPARQL
│   ├── test_analysis.py            # Unit tests: analysis
│   ├── test_integration.py         # Integration tests
│   └── sample_incidents.py         # 5 real incidents from AIAAIC
├── init_ollama.sh                  # Script para inicializar Ollama
├── Dockerfile                      # Container definition
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
└── README.md                       # This file
```

### Code Quality

```bash
# Format code
black app/

# Type checking
mypy app/

# Linting
pylint app/

# Security scan
bandit -r app/
```

### Agregar Nuevos Mappings

Para agregar mappings a otros frameworks (ej. GDPR, ISO 27001):

1. Crear archivo TTL en `/ontologias/mappings/`
2. Agregar método de query en `sparql_queries.py`
3. Integrar en `analysis_engine.py`
4. Actualizar reporte en `_generate_report()`
5. Agregar tests

---

## Roadmap

### ✅ Phase 1: MVP (Completado)
- [x] Extracción con LLM (Claude + Ollama)
- [x] SPARQL queries a ontología EU AI Act
- [x] Mappings ISO 42001 (15 mappings)
- [x] Mappings NIST AI RMF (16 mappings)
- [x] Multi-framework analysis engine
- [x] FastAPI REST API
- [x] Test suite completo
- [x] Docker + Docker Compose
- [x] Documentación completa

### 🔄 Phase 2: Multi-Framework Integration (En progreso)
- [ ] Mappings adicionales (GDPR, ISO 27001)
- [ ] Historical incident database (AIAAIC)
- [ ] Batch processing API
- [ ] Similar systems detection

### 📋 Phase 3: Expert Review System
- [ ] Expert review database schema
- [ ] Review queue management API
- [ ] Web UI para expert review
- [ ] Approval/rejection workflow
- [ ] Audit trail

### 🚀 Phase 4: Production Readiness
- [ ] Rate limiting y caching
- [ ] Monitoring y logging (Prometheus/Grafana)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Multi-language support (ES, FR, DE)
- [ ] Fine-tuned extraction model

---

## Integración

### Con Backend Principal

```python
import httpx

async def analyze_system_incident(incident_narrative: str):
    """Analyze incident using forensic agent"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://forensic_agent:8000/forensic/analyze",
            json={"narrative": incident_narrative}
        )
        return response.json()
```

### Con Base de Datos AIAAIC

```python
# Pseudocode para batch processing
incidents = fetch_from_aiaaic(limit=100)
results = await batch_analyze(incidents)
store_results(results)
generate_trends_report(results)
```

---

## Recursos

- **Arquitectura detallada:** [`/docs/FORENSIC_AGENT_ARCHITECTURE.md`](../docs/FORENSIC_AGENT_ARCHITECTURE.md)
- **Ontología EU AI Act:** [`/ontologias/ontologia-v0.37.2.ttl`](../ontologias/versions/0.37.2/)
- **ISO 42001 Mappings:** [`/ontologias/mappings/iso-42001-mappings.ttl`](../ontologias/mappings/)
- **NIST AI RMF Mappings:** [`/ontologias/mappings/nist-ai-rmf-mappings.ttl`](../ontologias/mappings/)
- **Ollama Docs:** [https://ollama.ai/](https://ollama.ai/)
- **Anthropic API:** [https://docs.anthropic.com/](https://docs.anthropic.com/)

---

## License

Part of the EU AI Act Unified Ontology project.
Licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

## Support

**Issues:** [GitHub Issues](https://github.com/your-org/ai-act-ontology/issues)
**Logs:** `docker-compose logs forensic_agent`
**Health Check:** `curl http://localhost:8002/health`

---

**Version:** 1.0.0 (Phase 1 MVP)
**Status:** ✅ Operacional (Testing Phase)
**Last Updated:** 2025-12-05
**LLM Support:** Anthropic Claude Sonnet 4.5 + Ollama (Llama 3.2, Mistral)
