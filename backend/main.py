
# main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from rdflib import Graph, URIRef, RDF, RDFS, Literal
from rdflib.namespace import split_uri
from models.system import IntelligentSystem
from db import get_database,ensure_indexes
import os, json
from routers.systems import router as systems_router
from routers.systems_fuseki import router as fuseki_router
from routers.reasoning import router as reasoning_router
from typing import List, Dict

app = FastAPI(title="AI Act Backend")



# Endpoint para escala de modelo según ontología v0.37.0
@app.get("/vocab/modelscales")
def get_model_scales(lang: str = Query("en")):
    return [
        {"id": "FoundationModelScale", "label": "Foundation Model Scale"},
        {"id": "RegularModelScale", "label": "Regular Model Scale"},
        {"id": "SmallModelScale", "label": "Small Model Scale"}
    ]

# Endpoint para capacidades principales (ajustar según ontología si es necesario)
@app.get("/vocab/capabilities")
def get_capabilities(lang: str = Query("en")):
    return [
        {"id": "Reasoning", "label": "Reasoning"},
        {"id": "Planning", "label": "Planning"},
        {"id": "Perception", "label": "Perception"},
        {"id": "Interaction", "label": "Interaction"}
    ]

# ENDPOINT DE PRUEBA SUPERPRIMARIO
@app.get("/test/superbasico")
def test_superprimario():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Leer la ruta de la ontología base desde la variable de entorno
ONTOLOGY_PATH = os.environ.get("ONTOLOGY_PATH")
if not ONTOLOGY_PATH or not os.path.isfile(ONTOLOGY_PATH):
    raise RuntimeError(f"No se encontró la ontología base en la ruta especificada por ONTOLOGY_PATH: {ONTOLOGY_PATH}")

ont = Graph()
ont.parse(ONTOLOGY_PATH, format="turtle")


def compact_uri(uri: str) -> str:
    try:
        namespace, name = split_uri(URIRef(uri))
        if "ai-act.eu/ai#" in namespace:
            return f"ai:{name}"
        return name
    except Exception:
        return uri

def get_label(graph: Graph, uri: URIRef, lang: str = "en") -> str:
    labels = list(graph.objects(uri, RDFS.label))
    for label in labels:
        if isinstance(label, Literal) and label.language == lang:
            return str(label)
    for label in labels:
        if isinstance(label, Literal) and label.language == "es":
            return str(label)
    if labels:
        return str(labels[0])
    return str(uri)

def get_options_for_property(graph: Graph, property_uri: str, lang: str = "en") -> List[Dict[str, str]]:
    property_ref = URIRef(property_uri)
    options = {}
    for range_uri in graph.objects(property_ref, RDFS.range):
        for instance in graph.subjects(RDF.type, range_uri):
            label = get_label(graph, instance, lang)
            options[str(instance)] = label
    for enum in graph.objects(property_ref, URIRef("http://www.w3.org/2002/07/owl#oneOf")):
        for item in graph.items(enum):
            label = get_label(graph, item, lang)
            options[str(item)] = label
    return [{"id": compact_uri(uri), "label": label} for uri, label in sorted(options.items(), key=lambda x: x[1])]

@app.get("/vocab/purposes")
def get_purposes(lang: str = Query("en")):
    return get_options_for_property(ont, "http://ai-act.eu/ai#hasPurpose", lang=lang)

@app.get("/vocab/risks")
def get_risks(lang: str = Query("en")):
    return get_options_for_property(ont, "http://ai-act.eu/ai#hasRiskLevel", lang=lang)

@app.get("/vocab/contexts")
def get_contexts(lang: str = Query("en")):
    return get_options_for_property(ont, "http://ai-act.eu/ai#hasDeploymentContext", lang=lang)

@app.get("/vocab/training_origins")
def get_origins(lang: str = Query("en")):
    return get_options_for_property(ont, "http://ai-act.eu/ai#hasTrainingDataOrigin", lang=lang)

