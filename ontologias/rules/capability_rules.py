# =============================================================
# REGLAS DE CAPACIDAD DEL SISTEMA (24-30)
# Reglas que procesan hasSystemCapabilityCriteria
# =============================================================

# REGLA 24: JudicialSupportCriterion -> múltiples requisitos
RULE_24A = {
    "id": "rule24a_judicial_capability_due_process",
    "name": "Judicial capability triggers due process",
    "description": "Systems with judicial capabilities must ensure due process",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:JudicialSupportCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:DueProcess"}
    ]
}

RULE_24B = {
    "id": "rule24b_judicial_capability_oversight",
    "name": "Judicial capability requires human oversight",
    "description": "Systems with judicial capabilities require human oversight",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:JudicialSupportCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:HumanOversightRequirement"}
    ]
}

RULE_24C = {
    "id": "rule24c_judicial_capability_assessment",
    "name": "Judicial capability triggers conformity assessment",
    "description": "Systems with judicial capabilities need conformity assessment",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:JudicialSupportCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:ConformityAssessmentRequirement"}
    ]
}

# REGLA 25: BiometricIdentificationCriterion -> múltiples requisitos
RULE_25A = {
    "id": "rule25a_biometric_capability_security",
    "name": "Biometric capability triggers security measures",
    "description": "Systems with biometric capabilities require enhanced security",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:BiometricIdentificationCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasContextualCriterion", "value": "ai:BiometricSecurity"}
    ]
}

RULE_25B = {
    "id": "rule25b_biometric_capability_encryption",
    "name": "Biometric capability requires data encryption",
    "description": "Systems with biometric capabilities need data encryption",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:BiometricIdentificationCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalRequirement", "value": "ai:DataEncryption"}
    ]
}

RULE_25C = {
    "id": "rule25c_biometric_capability_governance",
    "name": "Biometric capability triggers data governance",
    "description": "Systems with biometric capabilities require data governance",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:BiometricIdentificationCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:DataGovernanceRequirement"}
    ]
}

# REGLA 26: RecruitmentEmploymentCriterion -> múltiples requisitos
RULE_26A = {
    "id": "rule26a_recruitment_capability_nondiscrimination",
    "name": "Recruitment capability triggers non-discrimination",
    "description": "Systems with recruitment capabilities must ensure non-discrimination",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:RecruitmentEmploymentCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:NonDiscrimination"}
    ]
}

RULE_26B = {
    "id": "rule26b_recruitment_capability_transparency",
    "name": "Recruitment capability requires transparency",
    "description": "Systems with recruitment capabilities need transparency",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:RecruitmentEmploymentCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:TransparencyRequirement"}
    ]
}

RULE_26C = {
    "id": "rule26c_recruitment_capability_rights",
    "name": "Recruitment capability triggers rights assessment",
    "description": "Systems with recruitment capabilities need fundamental rights assessment",
    "conditions": [
        {"property": "ai:hasSystemCapabilityCriteria", "operator": "==", "value": "ai:RecruitmentEmploymentCriterion", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasRequirement", "value": "ai:FundamentalRightsAssessmentRequirement"}
    ]
}

# Lista de todas las reglas de capacidad
CAPABILITY_RULES = [
    RULE_24A, RULE_24B, RULE_24C,
    RULE_25A, RULE_25B, RULE_25C, 
    RULE_26A, RULE_26B, RULE_26C
]