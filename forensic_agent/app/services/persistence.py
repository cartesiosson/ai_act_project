"""Persistence service for storing analyzed AI systems in MongoDB and Fuseki"""

import os
import uuid
import json
from typing import Dict, Optional
from datetime import datetime
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "ai_act_db")

FUSEKI_ENDPOINT = os.getenv("FUSEKI_ENDPOINT", "http://fuseki:3030")
FUSEKI_DATASET = os.getenv("FUSEKI_DATASET", "ds")
FUSEKI_GRAPH = os.getenv("FUSEKI_GRAPH_DATA", "http://ai-act.eu/ontology/data")
FUSEKI_USER = os.getenv("FUSEKI_USER", "admin")
FUSEKI_PASSWORD = os.getenv("FUSEKI_PASSWORD", "admin")


class PersistenceService:
    """
    Service to persist analyzed AI systems to MongoDB and Fuseki.
    """

    def __init__(self):
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._db = None

    async def ensure_connected(self):
        """Ensure MongoDB connection is established."""
        if self._mongo_client is None:
            self._mongo_client = AsyncIOMotorClient(MONGO_URI)
            self._db = self._mongo_client[MONGO_DB]
            # Ensure indexes
            await self._db.forensic_systems.create_index("urn", unique=True)
            await self._db.forensic_systems.create_index("aiaaic_id", sparse=True)

    async def persist_analyzed_system(
        self,
        analysis_result: Dict,
        source: str = "forensic_agent",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Persist an analyzed AI system to MongoDB and Fuseki.

        Args:
            analysis_result: The complete forensic analysis result
            source: Source of the analysis (e.g., "forensic_agent", "AIAAIC")
            metadata: Additional metadata (e.g., aiaaic_id)

        Returns:
            Dict with persistence result including URN
        """
        await self.ensure_connected()

        # Extract system info from analysis result
        extraction = analysis_result.get("extraction", {})
        system_info = extraction.get("system", {})
        incident_info = extraction.get("incident", {})
        eu_ai_act = analysis_result.get("eu_ai_act", {})
        compliance_gaps = analysis_result.get("compliance_gaps", {})

        # Generate URN for the system
        urn = f"urn:forensic:{uuid.uuid4()}"

        # Build system document for MongoDB
        system_doc = {
            "urn": urn,
            "@id": urn,
            "@type": "ai:ForensicAnalyzedSystem",
            "hasName": system_info.get("system_name", "Unknown System"),
            "hasOrganization": system_info.get("organization", "Unknown"),
            "hasVersion": system_info.get("version"),

            # Classification from analysis
            "hasRiskLevel": f"ai:{eu_ai_act.get('risk_level', 'Unknown')}",
            "hasPurpose": [f"ai:{system_info.get('primary_purpose', 'Unknown')}"],
            "hasDeploymentContext": [f"ai:{ctx}" for ctx in system_info.get("deployment_context", [])],
            "processesDataTypes": system_info.get("processes_data_types", []),

            # Criteria and requirements from EU AI Act analysis
            "hasCriteria": eu_ai_act.get("criteria", []),
            "hasComplianceRequirement": [req.get("uri", req.get("label", "")) for req in eu_ai_act.get("requirements", [])],

            # Compliance metrics
            "complianceRatio": compliance_gaps.get("compliance_ratio", 0.0),
            "complianceSeverity": compliance_gaps.get("severity", "UNKNOWN"),
            "missingRequirements": compliance_gaps.get("missing_requirements", []),

            # System properties
            "isAutomatedDecision": system_info.get("is_automated_decision", False),
            "hasHumanOversight": system_info.get("has_human_oversight"),
            "modelScale": system_info.get("model_scale"),
            "jurisdiction": system_info.get("jurisdiction", "Unknown"),

            # Incident info
            "incident": {
                "type": incident_info.get("incident_type"),
                "severity": incident_info.get("severity"),
                "affectedPopulations": incident_info.get("affected_populations", []),
                "affectedCount": incident_info.get("affected_count"),
                "publicDisclosure": incident_info.get("public_disclosure", False)
            },

            # Metadata
            "source": source,
            "analysisTimestamp": analysis_result.get("analysis_timestamp", datetime.utcnow().isoformat()),
            "extractionConfidence": extraction.get("confidence", {}).get("overall", 0.0),
            "requiresExpertReview": analysis_result.get("requires_expert_review", True),
            "createdAt": datetime.utcnow().isoformat()
        }

        # Add external IDs if provided
        if metadata:
            if "aiaaic_id" in metadata:
                system_doc["aiaaic_id"] = metadata["aiaaic_id"]
            if "headline" in metadata:
                system_doc["headline"] = metadata["headline"]
            system_doc["metadata"] = metadata

        # Step 1: Save to MongoDB
        try:
            result = await self._db.forensic_systems.insert_one(system_doc)
            mongo_id = str(result.inserted_id)
            print(f"   ✓ Saved to MongoDB: {urn}")
        except Exception as e:
            print(f"   ✗ MongoDB save failed: {e}")
            return {"success": False, "error": f"MongoDB save failed: {e}"}

        # Step 2: Save to Fuseki as RDF
        try:
            ttl_data = self._build_turtle(system_doc, urn)
            await self._save_to_fuseki(ttl_data)
            print(f"   ✓ Saved to Fuseki: {urn}")
        except Exception as e:
            print(f"   ✗ Fuseki save failed: {e}")
            # Rollback MongoDB insert
            await self._db.forensic_systems.delete_one({"urn": urn})
            return {"success": False, "error": f"Fuseki save failed: {e}"}

        return {
            "success": True,
            "urn": urn,
            "mongo_id": mongo_id,
            "message": "System persisted to MongoDB and Fuseki"
        }

    def _build_turtle(self, system_doc: Dict, urn: str) -> str:
        """Build Turtle RDF representation of the analyzed system."""
        lines = [
            "@prefix ai: <http://ai-act.eu/ai#> .",
            "@prefix forensic: <http://ai-act.eu/forensic#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            ""
        ]

        # System declaration
        lines.append(f"<{urn}> a ai:AISystem, forensic:AnalyzedSystem ;")
        lines.append(f'    rdfs:label "{self._escape_turtle(system_doc.get("hasName", "Unknown"))}" ;')
        lines.append(f'    ai:hasName "{self._escape_turtle(system_doc.get("hasName", "Unknown"))}" ;')

        # Organization
        if system_doc.get("hasOrganization"):
            lines.append(f'    ai:hasOrganization "{self._escape_turtle(system_doc["hasOrganization"])}" ;')

        # Risk level
        risk_level = system_doc.get("hasRiskLevel", "ai:Unknown")
        if not risk_level.startswith("ai:"):
            risk_level = f"ai:{risk_level}"
        lines.append(f'    ai:hasRiskLevel {risk_level} ;')

        # Purpose
        for purpose in system_doc.get("hasPurpose", []):
            if purpose and purpose != "ai:Unknown":
                purpose_uri = purpose if purpose.startswith("ai:") else f"ai:{purpose}"
                lines.append(f'    ai:hasPurpose {purpose_uri} ;')

        # Deployment context
        for ctx in system_doc.get("hasDeploymentContext", []):
            if ctx:
                ctx_uri = ctx if ctx.startswith("ai:") else f"ai:{ctx}"
                lines.append(f'    ai:hasDeploymentContext {ctx_uri} ;')

        # Criteria
        for criterion in system_doc.get("hasCriteria", []):
            if criterion:
                crit_uri = criterion if criterion.startswith("<") or criterion.startswith("ai:") else f"<{criterion}>"
                if crit_uri.startswith("ai:"):
                    lines.append(f'    ai:hasCriteria {crit_uri} ;')
                else:
                    lines.append(f'    ai:hasCriteria {crit_uri} ;')

        # Compliance requirements
        for req in system_doc.get("hasComplianceRequirement", []):
            if req:
                req_uri = req if req.startswith("<") or req.startswith("ai:") else f"<{req}>"
                if req_uri.startswith("ai:"):
                    lines.append(f'    ai:hasComplianceRequirement {req_uri} ;')
                else:
                    lines.append(f'    ai:hasComplianceRequirement {req_uri} ;')

        # Compliance metrics
        lines.append(f'    forensic:complianceRatio "{system_doc.get("complianceRatio", 0.0)}"^^xsd:decimal ;')
        lines.append(f'    forensic:complianceSeverity "{system_doc.get("complianceSeverity", "UNKNOWN")}" ;')

        # Jurisdiction
        if system_doc.get("jurisdiction"):
            lines.append(f'    ai:hasJurisdiction "{system_doc["jurisdiction"]}" ;')

        # Incident type
        incident = system_doc.get("incident", {})
        if incident.get("type"):
            lines.append(f'    forensic:incidentType "{incident["type"]}" ;')
        if incident.get("severity"):
            lines.append(f'    forensic:incidentSeverity "{incident["severity"]}" ;')

        # Source and timestamp
        lines.append(f'    forensic:source "{system_doc.get("source", "forensic_agent")}" ;')
        lines.append(f'    forensic:analysisTimestamp "{system_doc.get("analysisTimestamp", "")}"^^xsd:dateTime ;')
        lines.append(f'    forensic:extractionConfidence "{system_doc.get("extractionConfidence", 0.0)}"^^xsd:decimal ;')

        # External IDs
        if system_doc.get("aiaaic_id"):
            lines.append(f'    forensic:aiaaicId "{system_doc["aiaaic_id"]}" ;')

        # Close the statement (replace last ; with .)
        lines[-1] = lines[-1].rstrip(" ;") + " ."

        return "\n".join(lines)

    def _escape_turtle(self, value: str) -> str:
        """Escape special characters for Turtle format."""
        if not value:
            return ""
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")

    async def _save_to_fuseki(self, ttl_data: str):
        """Save Turtle data to Fuseki."""
        url = f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/data?graph={FUSEKI_GRAPH}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                content=ttl_data.encode("utf-8"),
                headers={"Content-Type": "text/turtle"},
                auth=(FUSEKI_USER, FUSEKI_PASSWORD),
                timeout=30.0
            )

            if response.status_code not in (200, 201, 204):
                raise Exception(f"Fuseki error {response.status_code}: {response.text}")

    async def get_analyzed_systems(
        self,
        limit: int = 20,
        offset: int = 0,
        source: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> Dict:
        """Get list of analyzed systems from MongoDB."""
        await self.ensure_connected()

        query = {}
        if source:
            query["source"] = source
        if risk_level:
            query["hasRiskLevel"] = f"ai:{risk_level}" if not risk_level.startswith("ai:") else risk_level

        total = await self._db.forensic_systems.count_documents(query)
        cursor = self._db.forensic_systems.find(query).sort("createdAt", -1).skip(offset).limit(limit)

        systems = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            systems.append(doc)

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": systems
        }

    async def get_system_by_urn(self, urn: str) -> Optional[Dict]:
        """Get a specific analyzed system by URN."""
        await self.ensure_connected()
        doc = await self._db.forensic_systems.find_one({"urn": urn})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def delete_system(self, urn: str) -> bool:
        """Delete an analyzed system from both MongoDB and Fuseki."""
        await self.ensure_connected()

        # Delete from MongoDB
        result = await self._db.forensic_systems.delete_one({"urn": urn})
        if result.deleted_count == 0:
            return False

        # Delete from Fuseki
        sparql = f"""
        DELETE WHERE {{
            GRAPH <{FUSEKI_GRAPH}> {{
                <{urn}> ?p ?o .
            }}
        }}
        """

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update",
                content=sparql,
                headers={"Content-Type": "application/sparql-update"},
                auth=(FUSEKI_USER, FUSEKI_PASSWORD),
                timeout=30.0
            )

            if response.status_code not in (200, 204):
                print(f"Warning: Fuseki delete failed: {response.text}")

        return True
