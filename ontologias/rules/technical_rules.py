# =============================================================
# REGLAS TÉCNICAS PARA CRITERIOS INTERNOS GPAI
# Formato simplificado para procesamiento Python
# =============================================================

# REGLA 13: Modelos con >10^25 FLOPs -> SystemicRisk
RULE_13 = {
    "id": "rule13_flops_systemic_risk",
    "name": "High computational FLOPs trigger systemic risk",
    "description": "Models with computation >10^25 FLOPs are classified as systemic risk (Article 51)",
    "conditions": [
        {"property": "ai:hasComputationFLOPs", "operator": ">", "value": 1e25, "type": "float"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:SystemicRisk"}
    ]
}

# REGLA 14: Modelos con >1B parámetros -> HighImpactCapabilities
RULE_14 = {
    "id": "rule14_params_high_impact",
    "name": "High parameter count triggers high impact capabilities",
    "description": "Models with >1 billion parameters have high impact capabilities",
    "conditions": [
        {"property": "ai:hasParameterCount", "operator": ">", "value": 1000000000, "type": "int"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:HighImpactCapabilities"}
    ]
}

# REGLA 15: Alta autonomía (>0.8) -> LacksHumanOversight
RULE_15 = {
    "id": "rule15_autonomy_oversight",
    "name": "High autonomy indicates lack of human oversight",
    "description": "Systems with autonomy level >0.8 lack adequate human oversight",
    "conditions": [
        {"property": "ai:hasAutonomyLevel", "operator": ">", "value": 0.8, "type": "float"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:LacksHumanOversight"}
    ]
}

# REGLA 16: Sistema adaptativo -> AdaptiveCapability
RULE_16 = {
    "id": "rule16_adaptive_capability",
    "name": "Adaptive systems trigger adaptive capability criteria",
    "description": "Systems that continue learning after deployment",
    "conditions": [
        {"property": "ai:isAdaptiveSystem", "operator": "==", "value": True, "type": "bool"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:AdaptiveCapability"}
    ]
}

# REGLA 17: Alto alcance de mercado (>10,000 usuarios) -> SystemicRisk
RULE_17 = {
    "id": "rule17_market_reach_systemic",
    "name": "High market reach triggers systemic risk",
    "description": "Systems with >10,000 users have systemic risk potential",
    "conditions": [
        {"property": "ai:hasMarketReach", "operator": ">", "value": 10000, "type": "int"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:SystemicRisk"}
    ]
}

# REGLA 18: Baja precisión (<0.85) -> AccuracyLevel
RULE_18 = {
    "id": "rule18_accuracy_level",
    "name": "Low accuracy triggers accuracy level criteria",
    "description": "Systems with accuracy <0.85 require accuracy evaluation",
    "conditions": [
        {"property": "ai:hasAccuracyRate", "operator": "<", "value": 0.85, "type": "float"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:AccuracyLevel"}
    ]
}

# REGLA 19a: Modelos Foundation -> ModelComplexity
RULE_19A = {
    "id": "rule19a_foundation_complexity",
    "name": "Foundation models trigger complexity criteria",
    "description": "Foundation models have inherent complexity",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:FoundationModel", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelComplexity"}
    ]
}

# REGLA 19b: Modelos Transformer -> ModelComplexity
RULE_19B = {
    "id": "rule19b_transformer_complexity",
    "name": "Transformer models trigger complexity criteria",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:TransformerModel", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelComplexity"}
    ]
}

# REGLA 19c: Modelos Generativos -> ModelComplexity
RULE_19C = {
    "id": "rule19c_generative_complexity",
    "name": "Generative models trigger complexity criteria",
    "conditions": [
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:GenerativeModel", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ModelComplexity"}
    ]
}

# Lista de todas las reglas técnicas
TECHNICAL_RULES = [
    RULE_13, RULE_14, RULE_15, RULE_16, RULE_17, 
    RULE_18, RULE_19A, RULE_19B, RULE_19C
]