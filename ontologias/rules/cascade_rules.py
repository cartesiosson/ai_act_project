# =============================================================
# REGLAS DE CASCADA - ACTIVACIONES DE REQUISITOS
# Reglas que se activan cuando se cumplen criterios técnicos
# =============================================================

# REGLA 20: SystemicRisk -> múltiples requisitos de mitigación
RULE_20A = {
    "id": "rule20a_systemic_risk_management",
    "name": "Systemic risk triggers risk management",
    "description": "Systems with systemic risk require enhanced risk management",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:SystemicRisk", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:RiskManagementRequirement"}
    ]
}

RULE_20B = {
    "id": "rule20b_systemic_post_market",
    "name": "Systemic risk triggers post-market monitoring",
    "description": "Systems with systemic risk require enhanced monitoring",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:SystemicRisk", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:PostMarketMonitoringRequirement"}
    ]
}

RULE_20C = {
    "id": "rule20c_systemic_cybersecurity",
    "name": "Systemic risk triggers cybersecurity requirements",
    "description": "Systems with systemic risk require advanced cybersecurity",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:SystemicRisk", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:CybersecurityRequirement"}
    ]
}

# REGLA 21: HighImpactCapabilities -> evaluaciones especializadas
RULE_21 = {
    "id": "rule21_high_impact_assessment",
    "name": "High impact capabilities trigger conformity assessment",
    "description": "Systems with high impact capabilities require specialized evaluation",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:HighImpactCapabilities", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:ConformityAssessmentRequirement"}
    ]
}

# REGLA 22: AdaptiveCapability -> supervisión continua
RULE_22A = {
    "id": "rule22a_adaptive_oversight",
    "name": "Adaptive systems require human oversight",
    "description": "Adaptive systems need continuous human supervision",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:AdaptiveCapability", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:HumanOversightRequirement"}
    ]
}

RULE_22B = {
    "id": "rule22b_adaptive_logging",
    "name": "Adaptive systems require event logging",
    "description": "Adaptive systems need comprehensive logging",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:AdaptiveCapability", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:EventLoggingRequirement"}
    ]
}

# REGLA 23: ModelComplexity -> requisitos de transparencia
RULE_23A = {
    "id": "rule23a_complex_transparency",
    "name": "Complex models require transparency",
    "description": "Complex models need enhanced transparency measures",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:ModelComplexity", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:TransparencyRequirement"}
    ]
}

RULE_23B = {
    "id": "rule23b_complex_auditability",
    "name": "Complex models require auditability",
    "description": "Complex models need comprehensive audit capabilities",
    "conditions": [
        {"property": "ai:hasTechnicalCriterion", "operator": "==", "value": "ai:ModelComplexity", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:Auditability"}
    ]
}

# Lista de todas las reglas de cascada
CASCADE_RULES = [
    RULE_20A, RULE_20B, RULE_20C, RULE_21, 
    RULE_22A, RULE_22B, RULE_23A, RULE_23B
]