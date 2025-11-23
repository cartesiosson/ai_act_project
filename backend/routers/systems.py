from fastapi import APIRouter, Depends, HTTPException, Body
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from models.system import IntelligentSystem
from db import get_database
import uuid
import json
import requests
import os
from pymongo.errors import DuplicateKeyError
from fastapi import Query
from derivation import derive_classifications, derive_requirements_from_criteria

user = os.getenv("FUSEKI_USER", "admin")
password = os.getenv("FUSEKI_PASSWORD", "admin")
dataset =  os.getenv("FUSEKI_DATASET", "ds")
end_point = os.getenv("FUSEKI_ENDPOINT", "http://fuseki:3030")
graph_data= os.getenv("FUSEKI_GRAPH_DATA", "http://ai-act.eu/ontology/data")

router = APIRouter(prefix="/systems", tags=["systems"])

# Load ontology globally for derivation
_ontology = None


def get_ontology():
    """Get cached ontology graph"""
    global _ontology
    if _ontology is None:
        ontology_path = os.environ.get("ONTOLOGY_PATH")
        if not ontology_path:
            raise RuntimeError("ONTOLOGY_PATH not configured")
        _ontology = Graph()
        _ontology.parse(ontology_path, format="turtle")
    return _ontology


@router.post("/derive-classifications", status_code=200)
async def derive_system_classifications(data: dict):
    """
    Endpoint to derive Criteria, Requirements, and Risk Level from user input

    Input:
    {
        "hasPurpose": ["ai:EducationAccess"],
        "hasDeploymentContext": ["ai:Education"],
        "hasTrainingDataOrigin": ["ai:ExternalDataset"],
        "hasAlgorithmType": ["ai:TransformerModel"],
        "hasModelScale": "ai:FoundationModelScale"
    }

    Output:
    {
        "hasCriteria": ["ai:EducationEvaluationCriterion"],
        "hasComplianceRequirement": ["ai:DataGovernanceRequirement", ...],
        "hasRiskLevel": "ai:HighRisk",
        "hasGPAIClassification": ["ai:GeneralPurposeAI"]
    }
    """
    try:
        # Get ontology
        ont = get_ontology()

        # Perform derivation
        derived = derive_classifications(data, ont)

        return {
            "success": True,
            "derived": derived
        }
    except Exception as e:
        print(f"Error in derivation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error deriving classifications: {str(e)}"
        )


@router.post("", status_code=201)
async def create_system(json_ld: IntelligentSystem, db=Depends(get_database)):
    print(f"Datos recibidos por Pydantic: {json_ld}")
    json_ld = json_ld.dict(by_alias=True)
    print(f"Después de dict(by_alias=True): {json_ld}")

    # DERIVE CLASSIFICATIONS FROM USER INPUT
    try:
        ont = get_ontology()
        # Prepare input for derivation (convert from ai: prefix format)
        derivation_input = {
            'hasPurpose': json_ld.get('hasPurpose', []),
            'hasDeploymentContext': json_ld.get('hasDeploymentContext', []),
            'hasTrainingDataOrigin': json_ld.get('hasTrainingDataOrigin', []),
            'hasAlgorithmType': json_ld.get('hasAlgorithmType', []),
            'hasModelScale': json_ld.get('hasModelScale', '')
        }

        derived = derive_classifications(derivation_input, ont)

        # Merge derived data with user input
        json_ld['hasCriteria'] = derived.get('hasCriteria', [])
        json_ld['hasComplianceRequirement'] = derived.get('hasComplianceRequirement', [])
        json_ld['hasRiskLevel'] = derived.get('hasRiskLevel', 'ai:MinimalRisk')
        json_ld['hasGPAIClassification'] = derived.get('hasGPAIClassification', [])

        print(f"Derived classifications: Criteria={json_ld.get('hasCriteria')}, Risk={json_ld.get('hasRiskLevel')}")
    except Exception as e:
        print(f"Warning: Could not derive classifications: {str(e)}")
        # Continue without derivation rather than failing
        json_ld['hasCriteria'] = []
        json_ld['hasComplianceRequirement'] = []
        json_ld['hasRiskLevel'] = 'ai:MinimalRisk'
        json_ld['hasGPAIClassification'] = []

    urn = f"urn:uuid:{uuid.uuid4()}"
    json_ld["ai:hasUrn"] = urn
    json_ld["@id"] = urn

    try:
        result = await db.systems.insert_one(json_ld)
    except DuplicateKeyError as e:
        print(f"[ERROR] DuplicateKeyError al crear sistema: {e}")
        # Intentar liberar recursos explícitamente (por si acaso)
        try:
            await db.client.close()
            print("[INFO] Conexión a MongoDB cerrada tras DuplicateKeyError")
        except Exception as close_err:
            print(f"[WARN] Error cerrando conexión MongoDB tras 409: {close_err}")
        raise HTTPException(status_code=409, detail="System with same URN already exists")

    json_ld.pop("_id", None)
    print(f"Insertando en MongoDB: {json.dumps(json_ld)}")

    g = Graph()
    mapped = {}
    print(f"Datos mapeados: {json.dumps(mapped)}")
    for k, v in json_ld.items():
        if not k.startswith("ai:") and k not in ["@id", "@type", "@context"]:
            mapped[f"ai:{k}"] = v
        else:
            mapped[k] = v

    # Asegurar que los valores múltiples se representen como listas
    for multivalue_key in [
        "ai:hasPurpose", "ai:hasDeploymentContext", "ai:hasTrainingDataOrigin",
        "ai:hasAlgorithmType", "ai:hasModelScale", "ai:hasCapability",
        "ai:hasSystemCapabilityCriteria"
    ]:
        if multivalue_key in mapped:
            if mapped[multivalue_key] is None:
                mapped[multivalue_key] = []
            elif not isinstance(mapped[multivalue_key], list):
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


