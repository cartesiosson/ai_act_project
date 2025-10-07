#!/usr/bin/env python3
"""
Script para aplicar automáticamente todas las traducciones faltantes en la ontología
"""

import re

def apply_translations(file_path):
    """Aplica las traducciones faltantes en la ontología"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de reemplazos a realizar
    replacements = [
        # Clases principales que necesitan etiquetas en español
        (r'(ai:JudicialDecisionSupport.*?rdfs:label "Judicial Decision Support"@en),(\s*"Apoyo a la decisión judicial"@es ;)',
         r'\1,\n        "Apoyo a Decisiones Judiciales"@es ;'),
        
        (r'(ai:LawEnforcementSupport.*?rdfs:label "Law Enforcement Support"@en),(\s*"Apoyo a la aplicación de la ley"@es ;)',
         r'\1,\n        "Apoyo a la Aplicación de la Ley"@es ;'),
        
        (r'(ai:LoggingRequirement.*?rdfs:label "Logging Requirement"@en),',
         r'\1,\n        "Requisito de Registro"@es ;'),
        
        (r'(ai:MigrationControl.*?rdfs:label "Migration Control"@en),(\s*"Control migratorio"@es ;)',
         r'\1,\n        "Control Migratorio"@es ;'),
        
        (r'(ai:PostDeploymentAssessment.*?rdfs:label "PostDeployment Assessment"@en),(\s*"Evaluación posterior al despliegue"@es ;)',
         r'\1,\n        "Evaluación Post-Despliegue"@es ;'),
        
        (r'(ai:PreDeploymentAssessment.*?rdfs:label "PreDeployment Assessment"@en),(\s*"Evaluación previa al despliegue"@es ;)',
         r'\1,\n        "Evaluación Pre-Despliegue"@es ;'),
        
        (r'(ai:ProfessionalUser.*?rdfs:label "ProfessionalUser"@en),(\s*"Usuario profesional"@es ;)',
         r'\1,\n        "Usuario Profesional"@es ;'),
        
        (r'(ai:PublicServiceAllocation.*?rdfs:label "Public Service Allocation"@en),(\s*"Asignación de servicios públicos"@es ;)',
         r'\1,\n        "Asignación de Servicios Públicos"@es ;'),
        
        (r'(ai:RecruitmentOrEmployment.*?rdfs:label "Recruitment and Employment"@en),(\s*"Reclutamiento y empleo"@es ;)',
         r'\1,\n        "Reclutamiento y Empleo"@es ;'),
        
        (r'(ai:SecurityRequirement.*?rdfs:label "Security Requirement"@en),(\s*"Requisito de seguridad"@es ;)',
         r'\1,\n        "Requisito de Seguridad"@es ;'),
        
        (r'(ai:RobustnessRequirement.*?rdfs:label "Robustness Requirement"@en),(\s*"Requisito de robustez"@es ;)',
         r'\1,\n        "Requisito de Robustez"@es ;'),
        
        (r'(ai:TransparencyRequirement.*?rdfs:label "Transparency Requirement"@en),(\s*"Requisito de transparencia"@es ;)',
         r'\1,\n        "Requisito de Transparencia"@es ;'),
    ]
    
    # Aplicar cada reemplazo
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Escribir el archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Traducciones aplicadas exitosamente")

if __name__ == "__main__":
    ontology_file = "/home/cartesio/workspace/FTM/ai_act_project/ontologias/versions/0.36.0/ontologia-v0.36.0.ttl"
    apply_translations(ontology_file)