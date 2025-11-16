from fastapi import FastAPI, File, UploadFile, Form
from fastapi import responses
from fastapi import status
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from owlready2 import get_ontology, onto_path, World, sync_reasoner_pellet
import tempfile
import shutil
import os
from typing import List

app = FastAPI(title="SWRL Reasoner Service", description="Microservicio para inferencia OWL+SWRL usando owlready2", version="1.0.0")

# Permitir CORS para facilitar pruebas y despliegue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leer la ruta de la ontología base desde la variable de entorno
ONTOLOGY_PATH = os.environ.get("ONTOLOGY_PATH", os.path.join(os.path.dirname(__file__), "ontology", "ontologia.ttl"))
ONTOLOGY_IRI = "http://example.org/ontologia#"  # Cambia esto por el IRI real de tu ontología

# Depuración: mostrar la ruta de la ontología y verificar si el archivo existe
print("DEBUG ONTOLOGY_PATH:", ONTOLOGY_PATH)
print("DEBUG exists:", os.path.isfile(ONTOLOGY_PATH))

# Cargar la ontología base al iniciar el servidor
base_world = World()
# Carga diferida de la ontología - solo cuando sea necesario para evitar errores al inicio
base_onto = None
def get_base_ontology():
    global base_onto
    if base_onto is None and os.path.exists(ONTOLOGY_PATH):
        try:
            # Crear un mundo temporal para probar la carga
            temp_world = World()
            base_onto = temp_world.get_ontology("file://" + ONTOLOGY_PATH)
            base_onto.load()
            print(f"DEBUG: Ontología cargada exitosamente")
        except Exception as e:
            print(f"WARN: Error cargando ontología base: {e}")
            base_onto = None
    return base_onto