@router.get("", response_model=dict)
async def list_systems(
    db=Depends(get_database),
    name: str = Query(None),
    risk: str = Query(None),
    purpose: str = Query(None),
    context: str = Query(None),
    training_origin: str = Query(None),
    algorithm_type: str = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort: str = Query("asc", regex="^(asc|desc)$"),
):
    query = {}
    if name:
        query["hasName"] = {"$regex": name, "$options": "i"}
    if risk:
        query["hasRiskLevel"] = risk
    if purpose:
        query["hasPurpose"] = purpose
    if context:
        query["hasDeploymentContext"] = context
    if training_origin:
        query["hasTrainingDataOrigin"] = training_origin
    if algorithm_type:
        query["hasAlgorithmType"] = algorithm_type

    sort_order = 1 if sort == "asc" else -1

    total = await db.systems.count_documents(query)
    cursor = (
        db.systems.find(query)
        .sort("hasName", sort_order)
        .skip(offset)
        .limit(limit)
    )

    systems = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        systems.append(doc)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": systems,
    }

@router.get("/{urn}")
async def get_system_by_urn(urn: str, db=Depends(get_database)):
    doc = await db.systems.find_one({"ai:hasUrn": urn})
    if doc:
        doc["_id"] = str(doc["_id"])
        return doc
    raise HTTPException(status_code=404, detail="System not found")

@router.put("/{urn}")
async def update_system(urn: str, json_ld: IntelligentSystem = Body(...), db=Depends(get_database)):
        # Buscar sistema existente
        existing = await db.systems.find_one({"ai:hasUrn": urn})
        if not existing:
                raise HTTPException(status_code=404, detail="System not found")

        # Actualizar en MongoDB
        json_ld = json_ld.dict(by_alias=True)
        json_ld["ai:hasUrn"] = urn
        json_ld["@id"] = urn
        json_ld.pop("_id", None)
        await db.systems.replace_one({"ai:hasUrn": urn}, json_ld)

        # Actualizar en Fuseki: borrar el sistema anterior y subir el nuevo
        # 1. Borrar triples anteriores
        sparql = f"""
        DELETE WHERE {{
            GRAPH <http://ai-act.eu/ontology/data> {{
                <{urn}> ?p ?o .
            }}
        }};
        DELETE WHERE {{
            GRAPH <http://ai-act.eu/ontology/data> {{
                ?s ?p <{urn}> .
            }}
        }}
        """
        headers = {"Content-Type": "application/sparql-update"}
        res = requests.post(f"{end_point}/{dataset}/update", data=sparql, headers=headers, auth=(user, password))
        if not res.ok:
                raise HTTPException(status_code=500, detail="Error deleting from Fuseki for update")

        # 2. Subir el sistema actualizado
        from rdflib import Graph
        g = Graph()
        mapped = {}
        for k, v in json_ld.items():
                if not k.startswith("ai:") and k not in ["@id", "@type", "@context"]:
                        mapped[f"ai:{k}"] = v
                else:
                        mapped[k] = v
        for multivalue_key in [
            "ai:hasPurpose", "ai:hasDeploymentContext", "ai:hasTrainingDataOrigin",
            "ai:hasAlgorithmType", "ai:hasModelScale", "ai:hasCapability",
            "ai:hasSystemCapabilityCriteria"
        ]:
            if multivalue_key in mapped:
                if mapped[multivalue_key] is None:
                    mapped[multivalue_key] = []
                elif not isinstance(mapped[multivalue_key], list):
                    mapped[multivalue_key] = [mapped[multivalue_key]]
        g.parse(data=json.dumps(mapped), format="json-ld")
        fuseki_url = f"{end_point}/{dataset}/data?graph={graph_data}"
        nt_data = g.serialize(format="nt")
        headers = {"Content-Type": "application/n-triples"}
        res = requests.post(fuseki_url, data=nt_data, headers=headers, auth=(user, password))
        if not res.ok:
                raise HTTPException(status_code=500, detail="Error uploading updated system to Fuseki")

        return {"status": "updated", "urn": urn}

