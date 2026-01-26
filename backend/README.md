# SERAMIS Backend

API REST para SERAMIS (Semantic Regulation Intelligence System) - Plataforma de cumplimiento EU AI Act.

## Descripción

Backend FastAPI que proporciona:
- Gestión de sistemas de IA con persistencia dual (MongoDB + Fuseki RDF)
- Vocabularios semánticos extraídos de la ontología EU AI Act
- Derivación automática de clasificaciones y requisitos
- Integración con el servicio de razonamiento SWRL
- Validación SHACL de sistemas
- Servicio de datos AIAAIC

## Estructura del Proyecto

```
backend/
├── main.py                    # Aplicación FastAPI principal
├── db.py                      # Conexión MongoDB (Motor async)
├── fuseki.py                  # Cliente Fuseki para inserción RDF
├── derivation.py              # Lógica de derivación de clasificaciones
├── swrl_rules.py              # Definición de reglas SWRL
├── models/
│   └── system.py              # Modelo Pydantic IntelligentSystem
├── routers/
│   ├── systems.py             # CRUD de sistemas (/systems)
│   ├── systems_fuseki.py      # Consultas Fuseki (/systems/fuseki)
│   └── reasoning.py           # Razonamiento simbólico (/reasoning)
├── schema/
│   └── json-ld-context.json   # Contexto JSON-LD
└── requirements.txt           # Dependencias Python
```

## Endpoints Principales

### Sistemas de IA

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/systems` | Lista todos los sistemas registrados |
| `POST` | `/systems` | Crea nuevo sistema de IA |
| `GET` | `/systems/{urn}` | Obtiene sistema por URN |
| `DELETE` | `/systems/{urn}` | Elimina sistema |
| `POST` | `/systems/derive-classifications` | Deriva clasificaciones de riesgo |
| `GET` | `/systems/{urn}/evidence-plan` | Obtiene Evidence Plan DPV |
| `POST` | `/systems/{urn}/generate-evidence-plan` | Genera Evidence Plan |

### Fuseki (RDF)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/systems/fuseki/{urn}` | Obtiene sistema desde Fuseki (JSON-LD) |

### Razonamiento

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/reasoning/reason` | Ejecuta razonamiento SWRL sobre sistema |
| `GET` | `/reasoning/swrl-rules` | Lista reglas SWRL disponibles |
| `POST` | `/reasoning/validate-shacl` | Valida sistema con SHACL shapes |

### Vocabularios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/vocab/purposes` | Propósitos de sistema (hasPurpose) |
| `GET` | `/vocab/contexts` | Contextos de despliegue |
| `GET` | `/vocab/risks` | Niveles de riesgo |
| `GET` | `/vocab/algorithmtypes` | Tipos de algoritmo |
| `GET` | `/vocab/training_origins` | Orígenes de datos de entrenamiento |
| `GET` | `/vocab/system_capability_criteria` | Criterios de capacidad |
| `GET` | `/vocab/gpai` | Clasificaciones GPAI |
| `GET` | `/vocab/compliance` | Requisitos de cumplimiento |
| `GET` | `/vocab/technical` | Requisitos técnicos |
| `GET` | `/vocab/security` | Requisitos de seguridad |
| `GET` | `/vocab/prohibited_practices` | Prácticas prohibidas Art. 5 |
| `GET` | `/vocab/legal_exceptions` | Excepciones legales Art. 5.2 |
| `GET` | `/vocab/modelscales` | Escalas de modelo |
| `GET` | `/vocab/capabilities` | Capacidades del sistema |

### Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/healthz` | Health check |
| `GET` | `/aiaaic/incidents` | Datos CSV de incidentes AIAAIC |

## Modelo de Datos

### IntelligentSystem

```python
class IntelligentSystem(BaseModel):
    hasName: str                              # Nombre del sistema
    hasPurpose: List[str]                     # Propósitos (ej: ["ai:BiometricIdentification"])
    hasDeploymentContext: List[str]           # Contextos de despliegue
    hasTrainingDataOrigin: List[str]          # Orígenes de datos
    hasSystemCapabilityCriteria: List[str]    # Criterios de capacidad
    hasAlgorithmType: List[str]               # Tipos de algoritmo
    hasModelScale: Optional[List[str]]        # Escala de modelo
    hasCapability: Optional[List[str]]        # Capacidades
    hasVersion: str                           # Versión
    hasUrn: Optional[str]                     # URN generado
    hasFLOPS: Optional[float]                 # FLOPS (opcional)

    # Article 5: Prohibited Practices
    hasProhibitedPractice: Optional[List[str]]  # Prácticas prohibidas
    hasLegalException: Optional[List[str]]       # Excepciones legales
    hasJudicialAuthorization: Optional[bool]     # Autorización judicial
```

