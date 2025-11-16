"""
Logic and Knowledge-Based AI SWRL Rules
Reglas SWRL para IA Basada en Lógica y Conocimiento

These rules apply to logic and knowledge-based approaches
as defined in EU AI Act Annex I (b).
"""

from rdflib import Namespace, Graph, Literal

AI = Namespace("http://ai-act.eu/ai#")

# =============================================================================
# RULE_24: Expert Systems → Explainability
# =============================================================================
# Expert systems must provide explanations for their recommendations

RULE_24 = {
    "id": "rule24_expertsystem_explainability",
    "name": "Expert systems require explainability",
    "description": "Expert systems must provide explanations for decisions",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:ExpertSystem", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:TransparencyRequirement"},
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelInterpretability"}
    ]
}

# =============================================================================
# RULE_25: Rule-Based Systems → Auditability
# =============================================================================
# Rule-based systems must maintain auditable rule sets

RULE_25 = {
    "id": "rule25_rulebased_auditability",
    "name": "Rule-based systems require auditability",
    "description": "Rule-based systems must maintain auditable rules and decision logs",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:RuleBasedSystem", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:Auditability"},
        {"property": "ai:hasTechnicalRequirement", "value": "ai:LoggingRequirement"}
    ]
}

# =============================================================================
# RULE_26: Knowledge Graphs → Data Governance
# =============================================================================
# Knowledge graphs require strong data governance

RULE_26 = {
    "id": "rule26_knowledgegraph_datagovernance",
    "name": "Knowledge graphs require data governance",
    "description": "Knowledge graph systems must implement data governance practices",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:KnowledgeGraph", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:DataGovernanceRequirement"}
    ]
}

# =============================================================================
# RULE_27: Symbolic Reasoning → Traceability
# =============================================================================
# Symbolic reasoning systems must provide traceable inference chains

RULE_27 = {
    "id": "rule27_symbolic_traceability",
    "name": "Symbolic reasoning requires traceability",
    "description": "Symbolic reasoning systems must provide traceable inference chains",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:SymbolicReasoning", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:TraceabilityRequirement"},
        {"property": "ai:hasTechnicalRequirement", "value": "ai:LoggingRequirement"}
    ]
}

# =============================================================================
# RULE_28: Logic-Based Systems in Healthcare → Privacy Protection
# =============================================================================
# Logic-based AI in healthcare requires privacy protections

RULE_28 = {
    "id": "rule28_logic_healthcare_privacy",
    "name": "Logic-based healthcare systems require privacy protection",
    "description": "Logic-based systems in healthcare must implement privacy protections",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:LogicKnowledgeBasedApproach", "type": "uri"},
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:Healthcare", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:PrivacyProtection"},
        {"property": "ai:hasRequirement", "value": "ai:DataGovernanceRequirement"}
    ]
}

# Collect all logic-based rules
ALL_RULES = [
    RULE_24,
    RULE_25,
    RULE_26,
    RULE_27,
    RULE_28
]
