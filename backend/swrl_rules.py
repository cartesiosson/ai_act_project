"""
Reglas SWRL para inferencia automática de criterios y requisitos del AI Act
"""

# Reglas SWRL completas que implementan la lógica del AI Act
AI_ACT_SWRL_RULES = """
@prefix ai: <http://ai-act.eu/ai#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ============================================================================
# REGLAS SWRL PARA EL AI ACT - INFERENCIAS SEMÁNTICAS COMPLETAS
# ============================================================================

# Regla 1: Sistemas educativos requieren protección de menores
ai:EducationProtectionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:EducationAccess ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ProtectionOfMinors ] ;
                rdf:rest rdf:nil ] .

# Regla 2: Sistemas de empleo requieren no discriminación  
ai:EmploymentNonDiscriminationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:Employment ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:NonDiscrimination ] ;
                rdf:rest rdf:nil ] .

# Regla 3: Sistemas de salud requieren privacidad
ai:HealthCarePrivacyRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasMainPurpose ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:HealthCare ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:PrivacyProtection ] ;
                rdf:rest rdf:nil ] .

# Regla 4: Sistemas de aplicación de la ley requieren due process
ai:LawEnforcementDueProcessRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasMainPurpose ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:LawEnforcement ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:DueProcess ] ;
                rdf:rest rdf:nil ] .

# Regla 4.2: Sistemas desplegados en contexto educativo requieren protección de menores
ai:EducationContextProtectionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasDeploymentContext ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:Education ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ProtectionOfMinors ] ;
                rdf:rest rdf:nil ] .

# Regla 5: Procesamiento en tiempo real requiere criterios de performance
ai:RealTimePerformanceRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasDeploymentContext ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:RealTimeProcessing ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:PerformanceRequirements ] ;
                rdf:rest rdf:nil ] .

# Regla 6: Alto volumen requiere escalabilidad
ai:HighVolumeScalabilityRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasDeploymentContext ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:HighVolumeProcessing ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ScalabilityRequirements ] ;
                rdf:rest rdf:nil ] .

# Regla 7: Datos biométricos requieren seguridad especial
ai:BiometricSecurityRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:processesDataType ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:BiometricData ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasContextualCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:BiometricSecurity ] ;
                rdf:rest rdf:nil ] .

# Regla 8: Datos de menores requieren protección infantil
ai:MinorDataProtectionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:processesDataType ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:MinorData ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasContextualCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ChildProtection ] ;
                rdf:rest rdf:nil ] .

# Regla 9: Protección de menores requiere consentimiento parental
ai:MinorConsentRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ProtectionOfMinors ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasRequirement ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:ParentalConsent ] ;
                rdf:rest rdf:nil ] .

# Regla 10: Performance requiere métricas de latencia
ai:PerformanceLatencyRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:PerformanceRequirements ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalRequirement ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:LatencyMetrics ] ;
                rdf:rest rdf:nil ] .

# Regla 11: Seguridad biométrica requiere cifrado
ai:BiometricEncryptionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasContextualCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:BiometricSecurity ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalRequirement ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:DataEncryption ] ;
                rdf:rest rdf:nil ] .

# Regla 12: No discriminación requiere auditabilidad
ai:NonDiscriminationAuditRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:NonDiscrimination ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasRequirement ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:Auditability ] ;
                rdf:rest rdf:nil ] .
"""

def get_swrl_rules() -> str:
    """Retorna las reglas SWRL completas para inferencia del AI Act"""
    return AI_ACT_SWRL_RULES

def get_ai_act_concepts() -> str:
    """Retorna las definiciones de conceptos base del AI Act necesarios para las reglas SWRL"""
    return """
# ============================================================================
# DEFINICIONES DE CONCEPTOS BASE DEL AI ACT
# ============================================================================

# Propósitos principales
ai:EducationAccess rdf:type ai:Purpose ;
    rdfs:label "EducationAccess" ;
    rdfs:comment "Educational access and assessment systems" .

ai:Education rdf:type ai:DeploymentContext ;
    rdfs:label "Education" ;
    rdfs:comment "Educational deployment context" .

ai:Employment rdf:type ai:Purpose ;
    rdfs:label "Employment" ;
    rdfs:comment "Employment and recruitment systems" .

ai:HealthCare rdf:type ai:Purpose ;
    rdfs:label "HealthCare" ;
    rdfs:comment "Healthcare and medical systems" .

ai:LawEnforcement rdf:type ai:Purpose ;
    rdfs:label "LawEnforcement" ;
    rdfs:comment "Law enforcement and justice systems" .

# Contextos de despliegue
ai:RealTimeProcessing rdf:type ai:DeploymentContext ;
    rdfs:label "RealTimeProcessing" ;
    rdfs:comment "Real-time processing environment" .

ai:HighVolumeProcessing rdf:type ai:DeploymentContext ;
    rdfs:label "HighVolumeProcessing" ;
    rdfs:comment "High-volume data processing environment" .

# Tipos de datos
ai:BiometricData rdf:type ai:DataType ;
    rdfs:label "BiometricData" ;
    rdfs:comment "Biometric identification data" .

ai:MinorData rdf:type ai:DataType ;
    rdfs:label "MinorData" ;
    rdfs:comment "Data related to minors" .

# Criterios normativos
ai:ProtectionOfMinors rdf:type ai:NormativeCriterion ;
    rdfs:label "ProtectionOfMinors" ;
    rdfs:comment "Protection of minors criterion" .

ai:NonDiscrimination rdf:type ai:NormativeCriterion ;
    rdfs:label "NonDiscrimination" ;
    rdfs:comment "Non-discrimination criterion" .

ai:PrivacyProtection rdf:type ai:NormativeCriterion ;
    rdfs:label "PrivacyProtection" ;
    rdfs:comment "Privacy protection criterion" .

ai:DueProcess rdf:type ai:NormativeCriterion ;
    rdfs:label "DueProcess" ;
    rdfs:comment "Due process criterion" .

# Criterios técnicos
ai:PerformanceRequirements rdf:type ai:TechnicalCriterion ;
    rdfs:label "PerformanceRequirements" ;
    rdfs:comment "Performance requirements criterion" .

ai:ScalabilityRequirements rdf:type ai:TechnicalCriterion ;
    rdfs:label "ScalabilityRequirements" ;
    rdfs:comment "Scalability requirements criterion" .

# Criterios contextuales
ai:BiometricSecurity rdf:type ai:ContextualCriterion ;
    rdfs:label "BiometricSecurity" ;
    rdfs:comment "Biometric security criterion" .

ai:ChildProtection rdf:type ai:ContextualCriterion ;
    rdfs:label "ChildProtection" ;
    rdfs:comment "Child protection criterion" .

# Requisitos de cumplimiento
ai:ParentalConsent rdf:type ai:Requirement ;
    rdfs:label "ParentalConsent" ;
    rdfs:comment "Parental consent requirement" .

ai:Auditability rdf:type ai:Requirement ;
    rdfs:label "Auditability" ;
    rdfs:comment "Auditability requirement" .

# Requisitos técnicos
ai:LatencyMetrics rdf:type ai:TechnicalRequirement ;
    rdfs:label "LatencyMetrics" ;
    rdfs:comment "Latency metrics requirement" .

ai:DataEncryption rdf:type ai:TechnicalRequirement ;
    rdfs:label "DataEncryption" ;
    rdfs:comment "Data encryption requirement" .

"""

def get_basic_prefixes() -> str:
    """Retorna los prefijos básicos para TTL"""
    return """
@prefix ai: <http://ai-act.eu/ai#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""