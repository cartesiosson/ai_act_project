"""
Router para servicios de razonamiento semántico
"""


import logging
import os
import json
from rdflib import Namespace, Graph, RDF
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List, Tuple
import httpx
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorDatabase
from db import get_database
from swrl_rules import get_swrl_rules, get_basic_prefixes, get_ai_act_concepts
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime

# SHACL Validation
try:
    from pyshacl import validate as shacl_validate
    SHACL_AVAILABLE = True
except ImportError:
    SHACL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pyshacl not installed - SHACL validation will be disabled")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reasoning", tags=["reasoning"])

# Configuración del servicio reasoner
REASONER_SERVICE_URL = os.environ.get("REASONER_SERVICE_URL", "http://reasoner:8001")
ONTOLOGY_PATH = os.environ.get("ONTOLOGY_PATH", "/ontologias/versions/0.37.2/ontologia-v0.37.2.ttl")
SHACL_SHAPES_PATH = os.environ.get("SHACL_SHAPES_PATH", "/ontologias/shacl/ai-act-shapes.ttl")
ENABLE_SHACL_VALIDATION = os.environ.get("ENABLE_SHACL_VALIDATION", "true").lower() == "true"

# Namespaces
AI = Namespace("http://ai-act.eu/ai#")

# Fuseki configuration
FUSEKI_ENDPOINT = os.environ.get("FUSEKI_ENDPOINT", "http://fuseki:3030")
FUSEKI_DATASET = os.environ.get("FUSEKI_DATASET", "ds")
FUSEKI_USER = os.environ.get("FUSEKI_USER", "admin")
FUSEKI_PASSWORD = os.environ.get("FUSEKI_PASSWORD", "admin")
FUSEKI_GRAPH_DATA = os.environ.get("FUSEKI_GRAPH_DATA", "http://ai-act.eu/ontology/data")

# Evidence Plan Service URL (forensic_agent)
FORENSIC_AGENT_URL = os.environ.get("FORENSIC_AGENT_URL", "http://forensic_agent:8000")


# ===== FUSEKI PERSISTENCE FUNCTIONS =====

async def persist_inferences_to_fuseki(system_urn: str, relationships: Dict[str, List[str]]) -> bool:
    """
    Persiste las inferencias del razonamiento simbólico en Fuseki.
    Usa las propiedades estándar de la ontología (no propiedades inventadas).

    Args:
        system_urn: URN del sistema (ej: urn:uuid:...)
        relationships: Dict con las relaciones inferidas

    Returns:
        True si se persistió correctamente, False en caso contrario
    """
    import requests

    if not relationships:
        logger.info("No hay inferencias para persistir en Fuseki")
        return True

    try:
        # Mapeo de nombres de relación a propiedades RDF estándar de la ontología
        # Estas propiedades YA EXISTEN en la ontología ai-act
        property_map = {
            "hasNormativeCriterion": "ai:hasNormativeCriterion",
            "hasTechnicalCriterion": "ai:hasTechnicalCriterion",
            "hasContextualCriterion": "ai:hasContextualCriterion",
            "hasRequirement": "ai:hasRequirement",
            "hasTechnicalRequirement": "ai:hasTechnicalRequirement",
            "hasCriteria": "ai:hasActivatedCriterion",  # Mapea a hasActivatedCriterion
            "hasComplianceRequirement": "ai:hasComplianceRequirement",
            "hasRiskLevel": "ai:hasRiskLevel",
            "hasGPAIClassification": "ai:hasGPAIClassification"
        }

        # Primero eliminamos las propiedades existentes que vamos a actualizar
        # para evitar duplicados
        delete_patterns = []
        for rel_type in relationships.keys():
            if relationships[rel_type]:  # Solo si hay valores
                prop = property_map.get(rel_type)
                if prop:
                    delete_patterns.append(f"OPTIONAL {{ <{system_urn}> {prop} ?{rel_type} . }}")

        if not delete_patterns:
            logger.info("No hay propiedades para actualizar")
            return True

        # Construir DELETE WHERE
        delete_sparql = f"""
        PREFIX ai: <http://ai-act.eu/ai#>

        DELETE {{
            GRAPH <{FUSEKI_GRAPH_DATA}> {{
                {chr(10).join([f"<{system_urn}> {property_map[rt]} ?{rt} ." for rt in relationships.keys() if relationships[rt] and property_map.get(rt)])}
            }}
        }} WHERE {{
            GRAPH <{FUSEKI_GRAPH_DATA}> {{
                {chr(10).join(delete_patterns)}
            }}
        }}
        """

        # Ejecutar DELETE
        headers = {"Content-Type": "application/sparql-update"}
        res = requests.post(
            f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update",
            data=delete_sparql,
            headers=headers,
            auth=(FUSEKI_USER, FUSEKI_PASSWORD)
        )

        if not res.ok:
            logger.warning(f"Error eliminando propiedades anteriores de Fuseki: {res.status_code} - {res.text}")

        # Construir INSERT para las nuevas inferencias
        insert_triples = []

        for rel_type, values in relationships.items():
            if not values:
                continue

            prop = property_map.get(rel_type)
            if not prop:
                logger.warning(f"Propiedad no mapeada: {rel_type}")
                continue

            for value in values:
                # Normalizar el valor a URI completa
                if value.startswith("http://") or value.startswith("https://"):
                    value_uri = f"<{value}>"
                elif value.startswith("ai:"):
                    value_uri = f"<http://ai-act.eu/ai#{value[3:]}>"
                else:
                    value_uri = f"<http://ai-act.eu/ai#{value}>"

                insert_triples.append(f"<{system_urn}> {prop} {value_uri} .")

        if not insert_triples:
            logger.info("No hay triples de inferencia para insertar")
            return True

        # Construir INSERT DATA
        insert_sparql = f"""
        PREFIX ai: <http://ai-act.eu/ai#>

        INSERT DATA {{
            GRAPH <{FUSEKI_GRAPH_DATA}> {{
                {chr(10).join(insert_triples)}
            }}
        }}
        """

        logger.debug(f"SPARQL INSERT: {insert_sparql}")

        # Ejecutar INSERT
        res = requests.post(
            f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update",
            data=insert_sparql,
            headers=headers,
            auth=(FUSEKI_USER, FUSEKI_PASSWORD)
        )

        if not res.ok:
            logger.error(f"Error insertando inferencias en Fuseki: {res.status_code} - {res.text}")
            return False

        logger.info(f"Persistidas {len(insert_triples)} inferencias en Fuseki para {system_urn}")
        return True

    except Exception as e:
        logger.error(f"Error persistiendo inferencias en Fuseki: {str(e)}")
        return False