## Stack Tecnológico

| Tecnología | Uso |
|------------|-----|
| **FastAPI 0.124** | Framework API REST |
| **Uvicorn** | Servidor ASGI |
| **Motor** | Driver async MongoDB |
| **RDFLib** | Manipulación RDF/OWL |
| **PyLD** | Procesamiento JSON-LD |
| **PySHACL** | Validación SHACL |
| **HTTPX** | Cliente HTTP async |
| **Requests** | Cliente HTTP sync |

## Configuración

### Variables de Entorno

```bash
# Ontología
ONTOLOGY_PATH=/ontologias/versions/0.41.0/ontologia-v0.41.0.ttl

# Fuseki
FUSEKI_ENDPOINT=http://fuseki:3030
FUSEKI_DATASET=ds
FUSEKI_GRAPH_DATA=http://ai-act.eu/ontology/data
FUSEKI_USER=admin
FUSEKI_PASSWORD=admin

# MongoDB
MONGODB_URL=mongodb://mongo:27017

# Servicios externos
REASONER_SERVICE_URL=http://reasoner:8001
FORENSIC_AGENT_URL=http://forensic_agent:8002

# SHACL
SHACL_SHAPES_PATH=/ontologias/shacl/ai-act-shapes.ttl
ENABLE_SHACL_VALIDATION=true

# JSON-LD
JSONLD_CONTEXT_PATH=/ontologias/json-ld-context.json
```

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

El backend se ejecuta en contenedor Docker:

```yaml
backend:
  build:
    context: ./backend
  ports:
    - "8000:8000"
  environment:
    - ONTOLOGY_PATH=/ontologias/versions/0.41.0/ontologia-v0.41.0.ttl
    - FUSEKI_ENDPOINT=http://fuseki:3030
  volumes:
    - ./ontologias:/ontologias:ro
    - ./data:/data:ro
  depends_on:
    - mongo
    - fuseki
```

## Persistencia Dual

Los sistemas se persisten en dos almacenes:

1. **MongoDB** (`ai_act_db.systems`)
   - Almacenamiento principal JSON
   - Índice único en `hasUrn`
   - Búsquedas rápidas

2. **Apache Jena Fuseki** (grafo `http://ai-act.eu/ontology/data`)
   - Almacenamiento RDF/Turtle
   - Consultas SPARQL
   - Razonamiento semántico

## Derivación de Clasificaciones

El endpoint `/systems/derive-classifications` implementa lógica de derivación:

```
Input: hasPurpose, hasDeploymentContext, hasTrainingDataOrigin, hasAlgorithmType
         ↓
    [Análisis de ontología]
         ↓
Output: hasCriteria, hasComplianceRequirement, hasRiskLevel, hasGPAIClassification
```

### Ejemplo

```bash
curl -X POST http://localhost:8000/systems/derive-classifications \
  -H "Content-Type: application/json" \
  -d '{
    "hasPurpose": ["ai:BiometricIdentification"],
    "hasDeploymentContext": ["ai:LawEnforcement"],
    "hasTrainingDataOrigin": ["ai:ExternalDataset"]
  }'
```

**Respuesta:**
```json
{
  "hasCriteria": ["ai:BiometricIdentificationCriterion", "ai:LawEnforcementCriterion"],
  "hasComplianceRequirement": ["ai:HumanOversightRequirement", "ai:DataGovernanceRequirement"],
  "hasRiskLevel": "ai:HighRisk",
  "hasGPAIClassification": []
}
```

## Integración con Servicios

```
Backend (8000) ────► MongoDB (27017)
                    └── ai_act_db.systems

Backend (8000) ────► Fuseki (3030)
                    └── /ds/sparql
                    └── /ds/data

Backend (8000) ────► Reasoner Service (8001)
                    └── /reason

Backend (8000) ────► Forensic Agent (8002)
                    └── /evidence-plan
```

## Documentación API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

**Versión:** 1.0.0
**Compatibilidad:** Ontología EU AI Act v0.41.0
**Puerto por defecto:** 8000
**Última Actualización:** Enero 2026
