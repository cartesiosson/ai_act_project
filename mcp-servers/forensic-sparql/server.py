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


@mcp.tool()
async def get_inference_rules() -> str:
    """
    Get all inference rules for EU AI Act compliance analysis.
    Returns condition-based rules (base, technical, cascade) and navigation rules.
    """
    # Base contextual rules (Rules 1-12)
    base_rules = [
        {"id": "rule01a_education_context_minors", "name": "Education context triggers protection of minors", "category": "base_contextual",
         "conditions": [{"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:Education"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:ProtectionOfMinors"}]},
        {"id": "rule01b_education_purpose_minors", "name": "Education purpose triggers protection of minors", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:EducationAccess"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:ProtectionOfMinors"}]},
        {"id": "rule02_recruitment_nondiscrimination", "name": "Recruitment systems require non-discrimination", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:RecruitmentOrEmployment"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:NonDiscrimination"}]},
        {"id": "rule03_judicial_support", "name": "Judicial support systems trigger specialized criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:JudicialDecisionSupport"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:JudicialSupportCriterion"}]},
        {"id": "rule04_law_enforcement", "name": "Law enforcement systems trigger specialized criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:LawEnforcementSupport"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:LawEnforcementCriterion"}]},
        {"id": "rule05_migration_control", "name": "Migration systems trigger border control criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:MigrationControl"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:MigrationBorderCriterion"}]},
        {"id": "rule06_critical_infrastructure", "name": "Critical infrastructure systems trigger specialized criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:CriticalInfrastructureOperation"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:CriticalInfrastructureCriterion"}]},
        {"id": "rule07_healthcare_privacy", "name": "Healthcare systems require privacy protection", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:HealthCare"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:PrivacyProtection"}]},
        {"id": "rule08a_biometric_data_security", "name": "Biometric data processing triggers security criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:processesDataType", "operator": "==", "value": "ai:BiometricData"}],
         "consequences": [{"property": "ai:hasContextualCriterion", "value": "ai:BiometricSecurity"}]},
        {"id": "rule08b_biometric_purpose_security", "name": "Biometric identification triggers security criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:BiometricIdentification"}],
         "consequences": [{"property": "ai:hasContextualCriterion", "value": "ai:BiometricSecurity"}]},
        {"id": "rule09_realtime_performance", "name": "Real-time systems require performance criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:RealTimeProcessing"}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:PerformanceRequirements"}]},
        {"id": "rule10_highvolume_scalability", "name": "High-volume systems require scalability", "category": "base_contextual",
         "conditions": [{"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:HighVolumeProcessing"}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:ScalabilityRequirements"}]},
        {"id": "rule11a_healthcare_essential", "name": "Healthcare context triggers essential services criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:Healthcare"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:EssentialServicesAccessCriterion"}]},
        {"id": "rule12_public_services", "name": "Public services trigger essential services criteria", "category": "base_contextual",
         "conditions": [{"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:PublicServices"}],
         "consequences": [{"property": "ai:hasNormativeCriterion", "value": "ai:EssentialServicesAccessCriterion"}]},
    ]

    # GPAI / Generative AI rules
    gpai_rules = [
        {"id": "rule_gpai_generative_transparency", "name": "GPAI systems require transparency (Art. 50-52)", "category": "gpai",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:GenerativeAIContentCreation"}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:GPAITransparency"},
                         {"property": "ai:hasNormativeCriterion", "value": "ai:ContentLabelingRequirement"}]},
        {"id": "rule_gpai_foundation_scale", "name": "Foundation models are classified as GPAI", "category": "gpai",
         "conditions": [{"property": "ai:hasModelScale", "operator": "==", "value": "ai:FoundationModelScale"}],
         "consequences": [{"property": "ai:hasGPAIClassification", "value": "ai:GeneralPurposeAI"}]},
        {"id": "rule_gpai_systemic_risk", "name": "High-capacity GPAI triggers systemic risk", "category": "gpai",
         "conditions": [{"property": "ai:hasGPAIClassification", "operator": "==", "value": "ai:GeneralPurposeAI"}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:SystemicRiskPotential"}]},
        {"id": "rule19c_generative_complexity", "name": "Generative models trigger complexity criteria", "category": "technical",
         "conditions": [{"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:GenerativeModel"}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:ModelComplexity"}]},
    ]

    # Technical rules
    technical_rules = [
        {"id": "rule_model_scale_foundation", "name": "Foundation model scale based on FLOPs", "category": "technical",
         "conditions": [{"property": "ai:hasFLOPS", "operator": ">=", "value": 1e16}],
         "consequences": [{"property": "ai:hasModelScale", "value": "ai:FoundationModelScale"}]},
        {"id": "rule13_flops_systemic_risk", "name": "High computational FLOPs trigger systemic risk", "category": "technical",
         "conditions": [{"property": "ai:hasComputationFLOPs", "operator": ">", "value": 1e25}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:SystemicRisk"}]},
        {"id": "rule15_autonomy_oversight", "name": "High autonomy indicates lack of human oversight", "category": "technical",
         "conditions": [{"property": "ai:hasAutonomyLevel", "operator": ">", "value": 0.8}],
         "consequences": [{"property": "ai:hasTechnicalCriterion", "value": "ai:LacksHumanOversight"}]},
    ]

    # Cascade rules (criteria -> requirements)
    cascade_rules = [
        {"id": "rule20a_systemic_risk_management", "name": "Systemic risk triggers risk management", "category": "cascade",
         "conditions": [{"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:SystemicRisk"}],
         "consequences": [{"property": "ai:hasRequirement", "value": "ai:RiskManagementRequirement"}]},
        {"id": "rule22a_adaptive_oversight", "name": "Adaptive capability triggers oversight requirement", "category": "cascade",
         "conditions": [{"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:AdaptiveCapability"}],
         "consequences": [{"property": "ai:hasRequirement", "value": "ai:HumanOversightRequirement"}]},
        {"id": "rule23a_complexity_transparency", "name": "Model complexity triggers transparency", "category": "cascade",
         "conditions": [{"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:ModelComplexity"}],
         "consequences": [{"property": "ai:hasTechnicalRequirement", "value": "ai:TransparencyRequirement"}]},
        {"id": "rule_gpai_transparency_cascade", "name": "GPAI transparency triggers documentation", "category": "cascade",
         "conditions": [{"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:GPAITransparency"}],
         "consequences": [{"property": "ai:hasRequirement", "value": "ai:DocumentationRequirement"},
                         {"property": "ai:hasRequirement", "value": "ai:TransparencyRequirement"}]},
    ]

    # Prohibited practices (Article 5)
    prohibited_rules = [
        {"id": "rule_art5_1a_subliminal", "name": "Article 5.1(a): Subliminal manipulation prohibited", "category": "prohibited_practices",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:SubliminalManipulation"}],
         "consequences": [{"property": "ai:hasProhibitedPractice", "value": "ai:SubliminalManipulationCriterion"}]},
        {"id": "rule_art5_1c_social_scoring", "name": "Article 5.1(c): Social scoring prohibited", "category": "prohibited_practices",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:SocialScoring"}],
         "consequences": [{"property": "ai:hasProhibitedPractice", "value": "ai:SocialScoringCriterion"}]},
        {"id": "rule_art5_1h_realtime_biometric", "name": "Article 5.1(h): Real-time biometric in public spaces prohibited", "category": "prohibited_practices",
         "conditions": [{"property": "ai:hasPurpose", "operator": "==", "value": "ai:BiometricIdentification"},
                       {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:RealTimeProcessing"},
                       {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:PublicSpaces"}],
         "consequences": [{"property": "ai:hasProhibitedPractice", "value": "ai:RealTimeBiometricIdentificationCriterion"}]},
    ]

    # Navigation rules (transitive inference)
    navigation_rules = [
        {"id": "rule_nav_purpose_criterion", "name": "Purpose activates criterion derivation", "navigation_type": "transitive",
         "source_property": "ai:hasPurpose", "link_property": "ai:activatesCriterion", "target_property": "ai:hasCriteria"},
        {"id": "rule_nav_context_criterion", "name": "Context triggers criterion derivation", "navigation_type": "transitive",
         "source_property": "ai:hasDeploymentContext", "link_property": "ai:triggersCriterion", "target_property": "ai:hasCriteria"},
        {"id": "rule_nav_criterion_requirement", "name": "Criterion activates requirement derivation", "navigation_type": "transitive",
         "source_property": "ai:hasCriteria", "link_property": "ai:activatesRequirement", "target_property": "ai:hasComplianceRequirement"},
        {"id": "rule_nav_criterion_risk", "name": "Criterion assigns risk level", "navigation_type": "transitive",
         "source_property": "ai:hasCriteria", "link_property": "ai:assignsRiskLevel", "target_property": "ai:hasRiskLevel"},
        {"id": "rule_nav_data_requirement", "name": "Data type triggers data requirement", "navigation_type": "transitive",
         "source_property": "ai:processesDataType", "link_property": "ai:triggersDataRequirement", "target_property": "ai:hasDataRequirement"},
    ]

    # Combine all condition-based rules
    all_condition_rules = base_rules + gpai_rules + technical_rules + cascade_rules + prohibited_rules

    result = {
        "condition_consequence_rules": all_condition_rules,
        "navigation_rules": navigation_rules,
        "metadata": {
            "total_condition_rules": len(all_condition_rules),
            "total_navigation_rules": len(navigation_rules),
            "categories": ["base_contextual", "gpai", "technical", "cascade", "prohibited_practices"],
            "version": "1.0.0"
        }
    }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
