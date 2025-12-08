#!/usr/bin/env python3
"""
MCP Server for Forensic Agent SPARQL Endpoint
Uses FastMCP 2.0 - Compatible with any MCP client
"""

import os
import json
import httpx
from fastmcp import FastMCP

# Configuration from environment variables (Docker) or defaults (local)
FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030")
FUSEKI_DATASET = os.getenv("FUSEKI_DATASET", "ds")
FUSEKI_GRAPH = os.getenv("FUSEKI_GRAPH", "http://ai-act.eu/ontology")

# Initialize FastMCP 2.0 server
mcp = FastMCP("forensic-sparql")


async def _execute_sparql(query: str) -> str:
    """Internal function to execute SPARQL queries."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FUSEKI_URL}/{FUSEKI_DATASET}/query",
                data={
                    "query": query,
                    "default-graph-uri": FUSEKI_GRAPH
                },
                headers={"Accept": "application/sparql-results+json"},
                timeout=30.0
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})


@mcp.tool()
async def query_ontology(query: str) -> str:
    """
    Execute a SPARQL query against the EU AI Act ontology.

    Args:
        query: SPARQL SELECT or CONSTRUCT query
    """
    return await _execute_sparql(query)


@mcp.tool()
async def get_requirements_for_system(
    purpose: str,
    contexts: list[str] | None = None
) -> str:
    """
    Get EU AI Act requirements for a system based on purpose and context.

    Args:
        purpose: System purpose (e.g., BiometricIdentification, EmotionRecognition)
        contexts: Deployment contexts (e.g., PublicSpaces, LawEnforcement)
    """
    contexts = contexts or []
    context_uris = " ".join([f"ai:{ctx}" for ctx in contexts])

    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?requirement ?label ?criterion
    WHERE {{
      {{
        ai:{purpose} ai:activatesCriterion ?criterion .
      }}
      {f"UNION {{ VALUES ?context {{ {context_uris} }} ?context ai:triggersCriterion ?criterion . }}" if context_uris else ""}

      ?criterion ai:activatesRequirement ?requirement .
      ?requirement rdfs:label ?label .
    }}
    ORDER BY ?label
    """

    return await _execute_sparql(query)


@mcp.tool()
async def determine_risk_level(
    purpose: str,
    contexts: list[str] | None = None
) -> str:
    """
    Determine EU AI Act risk level for a system.

    Args:
        purpose: System purpose
        contexts: Deployment contexts
    """
    contexts = contexts or []
    context_uris = " ".join([f"ai:{ctx}" for ctx in contexts])

    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?criterion ?label
    WHERE {{
      {{
        ai:{purpose} ai:activatesCriterion ?criterion .
      }}
      {f"UNION {{ VALUES ?context {{ {context_uris} }} ?context ai:triggersCriterion ?criterion . }}" if context_uris else ""}

      ?criterion rdfs:label ?label .
    }}
    """

    result = await _execute_sparql(query)

    try:
        data = json.loads(result)
        bindings = data.get("results", {}).get("bindings", [])

        if bindings:
            criteria = [b['label']['value'] for b in bindings]
            return f"Risk Level: HighRisk\n\nCriteria:\n" + "\n".join([f"- {c}" for c in criteria])
        else:
            return "Risk Level: MinimalRisk\n\nNo specific criteria found."
    except:
        return result


@mcp.tool()
async def list_analyzed_systems(limit: int = 20) -> str:
    """
    List AI systems analyzed by the forensic agent.

    Args:
        limit: Maximum number of systems to return
    """
    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX forensic: <http://ai-act.eu/forensic#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?system ?label ?riskLevel ?incidentType
    WHERE {{
      ?system a ai:AISystem .
      OPTIONAL {{ ?system rdfs:label ?label }}
      OPTIONAL {{ ?system ai:hasRiskLevel ?riskLevel }}
      OPTIONAL {{
        ?system forensic:hasIncident ?incident .
        ?incident forensic:incidentType ?incidentType
      }}
    }}
    LIMIT {limit}
    """

    return await _execute_sparql(query)