# ===== SHACL VALIDATION FUNCTIONS =====

def load_shacl_shapes() -> Optional[Graph]:
    """Carga las SHACL shapes desde archivo"""
    if not SHACL_AVAILABLE or not ENABLE_SHACL_VALIDATION:
        return None

    try:
        shapes_path = Path(SHACL_SHAPES_PATH)
        if not shapes_path.exists():
            logger.warning(f"SHACL shapes file not found at {SHACL_SHAPES_PATH}")
            return None

        shapes_graph = Graph()
        shapes_graph.parse(str(shapes_path), format="turtle")
        logger.info(f"SHACL shapes loaded from {SHACL_SHAPES_PATH}")
        return shapes_graph
    except Exception as e:
        logger.error(f"Error loading SHACL shapes: {str(e)}")
        return None


def validate_system_pre(system_ttl: str, shapes_graph: Optional[Graph]) -> Tuple[bool, Optional[str]]:
    """
    Valida datos PRE-razonamiento usando SHACL
    Retorna: (is_valid, error_message)
    """
    if not SHACL_AVAILABLE or not ENABLE_SHACL_VALIDATION or shapes_graph is None:
        return True, None

    try:
        # Cargar datos a validar
        data_graph = Graph()
        data_graph.parse(data=system_ttl, format="turtle")

        # Ejecutar validación SHACL
        conforms, report_graph, report_text = shacl_validate(
            data_graph,
            shapes_graph=shapes_graph,
            inplace=False
        )

        if not conforms:
            error_msg = f"Sistema incumple restricciones pre-razonamiento:\n{report_text}"
            logger.warning(f"Pre-validation failed: {error_msg[:200]}...")
            return False, error_msg

        logger.info("Pre-validation passed")
        return True, None

    except Exception as e:
        error_msg = f"Error en validación SHACL pre-razonamiento: {str(e)}"
        logger.error(error_msg)
        # No falla si hay error de validación, solo registra
        return True, None


def validate_results_post(results_ttl: str, shapes_graph: Optional[Graph]) -> Dict[str, Any]:
    """
    Valida resultados POST-razonamiento usando SHACL
    Retorna: {"valid": bool, "message": str, "report": str}
    """
    if not SHACL_AVAILABLE or not ENABLE_SHACL_VALIDATION or shapes_graph is None:
        return {"valid": True, "message": "SHACL validation disabled", "report": ""}

    try:
        # Cargar resultados
        results_graph = Graph()
        results_graph.parse(data=results_ttl, format="turtle")

        # Ejecutar validación SHACL
        conforms, report_graph, report_text = shacl_validate(
            results_graph,
            shapes_graph=shapes_graph,
            inplace=False
        )

        return {
            "valid": conforms,
            "message": "Válido" if conforms else "Incumple restricciones",
            "report": report_text if not conforms else ""
        }

    except Exception as e:
        logger.error(f"Error in post-validation: {str(e)}")
        return {
            "valid": True,
            "message": "Error in validation",
            "report": str(e)
        }


