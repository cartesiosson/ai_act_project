"""
Statistical Approaches SWRL Rules
Reglas SWRL para Enfoques Estadísticos

These rules apply to statistical approaches and methods
as defined in EU AI Act Annex I (c).
"""

from rdflib import Namespace, Graph, Literal

AI = Namespace("http://ai-act.eu/ai#")

# =============================================================================
# RULE_29: Bayesian Models → Uncertainty Quantification
# =============================================================================
# Bayesian models must quantify uncertainty in predictions

RULE_29 = {
    "id": "rule29_bayesian_uncertainty",
    "name": "Bayesian models require uncertainty quantification",
    "description": "Bayesian models must quantify and communicate prediction uncertainty",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:BayesianModel", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:UncertaintyQuantification"},
        {"property": "ai:hasRequirement", "value": "ai:TransparencyRequirement"}
    ]
}

# =============================================================================
# RULE_30: Statistical Inference → Data Quality Requirements
# =============================================================================
# Statistical inference methods require high-quality training data

RULE_30 = {
    "id": "rule30_statistical_dataquality",
    "name": "Statistical inference requires data quality",
    "description": "Statistical inference systems must ensure data quality and representativeness",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:StatisticalInference", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:DataQualityRequirement"},
        {"property": "ai:hasTechnicalRequirement", "value": "ai:DataValidationRequirement"}
    ]
}

# =============================================================================
# RULE_31: Optimization Methods → Robustness Testing
# =============================================================================
# Optimization-based AI systems need robustness evaluation

RULE_31 = {
    "id": "rule31_optimization_robustness",
    "name": "Optimization methods require robustness testing",
    "description": "Optimization-based systems must demonstrate robustness to input variations",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:OptimizationMethod", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:RobustnessRequirement"},
        {"property": "ai:hasTechnicalCriterion", "value": "ai:AccuracyLevel"}
    ]
}

# =============================================================================
# RULE_32: Statistical Approaches in High-Risk → Validation Requirements
# =============================================================================
# Statistical AI in high-risk contexts requires rigorous validation

RULE_32 = {
    "id": "rule32_statistical_highrisk_validation",
    "name": "Statistical high-risk systems require validation",
    "description": "Statistical approaches in high-risk contexts must undergo rigorous validation",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:StatisticalApproach", "type": "uri"},
        {"property": "ai:hasRiskLevel", "operator": "==", "value": "ai:HighRisk", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:ValidationRequirement"},
        {"property": "ai:hasTechnicalRequirement", "value": "ai:TestingRequirement"}
    ]
}

# =============================================================================
# RULE_33: Statistical Models → Documentation Requirements
# =============================================================================
# Statistical models must document assumptions and limitations

RULE_33 = {
    "id": "rule33_statistical_documentation",
    "name": "Statistical models require comprehensive documentation",
    "description": "Statistical models must document statistical assumptions and limitations",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:StatisticalApproach", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:DocumentationRequirement"},
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelInterpretability"}
    ]
}

# Collect all statistical rules
ALL_RULES = [
    RULE_29,
    RULE_30,
    RULE_31,
    RULE_32,
    RULE_33
]
