from fastapi import APIRouter, HTTPException
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from rdflib.plugin import register, Serializer
from pyld import jsonld
import os
import requests
import json

router = APIRouter(prefix="/systems/fuseki", tags=["systems_fuseki"])

FUSEKI_URL = "http://fuseki:3030/ds/sparql"
FUSEKI_GRAPH_DATA = os.getenv("FUSEKI_GRAPH_DATA", "http://ai-act.eu/ontology/data")
CONTEXT_URL = "http://ontologias/docs/context.jsonld"

@router.get("/{urn}")
async def get_system_fuseki_raw(urn: str):
    urn_uri = f"{urn}"

    query = f"""
    PREFIX ai: <http://ai-act.eu/ai#>
    CONSTRUCT {{
        <{urn_uri}> ?p ?o .
    }} WHERE {{
        GRAPH <{FUSEKI_GRAPH_DATA}> {{
            <{urn_uri}> ?p ?o .
        }}
    }}
    """

    res = requests.post(
        FUSEKI_URL,
        data={"query": query},
        headers={"Accept": "text/turtle"}
    )

    if not res.ok:
        raise HTTPException(status_code=500, detail=f"Error al consultar Fuseki: {res.text}")

    g = Graph()
    g.parse(data=res.text, format="turtle")

    AI = Namespace("http://ai-act.eu/ai#")
    g.bind("ai", AI)

    jsonld_data = json.loads(g.serialize(format="json-ld"))

    ctx_res = requests.get(CONTEXT_URL)
    ctx_res.raise_for_status()
    context_full = ctx_res.json()
    context_only = context_full.get("@context", context_full)

    compacted = jsonld.compact(jsonld_data, context_only)

    def shorten_keys(obj):
        if isinstance(obj, dict):
            return {
                key.replace("http://ai-act.eu/ai#", "ai:")
                if key.startswith("http://ai-act.eu/ai#") else key: shorten_keys(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [shorten_keys(item) for item in obj]
        else:
            return obj

    compacted_clean = shorten_keys(compacted)
    compacted_clean["@context"] = CONTEXT_URL

    # Normalizar campos múltiples como listas si aparecen repetidos
    def normalize_multivalue_fields(data, fields):
        for field in fields:
            if field in data and not isinstance(data[field], list):
                data[field] = [data[field]]
        return data

    compacted_clean = normalize_multivalue_fields(
        compacted_clean,
        ["ai:hasPurpose", "ai:hasDeploymentContext"]
    )

    return compacted_clean