def system_to_ttl(system: Dict[str, Any]) -> str:
    """Convierte un sistema a formato TTL"""
    prefixes = get_basic_prefixes()
    
    # Generar URN si no existe
    system_urn = system.get("ai:hasUrn") or system.get("@id") or f"urn:uuid:{system.get('_id', 'unknown')}"
    subject = f"<{system_urn}>"
    
    # Construir propiedades
    properties = []
    properties.append(f"{subject} a ai:IntelligentSystem")
    
    # Propiedades básicas
    if system.get("hasName"):
        properties.append(f'{subject} ai:hasName "{system["hasName"]}"')
    
    if system.get("hasVersion"):
        properties.append(f'{subject} ai:hasVersion "{system["hasVersion"]}"')
        
    if system.get("ai:hasUrn"):
        properties.append(f'{subject} ai:hasUrn "{system["ai:hasUrn"]}"')
    
    # Propósitos
    for purpose in system.get("hasPurpose", []):
        purpose_uri = purpose if purpose.startswith("ai:") else f"ai:{purpose}"
        properties.append(f"{subject} ai:hasPurpose {purpose_uri}")
    
    # Contextos de despliegue
    for context in system.get("hasDeploymentContext", []):
        context_uri = context if context.startswith("ai:") else f"ai:{context}"
        properties.append(f"{subject} ai:hasDeploymentContext {context_uri}")
    
    # Orígenes de datos de entrenamiento
    for origin in system.get("hasTrainingDataOrigin", []):
        origin_uri = origin if origin.startswith("ai:") else f"ai:{origin}"
        properties.append(f"{subject} ai:hasTrainingDataOrigin {origin_uri}")
    
    # Criterios de capacidad del sistema
    for criterion in system.get("hasSystemCapabilityCriteria", []):
        criterion_uri = criterion if criterion.startswith("ai:") else f"ai:{criterion}"
        properties.append(f"{subject} ai:hasSystemCapabilityCriteria {criterion_uri}")
    
    # Compatibilidad hacia atrás para hasInnerSystemCriteria
    for criterion in system.get("hasInnerSystemCriteria", []):
        criterion_uri = criterion if criterion.startswith("ai:") else f"ai:{criterion}"
        properties.append(f"{subject} ai:hasSystemCapabilityCriteria {criterion_uri}")

    # Tipos de algoritmo (nueva propiedad)
    for algo_type in system.get("hasAlgorithmType", []):
        algo_uri = algo_type if algo_type.startswith("ai:") else f"ai:{algo_type}"
        properties.append(f"{subject} ai:hasAlgorithmType {algo_uri}")

    # Escala del modelo (nueva propiedad)
    for model_scale in system.get("hasModelScale", []):
        scale_uri = model_scale if model_scale.startswith("ai:") else f"ai:{model_scale}"
        properties.append(f"{subject} ai:hasModelScale {scale_uri}")

    # Capacidades del sistema (nueva propiedad)
    for capability in system.get("hasCapability", []):
        cap_uri = capability if capability.startswith("ai:") else f"ai:{capability}"
        properties.append(f"{subject} ai:hasCapability {cap_uri}")

    # Nivel de riesgo
    if system.get("hasRiskLevel"):
        risk_uri = system["hasRiskLevel"]
        # Handle array or string
        if isinstance(risk_uri, list):
            risk_uri = risk_uri[0] if risk_uri else None
        if risk_uri:
            risk_uri = str(risk_uri)
            if not risk_uri.startswith("ai:"):
                risk_uri = f"ai:{risk_uri}"
            properties.append(f"{subject} ai:hasRiskLevel {risk_uri}")

    # Combinar prefijos y propiedades
    ttl_content = prefixes + "\n" + " .\n".join(properties) + " .\n"
    
    return ttl_content

async def call_reasoner_service(system_ttl: str, swrl_rules: str) -> Dict[str, Any]:
    """Llama al servicio de razonamiento con los datos del sistema y reglas SWRL"""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Preparar archivos para el reasoner
            files = {
                "data": ("system.ttl", system_ttl.encode(), "text/turtle"),
                "swrl_rules": ("rules.ttl", swrl_rules.encode(), "text/turtle")
            }
            
            response = await client.post(
                f"{REASONER_SERVICE_URL}/reason",
                files=files,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Reasoner service error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error del servicio de razonamiento: {response.status_code}"
                )
            
            # Parsear respuesta JSON
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Response text: {response.text[:500]}...")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Error parseando respuesta del servicio de razonamiento"
                )
            
    except httpx.ConnectError:
        logger.error("Cannot connect to reasoner service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de razonamiento no disponible"
        )
    except Exception as e:
        logger.error(f"Error calling reasoner service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servicio de razonamiento: {str(e)}"
        )

