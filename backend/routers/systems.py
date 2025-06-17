from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from rdflib import Graph
from pathlib import Path
import json

from models.system import IntelligentSystem
from db import get_database

router = APIRouter(prefix="/systems", tags=["systems"])

@router.get("/", response_model=list[IntelligentSystem])
async def get_systems(db: AsyncIOMotorDatabase = Depends(get_database)):
    docs = await db["systems"].find().to_list(length=None)
    return [IntelligentSystem(**doc) for doc in docs]

@router.post(
    "/",
    response_model=IntelligentSystem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new IntelligentSystem from JSON-LD",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/ld+json": {
                    "schema": {"$ref": "#/components/schemas/IntelligentSystem"},
                    "example": {
                        "@context": "http://localhost:8000/static/json-ld-context.json",
                        "@type": "ai:IntelligentSystem",
                        "hasName": "Sim-01",
                        "hasPurpose": "ai:ForEducation",
                        "hasRiskLevel": "ai:HighRisk",
                        "hasDeploymentContext": "ai:Education",
                        "hasTrainingDataOrigin": "ai:InternalDataset",
                        "hasVersion": "1.0.0"
                    }
                }
            }
        }
    }
)
async def create_system(
    raw_body: dict = Body(..., media_type="application/ld+json"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # 1) Leemos el JSON-LD bruto
    data = raw_body

    # 2) Si "@context" es una URL, la reemplazamos por el JSON local para evitar fetch externo
    ctx = data.get("@context")
    if isinstance(ctx, str):
        try:
            context_file = Path("schema/json-ld-context.json")
            full = json.loads(context_file.read_text(encoding="utf-8"))
            data["@context"] = full["@context"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No pude cargar el contexto JSON-LD: {e}"
            )

    # 3) Parseamos el JSON-LD ya completo
    try:
        inst_graph = Graph().parse(data=json.dumps(data), format="json-ld")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JSON-LD inválido: {e}"
        )

    # 4) Validación SPARQL ASK para asegurar el tipo
    ask_q = """
    PREFIX ai: <http://ai-act.eu/ai#>
    ASK { ?s a ai:IntelligentSystem }
    """
    if not inst_graph.query(ask_q).askAnswer:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Falta rdf:type ai:IntelligentSystem"
        )

    # 5) Extracción de propiedades mediante SPARQL SELECT
    select_q = """
    PREFIX ai: <http://ai-act.eu/ai#>
    SELECT ?name ?purpose ?risk ?depCtx ?trainOrig ?ver WHERE {
      ?s a ai:IntelligentSystem ;
         ai:hasName               ?name ;
         ai:hasPurpose            ?purpose ;
         ai:hasRiskLevel          ?risk ;
         ai:hasDeploymentContext  ?depCtx ;
         ai:hasTrainingDataOrigin ?trainOrig ;
         ai:hasVersion            ?ver .
    }
    """
    res = inst_graph.query(select_q)
    rows = list(res)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Faltan propiedades requeridas para ai:IntelligentSystem"
        )
    row = rows[0]

    payload = {
        "hasName": str(row.name),
        "hasPurpose": str(row.purpose),
        "hasRiskLevel": str(row.risk),
        "hasDeploymentContext": str(row.depCtx),
        "hasTrainingDataOrigin": str(row.trainOrig),
        "hasVersion": str(row.ver)
    }

    # 6) Validación Pydantic
    system = IntelligentSystem(**payload)

    # 7) Serialización a str e inserción en MongoDB
    doc = { field: str(value) for field, value in system.dict(by_alias=True).items() }
    result = await db["systems"].insert_one(doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo insertar el IntelligentSystem en la base de datos"
        )

    return system

