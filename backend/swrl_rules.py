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

# REGLAS DE ASIGNACIÓN AUTOMÁTICA DE MODEL SCALE SEGÚN FLOPS
# Si el sistema tiene hasFLOPS < 1e12, asignar SmallModelScale
ai:SmallModelScaleRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:DatavaluedPropertyAtom ;
                          swrl:propertyPredicate ai:hasFLOPS ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "flops" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:BuiltinAtom ;
                        swrl:builtin swrlb:lessThan ;
                        swrl:arguments ( [ rdf:type swrl:Variable ; rdfs:label "flops" ] "1000000000000"^^xsd:double )
                    ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasModelScale ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:SmallModelScale ] ;
                rdf:rest rdf:nil ] .

# Si el sistema tiene 1e12 <= hasFLOPS < 1e16, asignar RegularModelScale
ai:RegularModelScaleRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:DatavaluedPropertyAtom ;
                          swrl:propertyPredicate ai:hasFLOPS ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "flops" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:BuiltinAtom ;
                        swrl:builtin swrlb:greaterThanOrEqual ;
                        swrl:arguments ( [ rdf:type swrl:Variable ; rdfs:label "flops" ] "1000000000000"^^xsd:double )
                    ] ;
                    rdf:rest [ rdf:type swrl:AtomList ;
                        rdf:first [ rdf:type swrl:BuiltinAtom ;
                            swrl:builtin swrlb:lessThan ;
                            swrl:arguments ( [ rdf:type swrl:Variable ; rdfs:label "flops" ] "10000000000000000"^^xsd:double )
                        ] ;
                        rdf:rest rdf:nil
                    ]
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasModelScale ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:RegularModelScale ] ;
                rdf:rest rdf:nil ] .

# Si el sistema tiene hasFLOPS >= 1e16, asignar FoundationalModelScale
ai:FoundationalModelScaleRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:DatavaluedPropertyAtom ;
                          swrl:propertyPredicate ai:hasFLOPS ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "flops" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:BuiltinAtom ;
                        swrl:builtin swrlb:greaterThanOrEqual ;
                        swrl:arguments ( [ rdf:type swrl:Variable ; rdfs:label "flops" ] "10000000000000000"^^xsd:double )
                    ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasModelScale ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:FoundationalModelScale ] ;
                rdf:rest rdf:nil ] .

# ============================================================================
# REGLAS GENÉRICAS PARA NAVEGAR LA ONTOLOGÍA
# ============================================================================

# REGLA 1: Purpose → activatesCriterion → hasCriteria
# Si un sistema tiene un propósito, y ese propósito activa un criterio,
# entonces el sistema tiene ese criterio
ai:PurposeCriterionDerivationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "purpose" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                              swrl:propertyPredicate ai:activatesCriterion ;
                              swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "purpose" ] ;
                              swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                rdf:rest rdf:nil ] .

# REGLA 2: DeploymentContext → triggersCriterion → hasCriteria
# Si un sistema tiene un contexto de despliegue, y ese contexto dispara un criterio,
# entonces el sistema tiene ese criterio
ai:ContextCriterionDerivationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasDeploymentContext ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "context" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                              swrl:propertyPredicate ai:triggersCriterion ;
                              swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "context" ] ;
                              swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                rdf:rest rdf:nil ] .

# REGLA 3: SystemCapabilityCriteria → (actúan como criterios derivados)
# Si un sistema tiene SystemCapabilityCriteria, se trata como criterios
ai:SystemCapabilityCriterionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasSystemCapabilityCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "capability" ] ] ;
                rdf:rest rdf:nil
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "capability" ] ] ;
                rdf:rest rdf:nil ] .

# REGLA 4: Criterion → activatesRequirement → hasComplianceRequirement
# Si un sistema tiene un criterio, y ese criterio activa requisitos,
# entonces el sistema tiene esos requisitos
ai:CriterionRequirementDerivationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                              swrl:propertyPredicate ai:activatesRequirement ;
                              swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ;
                              swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "requirement" ] ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasComplianceRequirement ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "requirement" ] ] ;
                rdf:rest rdf:nil ] .

# REGLA 5: Criterion → assignsRiskLevel → hasRiskLevel
# Si un sistema tiene un criterio, y ese criterio asigna un nivel de riesgo,
# entonces el sistema tiene ese nivel de riesgo
ai:CriterionRiskLevelRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasCriteria ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ] ;
                rdf:rest [ rdf:type swrl:AtomList ;
                    rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                              swrl:propertyPredicate ai:assignsRiskLevel ;
                              swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "criterion" ] ;
                              swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "riskLevel" ] ] ;
                    rdf:rest rdf:nil
                ]
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasRiskLevel ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 [ rdf:type swrl:Variable ; rdfs:label "riskLevel" ] ] ;
                rdf:rest rdf:nil ] .