@app.get("/vocab/algorithmtypes")
def get_algorithm_types(lang: str = Query("en")):
    """Devuelve solo los tipos de algoritmo individuales (hojas) recursivamente"""
    base = URIRef("http://ai-act.eu/ai#AlgorithmType")
    # Recursively find all leaf instances (those that are not a superclass of any other type)
    def get_true_leaves(node):
        children = set(ont.subjects(RDFS.subClassOf, node))
        leaves = []
        if not children:
            # If no subclasses, return instances (rdf:type) of this node
            instances = set(ont.subjects(RDF.type, node))
            return list(instances)
        for child in children:
            leaves.extend(get_true_leaves(child))
        return leaves

    # Get all leaf instances recursively
    leaf_instances = get_true_leaves(base)
    # Remove base node if present
    leaf_instances = [uri for uri in leaf_instances if uri != base]
    return [
        {"id": compact_uri(uri), "label": get_label(ont, uri, lang)}
        for uri in sorted(leaf_instances, key=lambda x: get_label(ont, x, lang))
    ]

@app.post("/debug/system")
def debug_system_creation(data: dict):
    """Endpoint de debug para ver qué datos llegan"""
    print(f"DEBUG - Datos recibidos: {data}")
    return {"received": data}


@app.get("/vocab/system_capability_criteria")
def get_system_capability_criteria(lang: str = Query("en")):
    # Encuentra todos los criterios (NormativeCriterion, TechnicalCriterion, ContextualCriterion)
    # que NO son objeto de ai:activatesCriterion desde ningún Purpose ni Context
    # Estos son criterios de capacidad del sistema

    # Tipos de criterios relevantes
    CRITERION_TYPES = [
        URIRef("http://ai-act.eu/ai#NormativeCriterion"),
        URIRef("http://ai-act.eu/ai#TechnicalCriterion"),
        URIRef("http://ai-act.eu/ai#ContextualCriterion"),
    ]

    # Criterios activados por algún propósito o contexto
    activated_criteria = set()
    
    # Buscar tanto activatesCriterion como triggersCriterion
    activates_predicate = URIRef("http://ai-act.eu/ai#activatesCriterion")
    triggers_predicate = URIRef("http://ai-act.eu/ai#triggersCriterion")
    
    for subj, _, obj in ont.triples((None, activates_predicate, None)):
        activated_criteria.add(obj)
    
    for subj, _, obj in ont.triples((None, triggers_predicate, None)):
        activated_criteria.add(obj)

    # Todos los criterios definidos en la ontología
    all_criteria = set()
    for t in CRITERION_TYPES:
        for crit in ont.subjects(RDF.type, t):
            all_criteria.add(crit)

    # Criterios de capacidad del sistema = definidos pero no activados por propósito/contexto
    system_capability_criteria = all_criteria - activated_criteria

    # Devuelve como lista de {id, label}
    return [
        {"id": compact_uri(uri), "label": get_label(ont, uri, lang)}
        for uri in sorted(system_capability_criteria, key=lambda x: get_label(ont, x, lang))
    ]

# Endpoint legacy para compatibilidad hacia atrás
@app.get("/vocab/inner_criteria")
def get_inner_criteria(lang: str = Query("en")):
    return get_system_capability_criteria(lang)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    await ensure_indexes()

app.mount("/static", StaticFiles(directory="schema"), name="static")

app.include_router(systems_router)
app.include_router(fuseki_router)
app.include_router(reasoning_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    path_key = None
    for p in openapi_schema["paths"].keys():
        if p.rstrip("/") == "/systems":
            path_key = p
            break

    if not path_key:
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    post_op = openapi_schema["paths"][path_key].get("post")
    if post_op:
        post_op["requestBody"] = {
            "required": True,
            "content": {
                "application/ld+json": {
                    "schema": {"$ref": "#/components/schemas/IntelligentSystem"},
                    "example": {
                        "@context": "http://ontologias/docs/context.jsonld",
                        "@type": "ai:IntelligentSystem",
                        "hasName": "Sim-01",
                        "hasPurpose": ["ai:ForEducation"],
                        "hasRiskLevel": "ai:HighRisk",
                        "hasDeploymentContext": ["ai:Education"],
                        "hasTrainingDataOrigin": ["ai:InternalDataset"],
                        "hasVersion": "1.0.0"
                    }
                }
            }
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi



