#!/usr/bin/env python3
"""
🔥 SISTEMA MEGA-COMPLEJO PARA MÁXIMAS INFERENCIAS 🔥
=================================================

Sistema diseñado científicamente para activar el máximo número de reglas
basado en las entidades confirmadas que funcionan en los tests anteriores.
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


def create_mega_system(unique_suffix):
    """
    Sistema mega-complejo usando solo entidades confirmadas como funcionales
    """
    
    system_name = f"SISTEMA_MEGA_COMPLEJO_{unique_suffix}"
    system_version = f"4.0-MEGACOMPLEX-{unique_suffix}"
    mega_system = {
        "@type": "ai:IntelligentSystem",
        "hasName": system_name,
        "hasVersion": system_version,
        
        # Propósitos que sabemos funcionan
        "hasPurpose": [
            "ai:BiometricIdentification",
            "ai:EducationAccess", 
            "ai:MigrationControl",
            "ai:LawEnforcement"
        ],
        
        # Contextos confirmados
        "hasDeploymentContext": [
            "ai:Education",
            "ai:RealTimeProcessing",
            "ai:HighVolumeProcessing"
        ],
        
        # Datos que activan reglas
        "processesDataType": [
            "ai:BiometricData",
            "ai:MinorData"
        ],
        
        # Algoritmos existentes
        "hasAlgorithmType": [
            "ai:NeuralNetwork",
            "ai:TransformerModel"
        ],
        
        # Capacidades del sistema - ESTAS SON LAS QUE MÁS REGLAS ACTIVAN
        "hasSystemCapabilityCriteria": [
            "ai:JudicialSupportCriterion",
            "ai:BiometricIdentificationCriterion", 
            "ai:RecruitmentEmploymentCriterion"
        ],
        
        # Orígenes de datos múltiples
        "hasTrainingDataOrigin": [
            "ai:ExternalDataset",
            "ai:InternalDataset",
            "ai:SyntheticDataset"
        ],
        
        # Criterios normativos confirmados
        "hasNormativeCriterion": [
            "ai:DueProcess",
            "ai:ProtectionOfMinors", 
            "ai:PrivacyProtection",
            "ai:NonDiscrimination"
        ],
        
        # Criterios técnicos confirmados
        "hasTechnicalCriterion": [
            "ai:PerformanceRequirements",
            "ai:ScalabilityRequirements"
        ],
        
        # Propiedades numéricas para activar más reglas
        "hasParameterCount": 175000000000,
        "hasComputationFLOPs": 1.5e26,
        "hasMarketReach": 50000000,
        "hasAutonomyLevel": 0.95,
        "hasAccuracyRate": 0.73,
        "isAdaptiveSystem": True
    }
    
    print("🚀 CREANDO MEGA-SISTEMA DE MÁXIMA COMPLEJIDAD...")
    print("=" * 60)
    print(f"📋 Nombre: {mega_system['hasName']}")
    print(f"🎯 Propósitos: {len(mega_system['hasPurpose'])}")
    print(f"🌍 Contextos: {len(mega_system['hasDeploymentContext'])}")
    print(f"⚡ Capacidades del Sistema: {len(mega_system['hasSystemCapabilityCriteria'])}")
    print(f"🔧 Algoritmos: {len(mega_system['hasAlgorithmType'])}")
    print(f"📊 Criterios Normativos: {len(mega_system['hasNormativeCriterion'])}")
    print(f"⚙️ Criterios Técnicos: {len(mega_system['hasTechnicalCriterion'])}")
    print("=" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/systems", json=mega_system, timeout=30)
        
        
        if response.status_code == 201:
            result = response.json()
            system_id = result.get("id") or result.get("inserted_id")
            print(f"✅ MEGA-SISTEMA CREADO EXITOSAMENTE!")
            print(f"🆔 ID: {system_id}")
            return system_id
        else:
            print(f"❌ Error creando mega-sistema: {response.status_code}")
            print(f"📄 Respuesta completa: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Excepción creando sistema: {e}")
        return None

def analyze_mega_reasoning(system_id):
    """Análisis detallado del razonamiento mega-complejo"""
    print("\n🧠 EJECUTANDO RAZONAMIENTO MEGA-COMPLEJO...")
    print("=" * 70)
    
    try:
        response = requests.post(f"{BASE_URL}/reasoning/system/{system_id}", timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            relationships = result.get("inferred_relationships", {})
            rules_applied = result.get("rules_applied", 0)
            
            print(f"🔥🔥 RESULTADO ÉPICO: {rules_applied} REGLAS APLICADAS 🔥🔥")
            print("=" * 70)
            
            # Análisis detallado por categoría
            total_relations = 0
            categories = {
                "hasNormativeCriterion": "🏛️ CRITERIOS NORMATIVOS",
                "hasTechnicalCriterion": "⚙️ CRITERIOS TÉCNICOS", 
                "hasContextualCriterion": "🌍 CRITERIOS CONTEXTUALES",
                "hasRequirement": "📋 REQUISITOS GENERALES",
                "hasTechnicalRequirement": "🔧 REQUISITOS TÉCNICOS"
            }
            
            for prop, label in categories.items():
                objects = relationships.get(prop, [])
                if objects:
                    total_relations += len(objects)
                    print(f"\n{label}: {len(objects)} elementos")
                    
                    for obj in objects:
                        obj_name = obj.split('#')[-1] if '#' in obj else obj.split('/')[-1]
                        
                        # Clasificar por importancia
                        if any(x in obj_name for x in ['Judicial', 'Biometric', 'Recruitment', 'Due', 'Protection']):
                            print(f"      🟡 {obj_name} (ALTO IMPACTO)")
                        elif any(x in obj_name for x in ['Performance', 'Latency', 'Security', 'Governance']):
                            print(f"      🟢 {obj_name} (TÉCNICO)")
                        else:
                            print(f"      🔵 {obj_name}")
            
            # Estadísticas épicas
            print("\n" + "🎯" * 35)
            print("📊 ESTADÍSTICAS ÉPICAS DEL MEGA-SISTEMA")
            print("🎯" * 35)
            print(f"⚡ Reglas del motor aplicadas: {rules_applied}")
            print(f"📈 Total relaciones inferidas: {total_relations}")
            print(f"🔥 Ratio inferencia/regla: {total_relations/rules_applied if rules_applied > 0 else 0:.2f}")
            print(f"🎯 Categorías activadas: {len([k for k,v in relationships.items() if v])}/5")
            print(f"💫 Eficiencia del sistema: {(total_relations/50)*100:.1f}% (de 50 posibles)")
            
            # Evaluación de rendimiento
            if rules_applied >= 25:
                print("\n🏆🏆 RESULTADO LEGENDARIO! 🏆🏆")
                print("🔥 Más de 25 reglas activadas - Sistema ULTRA-COMPLEJO")
            elif rules_applied >= 20:
                print("\n🏆 EXCELENTE RENDIMIENTO! 🏆")
                print("💪 Entre 20-25 reglas - Sistema MUY COMPLEJO")
            elif rules_applied >= 15:
                print("\n✅ MUY BUEN RENDIMIENTO!")
                print("👍 Entre 15-20 reglas - Sistema COMPLEJO")
            elif rules_applied >= 10:
                print("\n👍 BUEN RENDIMIENTO")
                print("📈 Entre 10-15 reglas - Sistema MODERADO")
            else:
                print("\n⚠️ RENDIMIENTO BÁSICO")
                print("🔧 Menos de 10 reglas - Necesita optimización")
            
            return rules_applied
            
        else:
            print(f"❌ Error en razonamiento mega: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return 0
            
    except Exception as e:
        print(f"💥 Excepción en razonamiento: {e}")
        return 0

def main():
    print("🚀 Iniciando prueba de sistema mega-complejo")
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
    # system_name = f"SISTEMA_MEGA_COMPLEJO_{unique_suffix}"
    # delete_system_if_exists(system_name)
    mega_system_id = create_mega_system(unique_suffix)
    if not mega_system_id:
        print("❌ Error creando el sistema mega-complejo")
        return

    # Ejecutar análisis de razonamiento
    result = analyze_mega_reasoning(mega_system_id)
    print("\n" + "=" * 60)
    print("🎯 Test mega-complejo completado")

    # Guardar resultado para análisis
    if result:
        with open("mega_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("💾 Resultado guardado en mega_test_result.json")

if __name__ == "__main__":
    main()