# REGLA 6: FoundationModelScale → GPAI Classification
# Si un sistema tiene FoundationModelScale, es un GPAI
ai:GPAIClassificationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasModelScale ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:FoundationModelScale ] ;
                rdf:rest rdf:nil
    ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasGPAIClassification ;
                          swrl:argument1 [ rdf:type swrl:Variable ; rdfs:label "system" ] ;
                          swrl:argument2 ai:GeneralPurposeAI ] ;
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
# Nueva regla: BiometricIdentification → BiometricSecurity
ai:BiometricIdentificationRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:BiometricIdentification ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasContextualCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:BiometricSecurity ] ;
                rdf:rest rdf:nil ] .

# NUEVAS REGLAS DE PROPÓSITO
ai:JudicialSupportRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:JudicialDecisionSupport ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:JudicialSupportCriterion ] ;
                rdf:rest rdf:nil ] .

ai:LawEnforcementSupportRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:LawEnforcementSupport ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:LawEnforcementCriterion ] ;
                rdf:rest rdf:nil ] .

ai:MigrationControlRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:MigrationControl ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:MigrationBorderCriterion ] ;
                rdf:rest rdf:nil ] .

ai:CriticalInfrastructureRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:CriticalInfrastructureOperation ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:CriticalInfrastructureCriterion ] ;
                rdf:rest rdf:nil ] .

ai:HealthCarePrivacyRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:HealthCare ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:PrivacyProtection ] ;
                rdf:rest rdf:nil ] .

ai:EducationAccessRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasPurpose ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:EducationAccess ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasNormativeCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:EducationEvaluationCriterion ] ;
                rdf:rest rdf:nil ] .

ai:BiometricEncryptionRule rdf:type swrl:Rule ;
    swrl:body [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasContextualCriterion ;
                          swrl:argument1 ?system ;
                          swrl:argument2 ai:BiometricSecurity ] ;
                rdf:rest rdf:nil ] ;
    swrl:head [ rdf:type swrl:AtomList ;
                rdf:first [ rdf:type swrl:IndividualPropertyAtom ;
                          swrl:propertyPredicate ai:hasTechnicalRequirement ;
                          swrl:argument1 ?system ;
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

ai:EducationEvaluationCriterion rdf:type ai:NormativeCriterion ;
    rdfs:label "EducationEvaluationCriterion" ;
    rdfs:comment "Education or Vocational Training Evaluation criterion" .

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

# NUEVOS CONCEPTOS Y REQUISITOS
ai:JudicialSupportCriterion rdf:type ai:NormativeCriterion ;
    rdfs:label "JudicialSupportCriterion" ;
    rdfs:comment "Criterion for judicial decision support systems" .

ai:DueProcess rdf:type ai:NormativeCriterion ;
    rdfs:label "DueProcess" ;
    rdfs:comment "Due process criterion for legal systems" .

ai:ConformityAssessmentRequirement rdf:type ai:Requirement ;
    rdfs:label "ConformityAssessmentRequirement" ;
    rdfs:comment "Conformity assessment requirement" .

ai:RiskManagementRequirement rdf:type ai:Requirement ;
    rdfs:label "RiskManagementRequirement" ;
    rdfs:comment "Risk management requirement" .

ai:AccuracyEvaluationRequirement rdf:type ai:Requirement ;
    rdfs:label "AccuracyEvaluationRequirement" ;
    rdfs:comment "Accuracy evaluation requirement" .

ai:CybersecurityRequirement rdf:type ai:TechnicalRequirement ;
    rdfs:label "CybersecurityRequirement" ;
    rdfs:comment "Cybersecurity requirement" .

ai:PerformanceMonitoringRequirement rdf:type ai:TechnicalRequirement ;
    rdfs:label "PerformanceMonitoringRequirement" ;
    rdfs:comment "Performance monitoring requirement" .

ai:TraceabilityRequirement rdf:type ai:ComplianceRequirement ;
    rdfs:label "TraceabilityRequirement" ;
    rdfs:comment "Traceability requirement for education systems" .

# PROPÓSITOS ADICIONALES
ai:JudicialDecisionSupport rdf:type ai:Purpose ;
    rdfs:label "JudicialDecisionSupport" ;
    rdfs:comment "Judicial decision support purpose" .

ai:LawEnforcementSupport rdf:type ai:Purpose ;
    rdfs:label "LawEnforcementSupport" ;
    rdfs:comment "Law enforcement support purpose" .

ai:MigrationControl rdf:type ai:Purpose ;
    rdfs:label "MigrationControl" ;
    rdfs:comment "Migration control purpose" .

ai:CriticalInfrastructureOperation rdf:type ai:Purpose ;
    rdfs:label "CriticalInfrastructureOperation" ;
    rdfs:comment "Critical infrastructure operation purpose" .

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