@mcp.tool()
async def get_compliance_gaps(system_id: str | None = None) -> str:
    """
    Get compliance gaps (missing requirements) for analyzed systems.

    Args:
        system_id: Optional system ID (e.g., BENCH-0001). If not provided, returns aggregated gaps.
    """
    if system_id:
        query = f"""
        PREFIX forensic: <http://ai-act.eu/forensic#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?gap ?label
        WHERE {{
          forensic:System_{system_id} forensic:missingRequirement ?gap .
          OPTIONAL {{ ?gap rdfs:label ?label }}
        }}
        """
    else:
        query = """
        PREFIX forensic: <http://ai-act.eu/forensic#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?gap ?label (COUNT(?system) as ?count)
        WHERE {
          ?system forensic:missingRequirement ?gap .
          OPTIONAL { ?gap rdfs:label ?label }
        }
        GROUP BY ?gap ?label
        ORDER BY DESC(?count)
        LIMIT 10
        """

    return await _execute_sparql(query)


@mcp.tool()
async def get_ontology_stats() -> str:
    """Get statistics about the loaded ontology (triples, requirements, criteria, systems)."""
    queries = {
        "total_triples": "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }",
        "requirements": "PREFIX ai: <http://ai-act.eu/ai#> SELECT (COUNT(?r) as ?count) WHERE { ?r a ai:Requirement }",
        "criteria": "PREFIX ai: <http://ai-act.eu/ai#> SELECT (COUNT(?c) as ?count) WHERE { ?c a ai:Criterion }",
        "systems": "PREFIX ai: <http://ai-act.eu/ai#> SELECT (COUNT(?s) as ?count) WHERE { ?s a ai:AISystem }"
    }

    stats = {}
    for key, query in queries.items():
        result = await _execute_sparql(query)
        try:
            data = json.loads(result)
            bindings = data.get("results", {}).get("bindings", [])
            if bindings:
                stats[key] = int(bindings[0].get("count", {}).get("value", 0))
        except:
            stats[key] = 0

    return json.dumps(stats, indent=2)


@mcp.tool()
async def query_iso_mappings(requirement: str) -> str:
    """
    Query ISO 42001 mappings for an EU AI Act requirement.

    Args:
        requirement: Requirement name (e.g., DataGovernanceRequirement)
    """
    if not requirement.startswith("http"):
        requirement = f"ai:{requirement}"

    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX iso: <http://iso.org/42001#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?isoControl ?isoSection ?description ?confidence
    WHERE {{
      {requirement} ai:equivalentToISOControl ?isoControl .
      OPTIONAL {{ {requirement} ai:isoSection ?isoSection }}
      OPTIONAL {{ {requirement} ai:isoControlDescription ?description }}
      OPTIONAL {{ {requirement} ai:mappingConfidence ?confidence }}
    }}
    """

    return await _execute_sparql(query)


@mcp.tool()
async def query_nist_mappings(requirement: str) -> str:
    """
    Query NIST AI RMF mappings for an EU AI Act requirement.

    Args:
        requirement: Requirement name (e.g., DataGovernanceRequirement)
    """
    if not requirement.startswith("http"):
        requirement = f"ai:{requirement}"

    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    PREFIX nist: <http://nist.gov/ai-rmf#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?nistFunction ?category ?description ?confidence ?applicability
    WHERE {{
      {requirement} ai:equivalentToNISTFunction ?nistFunction .
      OPTIONAL {{ {requirement} ai:nistCategory ?category }}
      OPTIONAL {{ {requirement} ai:nistCategoryDescription ?description }}
      OPTIONAL {{ {requirement} ai:nistMappingConfidence ?confidence }}
      OPTIONAL {{ {requirement} ai:nistApplicabilityContext ?applicability }}
    }}
    """

    return await _execute_sparql(query)


if __name__ == "__main__":
    mcp.run()
