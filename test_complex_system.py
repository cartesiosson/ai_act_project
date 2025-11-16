#!/usr/bin/env python3
"""
🔥 PRUEBA DE SISTEMA SÚPER COMPLEJO 🔥
====================================

Este script crea un sistema de IA diseñado para activar el MÁXIMO número de reglas posible
combinando múltiples criterios de alto riesgo del AI Act.
"""

import requests
import json
import time
import random
import string

BASE_URL = "http://localhost:8000"

def get_unique_suffix():
    ts = int(time.time())
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{ts}_{rand}"


def create_ultra_complex_system(unique_suffix):
    """
    Crear el sistema más complejo posible que active múltiples reglas simultáneamente
    
    CARACTERÍSTICAS DEL SISTEMA:
    - 🏛️ JUDICIAL: Procesamiento de decisiones judiciales 
    - 👮 POLICIAL: Apoyo a fuerzas del orden
    - 🆔 BIOMÉTRICO: Identificación facial y de huellas
    - 🎓 EDUCATIVO: Evaluación de estudiantes  
    - 🏥 SANITARIO: Acceso a servicios de salud
    - 💼 RECLUTAMIENTO: Selección de personal
    - 🚨 INFRAESTRUCTURA: Gestión de sistemas críticos
    - 🛂 MIGRACIÓN: Control fronterizo
    - 👶 MENORES: Procesamiento de datos de niños
    - ⚡ TIEMPO REAL: Procesamiento de alta velocidad
    - 🔄 ADAPTATIVO: Aprendizaje continuo
    - 🌐 ALTO VOLUMEN: Procesamiento masivo de datos
    """
    
    system_name = f"SISTEMA_SUPER_COMPLEJO_{unique_suffix}"
    system_version = f"3.0-COMPLEX-{unique_suffix}"
    ultra_complex_system = {
        "@type": "ai:IntelligentSystem",
        "hasName": system_name,
        "hasVersion": system_version,
        
        # 🎯 PROPÓSITOS MÚLTIPLES (activarán diferentes criterios)
        "hasPurpose": [
            "ai:BiometricIdentification",     # → BiometricIdentificationCriterion
            "ai:EducationAccess",             # → EducationEvaluationCriterion
            "ai:RecruitmentOrEmployment",     # → RecruitmentEmploymentCriterion
            "ai:MigrationControl",            # → MigrationBorderCriterion
            "ai:PublicServiceAllocation",     # → EssentialServicesAccessCriterion
            "ai:LawEnforcement",              # → LawEnforcementCriterion
            "ai:HealthCare"                   # → EssentialServicesAccessCriterion
        ],
        
        # 🌍 CONTEXTOS DE DESPLIEGUE MÚLTIPLES  
        "hasDeploymentContext": [
            "ai:Education",                   # → EducationEvaluationCriterion
            "ai:PublicServices",              # → EssentialServicesAccessCriterion
            "ai:RealTimeProcessing",          # → PerformanceRequirements
            "ai:HighVolumeProcessing"         # → ScalabilityRequirements
        ],
        
        # 📊 TIPOS DE DATOS SENSIBLES
        "processesDataType": [
            "ai:BiometricData",               # → BiometricSecurity
            "ai:MinorData"                    # → ChildProtection + ParentalConsent
        ],
        
        # 🔧 CARACTERÍSTICAS TÉCNICAS COMPLEJAS
        "hasAlgorithmType": [
            "ai:NeuralNetwork",               # → DeepLearning
            "ai:TransformerModel"             # → FoundationModel
        ],
        
        # 📈 CAPACIDADES DEL SISTEMA
        "hasSystemCapabilityCriteria": [
            "ai:JudicialSupportCriterion",           # → DueProcess + HumanOversight
            "ai:BiometricIdentificationCriterion",   # → BiometricSecurity + DataEncryption  
            "ai:RecruitmentEmploymentCriterion"      # → NonDiscrimination + TransparencyRequirement
        ],
        
        # 📊 PARÁMETROS TÉCNICOS EXTREMOS
        "hasParameterCount": 175000000000,   # > 100B parámetros → SystemicRisk
        "hasComputationFLOPs": 1.5e26,      # > 10^25 FLOPs → SystemicRisk
        "hasMarketReach": 50000000,          # > 10M usuarios → FoundationModel
        "hasAutonomyLevel": 0.95,            # Muy autónomo → LacksHumanOversight
        "hasAccuracyRate": 0.73,             # < 80% → AccuracyEvaluationRequirement
        "isAdaptiveSystem": True,            # → ContinuousLearning
        
        # 📁 ORIGEN DE DATOS MÚLTIPLE
        "hasTrainingDataOrigin": [
            "ai:ExternalDataset",             # → Enhanced DataGovernance
            "ai:SyntheticDataset",            # → TransparencyRequirement
            "ai:InternalDataset"              # → Controlled access
        ],
        
        # 🎯 CRITERIOS ADICIONALES
        "hasNormativeCriterion": [
            "ai:PrivacyProtection",           # → PrivacyRequirement
            "ai:NonDiscrimination",           # → FairnessRequirement
            "ai:ProtectionOfMinors",          # → ParentalConsent
            "ai:DueProcess"                   # → HumanOversight
        ],
        
        "hasTechnicalCriterion": [
            "ai:PerformanceRequirements",     # → LatencyMetrics
            "ai:ScalabilityRequirements"      # → PerformanceMonitoring
        ]
    }
    
    print("🚀 CREANDO SISTEMA SÚPER COMPLEJO...")
    print("=" * 80)
    print(f"📋 Nombre: {ultra_complex_system['hasName']}")
    print(f"🎯 Propósitos: {len(ultra_complex_system['hasPurpose'])}")
    print(f"🌍 Contextos: {len(ultra_complex_system['hasDeploymentContext'])}")
    print(f"📊 Tipos de datos: {len(ultra_complex_system['processesDataType'])}")
    print(f"🔧 Algoritmos: {len(ultra_complex_system['hasAlgorithmType'])}")
    print(f"⚡ Capacidades del sistema: {len(ultra_complex_system['hasSystemCapabilityCriteria'])}")
    print(f"🔥 Criterios normativos: {len(ultra_complex_system['hasNormativeCriterion'])}")
    print(f"⚙️ Criterios técnicos: {len(ultra_complex_system['hasTechnicalCriterion'])}")
    print("=" * 80)
    
    # Crear sistema
    response = requests.post(f"{BASE_URL}/systems", json=ultra_complex_system, timeout=30)
    
    if response.status_code == 201:
        system_id = response.json().get("id")
        print(f"✅ Sistema creado exitosamente!")
        print(f"🆔 ID: {system_id}")
        return system_id
    else:
        print(f"❌ Error creando sistema: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        return None

def run_complex_reasoning(system_id):
    """Ejecutar razonamiento sobre el sistema complejo"""
    print("\n🧠 EJECUTANDO RAZONAMIENTO COMPLEJO...")
    print("=" * 80)
    
    response = requests.post(f"{BASE_URL}/reasoning/system/{system_id}", timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        relationships = result.get("inferred_relationships", {})
        rules_applied = result.get("rules_applied", 0)
        
        print(f"🔥 TOTAL INFERENCIAS APLICADAS: {rules_applied}")
        print("=" * 80)
        
        # Analizar inferencias por tipo
        total_inferences = 0
        for prop, objects in relationships.items():
            if objects:
                total_inferences += len(objects)
                print(f"\n📋 {prop}: {len(objects)} criterios/requisitos")
                
                for obj in objects:
                    # Extraer nombre legible del URI
                    obj_name = obj.split('#')[-1] if '#' in obj else obj.split('/')[-1]
                    
                    # Identificar tipo de riesgo por color
                    if any(risk in obj_name for risk in ['Unacceptable', 'Prohibited', 'SocialScoring', 'SubliminalManipulation']):
                        print(f"      🚫 {obj_name} (PROHIBIDO)")
                    elif any(high in obj_name for high in ['HighRisk', 'Critical', 'Judicial', 'Biometric', 'Essential']):
                        print(f"      🔴 {obj_name} (ALTO RIESGO)")
                    elif any(limited in obj_name for limited in ['LimitedRisk', 'Transparency', 'Deepfake']):
                        print(f"      🟡 {obj_name} (RIESGO LIMITADO)")
                    else:
                        print(f"      🟢 {obj_name}")
        
        print("=" * 80)
        print(f"📊 RESUMEN FINAL:")
        print(f"   🎯 Reglas aplicadas por el motor: {rules_applied}")
        print(f"   📈 Total relaciones inferidas: {total_inferences}")
        print(f"   ⚡ Promedio inferencias/regla: {total_inferences/rules_applied if rules_applied > 0 else 0:.2f}")
        
        # Análisis de cobertura de reglas
        rule_types = len([k for k, v in relationships.items() if v])
        print(f"   📋 Tipos de propiedades activadas: {rule_types}/5")
        print(f"   🔥 Cobertura de reglas: {(rule_types/5)*100:.1f}%")
        
        return rules_applied
        
    else:
        print(f"❌ Error en razonamiento: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        return 0

def main():
    print("🔥 INICIANDO TEST DE SISTEMA SÚPER COMPLEJO 🔥")
    print("=" * 60)

    # Validar tipos hoja desde backend
    print("🔎 Validando tipos de algoritmo hoja desde backend...")
    import requests
    BASE_URL = "http://localhost:8000"
    valid_types = set(x['id'] for x in requests.get(f"{BASE_URL}/vocab/algorithmtypes?lang=es").json())
    used_types = set([
        "ai:TransformerModel",
        "ai:DecisionTree",
        "ai:ConvolutionalNeuralNetwork",
        "ai:RandomForest"
    ])
    assert all(t in valid_types for t in used_types), "Algoritmos usados no son hojas válidas!"

    # Crear sistema con URN único y borrado previo
    unique_suffix = get_unique_suffix()
    # system_name = f"SISTEMA_SUPER_COMPLEJO_{unique_suffix}"
    # delete_system_if_exists(system_name)
    ultra_system_id = create_ultra_complex_system(unique_suffix)
    if not ultra_system_id:
        print("❌ Error creando el sistema súper complejo")
        return

    # Ejecutar análisis de razonamiento
    result = run_complex_reasoning(ultra_system_id)
    print("\n" + "=" * 60)
    print("🎯 Test súper complejo completado")

    # Guardar resultado para análisis
    if result:
        with open("complex_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("💾 Resultado guardado en complex_test_result.json")

if __name__ == "__main__":
    main()