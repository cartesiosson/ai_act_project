"""
Derivation Logic for Automated Classification from Ontology

This module implements the semantic reasoning to derive Criteria, Requirements,
and Risk Levels from user input (Purpose, DeploymentContext, TrainingDataOrigin, etc.)

The reasoning follows this pattern:
1. Purpose instances → activatesCriterion → Criteria
2. DeploymentContext instances → triggersCriterion → Criteria
3. TrainingDataOrigin instances → requiresDataGovernance → Requirements
4. Criteria instances → activatesRequirement → Requirements
5. Criteria instances → assignsRiskLevel → RiskLevel
6. ModelScale = FoundationModelScale → GPAI Classification
"""

from typing import Set, Dict, List, Optional
from rdflib import Graph, URIRef, Namespace
import logging

logger = logging.getLogger(__name__)

# Namespaces
AI = Namespace("http://ai-act.eu/ai#")


def compact_uri(uri: str) -> str:
    """Convert full URI to compact form (e.g., ai:EducationAccess)"""
    if isinstance(uri, URIRef):
        uri = str(uri)

    if "ai-act.eu/ai#" in uri:
        return f"ai:{uri.split('#')[1]}"
    return uri


def get_ontology_values(
    instance_uri: str,
    property_uri: str,
    graph: Graph
) -> Set[str]:
    """
    Generic function to traverse ontology and get values following a property

    Args:
        instance_uri: The instance to start from (e.g., "ai:EducationAccess")
        property_uri: The property to follow (e.g., "http://ai-act.eu/ai#activatesCriterion")
        graph: The RDF graph to traverse

    Returns:
        Set of compact URIs found following the property
    """
    # Build full URIs
    if not instance_uri.startswith("http"):
        instance_ref = URIRef(f"http://ai-act.eu/ai#{instance_uri.split(':')[-1]}")
    else:
        instance_ref = URIRef(instance_uri)

    property_ref = URIRef(property_uri)

    # Traverse graph to find all objects
    results = set()
    for obj in graph.objects(instance_ref, property_ref):
        results.add(compact_uri(obj))

    return results


def derive_classifications(data: Dict, graph: Graph) -> Dict:
    """
    Main derivation function that implements semantic reasoning

    Input data structure:
    {
        "hasPurpose": ["ai:EducationAccess", ...],
        "hasDeploymentContext": ["ai:Education", ...],
        "hasTrainingDataOrigin": ["ai:ExternalDataset", ...],
        "hasAlgorithmType": ["ai:TransformerModel", ...],
        "hasModelScale": "ai:FoundationModelScale"
    }

    Returns:
    {
        "hasCriteria": [...],
        "hasComplianceRequirement": [...],
        "hasRiskLevel": "ai:HighRisk",
        "hasGPAIClassification": ["ai:GeneralPurposeAI"] or []
    }
    """
    criteria_set: Set[str] = set()
    requirements_set: Set[str] = set()
    risk_levels: Set[str] = set()

    logger.info(f"Starting derivation with input: {data}")

    # Step 1: Process Purpose instances
    # Purpose activatesCriterion → Criteria
    for purpose in data.get('hasPurpose', []):
        logger.info(f"Processing Purpose: {purpose}")
        criteria = get_ontology_values(
            purpose,
            "http://ai-act.eu/ai#activatesCriterion",
            graph
        )
        logger.info(f"  -> activatesCriterion: {criteria}")
        criteria_set.update(criteria)

    # Step 2: Process DeploymentContext instances
    # DeploymentContext triggersCriterion → Criteria
    for context in data.get('hasDeploymentContext', []):
        logger.info(f"Processing DeploymentContext: {context}")
        criteria = get_ontology_values(
            context,
            "http://ai-act.eu/ai#triggersCriterion",
            graph
        )
        logger.info(f"  -> triggersCriterion: {criteria}")
        criteria_set.update(criteria)

    # Step 3: Process TrainingDataOrigin instances
    # TrainingDataOrigin requiresDataGovernance → Requirements
    for origin in data.get('hasTrainingDataOrigin', []):
        logger.info(f"Processing TrainingDataOrigin: {origin}")
        requirements = get_ontology_values(
            origin,
            "http://ai-act.eu/ai#requiresDataGovernance",
            graph
        )
        logger.info(f"  -> requiresDataGovernance: {requirements}")
        requirements_set.update(requirements)

    # Step 4: Process Criteria to derive Requirements and RiskLevel
    # Criteria activatesRequirement → Requirements
    # Criteria assignsRiskLevel → RiskLevel
    for criterion in criteria_set:
        logger.info(f"Processing Criterion: {criterion}")

        # Get requirements activated by this criterion
        requirements = get_ontology_values(
            criterion,
            "http://ai-act.eu/ai#activatesRequirement",
            graph
        )
        logger.info(f"  -> activatesRequirement: {requirements}")
        requirements_set.update(requirements)

        # Get risk level assigned by this criterion
        risks = get_ontology_values(
            criterion,
            "http://ai-act.eu/ai#assignsRiskLevel",
            graph
        )
        logger.info(f"  -> assignsRiskLevel: {risks}")
        risk_levels.update(risks)

    # Step 5: Determine highest risk level
    # Risk hierarchy: UnacceptableRisk > HighRisk > LimitedRisk > MinimalRisk
    max_risk = determine_max_risk(risk_levels) if risk_levels else 'ai:MinimalRisk'
    logger.info(f"Determined max risk level: {max_risk}")

    # Step 6: Check for GPAI Classification
    # ModelScale = FoundationModelScale → GeneralPurposeAI
    is_gpai = check_gpai_classification(data.get('hasModelScale'))
    gpai_classification = ['ai:GeneralPurposeAI'] if is_gpai else []
    logger.info(f"GPAI Classification: {gpai_classification}")

    result = {
        'hasCriteria': sorted(list(criteria_set)),
        'hasComplianceRequirement': sorted(list(requirements_set)),
        'hasRiskLevel': max_risk,
        'hasGPAIClassification': gpai_classification,
    }

    logger.info(f"Derivation complete. Result: {result}")
    return result


