"""
Router para servicios de razonamiento semántico
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import httpx
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from db import get_database
from swrl_rules import get_swrl_rules, get_basic_prefixes, get_ai_act_concepts
import json
import logging
from rdflib import Graph, URIRef, RDF, RDFS, Literal
from rdflib.namespace import Namespace
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reasoning", tags=["reasoning"])

# Configuración del servicio reasoner
REASONER_SERVICE_URL = os.environ.get("REASONER_SERVICE_URL", "http://reasoner:8001")
ONTOLOGY_PATH = os.environ.get("ONTOLOGY_PATH", "/ontologias/ontologia-v0.36.0.ttl")

# Namespaces
AI = Namespace("http://ai-act.eu/ai#")

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
    
    # Nivel de riesgo
    if system.get("hasRiskLevel"):
        risk_uri = system["hasRiskLevel"]
        if not risk_uri.startswith("ai:"):
            risk_uri = f"ai:{risk_uri}"
        properties.append(f"{subject} ai:hasRiskLevel {risk_uri}")
    
    # Combinar prefijos y propiedades
    ttl_content = prefixes + "\n" + " .\n".join(properties) + " .\n"
    
    return ttl_content

async def call_reasoner_service(system_ttl: str, swrl_rules: str) -> str:
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
                files=files
            )
            
            if response.status_code != 200:
                logger.error(f"Reasoner service error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error del servicio de razonamiento: {response.status_code}"
                )
            
            return response.text
            
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

@router.post("/system/{system_id}")
async def reason_system(
    system_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Ejecuta razonamiento semántico sobre un sistema específico
    """
    
    try:
        # 1. Obtener sistema de la base de datos
        from bson import ObjectId
        
        # Intentar convertir a ObjectId si es necesario
        try:
            if len(system_id) == 24:  # Longitud típica de ObjectId
                query_id = ObjectId(system_id)
            else:
                query_id = system_id
        except:
            query_id = system_id
            
        system = await db.systems.find_one({"_id": query_id})
        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sistema no encontrado"
            )
        
        # 2. Convertir sistema a TTL
        system_ttl = system_to_ttl(system)
        logger.info(f"Sistema convertido a TTL completo:\n{system_ttl}")
        logger.info(f"TTL preview: {system_ttl[:200]}...")
        
        # 3. Obtener reglas SWRL y conceptos
        swrl_rules = get_basic_prefixes() + get_ai_act_concepts() + get_swrl_rules()
        logger.info(f"Reglas SWRL y conceptos cargados: {len(swrl_rules.split('Rule'))} reglas")
        
        # 4. Ejecutar razonamiento
        inferred_ttl = await call_reasoner_service(system_ttl, swrl_rules)
        logger.info(f"Razonamiento completado, resultado: {len(inferred_ttl)} caracteres")
        
        # 5. Parsear relaciones inferidas
        relationships = parse_inferred_relationships(inferred_ttl)
        logger.info(f"Relaciones inferidas: {relationships}")
        
        # 6. Actualizar sistema con inferencias (opcional)
        update_data = {}
        for rel_type, values in relationships.items():
            if values:  # Solo actualizar si hay valores inferidos
                update_data[f"inferred_{rel_type}"] = values
        
        if update_data:
            await db.systems.update_one(
                {"_id": system_id},
                {"$set": update_data}
            )
            logger.info(f"Sistema actualizado con inferencias: {update_data.keys()}")
        
        # 7. Calcular número de reglas aplicadas (inferencias generadas)
        rules_applied = sum(len(values) for values in relationships.values())
        logger.info(f"DEBUG rules_applied calculation: {rules_applied}")
        logger.info(f"DEBUG relationships: {relationships}")
        
        # 8. Retornar resultado completo
        return {
            "system_id": system_id,
            "system_name": system.get("hasName", "Unnamed"),
            "reasoning_completed": True,
            "inferred_relationships": relationships,
            "raw_ttl": inferred_ttl,
            "rules_applied": rules_applied
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reasoning process: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el proceso de razonamiento: {str(e)}"
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
        from bson import ObjectId
        
        # Obtener sistema
        try:
            if len(system_id) == 24:
                query_id = ObjectId(system_id)
            else:
                query_id = system_id
        except:
            query_id = system_id
            
        system = await db.systems.find_one({"_id": query_id})
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