#!/usr/bin/env python3
"""
MCP Server for Forensic Agent SPARQL Endpoint
Uses FastMCP 2.0 - Compatible with any MCP client
"""

import os
import json
from pathlib import Path
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
async def get_benchmark_stats() -> str:
    """Get statistics from the 100-incident benchmark."""
    benchmark_dir = Path(__file__).parent.parent.parent / "forensic_agent" / "benchmark" / "results"

    if not benchmark_dir.exists():
        return "No benchmark results found"

    stats_files = sorted(benchmark_dir.glob("benchmark_stats_*.json"), reverse=True)

    if not stats_files:
        return "No benchmark results found"

    with open(stats_files[0]) as f:
        stats = json.load(f)

    return json.dumps(stats, indent=2)


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


@mcp.tool()
async def get_inference_rules() -> str:
    """
    Get all EU AI Act inference rules that the reasoning engine uses.

    Returns rules in two formats:
    1. Condition/Consequence rules: Used to derive technical criteria and classifications
    2. Navigation rules: Used for transitive property chain inference

    These rules explain HOW the system derives risk levels, criteria, and requirements
    from system properties like FLOPs, parameters, autonomy level, etc.
    """
    # Load rules from the rules engine
    import sys
    rules_path = Path(__file__).parent.parent.parent / "ontologias" / "rules"

    if not rules_path.exists():
        return json.dumps({"error": "Rules directory not found", "path": str(rules_path)})

    sys.path.insert(0, str(rules_path))

    try:
        # Load each rules module
        rules_data = {
            "condition_consequence_rules": [],
            "navigation_rules": [],
            "metadata": {
                "description": "EU AI Act inference rules for compliance determination",
                "categories": {}
            }
        }

        # Base rules
        try:
            from base_rules import BASE_RULES
            for rule in BASE_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "base_contextual",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["base_contextual"] = len(BASE_RULES)
        except ImportError:
            pass

        # Technical rules
        try:
            from technical_rules import TECHNICAL_RULES
            for rule in TECHNICAL_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "technical_gpai",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["technical_gpai"] = len(TECHNICAL_RULES)
        except ImportError:
            pass

        # Cascade rules
        try:
            from cascade_rules import CASCADE_RULES
            for rule in CASCADE_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "cascade",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["cascade"] = len(CASCADE_RULES)
        except ImportError:
            pass

        # Capability rules
        try:
            from capability_rules import CAPABILITY_RULES
            for rule in CAPABILITY_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "capability",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["capability"] = len(CAPABILITY_RULES)
        except ImportError:
            pass

        # ML Traditional rules
        try:
            from ml_traditional_rules import ALL_RULES as ML_RULES
            for rule in ML_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "ml_traditional",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["ml_traditional"] = len(ML_RULES)
        except ImportError:
            pass

        # Logic based rules
        try:
            from logic_based_rules import ALL_RULES as LOGIC_RULES
            for rule in LOGIC_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "logic_knowledge",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["logic_knowledge"] = len(LOGIC_RULES)
        except ImportError:
            pass

        # Statistical rules
        try:
            from statistical_rules import ALL_RULES as STAT_RULES
            for rule in STAT_RULES:
                rules_data["condition_consequence_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "category": "statistical",
                    "conditions": rule["conditions"],
                    "consequences": rule["consequences"]
                })
            rules_data["metadata"]["categories"]["statistical"] = len(STAT_RULES)
        except ImportError:
            pass

        # Navigation rules
        try:
            from navigation_rules import NAVIGATION_RULES
            for rule in NAVIGATION_RULES:
                rules_data["navigation_rules"].append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule.get("description", ""),
                    "navigation_type": rule.get("navigation_type", "transitive"),
                    "source_property": rule.get("source_property"),
                    "link_property": rule.get("link_property"),
                    "target_property": rule.get("target_property")
                })
            rules_data["metadata"]["categories"]["navigation"] = len(NAVIGATION_RULES)
        except ImportError:
            pass

        rules_data["metadata"]["total_condition_rules"] = len(rules_data["condition_consequence_rules"])
        rules_data["metadata"]["total_navigation_rules"] = len(rules_data["navigation_rules"])

        return json.dumps(rules_data, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        if str(rules_path) in sys.path:
            sys.path.remove(str(rules_path))


@mcp.tool()
async def get_swrl_rules_ttl() -> str:
    """
    Get SWRL inference rules in TTL (Turtle) format.

    Returns the unified SWRL rules file that defines all inference rules
    in standard Semantic Web format. This includes:
    - Model scale classification based on FLOPs
    - Navigation rules for property chain inference
    - Technical criteria rules for GPAI classification
    - Base contextual and normative rules
    """
    rules_file = Path(__file__).parent.parent.parent / "ontologias" / "rules" / "swrl-base-rules.ttl"

    if not rules_file.exists():
        return json.dumps({"error": "SWRL rules file not found", "path": str(rules_file)})

    try:
        with open(rules_file, "r", encoding="utf-8") as f:
            content = f.read()

        return json.dumps({
            "format": "text/turtle",
            "file": "swrl-base-rules.ttl",
            "content": content,
            "description": "SWRL inference rules in TTL format for EU AI Act compliance reasoning"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def explain_rule(rule_id: str) -> str:
    """
    Get detailed explanation of a specific inference rule.

    Args:
        rule_id: Rule identifier (e.g., rule13_flops_systemic_risk, rule_nav_purpose_criterion)
    """
    # Load all rules
    rules_result = await get_inference_rules()

    try:
        rules_data = json.loads(rules_result)

        # Search in condition/consequence rules
        for rule in rules_data.get("condition_consequence_rules", []):
            if rule["id"] == rule_id:
                explanation = {
                    "rule": rule,
                    "type": "condition_consequence",
                    "interpretation": _interpret_cc_rule(rule)
                }
                return json.dumps(explanation, indent=2)

        # Search in navigation rules
        for rule in rules_data.get("navigation_rules", []):
            if rule["id"] == rule_id:
                explanation = {
                    "rule": rule,
                    "type": "navigation",
                    "interpretation": _interpret_nav_rule(rule)
                }
                return json.dumps(explanation, indent=2)

        return json.dumps({"error": f"Rule '{rule_id}' not found"})

    except Exception as e:
        return json.dumps({"error": str(e)})


def _interpret_cc_rule(rule: dict) -> str:
    """Generate human-readable interpretation of condition/consequence rule."""
    conditions_text = []
    for cond in rule.get("conditions", []):
        prop = cond["property"].replace("ai:", "")
        op = cond["operator"]
        val = cond["value"]
        conditions_text.append(f"- {prop} {op} {val}")

    consequences_text = []
    for cons in rule.get("consequences", []):
        prop = cons["property"].replace("ai:", "")
        val = cons["value"].replace("ai:", "")
        consequences_text.append(f"- Set {prop} = {val}")

    return f"""
IF all conditions are met:
{chr(10).join(conditions_text)}

THEN apply consequences:
{chr(10).join(consequences_text)}

Category: {rule.get('category', 'unknown')}
"""


def _interpret_nav_rule(rule: dict) -> str:
    """Generate human-readable interpretation of navigation rule."""
    nav_type = rule.get("navigation_type", "transitive")
    source = rule.get("source_property", "").replace("ai:", "")
    link = rule.get("link_property", "").replace("ai:", "")
    target = rule.get("target_property", "").replace("ai:", "")

    if nav_type == "transitive":
        return f"""
TRANSITIVE NAVIGATION:
System --{source}--> IntermediateValue --{link}--> Result
                                          |
                                          v
System --{target}--> Result

This rule follows a chain: if a system has a {source} that {link}s to something,
then the system inherits that as its {target}.
"""
    else:
        return f"""
DIRECT NAVIGATION:
System --{source}--> Value
         |
         v
System --{target}--> Value

This rule directly copies: if a system has {source}, it also has {target} with the same value.
"""


if __name__ == "__main__":
    mcp.run()
