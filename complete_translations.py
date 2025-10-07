#!/usr/bin/env python3
"""
Script completo para añadir todas las traducciones faltantes en la ontología
"""

import re

def complete_translations(file_path):
    """Añade todas las traducciones faltantes identificadas por el análisis"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Diccionario de entidades que necesitan traducciones
    missing_translations = {
        # Clases principales sin etiquetas en español
        'ai:PostDeploymentAssessment': 'Evaluación Post-Despliegue',
        'ai:PreDeploymentAssessment': 'Evaluación Pre-Despliegue', 
        'ai:ProfessionalUser': 'Usuario Profesional',
        'ai:PublicServiceAllocation': 'Asignación de Servicios Públicos',
        'ai:RecruitmentOrEmployment': 'Reclutamiento y Empleo',
        'ai:SecurityRequirement': 'Requisito de Seguridad',
        'ai:RobustnessRequirement': 'Requisito de Robustez',
        'ai:TransparencyRequirement': 'Requisito de Transparencia',
        'ai:ContextualCriterion': 'Criterio Contextual',
        'ai:Deployer': 'Implementador',
        'ai:Distributor': 'Distribuidor',
        'ai:Importer': 'Importador',
        'ai:InterfaceSpec': 'Especificación de Interfaz',
        'ai:LimitedRisk': 'Riesgo Limitado',
        'ai:MinimalRisk': 'Riesgo Mínimo',
        'ai:HighRisk': 'Alto Riesgo',
        'ai:UnacceptableRisk': 'Riesgo Inaceptable',
        'ai:OversightBody': 'Organismo de Supervisión',
        'ai:Provider': 'Proveedor',
        'ai:AccuracyEvaluationRequirement': 'Requisito de Evaluación de Precisión',
        'ai:BiometricIdentificationCriterion': 'Criterio de Identificación Biométrica',
        'ai:Evidence': 'Evidencia',
        'ai:SocialScoring': 'Puntuación Social',
        'ai:SubliminalManipulation': 'Manipulación Subliminal',
        'ai:DeepfakeGeneration': 'Generación de Deepfakes',
        'ai:BiometricIdentificationOrCategorization': 'Identificación o Categorización Biométrica',
        'ai:DataGovernanceRequirement': 'Requisito de Gobernanza de Datos',
        'ai:FundamentalRightsAssessmentRequirement': 'Requisito de Evaluación de Derechos Fundamentales',
        'ai:HumanOversightRequirement': 'Requisito de Supervisión Humana',
        'ai:LacksHumanOversight': 'Carece de Supervisión Humana',
        'ai:LawEnforcementCriterion': 'Criterio de Aplicación de la Ley',
        'ai:MigrationBorderCriterion': 'Criterio de Migración y Control Fronterizo',
        'ai:PostMarketMonitoringRequirement': 'Requisito de Monitoreo Post-Comercialización',
        'ai:TrainingDataOrigin': 'Origen de Datos de Entrenamiento',
        'ai:DeploymentContext': 'Contexto de Despliegue',
        'ai:TechnicalRequirement': 'Requisito Técnico',
        'ai:CriticalInfrastructureCriterion': 'Criterio de Infraestructura Crítica',
        'ai:EducationEvaluationCriterion': 'Criterio de Evaluación Educativa',
        'ai:TechnicalCriterion': 'Criterio Técnico',
        
        # Propiedades sin etiquetas en español
        'ai:activatesRequirement': 'activa requisito',
        'ai:assessedSystem': 'sistema evaluado',
        'ai:assignedRiskLevel': 'nivel de riesgo asignado',
        'ai:assignsRiskLevel': 'asigna nivel de riesgo',
        'ai:considersCriterion': 'considera criterio',
        'ai:deploysSystem': 'despliega sistema',
        'ai:distributesSystem': 'distribuye sistema',
        'ai:expectedRiskLevel': 'nivel de riesgo esperado',
        'ai:generatesEvidence': 'genera evidencia',
        'ai:hasName': 'tiene nombre',
        'ai:hasNormativeCriterion': 'tiene criterio normativo',
        'ai:hasPurpose': 'tiene propósito',
        'ai:hasRequirement': 'tiene requisito de cumplimiento',
        'ai:hasRiskLevel': 'tiene nivel de riesgo',
        'ai:hasTechnicalCriterion': 'tiene criterio técnico',
        'ai:hasTechnicalRequirement': 'tiene requisito técnico',
        'ai:hasTrainingDataOrigin': 'tiene origen de datos de entrenamiento',
        'ai:hasVersion': 'tiene versión',
        'ai:importsSystem': 'importa sistema',
        'ai:isMonitoredBy': 'es supervisado por',
        'ai:justificationNote': 'nota de justificación',
        'ai:justifiedByCriterion': 'justificado por criterio',
        'ai:providesEvidenceFor': 'proporciona evidencia para',
        'ai:providesSystem': 'proporciona sistema',
        'ai:requiresCompliance': 'requiere cumplimiento',
        'ai:triggersComplianceRequirement': 'activa requisito de cumplimiento',
        'ai:triggersCriterion': 'activa criterio',
        'ai:usesSystem': 'usa sistema'
    }
    
    # Función para añadir etiqueta en español
    def add_spanish_label(match):
        entity = match.group(1)
        english_label = match.group(2)
        rest = match.group(3)
        
        if entity in missing_translations:
            spanish_label = missing_translations[entity]
            # Añadir la etiqueta en español
            return f'{entity} rdfs:label "{english_label}"@en,\n        "{spanish_label}"@es{rest}'
        return match.group(0)
    
    # Patrón para encontrar entidades con solo etiqueta en inglés
    pattern = r'(ai:\w+)\s+.*?rdfs:label\s+"([^"]+)"@en\s*([;\s])'
    content = re.sub(pattern, add_spanish_label, content, flags=re.DOTALL)
    
    # Función para añadir comentarios en español donde falten
    def add_spanish_comments(text):
        # Comentarios específicos que necesitan traducción
        comment_translations = {
            "End user who interacts with the system without participating in its development or deployment.": 
                "Usuario final que interactúa con el sistema sin participar en su desarrollo o despliegue.",
            "Professional user who uses the system in the exercise of their profession.":
                "Usuario profesional que utiliza el sistema en el ejercicio de su profesión.",
            "Technical requirement for AI systems to ensure security, such as protection against unauthorized access or attacks.":
                "Requisito técnico para que los sistemas de IA garanticen la seguridad, como protección contra accesos no autorizados o ataques.",
            "Technical requirement for AI systems to ensure robustness, such as resilience to errors or adversarial attacks.":
                "Requisito técnico para que los sistemas de IA aseguren la robustez, como resistencia a errores o ataques adversarios.",
            "Technical requirement for AI systems to provide transparency, such as disclosure of AI use or explainability.":
                "Requisito técnico para que los sistemas de IA proporcionen transparencia, como divulgación del uso de IA o explicabilidad.",
            "Risk assessment or evaluation performed after the deployment of an AI system.":
                "Evaluación o valoración de riesgos realizada después del despliegue de un sistema de IA.",
            "Risk assessment or evaluation performed before the deployment of an AI system.":
                "Evaluación o valoración de riesgos realizada antes del despliegue de un sistema de IA.",
            "A document, record, or artifact that serves as proof of compliance or assessment for an AI system.":
                "Documento, registro o artefacto que sirve como prueba de cumplimiento o evaluación para un sistema de IA.",
        }
        
        for en_comment, es_comment in comment_translations.items():
            if en_comment in text and es_comment not in text:
                text = text.replace(
                    f'rdfs:comment "{en_comment}"@en ;',
                    f'rdfs:comment "{en_comment}"@en,\n        "{es_comment}"@es ;'
                )
        
        return text
    
    content = add_spanish_comments(content)
    
    # Escribir el archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Todas las traducciones han sido aplicadas")
    print("📋 Ejecuta el análisis nuevamente para verificar los resultados")

if __name__ == "__main__":
    ontology_file = "/home/cartesio/workspace/FTM/ai_act_project/ontologias/versions/0.36.0/ontologia-v0.36.0.ttl"
    complete_translations(ontology_file)