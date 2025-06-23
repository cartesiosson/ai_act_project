# main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from rdflib import Graph
from models.system import IntelligentSystem
from db import get_database,ensure_indexes
import os, json
from routers.systems import router as systems_router
from routers.systems_fuseki import router as fuseki_router

from rdflib import URIRef, RDF, RDFS
from typing import List, Dict
from rdflib import Literal
from fastapi import Query
from rdflib.namespace import split_uri


app = FastAPI(title="AI Act Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # o ["*"] para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ont = Graph()
for ttl in os.listdir("ontologias"):
    if ttl.endswith(".ttl"):
        ont.parse(f"ontologias/{ttl}", format="turtle")


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

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    await ensure_indexes()

app.mount("/static", StaticFiles(directory="schema"), name="static")

app.include_router(systems_router)
app.include_router(fuseki_router)


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
                        "hasTrainingDataOrigin": "ai:InternalDataset",
                        "hasVersion": "1.0.0"
                    }
                }
            }
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