@app.post(
    "/reason",
    response_class=Response,
    responses={
        200: {
            "content": {"text/turtle": {}}
        }
    },
    status_code=200,
    summary="Inferencia SWRL sobre ontología base",
    description="Recibe datos y reglas SWRL (ambos RDF/TTL), ejecuta inferencia y devuelve el grafo inferido en formato Turtle."
)
async def reason(
    data: UploadFile = File(..., description="Datos RDF/TTL para instanciar en la ontología base"),
    swrl_rules: UploadFile = File(..., description="Archivo RDF/TTL con reglas SWRL")
):
    """
    Recibe datos y un archivo de reglas SWRL (TTL/RDF), ejecuta inferencia sobre la ontología base y devuelve los triples inferidos.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Guardar los datos recibidos
        data_file = os.path.join(tmpdir, data.filename)
        with open(data_file, "wb") as f:
            shutil.copyfileobj(data.file, f)
        # Guardar el archivo de reglas SWRL
        rules_file = os.path.join(tmpdir, swrl_rules.filename)
        with open(rules_file, "wb") as f:
            shutil.copyfileobj(swrl_rules.file, f)

        # Crear un nuevo World y clonar la ontología base
        world = World()
        
        # Cargar la ontología base
        try:
            if os.path.exists(ONTOLOGY_PATH):
                onto = world.get_ontology("file://" + ONTOLOGY_PATH)
                onto.load()
                print(f"DEBUG: Ontología base cargada en reasoner")
            else:
                print(f"WARN: Ontología base no disponible, creando ontología vacía")
                onto = world.get_ontology("http://ai-act.eu/ai#")
        except Exception as e:
            print(f"ERROR cargando ontología base: {e}")
            onto = world.get_ontology("http://ai-act.eu/ai#")
        
        # Implementar razonamiento SWRL usando RDFLib + lógica de inferencia manual
        from rdflib import Graph, Namespace, RDF, RDFS, Literal
        from rdflib.namespace import OWL
        
        # Definir namespaces
        AI = Namespace("http://ai-act.eu/ai#")
        
        try:
            print("DEBUG: *** INICIANDO RAZONAMIENTO HÍBRIDO (RDFLib + SWRL Manual) ***")
            
            # 1. Cargar ontología base si existe
            base_graph = Graph()
            if os.path.exists(ONTOLOGY_PATH):
                print(f"DEBUG: Cargando ontología base desde {ONTOLOGY_PATH}")
                base_graph.parse(ONTOLOGY_PATH, format="turtle")
                print(f"DEBUG: Ontología base cargada: {len(base_graph)} triples")
            else:
                print("DEBUG: No se encontró ontología base")
            
            # 2. Cargar datos del sistema
            print(f"DEBUG: Cargando datos del sistema desde {data_file}")
            system_graph = Graph()
            system_graph.parse(data_file, format="turtle")
            print(f"DEBUG: Datos del sistema cargados: {len(system_graph)} triples")
            
            # 3. Cargar reglas y conceptos
            print(f"DEBUG: Cargando reglas y conceptos desde {rules_file}")
            rules_graph = Graph()
            rules_graph.parse(rules_file, format="turtle")
            print(f"DEBUG: Reglas y conceptos cargados: {len(rules_graph)} triples")
            
            # 4. Combinar todos los grafos
            combined_graph = base_graph + system_graph + rules_graph
            print(f"DEBUG: Grafo combinado: {len(combined_graph)} triples total")
            
            # 5. APLICAR INFERENCIAS HÍBRIDAS (EXTERNAS + FALLBACK)
            inferences_count = 0
            
            # Intentar usar motor de reglas externas primero
            try:
                print(f"DEBUG: Intentando cargar motor de reglas externas...")
                import sys
                import os
                
                # Buscar directorio de reglas  
                ontology_dir = os.path.dirname(os.environ.get("ONTOLOGY_PATH", "/ontologias/ontologia-v0.36.0.ttl"))
                rules_dir = os.path.join(ontology_dir, "rules")
                
                if os.path.exists(rules_dir):
                    sys.path.insert(0, rules_dir)
                    from rules_engine import rules_engine
                    
                    # Aplicar reglas externas
                    external_inferences = rules_engine.apply_rules(system_graph, combined_graph)
                    inferences_count += external_inferences
                    print(f"DEBUG: ✅ Motor externo aplicó {external_inferences} inferencias")
                else:
                    print(f"DEBUG: ❌ Directorio de reglas no encontrado: {rules_dir}")
                    raise FileNotFoundError("Reglas externas no disponibles")
                    
            except Exception as e:
                print(f"DEBUG: ⚠️  Motor externo falló ({e}), usando fallback hardcodeado")
            
            # Aplicar reglas hardcodeadas como complemento/fallback  
            for system in combined_graph.subjects(RDF.type, AI.IntelligentSystem):
                print(f"DEBUG: Procesando sistema con reglas hardcodeadas: {system}")
                
                # REGLA 1 & 4.2: EducationAccess O contexto Education -> ProtectionOfMinors
                has_education_purpose = (system, AI.hasPurpose, AI.EducationAccess) in combined_graph
                has_education_context = (system, AI.hasDeploymentContext, AI.Education) in combined_graph
                
                if has_education_purpose or has_education_context:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.ProtectionOfMinors))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> ProtectionOfMinors")
                    inferences_count += 1
                
                # REGLA 9: ProtectionOfMinors -> ParentalConsent
                if (system, AI.hasNormativeCriterion, AI.ProtectionOfMinors) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.ParentalConsent))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> ParentalConsent")
                    inferences_count += 1
                
                # REGLA 2: RecruitmentOrEmployment -> NonDiscrimination
                if (system, AI.hasPurpose, AI.RecruitmentOrEmployment) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.NonDiscrimination))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> NonDiscrimination")
                    inferences_count += 1
                
                # NUEVA REGLA 3: JudicialDecisionSupport -> JudicialSupportCriterion
                if (system, AI.hasPurpose, AI.JudicialDecisionSupport) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.JudicialSupportCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> JudicialSupportCriterion")
                    inferences_count += 1
                
                # NUEVA REGLA 4: LawEnforcementSupport -> LawEnforcementCriterion
                if (system, AI.hasPurpose, AI.LawEnforcementSupport) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.LawEnforcementCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> LawEnforcementCriterion")
                    inferences_count += 1
                
                # NUEVA REGLA 5: MigrationControl -> MigrationBorderCriterion
                if (system, AI.hasPurpose, AI.MigrationControl) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.MigrationBorderCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> MigrationBorderCriterion")
                    inferences_count += 1
                
                # NUEVA REGLA 6: CriticalInfrastructureOperation -> CriticalInfrastructureCriterion
                if (system, AI.hasPurpose, AI.CriticalInfrastructureOperation) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.CriticalInfrastructureCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> CriticalInfrastructureCriterion")
                    inferences_count += 1
                
                # NUEVA REGLA 7: HealthCare (propósito) -> PrivacyProtection
                if (system, AI.hasPurpose, AI.HealthCare) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.PrivacyProtection))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> PrivacyProtection")
                    inferences_count += 1
                
                # NUEVA REGLA 8: EducationAccess (propósito) -> EducationEvaluationCriterion
                if (system, AI.hasPurpose, AI.EducationAccess) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.EducationEvaluationCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> EducationEvaluationCriterion")
                    inferences_count += 1
                
                # REGLA 12: NonDiscrimination -> Auditability
                if (system, AI.hasNormativeCriterion, AI.NonDiscrimination) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.Auditability))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> Auditability")
                    inferences_count += 1
                
                # REGLA 5: RealTimeProcessing -> PerformanceRequirements
                if (system, AI.hasDeploymentContext, AI.RealTimeProcessing) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.PerformanceRequirements))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> PerformanceRequirements")
                    inferences_count += 1
                
                # NUEVA REGLA: Healthcare -> EssentialServicesAccessCriterion
                if (system, AI.hasDeploymentContext, AI.Healthcare) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.EssentialServicesAccessCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> EssentialServicesAccessCriterion (Healthcare)")
                    inferences_count += 1
                
                # NUEVA REGLA: PublicServices -> EssentialServicesAccessCriterion
                if (system, AI.hasDeploymentContext, AI.PublicServices) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.EssentialServicesAccessCriterion))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> EssentialServicesAccessCriterion (PublicServices)")
                    inferences_count += 1
                
                # NUEVA REGLA: HighVolumeProcessing -> ScalabilityRequirements
                if (system, AI.hasDeploymentContext, AI.HighVolumeProcessing) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.ScalabilityRequirements))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> ScalabilityRequirements")
                    inferences_count += 1
                
                # NUEVA REGLA TÉCNICA: ScalabilityRequirements -> Performance + LoadBalancing
                if (system, AI.hasTechnicalCriterion, AI.ScalabilityRequirements) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.PerformanceMonitoringRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> PerformanceMonitoringRequirement")
                    inferences_count += 1
                
                # NUEVA REGLA: Sistemas con datos externos -> DataGovernance adicional
                if (system, AI.hasTrainingDataOrigin, AI.ExternalDataset) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.DataGovernanceRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> DataGovernanceRequirement (External Data)")
                    inferences_count += 1
                
                # REGLA 10: PerformanceRequirements -> LatencyMetrics  
                if (system, AI.hasTechnicalCriterion, AI.PerformanceRequirements) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.LatencyMetrics))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> LatencyMetrics")
                    inferences_count += 1
                
                # NUEVA REGLA: BiometricIdentification (propósito) -> BiometricSecurity
                print(f"DEBUG: Verificando BiometricIdentification para {system}")
                has_biometric_purpose = (system, AI.hasPurpose, AI.BiometricIdentification) in combined_graph
                print(f"DEBUG: ¿Tiene propósito BiometricIdentification? {has_biometric_purpose}")
                if has_biometric_purpose:
                    combined_graph.add((system, AI.hasContextualCriterion, AI.BiometricSecurity))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasContextualCriterion -> BiometricSecurity (por propósito)")
                    inferences_count += 1
                
                # REGLA 7: BiometricData -> BiometricSecurity
                if (system, AI.processesDataType, AI.BiometricData) in combined_graph:
                    combined_graph.add((system, AI.hasContextualCriterion, AI.BiometricSecurity))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasContextualCriterion -> BiometricSecurity")
                    inferences_count += 1
                
                # REGLA 11: BiometricSecurity -> DataEncryption
                if (system, AI.hasContextualCriterion, AI.BiometricSecurity) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.DataEncryption))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> DataEncryption")
                    inferences_count += 1
                
                # NUEVAS REGLAS EN CADENA: EssentialServicesAccessCriterion
                if (system, AI.hasNormativeCriterion, AI.EssentialServicesAccessCriterion) in combined_graph:
                    # -> HumanOversightRequirement
                    combined_graph.add((system, AI.hasRequirement, AI.HumanOversightRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> HumanOversightRequirement")
                    inferences_count += 1
                    
                    # -> DataGovernanceRequirement
                    combined_graph.add((system, AI.hasRequirement, AI.DataGovernanceRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> DataGovernanceRequirement")
                    inferences_count += 1
                    
                    # -> FundamentalRightsAssessmentRequirement
                    combined_graph.add((system, AI.hasRequirement, AI.FundamentalRightsAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> FundamentalRightsAssessmentRequirement")
                    inferences_count += 1
                
                # NUEVA CADENA: LawEnforcementCriterion -> DueProcess + ConformityAssessment
                if (system, AI.hasNormativeCriterion, AI.LawEnforcementCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.DueProcess))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> DueProcess")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.ConformityAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> ConformityAssessmentRequirement")
                    inferences_count += 1
                
                # NUEVA CADENA: MigrationBorderCriterion -> DataGovernance + RiskManagement
                if (system, AI.hasNormativeCriterion, AI.MigrationBorderCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.DataGovernanceRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> DataGovernanceRequirement (Migration)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.RiskManagementRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> RiskManagementRequirement")
                    inferences_count += 1
                
                # =============================================================
                # NUEVAS REGLAS TÉCNICAS PARA CRITERIOS INTERNOS (EU AI ACT)
                # =============================================================
                
                # REGLA 13: Modelos con >10^25 FLOPs -> SystemicRisk
                system_flops = None
                for _, _, flops_value in combined_graph.triples((system, AI.hasComputationFLOPs, None)):
                    system_flops = float(flops_value)
                    break
                
                if system_flops and system_flops > 1e25:  # 10^25 FLOPs threshold
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.SystemicRisk))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> SystemicRisk (FLOPs: {system_flops:.2e})")
                    inferences_count += 1
                
                # REGLA 14: Modelos con >1B parámetros -> HighImpactCapabilities
                system_params = None
                for _, _, params_value in combined_graph.triples((system, AI.hasParameterCount, None)):
                    system_params = int(params_value)
                    break
                
                if system_params and system_params > 1_000_000_000:  # 1B parameters threshold
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.HighImpactCapabilities))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> HighImpactCapabilities (Params: {system_params:,})")
                    inferences_count += 1
                
                # REGLA 15: Alta autonomía (>0.8) -> LacksHumanOversight
                system_autonomy = None
                for _, _, autonomy_value in combined_graph.triples((system, AI.hasAutonomyLevel, None)):
                    system_autonomy = float(autonomy_value)
                    break
                
                if system_autonomy and system_autonomy > 0.8:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.LacksHumanOversight))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> LacksHumanOversight (Autonomy: {system_autonomy})")
                    inferences_count += 1
                
                # REGLA 16: Sistema adaptativo -> AdaptiveCapability
                is_adaptive = None
                for _, _, adaptive_value in combined_graph.triples((system, AI.isAdaptiveSystem, None)):
                    is_adaptive = bool(adaptive_value.value) if hasattr(adaptive_value, 'value') else str(adaptive_value).lower() == 'true'
                    break
                
                if is_adaptive:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.AdaptiveCapability))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> AdaptiveCapability")
                    inferences_count += 1
                
                # REGLA 17: Alto alcance de mercado (>10,000 usuarios) -> SystemicRisk
                market_reach = None
                for _, _, reach_value in combined_graph.triples((system, AI.hasMarketReach, None)):
                    market_reach = int(reach_value)
                    break
                
                if market_reach and market_reach > 10000:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.SystemicRisk))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> SystemicRisk (Market reach: {market_reach:,})")
                    inferences_count += 1
                
                # REGLA 18: Baja precisión (<0.85) -> AccuracyLevel
                system_accuracy = None
                for _, _, accuracy_value in combined_graph.triples((system, AI.hasAccuracyRate, None)):
                    system_accuracy = float(accuracy_value)
                    break
                
                if system_accuracy and system_accuracy < 0.85:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.AccuracyLevel))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> AccuracyLevel (Accuracy: {system_accuracy})")
                    inferences_count += 1
                
                # REGLA 19: Modelos Transformer/Foundation -> ModelComplexity
                for algorithm_type in combined_graph.objects(system, AI.hasAlgorithmType):
                    if algorithm_type in [AI.TransformerModel, AI.FoundationModel, AI.GenerativeModel]:
                        combined_graph.add((system, AI.hasTechnicalCriterion, AI.ModelComplexity))
                        print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalCriterion -> ModelComplexity (Algorithm: {algorithm_type})")
                        inferences_count += 1
                        break
                
                # =============================================================
                # REGLAS EN CADENA PARA CRITERIOS TÉCNICOS
                # =============================================================
                
                # REGLA 20: SystemicRisk -> múltiples requisitos de mitigación
                if (system, AI.hasTechnicalCriterion, AI.SystemicRisk) in combined_graph:
                    # -> Evaluación continua de riesgo
                    combined_graph.add((system, AI.hasRequirement, AI.RiskManagementRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> RiskManagementRequirement (SystemicRisk)")
                    inferences_count += 1
                    
                    # -> Monitoreo post-mercado reforzado
                    combined_graph.add((system, AI.hasRequirement, AI.PostMarketMonitoringRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> PostMarketMonitoringRequirement (SystemicRisk)")
                    inferences_count += 1
                    
                    # -> Ciberseguridad avanzada
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.CybersecurityRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> CybersecurityRequirement (SystemicRisk)")
                    inferences_count += 1
                
                # REGLA 21: HighImpactCapabilities -> evaluaciones especializadas
                if (system, AI.hasTechnicalCriterion, AI.HighImpactCapabilities) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.ConformityAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> ConformityAssessmentRequirement (HighImpact)")
                    inferences_count += 1
                
                # REGLA 22: AdaptiveCapability -> supervisión continua
                if (system, AI.hasTechnicalCriterion, AI.AdaptiveCapability) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.HumanOversightRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> HumanOversightRequirement (Adaptive)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.EventLoggingRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> EventLoggingRequirement (Adaptive)")
                    inferences_count += 1
                
                # REGLA 23: ModelComplexity -> requisitos de transparencia
                if (system, AI.hasTechnicalCriterion, AI.ModelComplexity) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.TransparencyRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> TransparencyRequirement (Complex)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.Auditability))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> Auditability (Complex)")
                    inferences_count += 1
                
                # NUEVA CADENA: CriticalInfrastructureCriterion -> múltiples requisitos
                if (system, AI.hasNormativeCriterion, AI.CriticalInfrastructureCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.AccuracyEvaluationRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> AccuracyEvaluationRequirement")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.ConformityAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> ConformityAssessmentRequirement (Critical)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.CybersecurityRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> CybersecurityRequirement")
                    inferences_count += 1
                
                # NUEVA CADENA: PrivacyProtection -> DataProtection + Consent
                if (system, AI.hasNormativeCriterion, AI.PrivacyProtection) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.DataGovernanceRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> DataGovernanceRequirement (Privacy)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.DataEncryption))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> DataEncryption (Privacy)")
                    inferences_count += 1
                
                # NUEVA CADENA: EducationEvaluationCriterion -> AccuracyEvaluation + HumanOversight + Traceability
                if (system, AI.hasNormativeCriterion, AI.EducationEvaluationCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasRequirement, AI.AccuracyEvaluationRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> AccuracyEvaluationRequirement (Education)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.HumanOversightRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> HumanOversightRequirement (Education)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.TraceabilityRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> TraceabilityRequirement (Education)")
                    inferences_count += 1
                
                # FIN FALLBACK - Si llegamos aquí, el motor externo falló
                print(f"DEBUG: Fallback aplicó {inferences_count} inferencias")
            
            print(f"DEBUG: *** RAZONAMIENTO COMPLETADO: {inferences_count} inferencias aplicadas ***")
                
        except Exception as e:
            print(f"ERROR crítico en razonamiento híbrido: {e}")
            # Fallback básico
            combined_graph = Graph()
            combined_graph.parse(data_file, format="turtle")

        # Serializar el grafo combinado con todas las inferencias aplicadas
        try:
            print("DEBUG: Serializando grafo con inferencias...")
            ttl_output = combined_graph.serialize(format="turtle")
            print(f"DEBUG: Grafo final serializado: {len(ttl_output)} caracteres, {len(combined_graph)} triples")
            
            # Verificar que las inferencias estén en el TTL de salida
            inferences_in_output = 0
            if "hasNormativeCriterion" in ttl_output:
                inferences_in_output += ttl_output.count("hasNormativeCriterion")
            if "hasRequirement" in ttl_output:
                inferences_in_output += ttl_output.count("hasRequirement")
            if "hasTechnicalCriterion" in ttl_output:
                inferences_in_output += ttl_output.count("hasTechnicalCriterion")
            
            print(f"DEBUG: TTL de salida contiene {inferences_in_output} relaciones de inferencia")
                
        except Exception as e:
            print(f"ERROR serializando grafo: {e}")
            # Fallback: usar datos básicos
            try:
                fallback_graph = Graph()
                fallback_graph.parse(data_file, format="turtle")
                ttl_output = fallback_graph.serialize(format="turtle")
            except:
                with open(data_file, 'r') as f:
                    ttl_output = f.read()
    
    return Response(content=ttl_output, media_type="text/turtle")

@app.get("/")
def root():
    return {"message": "SWRL Reasoner Service. Use /reason endpoint."}
