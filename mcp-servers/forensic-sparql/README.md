# Forensic SPARQL MCP Server

MCP Server using FastMCP 2.0 for querying the EU AI Act ontology and forensic analysis results.

## Requirements

- Python 3.10+
- Fuseki running on `http://localhost:3030` with dataset `aiact`
- Forensic Agent running on `http://localhost:8002`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run as stdio server (for MCP clients)

```bash
python3 server.py
```

### Run as HTTP server

```bash
fastmcp run server.py --transport sse --port 8080
```

## Available Tools

| Tool | Description |
|------|-------------|
| `query_ontology` | Execute custom SPARQL queries |
| `get_requirements_for_system` | Get EU AI Act requirements by purpose/context |
| `determine_risk_level` | Determine risk level (HighRisk, MinimalRisk, etc.) |
| `list_analyzed_systems` | List systems from forensic benchmark |
| `get_compliance_gaps` | Get missing requirements |
| `analyze_incident` | Analyze new incident with Ollama/Llama |
| `get_benchmark_stats` | Get 100-incident benchmark statistics |
| `get_ontology_stats` | Get ontology triple counts |
| `query_iso_mappings` | Map requirements to ISO 42001 |
| `query_nist_mappings` | Map requirements to NIST AI RMF |

## Examples

### Determine risk level for facial recognition

```python
determine_risk_level(
    purpose="BiometricIdentification",
    contexts=["PublicSpaces", "LawEnforcement"]
)
```

### Analyze a new incident

```python
analyze_incident(
    narrative="Amazon Rekognition showed racial bias in facial recognition...",
    source="Media Report"
)
```

### Custom SPARQL query

```python
query_ontology("""
    PREFIX ai: <http://ai-act.eu/ai#>
    SELECT ?req ?label WHERE {
        ?req a ai:Requirement .
        ?req rdfs:label ?label
    }
""")
```

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│    MCP Client       │     │   Forensic Agent    │
│  (Any LLM client)   │────▶│  (Ollama + Llama)   │
└─────────────────────┘     └─────────────────────┘
         │                            │
         │ MCP Protocol               │ HTTP
         ▼                            ▼
┌─────────────────────┐     ┌─────────────────────┐
│  FastMCP 2.0 Server │────▶│   Apache Fuseki     │
│   (This server)     │     │   (SPARQL store)    │
└─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   EU AI Act         │
                            │   Ontology          │
                            │   + ISO/NIST maps   │
                            └─────────────────────┘
```
