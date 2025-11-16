"""
Traditional Machine Learning SWRL Rules
Reglas SWRL para Aprendizaje Automático Tradicional

These rules apply to traditional ML algorithms (supervised, unsupervised, reinforcement learning)
as defined in EU AI Act Annex I (a).
"""

from rdflib import Namespace, Graph, Literal

AI = Namespace("http://ai-act.eu/ai#")

# =============================================================================
# RULE_20: Decision Trees and Random Forests → Interpretability
# =============================================================================
# Decision trees and random forests are inherently interpretable
# They should meet interpretability requirements

RULE_20A = {
    "id": "rule20a_decisiontree_interpretability",
    "name": "Decision trees require interpretability documentation",
    "description": "Decision tree systems must document model interpretability",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:DecisionTree", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelInterpretability"}
    ]
}

RULE_20B = {
    "id": "rule20b_randomforest_interpretability",
    "name": "Random forests require interpretability assessment",
    "description": "Random forest systems must assess model interpretability",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:RandomForest", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelInterpretability"}
    ]
}

# =============================================================================
# RULE_21: Supervised Learning in High-Risk Contexts → Accuracy Evaluation
# =============================================================================
# Supervised learning systems in high-risk contexts must meet accuracy requirements

RULE_21 = {
    "id": "rule21_supervised_accuracy",
    "name": "Supervised learning in high-risk requires accuracy evaluation",
    "description": "Supervised learning systems must evaluate accuracy across subgroups",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:SupervisedLearning", "type": "uri"},
        {"property": "ai:hasRiskLevel", "operator": "==", "value": "ai:HighRisk", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:AccuracyLevel"},
        {"property": "ai:hasRequirement", "value": "ai:AccuracyEvaluationRequirement"}
    ]
}

# =============================================================================
# RULE_22: Unsupervised Learning → Robustness Requirements
# =============================================================================
# Unsupervised learning systems need robustness evaluation

RULE_22 = {
    "id": "rule22_unsupervised_robustness",
    "name": "Unsupervised learning requires robustness evaluation",
    "description": "Unsupervised learning systems must demonstrate robustness",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:UnsupervisedLearning", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:RobustnessRequirement"}
    ]
}

# =============================================================================
# RULE_23: Reinforcement Learning → Human Oversight
# =============================================================================
# Reinforcement learning systems require human oversight due to autonomy

RULE_23 = {
    "id": "rule23_reinforcement_oversight",
    "name": "Reinforcement learning requires human oversight",
    "description": "Reinforcement learning systems must have human oversight mechanisms",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "is_subclass_of", "value": "ai:ReinforcementLearning", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:HumanOversightRequirement"},
        {"property": "ai:hasTechnicalCriterion", "value": "ai:SystemAutonomy"}
    ]
}

# Collect all traditional ML rules
ALL_RULES = [
    RULE_20A,
    RULE_20B,
    RULE_21,
    RULE_22,
    RULE_23
]
