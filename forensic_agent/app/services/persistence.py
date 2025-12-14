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
        iso_42001 = analysis_result.get("iso_42001", {})
        nist_ai_rmf = analysis_result.get("nist_ai_rmf", {})
        evidence_plan = analysis_result.get("evidence_plan", {})
        report = analysis_result.get("report", "")

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

            # AIRO-aligned stakeholder fields (Art. 3.3-3.4 EU AI Act)
            "hasDeployer": system_info.get("deployer"),
            "hasDeveloper": system_info.get("developer"),

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
            "createdAt": datetime.utcnow().isoformat(),

            # ISO 42001 Assessment
            "iso_42001": {
                "total_mapped": iso_42001.get("total_mapped", 0),
                "certification_gap_detected": iso_42001.get("certification_gap_detected", False),
                "mappings": iso_42001.get("mappings", {})
            },

            # NIST AI RMF Assessment
            "nist_ai_rmf": {
                "total_mapped": nist_ai_rmf.get("total_mapped", 0),
                "jurisdiction_applicable": nist_ai_rmf.get("jurisdiction_applicable", False),
                "voluntary_guidance_ignored": nist_ai_rmf.get("voluntary_guidance_ignored", False),
                "mappings": nist_ai_rmf.get("mappings", {})
            },

            # Full markdown report
            "report": report,

            # Evidence Plan (if generated)
            "evidence_plan": evidence_plan if evidence_plan else None
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

            # Step 2b: Save Evidence Plan to Fuseki if present
            if evidence_plan:
                ev_ttl_data = self._build_evidence_plan_turtle(evidence_plan, urn)
                if ev_ttl_data:
                    await self._save_to_fuseki(ev_ttl_data)
                    print(f"   ✓ Evidence Plan saved to Fuseki: {evidence_plan.get('plan_id', 'unknown')}")

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
            "@prefix dpv: <https://w3id.org/dpv#> .",
            "@prefix dpv-ai: <https://w3id.org/dpv/ai#> .",
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

        # AIRO-aligned stakeholder properties (Art. 3.3-3.4 EU AI Act)
        if system_doc.get("hasDeployer"):
            lines.append(f'    ai:hasDeployer "{self._escape_turtle(system_doc["hasDeployer"])}" ;')
        if system_doc.get("hasDeveloper"):
            lines.append(f'    ai:hasDeveloper "{self._escape_turtle(system_doc["hasDeveloper"])}" ;')

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

    def _build_evidence_plan_turtle(self, evidence_plan: Dict, system_urn: str) -> str:
        """Build Turtle RDF representation of the Evidence Plan with DPV mappings."""
        if not evidence_plan:
            return ""

        plan_id = evidence_plan.get("plan_id", "")
        plan_urn = f"urn:evidence-plan:{plan_id}"

        lines = [
            "@prefix ai: <http://ai-act.eu/ai#> .",
            "@prefix forensic: <http://ai-act.eu/forensic#> .",
            "@prefix dpv: <https://w3id.org/dpv#> .",
            "@prefix dpv-ai: <https://w3id.org/dpv/ai#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            ""
        ]

        # Evidence Plan declaration
        lines.append(f"<{plan_urn}> a forensic:EvidencePlan ;")
        lines.append(f'    rdfs:label "Evidence Plan for {self._escape_turtle(evidence_plan.get("system_name", "Unknown"))}" ;')
        lines.append(f'    forensic:planId "{plan_id}" ;')
        lines.append(f'    forensic:forSystem <{system_urn}> ;')
        lines.append(f'    forensic:riskLevel "{evidence_plan.get("risk_level", "Unknown")}" ;')
        lines.append(f'    forensic:generatedAt "{evidence_plan.get("generated_at", "")}"^^xsd:dateTime ;')

        # Summary metrics
        summary = evidence_plan.get("summary", {})
        lines.append(f'    forensic:totalRequirements "{summary.get("total_requirements", 0)}"^^xsd:integer ;')
        lines.append(f'    forensic:totalEvidenceItems "{summary.get("total_evidence_items", 0)}"^^xsd:integer ;')

        # Link to requirement plans
        for req_plan in evidence_plan.get("requirement_plans", []):
            req_uri = req_plan.get("requirement_uri", "")
            if req_uri:
                # Create a unique URI for each requirement plan
                req_plan_urn = f"{plan_urn}:req:{req_uri.split('#')[-1]}"
                lines.append(f'    forensic:hasRequirementPlan <{req_plan_urn}> ;')

        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

        # Link system to evidence plan
        lines.append(f"<{system_urn}> forensic:hasEvidencePlan <{plan_urn}> .")
        lines.append("")

        # Generate RequirementPlan instances
        for req_plan in evidence_plan.get("requirement_plans", []):
            req_uri = req_plan.get("requirement_uri", "")
            if not req_uri:
                continue

            req_label = req_uri.split("#")[-1]
            req_plan_urn = f"{plan_urn}:req:{req_label}"

            lines.append(f"<{req_plan_urn}> a forensic:RequirementEvidencePlan ;")
            lines.append(f'    rdfs:label "{self._escape_turtle(req_plan.get("requirement_label", req_label))}" ;')
            lines.append(f'    forensic:forRequirement <{req_uri}> ;')
            lines.append(f'    forensic:articleReference "{req_plan.get("article_reference", "")}" ;')
            lines.append(f'    forensic:priority "{req_plan.get("priority", "medium")}" ;')
            lines.append(f'    forensic:deadline "{req_plan.get("deadline_recommendation", "")}" ;')

            # DPV measures mapping
            for measure in req_plan.get("dpv_measures", []):
                if measure.startswith("dpv:"):
                    lines.append(f'    ai:mapsToDPVMeasure {measure} ;')
                else:
                    lines.append(f'    ai:mapsToDPVMeasure dpv:{measure} ;')

            # Link to evidence items
            for ev_item in req_plan.get("evidence_items", []):
                ev_id = ev_item.get("id", "")
                if ev_id:
                    ev_urn = f"{req_plan_urn}:ev:{ev_id}"
                    lines.append(f'    forensic:requiresEvidence <{ev_urn}> ;')

            lines[-1] = lines[-1].rstrip(" ;") + " ."
            lines.append("")

            # Generate EvidenceItem instances
            for ev_item in req_plan.get("evidence_items", []):
                ev_id = ev_item.get("id", "")
                if not ev_id:
                    continue

                ev_urn = f"{req_plan_urn}:ev:{ev_id}"
                ev_type = ev_item.get("type", "Evidence")

                lines.append(f"<{ev_urn}> a forensic:EvidenceItem, forensic:{ev_type} ;")
                lines.append(f'    rdfs:label "{self._escape_turtle(ev_item.get("name", ev_id))}" ;')
                lines.append(f'    forensic:evidenceId "{ev_id}" ;')

                if ev_item.get("description"):
                    lines.append(f'    forensic:description "{self._escape_turtle(ev_item["description"])}" ;')

                lines.append(f'    forensic:priority "{ev_item.get("priority", "medium")}" ;')

                if ev_item.get("frequency"):
                    lines.append(f'    forensic:frequency "{ev_item["frequency"]}" ;')

                # DPV measure mapping for evidence item
                if ev_item.get("dpv_measure"):
                    measure = ev_item["dpv_measure"]
                    if measure.startswith("dpv:"):
                        lines.append(f'    dpv:hasOrganisationalMeasure {measure} ;')
                    else:
                        lines.append(f'    dpv:hasOrganisationalMeasure dpv:{measure} ;')

                lines[-1] = lines[-1].rstrip(" ;") + " ."
                lines.append("")

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

        # Get evidence plan ID before deleting from MongoDB
        doc = await self._db.forensic_systems.find_one({"urn": urn})
        evidence_plan_id = None
        if doc and doc.get("evidence_plan"):
            evidence_plan_id = doc["evidence_plan"].get("plan_id")

        # Delete from MongoDB
        result = await self._db.forensic_systems.delete_one({"urn": urn})
        if result.deleted_count == 0:
            return False

        # Delete system from Fuseki
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

            # Delete evidence plan and related items from Fuseki
            if evidence_plan_id:
                plan_urn = f"urn:evidence-plan:{evidence_plan_id}"
                sparql_plan = f"""
                DELETE WHERE {{
                    GRAPH <{FUSEKI_GRAPH}> {{
                        <{plan_urn}> ?p ?o .
                    }}
                }}
                """
                await client.post(
                    f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update",
                    content=sparql_plan,
                    headers={"Content-Type": "application/sparql-update"},
                    auth=(FUSEKI_USER, FUSEKI_PASSWORD),
                    timeout=30.0
                )

                # Delete requirement plans and evidence items (pattern match)
                sparql_items = f"""
                DELETE WHERE {{
                    GRAPH <{FUSEKI_GRAPH}> {{
                        ?s ?p ?o .
                        FILTER(STRSTARTS(STR(?s), "{plan_urn}:"))
                    }}
                }}
                """
                await client.post(
                    f"{FUSEKI_ENDPOINT}/{FUSEKI_DATASET}/update",
                    content=sparql_items,
                    headers={"Content-Type": "application/sparql-update"},
                    auth=(FUSEKI_USER, FUSEKI_PASSWORD),
                    timeout=30.0
                )
                print(f"   ✓ Evidence Plan deleted from Fuseki: {plan_urn}")

        return True
