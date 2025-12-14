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

# =============================================================
# ARTICLE 5: PROHIBITED PRACTICES (UNACCEPTABLE RISK) - v0.37.4
# =============================================================
# Systems triggering these rules CANNOT be deployed in the EU
# Maximum penalties: €35M or 7% global annual turnover

# REGLA ART5-1: Subliminal Manipulation Detection (Article 5.1.a)
RULE_ART5_1A = {
    "id": "rule_art5_1a_subliminal",
    "name": "Detect subliminal manipulation practices",
    "description": "Systems with subliminal manipulation purpose trigger Article 5.1.a prohibition. ABSOLUTELY PROHIBITED - NO EXCEPTIONS.",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:SubliminalManipulation", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasProhibitedPractice", "value": "ai:SubliminalManipulationCriterion"}
    ]
}

# REGLA ART5-2: Vulnerability Exploitation Detection (Article 5.1.b)
RULE_ART5_1B = {
    "id": "rule_art5_1b_vulnerability",
    "name": "Detect vulnerability exploitation practices",
    "description": "Systems with behavior manipulation purpose targeting vulnerable populations trigger Article 5.1.b prohibition. Protected groups: minors, persons with disabilities, economically disadvantaged. ABSOLUTELY PROHIBITED - NO EXCEPTIONS.",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:BehaviorManipulation", "type": "uri"},
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:VulnerablePopulationContext", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasProhibitedPractice", "value": "ai:VulnerabilityExploitationCriterion"}
    ]
}

# REGLA ART5-3: Social Scoring Detection (Article 5.1.c)
RULE_ART5_1C = {
    "id": "rule_art5_1c_social_scoring",
    "name": "Detect social scoring practices",
    "description": "Systems with social scoring purpose trigger Article 5.1.c prohibition. ONLY APPLIES TO PUBLIC AUTHORITIES. Examples: China-style 'social credit' systems. ABSOLUTELY PROHIBITED - NO EXCEPTIONS.",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:SocialScoring", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasProhibitedPractice", "value": "ai:SocialScoringCriterion"}
    ]
}

# REGLA ART5-4: Predictive Policing by Profiling Detection (Article 5.1.d)
RULE_ART5_1D = {
    "id": "rule_art5_1d_predictive_policing",
    "name": "Detect predictive policing based solely on profiling",
    "description": "Systems with crime prediction purpose using SOLELY profiling algorithms (without objective prior criminal behavior evidence) trigger Article 5.1.d prohibition. Risk assessment based on documented prior criminal behavior IS ALLOWED.",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:CrimeRiskPrediction", "type": "uri"},
        {"property": "ai:hasAlgorithmType", "operator": "==", "value": "ai:ProfilingAlgorithm", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasProhibitedPractice", "value": "ai:PredictivePolicingProfilingCriterion"}
    ]
}

# REGLA ART5-5: Real-Time Biometric Identification Detection (Article 5.1.h)
RULE_ART5_1H = {
    "id": "rule_art5_1h_realtime_biometric",
    "name": "Detect real-time remote biometric identification in public spaces",
    "description": "Systems with biometric identification purpose in real-time processing context in public spaces trigger Article 5.1.h prohibition. GENERALLY PROHIBITED with LIMITED EXCEPTIONS (Article 5.2): victim search, terrorist threat, serious crimes. Requires prior judicial authorization.",
    "conditions": [
        {"property": "ai:hasPurpose", "operator": "==", "value": "ai:BiometricIdentification", "type": "uri"},
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:RealTimeProcessing", "type": "uri"},
        {"property": "ai:hasDeploymentContext", "operator": "==", "value": "ai:PublicSpaces", "type": "uri"}
    ],
    "consequences": [
        {"property": "ai:hasProhibitedPractice", "value": "ai:RealTimeBiometricIdentificationCriterion"}
    ]
}

# Lista de todas las reglas básicas
BASE_RULES = [
    RULE_01A, RULE_01B, RULE_02, RULE_03, RULE_04, RULE_05,
    RULE_06, RULE_07, RULE_08A, RULE_08B, RULE_09, RULE_10,
    RULE_11A, RULE_12,
    RULE_ART5_1A, RULE_ART5_1B, RULE_ART5_1C, RULE_ART5_1D, RULE_ART5_1H
]