# Servidor MCP SPARQL Forense

Servidor MCP usando FastMCP 2.0 para consultar la ontología EU AI Act y los resultados de análisis forense.

## Descripción General

Este servidor implementa el **Model Context Protocol (MCP)** para exponer herramientas de consulta SPARQL y análisis forense a clientes LLM. Permite:

- Consultas SPARQL personalizadas sobre la ontología EU AI Act v0.41.0
- Determinación de nivel de riesgo según Anexo III
- Clasificación de incidentes graves según Art. 3(49)
- Mappings multi-framework (ISO 42001, NIST AI RMF)
- Integración con el Agente Forense para análisis de incidentes

## Requisitos

- Python 3.10+
- Fuseki ejecutándose en `http://localhost:3030` con dataset `aiact`
- Agente Forense ejecutándose en `http://localhost:8002`

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar como servidor stdio (para clientes MCP)

```bash
python3 server.py
```

### Ejecutar como servidor HTTP

```bash
fastmcp run server.py --transport sse --port 8080
```

## Herramientas Disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `query_ontology` | Ejecutar consultas SPARQL personalizadas |
| `get_requirements_for_system` | Obtener requisitos EU AI Act por propósito/contexto |
| `determine_risk_level` | Determinar nivel de riesgo (HighRisk, MinimalRisk, etc.) |
| `list_analyzed_systems` | Listar sistemas del benchmark forense |
| `get_compliance_gaps` | Obtener requisitos faltantes (gaps) |
| `analyze_incident` | Analizar nuevo incidente con Ollama/Llama |
| `get_benchmark_stats` | Obtener estadísticas del benchmark |
| `get_ontology_stats` | Obtener conteo de tripletas de la ontología |
| `query_iso_mappings` | Mapear requisitos a ISO 42001 |
| `query_nist_mappings` | Mapear requisitos a NIST AI RMF |
| `get_inference_rules` | Obtener reglas de inferencia SWRL |

## Ejemplos

### Determinar nivel de riesgo para reconocimiento facial

```python
determine_risk_level(
    purpose="BiometricIdentification",
    contexts=["PublicSpaces", "LawEnforcement"]
)
```

**Resultado esperado:**
```json
{
    "risk_level": "HighRisk",
    "criteria": ["BiometricIdentificationCriterion", "LawEnforcementCriterion"],
    "requirements": ["HumanOversightRequirement", "BiometricSecurityRequirement", ...]
}
```

### Analizar un nuevo incidente

```python
analyze_incident(
    narrative="Amazon Rekognition mostró sesgo racial en reconocimiento facial...",
    source="Media Report"
)
```

**Resultado esperado:**
```json
{
    "system_name": "Amazon Rekognition",
    "risk_level": "HighRisk",
    "incident_type": "FundamentalRightsInfringement",
    "triggers_article_73": true,
    "requirements": [...],
    "gaps": [...]
}
```

### Consulta SPARQL personalizada

```python
query_ontology("""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?req ?label WHERE {
        ?req a ai:Requirement .
        ?req rdfs:label ?label
    }
""")
```

### Obtener mappings ISO 42001

```python
query_iso_mappings("HumanOversightRequirement")
```

**Resultado esperado:**
```json
{
    "requirement": "HumanOversightRequirement",
    "iso_control": "Control_8_6",
    "iso_section": "8.6",
    "confidence": "HIGH"
}
```

### Obtener mappings NIST AI RMF

```python
query_nist_mappings("HumanOversightRequirement")
```

**Resultado esperado:**
```json
{
    "requirement": "HumanOversightRequirement",
    "nist_function": "MANAGE_4_1",
    "nist_category": "MANAGE-4.1",
    "applicability": "GLOBAL_INCIDENTS, COMPARATIVE_ANALYSIS",
    "confidence": "HIGH"
}
```

## Arquitectura

```
┌─────────────────────┐     ┌─────────────────────┐
│    Cliente MCP      │     │   Agente Forense    │
│  (Cliente LLM)      │────▶│  (Ollama + Llama)   │
└─────────────────────┘     └─────────────────────┘
         │                            │
         │ Protocolo MCP              │ HTTP
         ▼                            ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Servidor FastMCP   │────▶│   Apache Fuseki     │
│   (Este servidor)   │     │   (SPARQL store)    │
└─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   Ontología         │
                            │   EU AI Act v0.41.0 │
                            │   + Mappings        │
                            │   ISO/NIST/DPV      │
                            └─────────────────────┘
```

## Características de la Ontología v0.41.0

El servidor proporciona acceso a las siguientes características de la ontología:

### Taxonomía de Incidentes Graves (Art. 3(49))

| Tipo de Incidente | Artículo | Trigger Art. 73 |
|-------------------|----------|-----------------|
| `ai:DeathOrHealthHarm` | Art. 3(49)(a) | ✓ |
| `ai:CriticalInfrastructureDisruption` | Art. 3(49)(b) | ✓ |
| `ai:FundamentalRightsInfringement` | Art. 3(49)(c) | ✓ |
| `ai:PropertyOrEnvironmentHarm` | Art. 3(49)(d) | ✓ |

### Determinación de Ámbito (Art. 2)

- Exclusiones de scope (`ai:ScopeExclusion`)
- Contextos override (`ai:overridesExclusion`)
- Propiedad `ai:isInEUAIActScope`

### Mappings Multi-Framework

| Framework | Mappings | Confianza |
|-----------|----------|-----------|
| ISO 42001 | 15 | 87% HIGH |
| NIST AI RMF | 16 | 100% HIGH |
| DPV 2.2 | 14 | - |

## Configuración

### Variables de Entorno

```bash
# Fuseki endpoint
FUSEKI_ENDPOINT=http://fuseki:3030

# Agente Forense
FORENSIC_AGENT_URL=http://forensic_agent:8002

# Ontología
ONTOLOGY_GRAPH=http://ai-act.eu/ai
```

### Docker

El servidor se despliega automáticamente con `docker-compose`:

```yaml
mcp_sparql:
  build:
    context: ./mcp-servers/forensic-sparql
  ports:
    - "8080:8080"
  environment:
    - FUSEKI_ENDPOINT=http://fuseki:3030
    - FORENSIC_AGENT_URL=http://forensic_agent:8002
```

## Integración con Clientes

### Claude Desktop

Añadir al fichero de configuración MCP:

```json
{
  "mcpServers": {
    "forensic-sparql": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "FUSEKI_ENDPOINT": "http://localhost:3030"
      }
    }
  }
}
```

### Uso Programático

```python
from mcp import Client

async with Client("http://localhost:8080") as client:
    # Listar herramientas disponibles
    tools = await client.list_tools()

    # Ejecutar herramienta
    result = await client.call_tool(
        "determine_risk_level",
        purpose="BiometricIdentification",
        contexts=["PublicSpaces"]
    )
```

## Referencias

- **FastMCP 2.0:** https://github.com/jlowin/fastmcp
- **Model Context Protocol:** https://modelcontextprotocol.io/
- **Apache Jena Fuseki:** https://jena.apache.org/documentation/fuseki2/
- **Ontología EU AI Act:** [/ontologias/versions/0.41.0/](../../ontologias/versions/0.41.0/)
- **Mappings Multi-Framework:** [/ontologias/mappings/](../../ontologias/mappings/)

---

**Versión:** 1.1.0
**Estado:** Operacional
**Última Actualización:** Enero 2026
**Compatibilidad:** Ontología EU AI Act v0.41.0