def parse_inferred_relationships(ttl_result: str) -> Dict[str, List[str]]:
    """Extrae las relaciones inferidas del resultado TTL"""
    
    try:
        g = Graph()
        g.parse(data=ttl_result, format="turtle")
        
        relationships = {
            "hasNormativeCriterion": [],
            "hasTechnicalCriterion": [], 
            "hasContextualCriterion": [],
            "hasRequirement": [],
            "hasTechnicalRequirement": []
        }
        
        # Buscar sistemas en el grafo
        for system in g.subjects(RDF.type, AI.IntelligentSystem):
            
            # Criterios normativos
            for criterion in g.objects(system, AI.hasNormativeCriterion):
                relationships["hasNormativeCriterion"].append(str(criterion))
            
            # Criterios técnicos
            for criterion in g.objects(system, AI.hasTechnicalCriterion):
                relationships["hasTechnicalCriterion"].append(str(criterion))
                
            # Criterios contextuales  
            for criterion in g.objects(system, AI.hasContextualCriterion):
                relationships["hasContextualCriterion"].append(str(criterion))
            
            # Requisitos generales
            for requirement in g.objects(system, AI.hasRequirement):
                relationships["hasRequirement"].append(str(requirement))
            
            # Requisitos técnicos
            for requirement in g.objects(system, AI.hasTechnicalRequirement):
                relationships["hasTechnicalRequirement"].append(str(requirement))
        
        return relationships
        
    except Exception as e:
        logger.error(f"Error parsing inferred relationships: {str(e)}")
        return {}

def parse_inferred_relationships_json(json_graph: Any) -> Dict[str, List[str]]:
    """Extrae las relaciones inferidas del resultado JSON-LD"""
    
    relationships = {
        "hasNormativeCriterion": [],
        "hasTechnicalCriterion": [], 
        "hasContextualCriterion": [],
        "hasRequirement": [],
        "hasTechnicalRequirement": []
    }
    
    try:
        # JSON-LD puede ser una lista de objetos o un objeto
        items = json_graph if isinstance(json_graph, list) else [json_graph]
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            # Buscar sistemas de IA
            if item.get("@type") == "ai:IntelligentSystem" or "IntelligentSystem" in str(item.get("@type", "")):
                
                # Buscar las relaciones que nos interesan
                for prop_name, target_list in relationships.items():
                    # Buscar tanto la forma completa como abreviada
                    ai_prop = f"ai:{prop_name}"
                    
                    prop_value = item.get(ai_prop) or item.get(prop_name)
                    if prop_value:
                        # Manejar tanto objetos únicos como listas
                        if isinstance(prop_value, list):
                            for val in prop_value:
                                if isinstance(val, dict) and "@id" in val:
                                    target_list.append(val["@id"])
                                elif isinstance(val, str):
                                    target_list.append(val)
                        elif isinstance(prop_value, dict) and "@id" in prop_value:
                            target_list.append(prop_value["@id"])
                        elif isinstance(prop_value, str):
                            target_list.append(prop_value)
        
        return relationships
        
    except Exception as e:
        logger.error(f"Error parsing JSON-LD inferred relationships: {str(e)}")
        return relationships

