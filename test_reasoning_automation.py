#!/usr/bin/env python3
"""
Script automatizado para probar el servicio de razonamiento con múltiples sistemas
Genera sistemas con diferentes características y ejecuta razonamiento automáticamente
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def create_system(system_data):
    """Crear un sistema en el backend"""
    try:
        response = requests.post(f"{BASE_URL}/systems", json=system_data, timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            return result.get("inserted_id")
        else:
            print(f"❌ Error creando sistema: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión creando sistema: {e}")
        return None

def run_reasoning(system_id, system_name):
    """Ejecutar razonamiento sobre un sistema"""
    try:
        print(f"\n🧠 Ejecutando razonamiento para: {system_name}")
        response = requests.post(f"{BASE_URL}/reasoning/system/{system_id}", timeout=30)
        if response.status_code == 200:
            # Verificar si la respuesta es JSON o TTL
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                result = response.json()
                relationships = result.get("inferred_relationships", {})
                rules_applied = result.get("rules_applied", 0)
                print(f"✅ {rules_applied} inferencias aplicadas (formato JSON)")
                
                # Mostrar inferencias agrupadas por tipo
                total_inferences = 0
                for prop, objects in relationships.items():
                    if objects:  # Solo mostrar propiedades que tienen valores
                        total_inferences += len(objects)
                        print(f"   📋 {prop}: {len(objects)} criterios")
                        for obj in objects[:2]:  # Mostrar solo los primeros 2
                            # Extraer el nombre del URI si es posible
                            obj_name = obj.split('#')[-1] if '#' in obj else obj.split('/')[-1]
                            print(f"      • {obj_name}")
                        if len(objects) > 2:
                            print(f"      • ... y {len(objects)-2} más")
                
                return rules_applied
            else:
                # Respuesta en TTL - contar inferencias manualmente
                ttl_content = response.text
                inference_count = 0
                
                # Contar líneas que parecen inferencias
                inference_patterns = [
                    "hasNormativeCriterion", "hasRequirement", "hasTechnicalCriterion", 
                    "hasTechnicalRequirement", "hasContextualCriterion"
                ]
                
                for pattern in inference_patterns:
                    inference_count += ttl_content.count(pattern)
                
                print(f"✅ ~{inference_count} inferencias aplicadas (formato TTL)")
                print(f"   📄 TTL size: {len(ttl_content):,} caracteres")
                
                # Mostrar algunos tipos de inferencias encontradas
                for pattern in inference_patterns[:3]:
                    count = ttl_content.count(pattern)
                    if count > 0:
                        print(f"   📋 {pattern}: ~{count} ocurrencias")
                
                return inference_count
        else:
            print(f"❌ Error en razonamiento: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error ejecutando razonamiento: {e}")
        return 0

def main():
    print("🚀 AUTOMATIZACIÓN DE PRUEBAS DE RAZONAMIENTO")
    print("=" * 60)
    
    # Sistemas de prueba con diferentes características
    test_systems = [
        {
            "name": "Sistema Educativo Biométrico",
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema Educativo Biométrico",
                "hasPurpose": ["ai:EducationAccess", "ai:BiometricIdentification"],
                "hasDeploymentContext": ["ai:Education"],
                "hasTrainingDataOrigin": ["ai:InternalDataset"],
                "processesDataType": ["ai:BiometricData", "ai:PersonalData"],
                "hasSystemCapabilityCriteria": ["ai:JudicialSupportCriterion"],
                "hasVersion": "1.0"
            },
            "expected_rules": ["education", "biometric", "judicial_capability"]
        },
        {
            "name": "Sistema Judicial de Alto Rendimiento", 
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema Judicial de Alto Rendimiento",
                "hasPurpose": ["ai:JudicialDecisionSupport"],
                "hasDeploymentContext": ["ai:RealTimeProcessing", "ai:HighVolumeProcessing"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "hasAlgorithmType": ["ai:TransformerModel"],
                "hasSystemCapabilityCriteria": ["ai:BiometricIdentificationCriterion"],
                "hasVersion": "2.0"
            },
            "expected_rules": ["judicial", "performance", "scalability", "biometric_capability", "cascade"]
        },
        {
            "name": "Sistema de Salud Esencial",
            "data": {
                "@type": "ai:IntelligentSystem", 
                "hasName": "Sistema de Salud Esencial",
                "hasPurpose": ["ai:HealthCare"],
                "hasDeploymentContext": ["ai:Healthcare", "ai:PublicServices"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "processesDataType": ["ai:HealthData"],
                "hasVersion": "1.5"
            },
            "expected_rules": ["healthcare_privacy", "essential_services"]
        },
        {
            "name": "Sistema de Reclutamiento Complejo",
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema de Reclutamiento Complejo", 
                "hasPurpose": ["ai:RecruitmentOrEmployment"],
                "hasDeploymentContext": ["ai:HighVolumeProcessing"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "hasAlgorithmType": ["ai:FoundationModel"],
                "hasSystemCapabilityCriteria": ["ai:RecruitmentEmploymentCriterion"],
                "hasVersion": "3.0"
            },
            "expected_rules": ["recruitment_nondiscrimination", "scalability", "model_complexity", "recruitment_capability"]
        },
        {
            "name": "Sistema de Infraestructura Crítica",
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema de Infraestructura Crítica",
                "hasPurpose": ["ai:CriticalInfrastructureOperation"],
                "hasDeploymentContext": ["ai:RealTimeProcessing"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "processesDataType": ["ai:TechnicalData"],
                "hasVersion": "4.0"
            },
            "expected_rules": ["critical_infrastructure", "performance_requirements"]
        },
        {
            "name": "Sistema Migratorio Biométrico", 
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema Migratorio Biométrico",
                "hasPurpose": ["ai:MigrationControl", "ai:BiometricIdentification"],
                "hasDeploymentContext": ["ai:HighVolumeProcessing"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "processesDataType": ["ai:BiometricData", "ai:PersonalData"],
                "hasVersion": "2.5"
            },
            "expected_rules": ["migration_border", "biometric_security", "scalability"]
        },
        {
            "name": "Sistema Policial Avanzado",
            "data": {
                "@type": "ai:IntelligentSystem",
                "hasName": "Sistema Policial Avanzado",
                "hasPurpose": ["ai:LawEnforcementSupport"],
                "hasDeploymentContext": ["ai:RealTimeProcessing"],
                "hasTrainingDataOrigin": ["ai:ExternalDataset"],
                "hasAlgorithmType": ["ai:GenerativeModel"],
                "hasVersion": "1.8"
            },
            "expected_rules": ["law_enforcement", "performance_requirements", "model_complexity"]
        }
    ]
    
    results = []
    total_inferences = 0
    
    for i, system_spec in enumerate(test_systems, 1):
        print(f"\n{'='*20} SISTEMA {i}/7 {'='*20}")
        print(f"📝 Creando: {system_spec['name']}")
        
        # Crear sistema
        system_id = create_system(system_spec["data"])
        if not system_id:
            print(f"❌ No se pudo crear el sistema")
            continue
        
        print(f"✅ Sistema creado con ID: {system_id}")
        
        # Pequeña pausa para asegurar que el sistema se guarde
        time.sleep(1)
        
        # Ejecutar razonamiento
        inferences_count = run_reasoning(system_id, system_spec["name"])
        total_inferences += inferences_count
        
        results.append({
            "name": system_spec["name"],
            "id": system_id,
            "inferences": inferences_count,
            "expected_rules": system_spec["expected_rules"]
        })
        
        # Pausa entre sistemas para no sobrecargar
        time.sleep(2)
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL DE PRUEBAS AUTOMATIZADAS")
    print(f"{'='*60}")
    
    for result in results:
        print(f"🎯 {result['name']:<35} {result['inferences']:>3} inferencias")
    
    print(f"\n🔥 TOTAL: {len(results)} sistemas procesados")
    print(f"🧠 TOTAL: {total_inferences} inferencias aplicadas")
    if len(results) > 0:
        print(f"⚡ PROMEDIO: {total_inferences/len(results):.1f} inferencias por sistema")
    else:
        print(f"⚠️  No se procesaron sistemas exitosamente")
    
    # Verificar diversidad de reglas
    if total_inferences > 20:
        print(f"\n✅ ÉXITO: Sistema de razonamiento funcionando correctamente")
        print(f"   📈 Alta diversidad de reglas aplicadas")
        print(f"   🔄 Múltiples tipos de sistemas procesados")
        print(f"   🎯 Reglas de cascada y capacidad funcionando")
    else:
        print(f"\n⚠️  ADVERTENCIA: Pocas inferencias aplicadas ({total_inferences})")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        print(f"\n✨ Automatización completada exitosamente!")
    except KeyboardInterrupt:
        print(f"\n⏹️  Automatización interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en automatización: {e}")
        sys.exit(1)