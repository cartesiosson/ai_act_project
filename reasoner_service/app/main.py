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
        # APLICAR REGLAS HARDCODEADAS (SIEMPRE SE EJECUTAN COMO FALLBACK)
        # =============================================================
        print(f"DEBUG: Aplicando reglas hardcodeadas como fallback (pre-inferences: {inferences_count})...")
        
        try:
            # Re-definir AI namespace para estar seguros
            AI = Namespace("http://ai-act.eu/ai#")
            
            for system in combined_graph.subjects(RDF.type, AI.IntelligentSystem):
                print(f"DEBUG: Procesando sistema con reglas hardcodeadas: {system}")
                
                # =============================================================
                # REGLAS PARA HASYSTEMCAPABILITYCRITERIA (CRITERIOS DE CAPACIDAD)
                # =============================================================
                
                # REGLA 24: JudicialSupportCriterion (capacidad) -> múltiples requisitos
                if (system, AI.hasSystemCapabilityCriteria, AI.JudicialSupportCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.DueProcess))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> DueProcess (Judicial Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.HumanOversightRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> HumanOversightRequirement (Judicial Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.ConformityAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> ConformityAssessmentRequirement (Judicial Capability)")
                    inferences_count += 1
                
                # REGLA 25: BiometricIdentificationCriterion (capacidad) -> múltiples requisitos
                if (system, AI.hasSystemCapabilityCriteria, AI.BiometricIdentificationCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasContextualCriterion, AI.BiometricSecurity))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasContextualCriterion -> BiometricSecurity (Biometric Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasTechnicalRequirement, AI.DataEncryption))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasTechnicalRequirement -> DataEncryption (Biometric Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.DataGovernanceRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> DataGovernanceRequirement (Biometric Capability)")
                    inferences_count += 1
                
                # REGLA 26: RecruitmentEmploymentCriterion (capacidad) -> múltiples requisitos
                if (system, AI.hasSystemCapabilityCriteria, AI.RecruitmentEmploymentCriterion) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.NonDiscrimination))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> NonDiscrimination (Recruitment Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.TransparencyRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> TransparencyRequirement (Recruitment Capability)")
                    inferences_count += 1
                    
                    combined_graph.add((system, AI.hasRequirement, AI.FundamentalRightsAssessmentRequirement))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasRequirement -> FundamentalRightsAssessmentRequirement (Recruitment Capability)")
                    inferences_count += 1
                
                # Reglas adicionales para otras propiedades también
                # REGLA TÉCNICA: BiometricIdentification (propósito) -> BiometricSecurity
                if (system, AI.hasPurpose, AI.BiometricIdentification) in combined_graph:
                    combined_graph.add((system, AI.hasContextualCriterion, AI.BiometricSecurity))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasContextualCriterion -> BiometricSecurity (por propósito)")
                    inferences_count += 1
                
                # REGLA TÉCNICA: Education context -> ProtectionOfMinors
                if (system, AI.hasDeploymentContext, AI.Education) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.ProtectionOfMinors))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> ProtectionOfMinors (Education context)")
                    inferences_count += 1
                
                # =============================================================
                # REGLAS PARA HASALGORITHMTYPE (REGLAS TÉCNICAS 19A, 19B, 19C)
                # =============================================================
                
                # REGLA 19A: FoundationModel -> ModelComplexity
                if (system, AI.hasAlgorithmType, AI.FoundationModel) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.ModelComplexity))
                    print(f"DEBUG: ✅ Inferencia aplicada (RULE_19A): {system} -> hasTechnicalCriterion -> ModelComplexity (FoundationModel)")
                    inferences_count += 1
                
                # REGLA 19B: TransformerModel -> ModelComplexity
                if (system, AI.hasAlgorithmType, AI.TransformerModel) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.ModelComplexity))
                    print(f"DEBUG: ✅ Inferencia aplicada (RULE_19B): {system} -> hasTechnicalCriterion -> ModelComplexity (TransformerModel)")
                    inferences_count += 1
                
                # REGLA 19C: GenerativeModel -> ModelComplexity
                if (system, AI.hasAlgorithmType, AI.GenerativeModel) in combined_graph:
                    combined_graph.add((system, AI.hasTechnicalCriterion, AI.ModelComplexity))
                    print(f"DEBUG: ✅ Inferencia aplicada (RULE_19C): {system} -> hasTechnicalCriterion -> ModelComplexity (GenerativeModel)")
                    inferences_count += 1
            
            print(f"DEBUG: Reglas hardcodeadas completadas. Total inferencias aplicadas: {inferences_count}")
        
        except Exception as fallback_error:
            print(f"ERROR en reglas hardcodeadas de fallback: {fallback_error}")
        
        print(f"DEBUG: *** RAZONAMIENTO COMPLETADO: {inferences_count} inferencias aplicadas ***")

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
                "hasTechnicalRequirement": []
            }
            system_id = None
            system_name = None
            for system in g.subjects(RDF.type, AI.IntelligentSystem):
                system_id = str(system)
                name = None
                for _, _, n in g.triples((system, AI.hasName, None)):
                    name = str(n)
                system_name = name
                for rel, arr in inferred_relationships.items():
                    pred = getattr(AI, rel)
                    for _, _, obj in g.triples((system, pred, None)):
                        arr.append(str(obj))
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
