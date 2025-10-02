#!/usr/bin/env python3
"""
Script para generar traducciones en español para la ontología AI Act
"""

# Diccionario de traducciones para términos específicos del AI Act
TRANSLATIONS = {
    # Clases principales
    "Criterion": "Criterio",
    "Intelligent System": "Sistema Inteligente", 
    "EndUser": "Usuario Final",
    "ProfessionalUser": "Usuario Profesional",
    "Provider": "Proveedor",
    "Deployer": "Implementador",
    "Distributor": "Distribuidor", 
    "Importer": "Importador",
    "Evidence": "Evidencia",
    "Oversight Body": "Organismo de Supervisión",
    
    # Niveles de riesgo
    "High Risk": "Alto Riesgo",
    "Limited Risk": "Riesgo Limitado", 
    "Minimal Risk": "Riesgo Mínimo",
    "Unacceptable Risk": "Riesgo Inaceptable",
    
    # Criterios
    "Contextual Criterion": "Criterio Contextual",
    "Technical Criterion": "Criterio Técnico",
    "Biometric Identification or Categorization": "Identificación o Categorización Biométrica",
    "Management of Critical Infrastructure": "Gestión de Infraestructura Crítica",
    "Education or Vocational Training Evaluation": "Evaluación Educativa o de Formación Profesional",
    "Law Enforcement and Risk Assessment": "Aplicación de la Ley y Evaluación de Riesgo",
    "Migration, Asylum and Border Control": "Migración, Asilo y Control Fronterizo",
    "Lacks Human Oversight": "Carece de Supervisión Humana",
    "Social scoring": "Puntuación social",
    "Subliminal manipulation": "Manipulación subliminal", 
    "Deepfake generation": "Generación de deepfakes",
    "Biometric identification or categorization": "Identificación o categorización biométrica",
    
    # Contextos y propósitos
    "Education": "Educación",
    "Education Access": "Acceso a la Educación",
    "Healthcare": "Atención Sanitaria",
    "Migration Control": "Control Migratorio",
    "Public Service Allocation": "Asignación de Servicios Públicos",
    "Recruitment and Employment": "Reclutamiento y Empleo",
    "Judicial Decision Support": "Apoyo a Decisiones Judiciales",
    "Law Enforcement Support": "Apoyo a la Aplicación de la Ley",
    "Affects fundamental rights recognition": "Afecta el reconocimiento de derechos fundamentales",
    
    # Requisitos
    "Logging Requirement": "Requisito de Registro",
    "Security Requirement": "Requisito de Seguridad", 
    "Robustness Requirement": "Requisito de Robustez",
    "Transparency Requirement": "Requisito de Transparencia",
    "Accuracy Evaluation Requirement": "Requisito de Evaluación de Precisión",
    "Data Governance Requirement": "Requisito de Gobernanza de Datos",
    "Fundamental Rights Assessment Requirement": "Requisito de Evaluación de Derechos Fundamentales",
    "Human Oversight Requirement": "Requisito de Supervisión Humana",
    "Post-market monitoring requirement": "Requisito de monitoreo post-comercialización",
    "Technical Requirement": "Requisito Técnico",
    
    # Evaluaciones
    "PostDeployment Assessment": "Evaluación Post-Despliegue",
    "PreDeployment Assessment": "Evaluación Pre-Despliegue",
    
    # Datos y contextos
    "Training Data Origin": "Origen de Datos de Entrenamiento",
    "Deployment Context": "Contexto de Despliegue",
    "Interface Specification": "Especificación de Interfaz",
    
    # Propiedades
    "activates requirement": "activa requisito",
    "assessed system": "sistema evaluado", 
    "assigned risk level": "nivel de riesgo asignado",
    "assigns risk level": "asigna nivel de riesgo",
    "considers criterion": "considera criterio",
    "deploys system": "despliega sistema",
    "distributes system": "distribuye sistema", 
    "expected risk level": "nivel de riesgo esperado",
    "generates evidence": "genera evidencia",
    "has name": "tiene nombre",
    "has normative criterion": "tiene criterio normativo", 
    "has purpose": "tiene propósito",
    "has compliance requirement": "tiene requisito de cumplimiento",
    "has risk level": "tiene nivel de riesgo",
    "has technical criterion": "tiene criterio técnico",
    "has technical requirement": "tiene requisito técnico",
    "has training data origin": "tiene origen de datos de entrenamiento",
    "has version": "tiene versión",
    "imports system": "importa sistema",
    "is monitored by": "es supervisado por",
    "justification note": "nota de justificación",
    "justified by criterion": "justificado por criterio", 
    "provides evidence for": "proporciona evidencia para",
    "provides system": "proporciona sistema",
    "requires compliance": "requiere cumplimiento",
    "triggers compliance requirement": "activa requisito de cumplimiento",
    "triggers criterion": "activa criterio",
    "uses system": "usa sistema"
}

