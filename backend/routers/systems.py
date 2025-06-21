from fastapi import APIRouter, Depends, HTTPException
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from models.system import IntelligentSystem
from db import get_database
import uuid
import json
from bson import ObjectId

router = APIRouter(prefix="/systems", tags=["systems"])

@router.post("", status_code=201)
async def create_system(json_ld: IntelligentSystem, db=Depends(get_database)):
    # Convertimos a dict
    json_ld = json_ld.dict(by_alias=True)

    # Generamos un URN único
    urn = f"urn:uuid:{uuid.uuid4()}"
    json_ld["ai:hasUrn"] = urn
    json_ld["@id"] = urn  # <= Añade esto

    # Guardamos en MongoDB
    result = await db.systems.insert_one(json_ld)

    # Eliminamos _id antes de RDFLib
    json_ld.pop("_id", None)

    # Convertimos a tripletas RDF
    g = Graph()
    g.parse(data=json.dumps(json_ld), format="json-ld", context=json_ld["@context"])

    # Aquí podrías subir el grafo a Fuseki si lo deseas

    return {"inserted_id": str(result.inserted_id), "urn": urn}

from bson import ObjectId

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
