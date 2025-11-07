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
            
            # 5. APLICAR INFERENCIAS MANUALES BASADAS EN REGLAS SWRL
            inferences_count = 0
            
            # Buscar todos los sistemas inteligentes
            for system in combined_graph.subjects(RDF.type, AI.IntelligentSystem):
                print(f"DEBUG: Procesando sistema: {system}")
                
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
                
                # REGLA 2: Employment -> NonDiscrimination
                if (system, AI.hasPurpose, AI.Employment) in combined_graph:
                    combined_graph.add((system, AI.hasNormativeCriterion, AI.NonDiscrimination))
                    print(f"DEBUG: ✅ Inferencia aplicada: {system} -> hasNormativeCriterion -> NonDiscrimination")
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
