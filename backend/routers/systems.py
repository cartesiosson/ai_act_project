from fastapi import APIRouter, Depends, HTTPException
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from models.system import IntelligentSystem
from db import get_database
import uuid
import json
import requests
import os
from pymongo.errors import DuplicateKeyError

user = os.getenv("FUSEKI_USER", "admin")
password = os.getenv("FUSEKI_PASSWORD", "admin")
dataset =  os.getenv("FUSEKI_DATASET", "ds")
end_point = os.getenv("FUSEKI_ENDPOINT", "http://fuseki:3030")
graph_data= os.getenv("FUSEKI_GRAPH_DATA", "http://ai-act.eu/ontology/data")

router = APIRouter(prefix="/systems", tags=["systems"])

@router.post("", status_code=201)
async def create_system(json_ld: IntelligentSystem, db=Depends(get_database)):
    json_ld = json_ld.dict(by_alias=True)
    urn = f"urn:uuid:{uuid.uuid4()}"
    json_ld["ai:hasUrn"] = urn
    json_ld["@id"] = urn

    try:
        result = await db.systems.insert_one(json_ld)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="System with same URN already exists")

    json_ld.pop("_id", None)
    print(f"Insertando en MongoDB: {json.dumps(json_ld)})")

    g = Graph()
    mapped = {}
    for k, v in json_ld.items():
        if not k.startswith("ai:") and k not in ["@id", "@type", "@context"]:
            mapped[f"ai:{k}"] = v
        else:
            mapped[k] = v

    # Asegurar que los valores múltiples se representen como listas
    for multivalue_key in ["ai:hasPurpose", "ai:hasDeploymentContext"]:
        if multivalue_key in mapped and not isinstance(mapped[multivalue_key], list):
            mapped[multivalue_key] = [mapped[multivalue_key]]

    g.parse(data=json.dumps(mapped), format="json-ld")

    fuseki_url = f"{end_point}/{dataset}/data?graph={graph_data}"
    headers = {
        "Content-Type": "application/n-triples"
    }
    nt_data = g.serialize(format="nt")
    print(f"Subiendo a Fuseki: {fuseki_url} con datos: {nt_data}")

    try:
        res = requests.post(fuseki_url, data=nt_data, headers=headers, auth=(user, password))
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        await db.systems.delete_one({"ai:hasUrn": urn})  # rollback si falla
        raise HTTPException(status_code=500, detail=f"Error al subir a Fuseki: {str(e)}")

    return {"inserted_id": str(result.inserted_id), "urn": urn}


def fix_mongo_ids(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("", response_model=list[dict])
async def list_systems(db=Depends(get_database)):
    systems_cursor = db.systems.find()
    systems = []
    async for doc in systems_cursor:
        systems.append(fix_mongo_ids(doc))
    return systems

@router.get("/{urn}")
async def get_system_by_urn(urn: str, db=Depends(get_database)):
    doc = await db.systems.find_one({"ai:hasUrn": urn})
    if doc:
        return fix_mongo_ids(doc)
    raise HTTPException(status_code=404, detail="System not found")