@router.post("/system/{system_id}")
async def reason_system(
    system_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Ejecuta razonamiento semántico sobre un sistema específico
    CON validación SHACL (pre y post)
    """

    try:
        # 0. Cargar SHACL shapes (una sola vez)
        shapes_graph = load_shacl_shapes()

        # Decodificar system_id si está URL-encoded
        system_id = unquote(system_id)

        # 1. Obtener sistema de la base de datos
        from bson import ObjectId

        # Determinar cómo buscar el sistema
        if system_id.startswith("urn:uuid:"):
            # Es un URN, buscar por ai:hasUrn
            query = {"ai:hasUrn": system_id}
        else:
            # Podría ser un ObjectId o algún otro identificador
            try:
                if len(system_id) == 24:  # Longitud típica de ObjectId
                    query = {"_id": ObjectId(system_id)}
                else:
                    # Intentar buscar por URN primero, luego por _id
                    query = {"$or": [{"ai:hasUrn": system_id}, {"_id": system_id}]}
            except:
                # Si no es ObjectId válido, buscar por URN o _id
                query = {"$or": [{"ai:hasUrn": system_id}, {"_id": system_id}]}

        system = await db.systems.find_one(query)
        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sistema no encontrado"
            )

        # 2. Convertir sistema a TTL
        system_ttl = system_to_ttl(system)
        logger.info(f"Sistema convertido a TTL completo:\n{system_ttl}")
        logger.info(f"TTL preview: {system_ttl[:200]}...")

        # 2.5. PRE-VALIDACIÓN SHACL (NUEVO)
        logger.info("Iniciando pre-validación SHACL...")
        is_valid, validation_error = validate_system_pre(system_ttl, shapes_graph)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sistema incumple restricciones: {validation_error}"
            )
        logger.info("Pre-validación SHACL completada ✓")

        # 3. Obtener reglas SWRL y conceptos
        swrl_rules = get_basic_prefixes() + get_ai_act_concepts() + get_swrl_rules()
        logger.info(f"Reglas SWRL y conceptos cargados: {len(swrl_rules.split('Rule'))} reglas")

        # 4. Ejecutar razonamiento
        reasoner_response = await call_reasoner_service(system_ttl, swrl_rules)
        logger.info(f"Razonamiento completado, inferencias: {reasoner_response.get('rules_applied', 0)}")

        # 4.5. POST-VALIDACIÓN SHACL (NUEVO)
        logger.info("Iniciando post-validación SHACL...")
        raw_ttl = reasoner_response.get("raw_ttl", "")
        shacl_post_validation = validate_results_post(raw_ttl, shapes_graph)
        logger.info(f"Post-validación completada: {shacl_post_validation['message']}")

        # 5. Usar directamente las relaciones inferidas que vienen en la respuesta del reasoner
        # El reasoner service ya las procesa y las devuelve en formato correcto
        # Incluir todas las relaciones posibles (antiguas + nuevas SWRL)
        relationships = reasoner_response.get("inferred_relationships", {
            "hasNormativeCriterion": [],
            "hasTechnicalCriterion": [],
            "hasContextualCriterion": [],
            "hasRequirement": [],
            "hasTechnicalRequirement": [],
            "hasCriteria": [],
            "hasComplianceRequirement": [],
            "hasRiskLevel": [],
            "hasGPAIClassification": []
        })
        logger.info(f"Relaciones inferidas: {relationships}")

        # 6. Actualizar sistema con inferencias en MongoDB y Fuseki
        # Usar nombres de propiedades estándar (sin prefijo "inferred_")
        update_data = {}

        # Mapeo a nombres de campos en MongoDB (consistente con la ontología)
        mongo_field_map = {
            "hasNormativeCriterion": "hasNormativeCriterion",
            "hasTechnicalCriterion": "hasTechnicalCriterion",
            "hasContextualCriterion": "hasContextualCriterion",
            "hasRequirement": "hasRequirement",
            "hasTechnicalRequirement": "hasTechnicalRequirement",
            "hasCriteria": "hasActivatedCriterion",  # Mapea a hasActivatedCriterion
            "hasComplianceRequirement": "hasComplianceRequirement",
            "hasRiskLevel": "hasRiskLevel",
            "hasGPAIClassification": "hasGPAIClassification"
        }

        for rel_type, values in relationships.items():
            if values:  # Solo actualizar si hay valores inferidos
                field_name = mongo_field_map.get(rel_type, rel_type)
                update_data[field_name] = values

        if update_data:
            # FIX: Use correct query - system_id can be URN or ObjectId
            if system_id.startswith("urn:uuid:"):
                query = {"ai:hasUrn": system_id}
            else:
                query = {"_id": system_id}

            await db.systems.update_one(
                query,
                {"$set": update_data}
            )
            logger.info(f"Sistema actualizado en MongoDB con inferencias: {update_data.keys()}")

            # También persistir en Fuseki
            # FIX: Always use the URN from the system document, not the system_id parameter
            # which could be an ObjectId instead of a URN
            system_urn = system.get("ai:hasUrn") or system.get("@id") or system_id
            if not system_urn.startswith("urn:"):
                logger.warning(f"System URN not found, using system_id: {system_id}")
                system_urn = f"urn:uuid:{system_id}"  # Fallback to create valid URN
            await persist_inferences_to_fuseki(system_urn, relationships)
            logger.info(f"Inferencias persistidas en Fuseki para sistema: {system_urn}")

        # 7. Obtener número de reglas aplicadas del reasoner service
        # El reasoner devuelve este campo con el conteo exacto de inferencias
        rules_applied = reasoner_response.get("rules_applied", sum(len(values) for values in relationships.values()))
        logger.info(f"DEBUG rules_applied from reasoner: {rules_applied}")
        logger.info(f"DEBUG relationships: {relationships}")

        # 8. GENERAR PLAN DE EVIDENCIAS DPV automáticamente si hay compliance requirements
        evidence_plan_result = None
        compliance_requirements = relationships.get("hasComplianceRequirement", [])

        if compliance_requirements:
            logger.info(f"Generando plan de evidencias DPV para {len(compliance_requirements)} compliance requirements...")
            try:
                # Obtener risk level del sistema
                risk_level = "HighRisk"  # Default
                risk_levels = relationships.get("hasRiskLevel", [])
                if risk_levels:
                    risk_level = risk_levels[0].replace("ai:", "").replace("http://ai-act.eu/ai#", "")

                # Preparar request para el evidence planner
                evidence_request = {
                    "missing_requirements": compliance_requirements,
                    "risk_level": risk_level,
                    "system_name": system.get("hasName", "Unknown System"),
                    "critical_gaps": [],
                    "jurisdiction": "EU"
                }

                # Llamar al forensic agent para generar el plan
                response = requests.post(
                    f"{FORENSIC_AGENT_URL}/forensic/evidence-plan",
                    json=evidence_request,
                    timeout=30
                )
                response.raise_for_status()
                evidence_plan = response.json()

                # Guardar el plan en MongoDB
                urn = system.get("ai:hasUrn", system_id)
                await db.systems.update_one(
                    {"ai:hasUrn": urn} if urn.startswith("urn:") else {"_id": system_id},
                    {
                        "$set": {
                            "evidencePlan": evidence_plan,
                            "evidencePlanGeneratedAt": datetime.utcnow().isoformat()
                        }
                    }
                )

                evidence_plan_result = {
                    "status": "generated",
                    "total_requirements": len(evidence_plan.get("requirement_plans", [])),
                    "total_evidence_items": evidence_plan.get("summary", {}).get("total_evidence_items", 0)
                }
                logger.info(f"Plan de evidencias generado: {evidence_plan_result['total_requirements']} requirements, {evidence_plan_result['total_evidence_items']} items")

            except requests.exceptions.RequestException as e:
                logger.warning(f"No se pudo generar el plan de evidencias: {str(e)}")
                evidence_plan_result = {"status": "error", "message": str(e)}
            except Exception as e:
                logger.warning(f"Error generando plan de evidencias: {str(e)}")
                evidence_plan_result = {"status": "error", "message": str(e)}
        else:
            logger.info("No hay compliance requirements, omitiendo generación de plan de evidencias")

        # 9. Retornar resultado completo CON validación SHACL
        return {
            "system_id": system_id,
            "system_name": system.get("hasName", "Unnamed"),
            "reasoning_completed": True,
            "inferred_relationships": relationships,
            "raw_ttl": raw_ttl,
            "rules_applied": rules_applied,
            # Información de validación SHACL
            "shacl_validation": {
                "pre_validation": {
                    "status": "passed",
                    "enabled": ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE
                },
                "post_validation": {
                    "status": "passed" if shacl_post_validation["valid"] else "failed",
                    "valid": shacl_post_validation["valid"],
                    "message": shacl_post_validation["message"],
                    "enabled": ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE
                }
            },
            # Plan de evidencias DPV
            "evidence_plan": evidence_plan_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reasoning process: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el proceso de razonamiento: {str(e)}"
        )

def forensic_system_to_ttl(system: Dict[str, Any]) -> str:
    """Convierte un sistema forense a formato TTL para razonamiento"""
    prefixes = get_basic_prefixes()

    # Usar el URN del sistema forense
    system_urn = system.get("urn") or system.get("@id") or f"urn:forensic:{system.get('_id', 'unknown')}"
    subject = f"<{system_urn}>"

    # Construir propiedades
    properties = []
    properties.append(f"{subject} a ai:IntelligentSystem")

    # Propiedades básicas
    if system.get("hasName"):
        properties.append(f'{subject} ai:hasName "{system["hasName"]}"')

    if system.get("hasOrganization"):
        properties.append(f'{subject} ai:hasOrganization "{system["hasOrganization"]}"')

    # Propósitos (formato diferente en forensic systems)
    for purpose in system.get("hasPurpose", []):
        purpose_uri = purpose if purpose.startswith("ai:") else f"ai:{purpose}"
        properties.append(f"{subject} ai:hasPurpose {purpose_uri}")

    # Contextos de despliegue
    for context in system.get("hasDeploymentContext", []):
        context_uri = context if context.startswith("ai:") else f"ai:{context}"
        properties.append(f"{subject} ai:hasDeploymentContext {context_uri}")

    # Tipos de datos procesados -> convertir a algo razonable
    for data_type in system.get("processesDataTypes", []):
        if "Biometric" in data_type:
            properties.append(f"{subject} ai:hasTrainingDataOrigin ai:BiometricData")
        elif "Personal" in data_type:
            properties.append(f"{subject} ai:hasTrainingDataOrigin ai:PersonalData")

    # Criterios ya identificados
    for criterion in system.get("hasCriteria", []):
        # Extraer el nombre del criterio de la URI
        crit_name = criterion.split("#")[-1] if "#" in criterion else criterion.split("/")[-1]
        crit_uri = f"ai:{crit_name}" if not criterion.startswith("ai:") else criterion
        properties.append(f"{subject} ai:hasSystemCapabilityCriteria {crit_uri}")

    # Nivel de riesgo si existe
    if system.get("hasRiskLevel"):
        risk_level = system["hasRiskLevel"]
        # Handle array or string
        if isinstance(risk_level, list):
            risk_level = risk_level[0] if risk_level else None
        if risk_level:
            risk_level = str(risk_level)
            if not risk_level.startswith("ai:"):
                risk_level = f"ai:{risk_level.split(':')[-1] if ':' in risk_level else risk_level}"
            properties.append(f"{subject} ai:hasRiskLevel {risk_level}")

    # Si es decisión automatizada
    if system.get("isAutomatedDecision"):
        properties.append(f"{subject} ai:hasCapability ai:AutomatedDecisionMaking")

    # Escala del modelo
    if system.get("modelScale"):
        scale = system["modelScale"]
        if scale.lower() == "large":
            properties.append(f"{subject} ai:hasModelScale ai:LargeScale")
        elif scale.lower() == "medium":
            properties.append(f"{subject} ai:hasModelScale ai:MediumScale")

    # Combinar prefijos y propiedades
    ttl_content = prefixes + "\n" + " .\n".join(properties) + " .\n"

    return ttl_content


@router.post("/forensic/{urn:path}")
async def reason_forensic_system(
    urn: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Ejecuta razonamiento semántico sobre un sistema forense
    Los sistemas forenses están en la colección 'forensic_systems'
    """
    try:
        # 0. Cargar SHACL shapes
        shapes_graph = load_shacl_shapes()

        # Decodificar URN si está URL-encoded
        urn = unquote(urn)

        # 1. Obtener sistema forense de la base de datos
        system = await db.forensic_systems.find_one({"urn": urn})
        if not system:
            # Intentar también con @id
            system = await db.forensic_systems.find_one({"@id": urn})

        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sistema forense no encontrado: {urn}"
            )

        logger.info(f"Sistema forense encontrado: {system.get('hasName', 'Unknown')}")

        # 2. Convertir sistema forense a TTL
        system_ttl = forensic_system_to_ttl(system)
        logger.info(f"Sistema forense convertido a TTL:\n{system_ttl[:500]}...")

        # 2.5. PRE-VALIDACIÓN SHACL
        logger.info("Iniciando pre-validación SHACL para sistema forense...")
        is_valid, validation_error = validate_system_pre(system_ttl, shapes_graph)

        if not is_valid:
            logger.warning(f"Pre-validación fallida (continuando): {validation_error[:200]}")
        else:
            logger.info("Pre-validación SHACL completada ✓")

        # 3. Obtener reglas SWRL y conceptos
        swrl_rules = get_basic_prefixes() + get_ai_act_concepts() + get_swrl_rules()
        logger.info(f"Reglas SWRL y conceptos cargados")

        # 4. Ejecutar razonamiento
        reasoner_response = await call_reasoner_service(system_ttl, swrl_rules)
        logger.info(f"Razonamiento completado, inferencias: {reasoner_response.get('rules_applied', 0)}")

        # 4.5. POST-VALIDACIÓN SHACL
        raw_ttl = reasoner_response.get("raw_ttl", "")
        shacl_post_validation = validate_results_post(raw_ttl, shapes_graph)

        # 5. Extraer relaciones inferidas
        relationships = reasoner_response.get("inferred_relationships", {
            "hasNormativeCriterion": [],
            "hasTechnicalCriterion": [],
            "hasContextualCriterion": [],
            "hasRequirement": [],
            "hasTechnicalRequirement": [],
            "hasCriteria": [],
            "hasComplianceRequirement": [],
            "hasRiskLevel": [],
            "hasGPAIClassification": []
        })

        rules_applied = reasoner_response.get("rules_applied", sum(len(values) for values in relationships.values()))

        # 5.5. Persistir inferencias en MongoDB y Fuseki
        # Usar nombres de propiedades estándar (sin prefijo "inferred_")
        if relationships:
            # Mapeo a nombres de campos en MongoDB (consistente con la ontología)
            mongo_field_map = {
                "hasNormativeCriterion": "hasNormativeCriterion",
                "hasTechnicalCriterion": "hasTechnicalCriterion",
                "hasContextualCriterion": "hasContextualCriterion",
                "hasRequirement": "hasRequirement",
                "hasTechnicalRequirement": "hasTechnicalRequirement",
                "hasCriteria": "hasActivatedCriterion",
                "hasComplianceRequirement": "hasComplianceRequirement",
                "hasRiskLevel": "hasRiskLevel",
                "hasGPAIClassification": "hasGPAIClassification"
            }

            # Actualizar en MongoDB
            update_data = {}
            for rel_type, values in relationships.items():
                if values:
                    field_name = mongo_field_map.get(rel_type, rel_type)
                    update_data[field_name] = values

            if update_data:
                await db.forensic_systems.update_one(
                    {"urn": urn},
                    {"$set": update_data}
                )
                logger.info(f"Sistema forense actualizado en MongoDB con inferencias: {update_data.keys()}")

                # Persistir en Fuseki
                await persist_inferences_to_fuseki(urn, relationships)
                logger.info(f"Inferencias forenses persistidas en Fuseki para: {urn}")

        # 6. Retornar resultado
        return {
            "system_id": urn,
            "system_name": system.get("hasName", "Unknown Forensic System"),
            "system_type": "forensic",
            "organization": system.get("hasOrganization", "Unknown"),
            "original_risk_level": system.get("hasRiskLevel", "Unknown"),
            "reasoning_completed": True,
            "inferred_relationships": relationships,
            "raw_ttl": raw_ttl,
            "rules_applied": rules_applied,
            "shacl_validation": {
                "pre_validation": {
                    "status": "passed" if is_valid else "warning",
                    "enabled": ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE
                },
                "post_validation": {
                    "status": "passed" if shacl_post_validation["valid"] else "failed",
                    "valid": shacl_post_validation["valid"],
                    "message": shacl_post_validation["message"],
                    "enabled": ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forensic reasoning process: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el proceso de razonamiento forense: {str(e)}"
        )


@router.get("/rules")
async def get_available_rules():
    """
    Obtiene las reglas SWRL disponibles para razonamiento
    """
    swrl_rules = get_basic_prefixes() + get_ai_act_concepts() + get_swrl_rules()
    
    # Parse de las reglas para obtener metadata
    rules = []
    for line in swrl_rules.split('\n'):
        line = line.strip()
        if line.startswith('[') and line.endswith(']:'):
            rule_name = line[1:-2]  # Remove [ and ]:
            rules.append({
                "name": rule_name,
                "description": f"Regla SWRL: {rule_name}"
            })
    
    return {
        "total_rules": len(rules),
        "rules": rules,
        "raw_swrl": swrl_rules
    }

@router.get("/test-ttl/{system_id}")
async def test_ttl_generation(
    system_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Endpoint para testear la generación de TTL"""
    try:
        # Decodificar system_id si está URL-encoded
        system_id = unquote(system_id)
        
        from bson import ObjectId
        
        # Determinar cómo buscar el sistema
        if system_id.startswith("urn:uuid:"):
            # Es un URN, buscar por ai:hasUrn
            query = {"ai:hasUrn": system_id}
        else:
            # Podría ser un ObjectId o algún otro identificador
            try:
                if len(system_id) == 24:  # Longitud típica de ObjectId
                    query = {"_id": ObjectId(system_id)}
                else:
                    # Intentar buscar por URN primero, luego por _id
                    query = {"$or": [{"ai.hasUrn": system_id}, {"_id": system_id}]}
            except:
                # Si no es ObjectId válido, buscar por URN o _id
                query = {"$or": [{"ai.hasUrn": system_id}, {"_id": system_id}]}
        
        system = await db.systems.find_one(query)
        if not system:
            raise HTTPException(status_code=404, detail="Sistema no encontrado")
        
        # Generar TTL
        system_ttl = system_to_ttl(system)
        
        return {
            "system_id": system_id,
            "system_name": system.get("hasName", "Unknown"),
            "ttl_content": system_ttl,
            "ttl_length": len(system_ttl)
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/status")
async def reasoning_service_status():
    """
    Verifica el estado del servicio de razonamiento
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{REASONER_SERVICE_URL}/")

            if response.status_code == 200:
                return {
                    "reasoner_service": "available",
                    "url": REASONER_SERVICE_URL,
                    "response": response.json()
                }
            else:
                return {
                    "reasoner_service": "unavailable",
                    "url": REASONER_SERVICE_URL,
                    "status_code": response.status_code
                }

    except Exception as e:
        return {
            "reasoner_service": "error",
            "url": REASONER_SERVICE_URL,
            "error": str(e)
        }


@router.get("/shacl/status")
async def shacl_validation_status():
    """
    Verifica el estado de la validación SHACL
    """
    return {
        "shacl_validation": {
            "enabled": ENABLE_SHACL_VALIDATION,
            "available": SHACL_AVAILABLE,
            "shapes_path": SHACL_SHAPES_PATH,
            "shapes_file_exists": Path(SHACL_SHAPES_PATH).exists() if ENABLE_SHACL_VALIDATION else None,
            "status": "active" if (ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE) else "disabled"
        }
    }


@router.post("/validate-system")
async def validate_system_endpoint(system: Dict[str, Any]):
    """
    Endpoint para validar un sistema IA sin razonamiento
    Usa SHACL para validación pre-razonamiento
    """
    try:
        shapes_graph = load_shacl_shapes()

        # Convertir sistema a TTL
        system_ttl = system_to_ttl(system)

        # Validar
        is_valid, error_msg = validate_system_pre(system_ttl, shapes_graph)

        return {
            "valid": is_valid,
            "message": error_msg if not is_valid else "Sistema válido",
            "shacl_enabled": ENABLE_SHACL_VALIDATION and SHACL_AVAILABLE,
            "ttl_preview": system_ttl[:500]
        }

    except Exception as e:
        logger.error(f"Error validating system: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando sistema: {str(e)}"
        )