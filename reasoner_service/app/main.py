from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi import responses
from fastapi import status
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from owlready2 import get_ontology, onto_path, World, sync_reasoner_pellet
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL
import tempfile
import shutil
import os
import json
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
    request: Request,
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
            try:
                rules_graph.parse(rules_file, format="turtle")
                print(f"DEBUG: Reglas y conceptos cargados: {len(rules_graph)} triples")
            except Exception as e:
                print(f"DEBUG: ⚠️  No se pudieron parsear reglas SWRL ({e}), continuando con reglas Python")
                # Continuar sin reglas SWRL - usaremos motor externo Python
            
            # 4. Combinar todos los grafos
            combined_graph = base_graph + system_graph + rules_graph
            print(f"DEBUG: Grafo combinado: {len(combined_graph)} triples total")
            
            # 5. APLICAR INFERENCIAS HÍBRIDAS (EXTERNAS + FALLBACK)
            inferences_count = 0
            
            # Intentar usar motor de reglas externas primero
            try:
                print(f"DEBUG: Intentando cargar motor de reglas externas...")
                import sys
                
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
        


        except Exception as e:
            print(f"ERROR crítico en razonamiento híbrido: {e}")
            # Fallback básico - usar solo datos originales
            combined_graph = Graph()
            combined_graph.parse(data_file, format="turtle")
            inferences_count = 0
        
        # =============================================================
        # APLICAR REGLAS GENÉRICAS SWRL (NAVEGAN LA ONTOLOGÍA)
        # =============================================================
        print(f"DEBUG: Aplicando 6 reglas genéricas SWRL que navegan ontología (pre-inferences: {inferences_count})...")

        try:
            # Re-definir AI namespace para estar seguros
            AI = Namespace("http://ai-act.eu/ai#")

            for system in combined_graph.subjects(RDF.type, AI.IntelligentSystem):
                print(f"DEBUG: Procesando sistema con reglas genéricas SWRL: {system}")

                # =============================================================
                # REGLA 1: Purpose → activatesCriterion → hasCriteria
                # Si un sistema tiene un propósito, y ese propósito activa un criterio,
                # entonces el sistema tiene ese criterio
                # =============================================================
                for purpose in combined_graph.objects(system, AI.hasPurpose):
                    for criterion in combined_graph.objects(purpose, AI.activatesCriterion):
                        combined_graph.add((system, AI.hasCriteria, criterion))
                        print(f"DEBUG: ✅ REGLA 1 aplicada: {system} hasCriteria {criterion} (vía hasPurpose → activatesCriterion)")
                        inferences_count += 1

                # =============================================================
                # REGLA 2: DeploymentContext → triggersCriterion → hasCriteria
                # Si un sistema tiene un contexto de despliegue, y ese contexto dispara un criterio,
                # entonces el sistema tiene ese criterio
                # =============================================================
                for context in combined_graph.objects(system, AI.hasDeploymentContext):
                    for criterion in combined_graph.objects(context, AI.triggersCriterion):
                        combined_graph.add((system, AI.hasCriteria, criterion))
                        print(f"DEBUG: ✅ REGLA 2 aplicada: {system} hasCriteria {criterion} (vía hasDeploymentContext → triggersCriterion)")
                        inferences_count += 1

                # =============================================================
                # REGLA 3: SystemCapabilityCriteria → (actúan como criterios derivados)
                # Si un sistema tiene SystemCapabilityCriteria, se trata como criterios
                # =============================================================
                for capability in combined_graph.objects(system, AI.hasSystemCapabilityCriteria):
                    combined_graph.add((system, AI.hasCriteria, capability))
                    print(f"DEBUG: ✅ REGLA 3 aplicada: {system} hasCriteria {capability} (vía hasSystemCapabilityCriteria)")
                    inferences_count += 1

                # =============================================================
                # REGLA 4: Criterion → activatesRequirement → hasComplianceRequirement
                # Si un sistema tiene un criterio, y ese criterio activa requisitos,
                # entonces el sistema tiene esos requisitos
                # =============================================================
                for criterion in combined_graph.objects(system, AI.hasCriteria):
                    for requirement in combined_graph.objects(criterion, AI.activatesRequirement):
                        combined_graph.add((system, AI.hasComplianceRequirement, requirement))
                        print(f"DEBUG: ✅ REGLA 4 aplicada: {system} hasComplianceRequirement {requirement} (vía hasCriteria → activatesRequirement)")
                        inferences_count += 1

                # =============================================================
                # REGLA 4.5: hasProhibitedPractice → hasCriteria (Art. 5 AI Act)
                # Si un sistema tiene una práctica prohibida, esa práctica se convierte
                # en criterio activado para permitir inferencia de UnacceptableRisk
                # IMPORTANTE: Debe ejecutarse ANTES de REGLA 5 para que las prácticas
                # prohibidas puedan inferir su nivel de riesgo
                # =============================================================
                for practice in combined_graph.objects(system, AI.hasProhibitedPractice):
                    combined_graph.add((system, AI.hasCriteria, practice))
                    print(f"DEBUG: ✅ REGLA 4.5 aplicada: {system} hasCriteria {practice} (vía hasProhibitedPractice - Art. 5)")
                    inferences_count += 1

                # =============================================================
                # REGLA 5: Criterion → assignsRiskLevel → hasRiskLevel
                # Si un sistema tiene un criterio, y ese criterio asigna un nivel de riesgo,
                # entonces el sistema tiene ese nivel de riesgo
                # NOTA: Usamos list() para crear una copia de los criterios actuales,
                # incluyendo los añadidos por REGLA 4.5 (prácticas prohibidas)
                # =============================================================
                all_criteria = list(combined_graph.objects(system, AI.hasCriteria))
                for criterion in all_criteria:
                    for risk_level in combined_graph.objects(criterion, AI.assignsRiskLevel):
                        combined_graph.add((system, AI.hasRiskLevel, risk_level))
                        print(f"DEBUG: ✅ REGLA 5 aplicada: {system} hasRiskLevel {risk_level} (vía hasCriteria → assignsRiskLevel)")
                        inferences_count += 1

                # =============================================================
                # REGLA 5.5a: Excepciones Art. 5.2 para Identificación Biométrica Remota
                # Si el sistema tiene:
                # 1. Una práctica prohibida de identificación biométrica (RealTimeBiometricIdentificationCriterion)
                # 2. Una excepción legal válida (Art. 5.2)
                # 3. Autorización judicial previa
                # Entonces: El sistema pasa de UnacceptableRisk a HighRisk (puede desplegarse con restricciones)
                # =============================================================
                prohibited_practices = list(combined_graph.objects(system, AI.hasProhibitedPractice))
                legal_exceptions = list(combined_graph.objects(system, AI.hasLegalException))
                has_judicial_auth = any(combined_graph.objects(system, AI.hasJudicialAuthorization))

                # Verificar si tiene identificación biométrica remota en tiempo real
                has_biometric_prohibition = any(
                    "RealTimeBiometricIdentification" in str(p) or "BiometricIdentification" in str(p)
                    for p in prohibited_practices
                )

                # Excepciones válidas del Art. 5.2
                valid_exceptions = [
                    "VictimSearchException",      # Art. 5.2(a) - Búsqueda de víctimas
                    "TerroristThreatException",   # Art. 5.2(b) - Amenaza terrorista
                    "SeriousCrimeException"       # Art. 5.2(c) - Delito grave
                ]
                has_valid_exception = any(
                    any(exc in str(le) for exc in valid_exceptions)
                    for le in legal_exceptions
                )

                if has_biometric_prohibition and has_valid_exception and has_judicial_auth:
                    # Tiene excepción válida con autorización judicial
                    # Cambiar de UnacceptableRisk a HighRisk
                    for risk_level in list(combined_graph.objects(system, AI.hasRiskLevel)):
                        if "UnacceptableRisk" in str(risk_level):
                            combined_graph.remove((system, AI.hasRiskLevel, risk_level))
                            combined_graph.add((system, AI.hasRiskLevel, AI.HighRisk))
                            combined_graph.add((system, AI.hasArticle5Exception, Literal(True)))
                            print(f"DEBUG: ✅ REGLA 5.5a aplicada: {system} UnacceptableRisk → HighRisk (Art. 5.2 excepción con autorización judicial)")
                            inferences_count += 2

                # =============================================================
                # REGLA 5.5: Override de Niveles de Riesgo - El más restrictivo prevalece
                # Jerarquía: UnacceptableRisk > HighRisk > LimitedRisk > MinimalRisk
                # Si UnacceptableRisk está presente, eliminar todos los demás niveles
                # Si HighRisk está presente (sin Unacceptable), eliminar Limited y Minimal
                # =============================================================
                current_risk_levels = list(combined_graph.objects(system, AI.hasRiskLevel))
                risk_level_strs = [str(r) for r in current_risk_levels]

                has_unacceptable = any("UnacceptableRisk" in r for r in risk_level_strs)
                has_high = any("HighRisk" in r for r in risk_level_strs)
                has_limited = any("LimitedRisk" in r for r in risk_level_strs)
                has_minimal = any("MinimalRisk" in r for r in risk_level_strs)

                if has_unacceptable:
                    # UnacceptableRisk es el más restrictivo - eliminar todos los demás
                    for risk_level in current_risk_levels:
                        risk_str = str(risk_level)
                        if "HighRisk" in risk_str or "LimitedRisk" in risk_str or "MinimalRisk" in risk_str:
                            combined_graph.remove((system, AI.hasRiskLevel, risk_level))
                            print(f"DEBUG: ✅ REGLA 5.5 aplicada: ELIMINADO {risk_level} (override por UnacceptableRisk)")
                            inferences_count += 1
                elif has_high:
                    # HighRisk prevalece sobre Limited y Minimal
                    for risk_level in current_risk_levels:
                        risk_str = str(risk_level)
                        if "LimitedRisk" in risk_str or "MinimalRisk" in risk_str:
                            combined_graph.remove((system, AI.hasRiskLevel, risk_level))
                            print(f"DEBUG: ✅ REGLA 5.5 aplicada: ELIMINADO {risk_level} (override por HighRisk)")
                            inferences_count += 1
                elif has_limited:
                    # LimitedRisk prevalece sobre Minimal
                    for risk_level in current_risk_levels:
                        risk_str = str(risk_level)
                        if "MinimalRisk" in risk_str:
                            combined_graph.remove((system, AI.hasRiskLevel, risk_level))
                            print(f"DEBUG: ✅ REGLA 5.5 aplicada: ELIMINADO {risk_level} (override por LimitedRisk)")
                            inferences_count += 1

                # =============================================================
                # REGLA 6: FoundationModelScale → GPAI Classification
                # Si un sistema tiene FoundationModelScale, es un GPAI
                # =============================================================
                for model_scale in combined_graph.objects(system, AI.hasModelScale):
                    if str(model_scale).endswith("FoundationModelScale"):
                        combined_graph.add((system, AI.hasGPAIClassification, AI.GeneralPurposeAI))
                        print(f"DEBUG: ✅ REGLA 6 aplicada: {system} hasGPAIClassification GeneralPurposeAI (vía hasModelScale=FoundationModelScale)")
                        inferences_count += 1
                        break  # Solo una vez por sistema

                # =============================================================
                # REGLA 7: Affected Person + High Risk → Requires Explainability (Art. 86)
                # Si un sistema tiene affected persons Y es high-risk → requiere explicabilidad
                # =============================================================
                has_affected_person = any(combined_graph.objects(system, AI.hasSubject))
                risk_levels = list(combined_graph.objects(system, AI.hasRiskLevel))
                is_high_risk = any("HighRisk" in str(r) or "High" in str(r) for r in risk_levels)

                if has_affected_person and is_high_risk:
                    combined_graph.add((system, AI.requiresExplainability, Literal(True)))
                    combined_graph.add((system, AI.hasComplianceRequirement, AI.ExplainabilityRequirement))
                    print(f"DEBUG: ✅ REGLA 7 aplicada: {system} requiresExplainability=true (Art. 86: hasSubject + HighRisk)")
                    inferences_count += 2

                # =============================================================
                # REGLA 8: Affected Person Category → Fundamental Rights Assessment (Art. 27)
                # Si affected persons incluyen grupos vulnerables → FRIA obligatorio
                # =============================================================
                vulnerable_categories = ["Minor", "Child", "Elderly", "Disabled", "Migrant", "Asylum"]
                for subject in combined_graph.objects(system, AI.hasSubject):
                    subject_str = str(subject).lower()
                    if any(v.lower() in subject_str for v in vulnerable_categories):
                        combined_graph.add((system, AI.requiresFundamentalRightsAssessment, Literal(True)))
                        combined_graph.add((system, AI.hasComplianceRequirement, AI.FundamentalRightsImpactAssessment))
                        print(f"DEBUG: ✅ REGLA 8 aplicada: {system} requiresFundamentalRightsAssessment=true (Art. 27: vulnerable group detected in {subject})")
                        inferences_count += 2
                        break  # Solo una vez por sistema

                # =============================================================
                # REGLA 9: Employment Context + Affected Persons → Art. 26 Notification
                # Si deployer usa sistema para decisiones de empleo → notificación a affected persons
                # =============================================================
                employment_purposes = ["Employment", "Recruitment", "HiringDecision", "WorkerManagement"]
                for purpose in combined_graph.objects(system, AI.hasPurpose):
                    purpose_str = str(purpose)
                    if any(ep in purpose_str for ep in employment_purposes) and has_affected_person:
                        combined_graph.add((system, AI.requiresAffectedPersonNotification, Literal(True)))
                        combined_graph.add((system, AI.hasComplianceRequirement, AI.WorkerNotificationRequirement))
                        print(f"DEBUG: ✅ REGLA 9 aplicada: {system} requiresAffectedPersonNotification=true (Art. 26: employment purpose + affected persons)")
                        inferences_count += 2
                        break

                # =============================================================
                # REGLA 10: Biometric + Public Space + Affected Persons → Prohibited or Restricted
                # Si sistema biométrico en espacio público afecta ciudadanos → verificar prohibiciones Art. 5
                # =============================================================
                biometric_purposes = ["BiometricIdentification", "FacialRecognition", "RemoteBiometric"]
                public_contexts = ["PublicSpace", "PubliclyAccessible", "LawEnforcement"]

                has_biometric = any(any(bp in str(p) for bp in biometric_purposes) for p in combined_graph.objects(system, AI.hasPurpose))
                has_public_context = any(any(pc in str(c) for pc in public_contexts) for c in combined_graph.objects(system, AI.hasDeploymentContext))

                if has_biometric and has_public_context and has_affected_person:
                    combined_graph.add((system, AI.requiresProhibitionReview, Literal(True)))
                    combined_graph.add((system, AI.hasComplianceRequirement, AI.Article5ProhibitionReview))
                    print(f"DEBUG: ✅ REGLA 10 aplicada: {system} requiresProhibitionReview=true (Art. 5: biometric + public space + affected persons)")
                    inferences_count += 2

            print(f"DEBUG: Reglas genéricas SWRL completadas. Total inferencias aplicadas: {inferences_count}")

        except Exception as fallback_error:
            print(f"ERROR en reglas genéricas SWRL: {fallback_error}")
        
        print(f"DEBUG: *** RAZONAMIENTO COMPLETADO: {inferences_count} inferencias aplicadas ***")

        # Serializar el grafo combinado con todas las inferencias aplicadas
        try:
            print("DEBUG: Serializando grafo con inferencias...")
            print(f"DEBUG: Triples en combined_graph antes de serializar: {len(combined_graph)}")
            # Log sample of triples to verify inferences are in the graph
            print("DEBUG: Sample triples en combined_graph (primeras 20):")
            count = 0
            for s, p, o in combined_graph:
                if count < 20:
                    print(f"  {s} {p} {o}")
                    count += 1

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
    
    # Detectar el tipo de respuesta solicitado
    accept_header = request.headers.get("accept", "text/turtle")
    
    if "application/json" in accept_header.lower():
        # Convertir TTL a JSON-LD y crear respuesta JSON estructurada
        try:
            g = Graph()
            g.parse(data=ttl_output, format="turtle")
            AI = Namespace("http://ai-act.eu/ai#")
            print("DEBUG: Triples en el grafo tras parseo TTL:")
            for s, p, o in g:
                print(f"  {s} {p} {o}")
            inferred_relationships = {
                "hasNormativeCriterion": [],
                "hasTechnicalCriterion": [],
                "hasContextualCriterion": [],
                "hasRequirement": [],
                "hasTechnicalRequirement": [],
                "hasCriteria": [],
                "hasComplianceRequirement": [],
                "hasRiskLevel": [],
                "hasGPAIClassification": []
            }
            system_id = None
            system_name = None
            print(f"DEBUG: Total triples en grafo parseado: {len(g)}")
            for system in g.subjects(RDF.type, AI.IntelligentSystem):
                print(f"DEBUG: Encontrado sistema: {system}")
                system_id = str(system)
                name = None
                for _, _, n in g.triples((system, AI.hasName, None)):
                    name = str(n)
                system_name = name
                print(f"DEBUG: Extrayendo relaciones para sistema {system}...")
                for rel, arr in inferred_relationships.items():
                    pred = getattr(AI, rel)
                    matches = list(g.triples((system, pred, None)))
                    if matches:
                        print(f"DEBUG: ✅ Encontrados {len(matches)} triples para {rel}")
                    for _, _, obj in matches:
                        arr.append(str(obj))
                print(f"DEBUG: Resumen relaciones extraídas: {inferred_relationships}")
            response_data = {
                "system_id": system_id or "",
                "system_name": system_name or "",
                "reasoning_completed": True,
                "inferred_relationships": inferred_relationships,
                "raw_ttl": ttl_output,
                "rules_applied": sum(len(arr) for arr in inferred_relationships.values()),
                "formato": "JSON-LD",
                "graph": [
                    {
                        "@id": system_id or "",
                        "hasNormativeCriterion": inferred_relationships["hasNormativeCriterion"],
                        "hasTechnicalCriterion": inferred_relationships["hasTechnicalCriterion"],
                        "hasContextualCriterion": inferred_relationships["hasContextualCriterion"],
                        "hasRequirement": inferred_relationships["hasRequirement"],
                        "hasTechnicalRequirement": inferred_relationships["hasTechnicalRequirement"],
                        "hasCriteria": inferred_relationships["hasCriteria"],
                        "hasComplianceRequirement": inferred_relationships["hasComplianceRequirement"],
                        "hasRiskLevel": inferred_relationships["hasRiskLevel"],
                        "hasGPAIClassification": inferred_relationships["hasGPAIClassification"],
                        "system_name": system_name or ""
                    }
                ]
            }
            return Response(
                content=json.dumps(response_data, indent=2, ensure_ascii=False),
                media_type="application/json"
            )
        except Exception as e:
            print(f"ERROR generando JSON razonamiento: {e}")
            response_data = {
                "system_id": "",
                "system_name": "",
                "reasoning_completed": False,
                "inferred_relationships": {},
                "raw_ttl": ttl_output,
                "rules_applied": 0,
                "formato": "JSON-LD",
                "graph": []
            }
            return Response(
                content=json.dumps(response_data, indent=2, ensure_ascii=False),
                media_type="application/json"
            )
    else:
        return Response(content=ttl_output, media_type="text/turtle")