# Diccionario de comentarios/descripciones
COMMENT_TRANSLATIONS = {
    "A general criterion used for risk assessment, compliance, or classification of AI systems under the EU AI Act.": 
        "Criterio general utilizado para la evaluación de riesgos, cumplimiento o clasificación de sistemas de IA según el AI Act de la UE.",
    
    "Artificial Intelligence system as defined by the EU AI Act: a machine-based system designed to operate with varying levels of autonomy and that may exhibit adaptiveness after deployment, which, for explicit or implicit objectives, infers, recommends, or decides outputs influencing physical or virtual environments.":
        "Sistema de inteligencia artificial según se define en el AI Act de la UE: sistema basado en máquinas diseñado para operar con diversos niveles de autonomía y que puede mostrar adaptabilidad después del despliegue, que, para objetivos explícitos o implícitos, infiere, recomienda o decide resultados que influyen en entornos físicos o virtuales.",
    
    "This criterion reflects situations where an AI system may influence or condition the recognition, access or exercise of fundamental rights, in line with Article 6(2) of the EU AI Act.":
        "Este criterio refleja situaciones en las que un sistema de IA puede influir o condicionar el reconocimiento, acceso o ejercicio de derechos fundamentales, conforme al Artículo 6(2) del AI Act de la UE.",
    
    "End user who interacts with the system without participating in its development or deployment.":
        "Usuario final que interactúa con el sistema sin participar en su desarrollo o despliegue.",
    
    "Professional user who uses the system in the exercise of their profession.":
        "Usuario profesional que utiliza el sistema en el ejercicio de su profesión.",
    
    "Technical requirement for AI systems to log events or actions for traceability and accountability.":
        "Requisito técnico para que los sistemas de IA registren eventos o acciones para trazabilidad y rendición de cuentas.",
    
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
    
    "Origin of the training data used by an AI system (e.g., internal, external, synthetic).":
        "Origen de los datos de entrenamiento utilizados por un sistema de IA (por ejemplo, internos, externos, sintéticos).",
    
    "The context or environment in which an AI system is deployed (e.g., healthcare, public services, education).":
        "El contexto o entorno en el que se despliega un sistema de IA (por ejemplo, atención sanitaria, servicios públicos, educación).",
    
    "Technical specification of an interface used by an artificial intelligence system to communicate with other systems or users.":
        "Especificación técnica de una interfaz utilizada por un sistema de inteligencia artificial para comunicarse con otros sistemas o usuarios.",
    
    "A document, record, or artifact that serves as proof of compliance or assessment for an AI system.":
        "Documento, registro o artefacto que sirve como prueba de cumplimiento o evaluación para un sistema de IA.",
    
    "Criterion based on the structure, operation or technical design of the system.":
        "Criterio basado en la estructura, funcionamiento o diseño técnico del sistema.",
    
    "Technical requirement that an artificial intelligence system must comply with according to the AI Act, such as robustness, security, traceability or cybersecurity.":
        "Requisito técnico que debe cumplir un sistema de inteligencia artificial conforme al AI Act, como robustez, seguridad, trazabilidad o ciberseguridad.",
    
    # Propiedades - comentarios
    "Indicates that a criterion activates or makes applicable a compliance requirement.":
        "Indica que un criterio activa o hace aplicable un requisito de cumplimiento.",
    
    "Associates a criterion with the risk level it determines for an AI system.":
        "Asocia un criterio con el nivel de riesgo que determina para un sistema de IA.",
    
    "Relates an actor of type 'Deployer' with the corresponding AI system.":
        "Relaciona un actor de tipo 'Implementador' con el sistema de IA correspondiente.",
    
    "Relates an actor of type 'Distributor' with the corresponding AI system.":
        "Relaciona un actor de tipo 'Distribuidor' con el sistema de IA correspondiente.",
    
    "Relates an actor of type 'Importer' with the corresponding AI system.":
        "Relaciona un actor de tipo 'Importador' con el sistema de IA correspondiente.",
    
    "Relates an actor of type 'Provider' with the corresponding AI system.":
        "Relaciona un actor de tipo 'Proveedor' con el sistema de IA correspondiente.",
    
    "Relates an actor of type 'User' with the corresponding AI system.":
        "Relaciona un actor de tipo 'Usuario' con el sistema de IA correspondiente.",
    
    "Indicates that an instrument or process produces evidence for compliance or assessment.":
        "Indica que un instrumento o proceso produce evidencia para cumplimiento o evaluación.",
    
    "Associates an AI system with a normative criterion that applies to it.":
        "Asocia un sistema de IA con un criterio normativo que le aplica.",
    
    "Associates an AI system with a technical criterion that applies to it.":
        "Asocia un sistema de IA con un criterio técnico que le aplica.",
    
    "Indicates the criteria that justify the compliance requirement.":
        "Indica los criterios que justifican el requisito de cumplimiento.",
    
    "Indicates that a piece of evidence documents compliance with a specific requirement.":
        "Indica que una evidencia documenta el cumplimiento de un requisito específico.",
    
    "Compliance requirements arising from the system's risk assessment.":
        "Requisitos de cumplimiento derivados de la evaluación de riesgo del sistema.",
    
    "Indicates that a criterion activates or triggers a specific compliance requirement.":
        "Indica que un criterio activa o dispara un requisito de cumplimiento específico.",
    
    "Indicates that a deployment context or purpose activates or triggers a specific criterion.":
        "Indica que un contexto de despliegue o propósito activa o dispara un criterio específico."
}

def generate_translations():
    """Genera un reporte con todas las traducciones sugeridas"""
    
    print("=== TRADUCCIONES SUGERIDAS PARA LA ONTOLOGÍA AI ACT ===\n")
    
    print("📝 ETIQUETAS (rdfs:label):")
    print("=" * 60)
    for en, es in TRANSLATIONS.items():
        print(f'EN: "{en}"')
        print(f'ES: "{es}"')
        print("-" * 40)
    
    print("\n💬 COMENTARIOS (rdfs:comment):")
    print("=" * 60)
    for en, es in COMMENT_TRANSLATIONS.items():
        print(f'EN: "{en[:80]}..."')
        print(f'ES: "{es[:80]}..."')
        print("-" * 40)

if __name__ == "__main__":
    generate_translations()