def determine_max_risk(risk_levels: Set[str]) -> str:
    """
    Determine the maximum risk level from a set of risk levels

    Risk hierarchy (highest to lowest):
    1. UnacceptableRisk
    2. HighRisk
    3. LimitedRisk
    4. MinimalRisk
    """
    risk_hierarchy = {
        'ai:UnacceptableRisk': 4,
        'ai:HighRisk': 3,
        'ai:LimitedRisk': 2,
        'ai:MinimalRisk': 1
    }

    max_level = 0
    max_risk = 'ai:MinimalRisk'

    for risk in risk_levels:
        # Normalize the risk URI
        if not risk.startswith('ai:'):
            risk = f"ai:{risk.split('#')[-1]}"

        level = risk_hierarchy.get(risk, 0)
        if level > max_level:
            max_level = level
            max_risk = risk

    return max_risk


def check_gpai_classification(model_scale: Optional[str]) -> bool:
    """
    Check if the system qualifies as General Purpose AI (GPAI)

    A system is GPAI if:
    - ModelScale = FoundationModelScale

    This triggers Articles 51-53 of the EU AI Act (GPAI obligations)
    """
    if not model_scale:
        return False

    # Normalize the model scale
    if isinstance(model_scale, list):
        model_scale = model_scale[0] if model_scale else None

    if not model_scale:
        return False

    # Check for FoundationModelScale
    normalized = str(model_scale)
    is_foundation = (
        'FoundationModelScale' in normalized or
        'ai:FoundationModelScale' in normalized
    )

    logger.info(f"GPAI check for {model_scale}: {is_foundation}")
    return is_foundation


def debug_ontology_traversal(data: Dict, graph: Graph) -> Dict:
    """
    Debug function to show step-by-step ontology traversal
    Useful for understanding what relationships exist in the ontology
    """
    debug_info = {
        "purposes": {},
        "contexts": {},
        "origins": {},
        "criteria": {}
    }

    # Debug each purpose
    for purpose in data.get('hasPurpose', []):
        debug_info["purposes"][purpose] = {
            "activatesCriterion": list(get_ontology_values(
                purpose,
                "http://ai-act.eu/ai#activatesCriterion",
                graph
            )),
            "triggersCriterion": list(get_ontology_values(
                purpose,
                "http://ai-act.eu/ai#triggersCriterion",
                graph
            ))
        }

    # Debug each context
    for context in data.get('hasDeploymentContext', []):
        debug_info["contexts"][context] = {
            "triggersCriterion": list(get_ontology_values(
                context,
                "http://ai-act.eu/ai#triggersCriterion",
                graph
            )),
            "assignsRiskLevel": list(get_ontology_values(
                context,
                "http://ai-act.eu/ai#assignsRiskLevel",
                graph
            ))
        }

    # Debug each training origin
    for origin in data.get('hasTrainingDataOrigin', []):
        debug_info["origins"][origin] = {
            "requiresDataGovernance": list(get_ontology_values(
                origin,
                "http://ai-act.eu/ai#requiresDataGovernance",
                graph
            ))
        }

    return debug_info
