# =============================================================
# REGLAS BÁSICAS CONTEXTUALES Y NORMATIVAS (1-12)
# Reglas que conectan contextos y propósitos con criterios
# =============================================================

# REGLA 1: Education Context/Purpose -> ProtectionOfMinors
RULE_01A = {
    "id": "rule01a_education_context_minors",
    "name": "Education context triggers protection of minors",
    "description": "Systems in educational context must protect minors",
    "conditions": [
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:Education", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:ProtectionOfMinors"}
    ]
}

RULE_01B = {
    "id": "rule01b_education_purpose_minors",
    "name": "Education purpose triggers protection of minors",
    "description": "Systems with educational purpose must protect minors",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:EducationAccess", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:ProtectionOfMinors"}
    ]
}

# REGLA 2: RecruitmentOrEmployment -> NonDiscrimination
RULE_02 = {
    "id": "rule02_recruitment_nondiscrimination",
    "name": "Recruitment systems require non-discrimination",
    "description": "Employment systems must ensure non-discriminatory practices",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:RecruitmentOrEmployment", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:NonDiscrimination"}
    ]
}

# REGLA 3: JudicialDecisionSupport -> JudicialSupportCriterion
RULE_03 = {
    "id": "rule03_judicial_support",
    "name": "Judicial support systems trigger specialized criteria",
    "description": "Systems supporting judicial decisions require due process",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:JudicialDecisionSupport", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:JudicialSupportCriterion"}
    ]
}

# REGLA 4: LawEnforcementSupport -> LawEnforcementCriterion
RULE_04 = {
    "id": "rule04_law_enforcement",
    "name": "Law enforcement systems trigger specialized criteria",
    "description": "Systems supporting law enforcement require strict oversight",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:LawEnforcementSupport", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:LawEnforcementCriterion"}
    ]
}

# REGLA 5: MigrationControl -> MigrationBorderCriterion
RULE_05 = {
    "id": "rule05_migration_control",
    "name": "Migration systems trigger border control criteria",
    "description": "Migration control systems require human rights protection",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:MigrationControl", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:MigrationBorderCriterion"}
    ]
}

# REGLA 6: CriticalInfrastructureOperation -> CriticalInfrastructureCriterion
RULE_06 = {
    "id": "rule06_critical_infrastructure",
    "name": "Critical infrastructure systems trigger specialized criteria",
    "description": "Systems managing critical infrastructure require high reliability",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:CriticalInfrastructureOperation", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:CriticalInfrastructureCriterion"}
    ]
}

# REGLA 7: HealthCare Purpose -> PrivacyProtection
RULE_07 = {
    "id": "rule07_healthcare_privacy",
    "name": "Healthcare systems require privacy protection",
    "description": "Healthcare systems must protect patient privacy",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:HealthCare", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:PrivacyProtection"}
    ]
}

# REGLA 8: BiometricData Processing -> BiometricSecurity
RULE_08A = {
    "id": "rule08a_biometric_data_security",
    "name": "Biometric data processing requires security measures",
    "description": "Systems processing biometric data need enhanced security",
    "conditions": [
        {"property": "ai:processesDataType", "operator": "==", "value": "ai:BiometricData", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasContextualCriterion", "value": "ai:BiometricSecurity"}
    ]
}

RULE_08B = {
    "id": "rule08b_biometric_purpose_security",
    "name": "Biometric identification triggers security criteria",
    "description": "Biometric identification systems require enhanced security",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:BiometricIdentification", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasContextualCriterion", "value": "ai:BiometricSecurity"}
    ]
}

# REGLA 9: RealTimeProcessing -> PerformanceRequirements
RULE_09 = {
    "id": "rule09_realtime_performance",
    "name": "Real-time processing requires performance criteria",
    "description": "Real-time systems need strict performance guarantees",
    "conditions": [
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:RealTimeProcessing", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:PerformanceRequirements"}
    ]
}

# REGLA 10: HighVolumeProcessing -> ScalabilityRequirements
RULE_10 = {
    "id": "rule10_highvolume_scalability",
    "name": "High volume processing requires scalability",
    "description": "High volume systems need scalability measures",
    "conditions": [
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:HighVolumeProcessing", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasTechnicalCriterion", "value": "ai:ScalabilityRequirements"}
    ]
}

# REGLA 11: Healthcare Context -> EssentialServicesAccessCriterion
RULE_11A = {
    "id": "rule11a_healthcare_essential_services",
    "name": "Healthcare context triggers essential services criteria",
    "description": "Healthcare systems provide essential services",
    "conditions": [
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:Healthcare", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:EssentialServicesAccessCriterion"}
    ]
}

# REGLA 12: PublicServices Context -> EssentialServicesAccessCriterion
RULE_12 = {
    "id": "rule12_public_essential_services",
    "name": "Public services trigger essential services criteria",
    "description": "Public services must ensure equal access",
    "conditions": [
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:PublicServices", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasNormativeCriterion", "value": "ai:EssentialServicesAccessCriterion"}
    ]
}

# Lista de todas las reglas básicas
BASE_RULES = [
    RULE_01A, RULE_01B, RULE_02, RULE_03, RULE_04, RULE_05,
    RULE_06, RULE_07, RULE_08A, RULE_08B, RULE_09, RULE_10,
    RULE_11A, RULE_12
]