@router.delete("/{urn}")
async def delete_system(urn: str, db=Depends(get_database)):
    # Eliminar de MongoDB
    result = await db.systems.delete_one({"ai:hasUrn": urn})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="System not found in MongoDB")

    # Eliminar de Fuseki
    sparql = f"""
    DELETE WHERE {{
      GRAPH <http://ai-act.eu/ontology/data> {{
        <{urn}> ?p ?o .
      }}
    }};
    DELETE WHERE {{
      GRAPH <http://ai-act.eu/ontology/data> {{
        ?s ?p <{urn}> .
      }}
    }}
    """
    headers = {"Content-Type": "application/sparql-update"}
    res = requests.post(f"{end_point}/{dataset}/update", data=sparql, headers=headers,auth=(user, password))
    if not res.ok:
        raise HTTPException(status_code=500, detail="Error deleting from Fuseki")

    return {"status": "deleted", "urn": urn}


@router.put("/{urn}/manually-identified-criteria", status_code=200)
async def set_manually_identified_criteria(
    urn: str,
    data: dict = Body(...),
    db=Depends(get_database)
):
    """
    Set manually identified criteria for a system and derive their associated requirements.

    This endpoint allows experts to manually identify risk criteria beyond what is
    automatically derived from Purpose/DeploymentContext (Article 6(3) residual cases).

    When criteria are set, this endpoint automatically derives all compliance requirements
    that are activated by those criteria via the ontology relationship activatesRequirement.

    Request body:
    {
        "hasManuallyIdentifiedCriterion": ["ai:CriticalInfrastructureCriterion", ...]
    }

    Returns:
        Updated system with manually identified criteria and derived requirements
    """
    try:
        # Find existing system
        existing = await db.systems.find_one({"ai:hasUrn": urn})
        if not existing:
            raise HTTPException(status_code=404, detail="System not found")

        # Extract criteria from request
        manually_identified = data.get("hasManuallyIdentifiedCriterion", [])
        if not isinstance(manually_identified, list):
            manually_identified = [manually_identified] if manually_identified else []

        # STEP 1: Derive requirements from manually identified criteria
        ont = get_ontology()
        derived_requirements = derive_requirements_from_criteria(manually_identified, ont)
        print(f"Manually identified criteria: {manually_identified}")
        print(f"Derived requirements: {derived_requirements}")

        # STEP 2: Get existing automatically derived criteria and requirements
        existing_activated = existing.get("hasActivatedCriterion", [])
        existing_requirements = existing.get("hasComplianceRequirement", [])
        print(f"Existing activated criteria: {existing_activated}")
        print(f"Existing requirements: {existing_requirements}")

        # STEP 3: Merge requirements (automatic + from manual criteria)
        # Keep existing automatic requirements and add new ones from manual criteria
        merged_requirements = list(set(existing_requirements + derived_requirements))
        merged_requirements.sort()

        # Update in MongoDB
        await db.systems.update_one(
            {"ai:hasUrn": urn},
            {
                "$set": {
                    "hasManuallyIdentifiedCriterion": manually_identified,
                    "hasComplianceRequirement": merged_requirements
                }
            }
        )

        # Update in Fuseki: remove old hasManuallyIdentifiedCriterion triples and add new ones
        sparql = f"""
        DELETE {{
          GRAPH <http://ai-act.eu/ontology/data> {{
            <{urn}> <http://ai-act.eu/ai#hasManuallyIdentifiedCriterion> ?o .
            <{urn}> <http://ai-act.eu/ai#hasComplianceRequirement> ?r .
          }}
        }} WHERE {{
          GRAPH <http://ai-act.eu/ontology/data> {{
            OPTIONAL {{ <{urn}> <http://ai-act.eu/ai#hasManuallyIdentifiedCriterion> ?o . }}
            OPTIONAL {{ <{urn}> <http://ai-act.eu/ai#hasComplianceRequirement> ?r . }}
          }}
        }};
        """

        # Add new criteria
        for criterion in manually_identified:
            criterion_uri = criterion if criterion.startswith("http") else f"http://ai-act.eu/ai#{criterion.split(':')[-1]}"
            sparql += f"""
        INSERT DATA {{
          GRAPH <http://ai-act.eu/ontology/data> {{
            <{urn}> <http://ai-act.eu/ai#hasManuallyIdentifiedCriterion> <{criterion_uri}> .
          }}
        }};
        """

        # Add merged requirements (both automatic and from manual criteria)
        for requirement in merged_requirements:
            requirement_uri = requirement if requirement.startswith("http") else f"http://ai-act.eu/ai#{requirement.split(':')[-1]}"
            sparql += f"""
        INSERT DATA {{
          GRAPH <http://ai-act.eu/ontology/data> {{
            <{urn}> <http://ai-act.eu/ai#hasComplianceRequirement> <{requirement_uri}> .
          }}
        }};
        """

        headers = {"Content-Type": "application/sparql-update"}
        res = requests.post(
            f"{end_point}/{dataset}/update",
            data=sparql,
            headers=headers,
            auth=(user, password)
        )
        if not res.ok:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating manually identified criteria in Fuseki: {res.text}"
            )

        return {
            "status": "updated",
            "urn": urn,
            "hasManuallyIdentifiedCriterion": manually_identified,
            "hasComplianceRequirement": merged_requirements,
            "message": f"Set {len(manually_identified)} manual criteria and derived {len(derived_requirements)} new requirements"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error setting manually identified criteria: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error setting manually identified criteria: {str(e)}"
        )



