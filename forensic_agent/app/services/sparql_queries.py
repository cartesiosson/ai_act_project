"""SPARQL query service for forensic compliance analysis"""

import os
from typing import Dict, List, Optional, Set
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
from pathlib import Path

AI = Namespace("http://ai-act.eu/ai#")
ISO = Namespace("http://iso.org/42001#")
NIST = Namespace("http://nist.gov/ai-rmf#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


class ForensicSPARQLService:
    """
    SPARQL query service for forensic compliance analysis
    with multi-framework support (EU AI Act + ISO 42001 + NIST AI RMF)
    """

    def __init__(self, ontology_path: Optional[str] = None, mappings_path: Optional[str] = None):
        """
        Initialize with ontology and mappings paths

        Args:
            ontology_path: Path to EU AI Act ontology file
            mappings_path: Path to mappings directory
        """
        self.ontology_path = ontology_path or os.getenv("ONTOLOGY_PATH", "/ontologias/ontologia-v0.37.2.ttl")
        self.mappings_path = mappings_path or os.getenv("MAPPINGS_PATH", "/ontologias/mappings")

        # Initialize RDF graph
        self.graph = Graph()

        # Bind namespaces
        self.graph.bind("ai", AI)
        self.graph.bind("iso", ISO)
        self.graph.bind("nist", NIST)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("rdf", RDF)

        # Load ontology and mappings
        self._load_ontology()

    def _load_ontology(self):
        """Load ontology and mappings from files"""
        try:
            # Load main ontology
            if os.path.exists(self.ontology_path):
                print(f"Loading ontology from: {self.ontology_path}")
                self.graph.parse(self.ontology_path, format="turtle")
                print(f"✓ Ontology loaded: {len(self.graph)} triples")
            else:
                print(f"⚠ Ontology file not found: {self.ontology_path}")

            # Load ISO 42001 mappings
            iso_mappings = os.path.join(self.mappings_path, "iso-42001-mappings.ttl")
            if os.path.exists(iso_mappings):
                print(f"Loading ISO 42001 mappings from: {iso_mappings}")
                self.graph.parse(iso_mappings, format="turtle")
                print(f"✓ ISO mappings loaded")
            else:
                print(f"⚠ ISO mappings not found: {iso_mappings}")

            # Load NIST AI RMF mappings
            nist_mappings = os.path.join(self.mappings_path, "nist-ai-rmf-mappings.ttl")
            if os.path.exists(nist_mappings):
                print(f"Loading NIST AI RMF mappings from: {nist_mappings}")
                self.graph.parse(nist_mappings, format="turtle")
                print(f"✓ NIST mappings loaded")
            else:
                print(f"⚠ NIST mappings not found: {nist_mappings}")

            print(f"✓ Total triples loaded: {len(self.graph)}")

        except Exception as e:
            print(f"✗ Error loading ontology/mappings: {e}")
            raise

    async def query_mandatory_requirements(self,
                                          purpose: str,
                                          contexts: List[str],
                                          data_types: List[str]) -> Dict:
        """
        Query ontology for mandatory EU AI Act requirements

        Args:
            purpose: Primary purpose (e.g., "BiometricIdentification")
            contexts: Deployment contexts (e.g., ["PublicSpaces", "HighVolume"])
            data_types: Data types processed (e.g., ["BiometricData"])

        Returns:
            Dict with criteria, requirements, and risk level
        """

        # Build purpose URI
        purpose_uri = AI[purpose] if purpose else None

        # Build context URIs
        context_uris = [AI[ctx] for ctx in contexts if ctx]

        # Build SPARQL query
        query_str = f"""
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?requirement ?requirementLabel ?criterion ?criterionLabel
        WHERE {{
          {{
            # Purpose-based criteria
            {f"<{purpose_uri}> ai:activatesCriterion ?criterion ." if purpose_uri else ""}
          }}
          UNION
          {{
            # Context-based criteria
            VALUES ?context {{ {" ".join([f"<{ctx}>" for ctx in context_uris])} }}
            ?context ai:triggersCriterion ?criterion .
          }}

          # Get requirements from criteria
          ?criterion ai:activatesRequirement ?requirement .
          ?requirement rdfs:label ?requirementLabel .

          OPTIONAL {{
            ?criterion rdfs:label ?criterionLabel .
          }}
        }}
        ORDER BY ?requirementLabel
        """

        try:
            results = self.graph.query(query_str)

            # Parse results
            requirements = []
            criteria = set()
            seen_requirements = set()  # Avoid duplicates

            for row in results:
                req_uri = str(row.requirement)

                # Skip duplicates
                if req_uri in seen_requirements:
                    continue
                seen_requirements.add(req_uri)

                requirements.append({
                    "uri": req_uri,
                    "label": str(row.requirementLabel) if row.requirementLabel else req_uri.split("#")[-1],
                    "criterion": str(row.criterion) if row.criterion else ""
                })

                if row.criterion:
                    criteria.add(str(row.criterion))

            # Determine risk level
            risk_level = self._determine_risk_level(list(criteria))

            return {
                "criteria": list(criteria),
                "requirements": requirements,
                "risk_level": risk_level,
                "total_requirements": len(requirements)
            }

        except Exception as e:
            print(f"Error querying mandatory requirements: {e}")
            return {
                "criteria": [],
                "requirements": [],
                "risk_level": "Unknown",
                "total_requirements": 0
            }

    async def query_iso_42001_mappings(self, eu_requirements: List[str]) -> Dict:
        """
        Query ISO 42001 mappings for EU AI Act requirements

        Args:
            eu_requirements: List of EU AI Act requirement URIs

        Returns:
            Dict with ISO controls mapped to each requirement
        """

        query_str = """
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX iso: <http://iso.org/42001#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?requirement ?isoControl ?isoSection ?isoDescription ?confidence
        WHERE {
          ?requirement ai:equivalentToISOControl ?isoControl ;
                       ai:isoSection ?isoSection ;
                       ai:isoControlDescription ?isoDescription ;
                       ai:mappingConfidence ?confidence .
        }
        """

        try:
            results = self.graph.query(query_str)

            iso_mappings = {}
            for row in results:
                req_uri = str(row.requirement)
                req_name = req_uri.split("#")[-1]

                # Check if this requirement is in our list
                if any(req in req_uri or req_name in req for req in eu_requirements):
                    iso_mappings[req_uri] = {
                        "iso_control": str(row.isoControl),
                        "iso_section": str(row.isoSection),
                        "description": str(row.isoDescription),
                        "confidence": str(row.confidence)
                    }

            return iso_mappings

        except Exception as e:
            print(f"Error querying ISO 42001 mappings: {e}")
            return {}

    async def query_nist_ai_rmf_mappings(self,
                                        eu_requirements: List[str],
                                        jurisdiction: str = "GLOBAL") -> Dict:
        """
        Query NIST AI RMF mappings for EU AI Act requirements

        Args:
            eu_requirements: List of EU AI Act requirement URIs
            jurisdiction: "US", "GLOBAL", or "EU" (for applicability filtering)

        Returns:
            Dict with NIST functions mapped to each requirement
        """

        query_str = """
        PREFIX ai: <http://ai-act.eu/ai#>
        PREFIX nist: <http://nist.gov/ai-rmf#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?requirement ?nistFunction ?nistCategory ?nistDescription
               ?confidence ?applicability
        WHERE {
          ?requirement ai:equivalentToNISTFunction ?nistFunction ;
                       ai:nistCategory ?nistCategory ;
                       ai:nistCategoryDescription ?nistDescription ;
                       ai:nistMappingConfidence ?confidence ;
                       ai:nistApplicabilityContext ?applicability .
        }
        """

        try:
            results = self.graph.query(query_str)

            nist_mappings = {}
            for row in results:
                req_uri = str(row.requirement)
                req_name = req_uri.split("#")[-1]
                applicability = str(row.applicability)

                # Filter by jurisdiction
                if jurisdiction == "US" and "US_INCIDENTS" not in applicability:
                    continue
                if jurisdiction == "EU" and "GLOBAL_INCIDENTS" not in applicability:
                    continue
                # GLOBAL accepts all

                # Check if this requirement is in our list
                if any(req in req_uri or req_name in req for req in eu_requirements):
                    nist_mappings[req_uri] = {
                        "nist_function": str(row.nistFunction),
                        "nist_category": str(row.nistCategory),
                        "description": str(row.nistDescription),
                        "confidence": str(row.confidence),
                        "applicability": applicability
                    }

            return nist_mappings

        except Exception as e:
            print(f"Error querying NIST AI RMF mappings: {e}")
            return {}

    async def analyze_compliance_gaps(self,
                                     mandatory_requirements: List[str],
                                     incident_properties: Dict) -> Dict:
        """
        Analyze compliance gaps based on incident properties

        Args:
            mandatory_requirements: List of required requirement URIs
            incident_properties: Incident details (to infer what was implemented)

        Returns:
            Gap analysis with missing requirements
        """

        # Infer implemented requirements from incident response
        implemented = self._infer_implemented_requirements(incident_properties)

        # Compute gaps
        mandatory_set = set(mandatory_requirements)
        implemented_set = set(implemented)
        missing = mandatory_set - implemented_set

        # Categorize by severity
        critical_gaps = self._categorize_critical_gaps(list(missing))

        # Calculate compliance ratio
        compliance_ratio = len(implemented) / len(mandatory_requirements) if mandatory_requirements else 0.0

        return {
            "total_required": len(mandatory_requirements),
            "implemented": len(implemented),
            "missing": len(missing),
            "compliance_ratio": compliance_ratio,
            "missing_requirements": list(missing),
            "critical_gaps": critical_gaps,
            "severity": self._assess_gap_severity(len(missing), len(mandatory_requirements))
        }

    def _determine_risk_level(self, criteria: List[str]) -> str:
        """Determine risk level from activated criteria"""
        criteria_str = " ".join(criteria).lower()

        # Check for high-risk indicators (Annex III)
        high_risk_keywords = [
            "biometric", "lawenforcement", "migration", "employment",
            "education", "criticalinfrastructure", "emotionrecognition",
            "socialscoring", "predictivepolicing"
        ]

        for keyword in high_risk_keywords:
            if keyword in criteria_str:
                return "HighRisk"

        # Check for limited risk indicators
        limited_risk_keywords = [
            "limitedemotion", "deepfake", "contentclassification"
        ]

        for keyword in limited_risk_keywords:
            if keyword in criteria_str:
                return "LimitedRisk"

        return "MinimalRisk"

    def _infer_implemented_requirements(self, incident_properties: Dict) -> List[str]:
        """
        Infer which requirements were implemented based on incident description

        This is heuristic-based - can be enhanced with LLM reasoning
        """
        implemented = []

        response = incident_properties.get("response", {})
        actions = response.get("actions_taken", [])

        # Simple keyword matching (can be improved)
        action_str = " ".join(actions).lower()

        # Documentation
        if "documentation" in action_str or "record" in action_str or "log" in action_str:
            implemented.append("http://ai-act.eu/ai#DocumentationRequirement")

        # Transparency
        if "transparency" in action_str or "disclosure" in action_str or "inform" in action_str:
            implemented.append("http://ai-act.eu/ai#TransparencyRequirement")

        # Monitoring
        if "monitoring" in action_str or "audit" in action_str or "review" in action_str:
            implemented.append("http://ai-act.eu/ai#MonitoringRequirement")

        # Data governance
        if "data" in action_str and ("quality" in action_str or "governance" in action_str):
            implemented.append("http://ai-act.eu/ai#DataGovernanceRequirement")

        # Human oversight
        if "human" in action_str and ("oversight" in action_str or "review" in action_str):
            implemented.append("http://ai-act.eu/ai#HumanOversightRequirement")

        # Accuracy/Testing
        if "test" in action_str or "accuracy" in action_str or "validation" in action_str:
            implemented.append("http://ai-act.eu/ai#AccuracyRequirement")

        # Note: Most incidents show lack of implementation, so default is minimal
        # This is intentionally conservative - assumes nothing unless explicitly mentioned
        return implemented

    def _categorize_critical_gaps(self, missing: List[str]) -> List[Dict]:
        """Categorize missing requirements by criticality"""
        critical_keywords = [
            ("Biometric", "Critical: Biometric data protection requirement"),
            ("Security", "Critical: Security requirement"),
            ("Safety", "Critical: Safety requirement"),
            ("HumanOversight", "Critical: Human oversight requirement"),
            ("FundamentalRights", "Critical: Fundamental rights requirement"),
            ("NonDiscrimination", "Critical: Non-discrimination requirement"),
            ("Fairness", "Critical: Fairness requirement"),
            ("Bias", "Critical: Bias detection/mitigation requirement")
        ]

        critical = []
        for req in missing:
            req_name = req.split("#")[-1] if "#" in req else req

            for keyword, reason in critical_keywords:
                if keyword.lower() in req_name.lower():
                    critical.append({
                        "requirement": req,
                        "reason": reason
                    })
                    break

        return critical

    def _assess_gap_severity(self, missing_count: int, total_count: int) -> str:
        """Assess severity of compliance gaps"""
        if total_count == 0:
            return "UNKNOWN"

        ratio = missing_count / total_count

        if ratio >= 0.7:
            return "CRITICAL"
        elif ratio >= 0.4:
            return "HIGH"
        elif ratio >= 0.2:
            return "MEDIUM"
        elif ratio > 0:
            return "LOW"
        else:
            return "COMPLIANT"

    async def query_similar_systems_at_risk(self,
                                           incident_type: str,
                                           missing_requirement: str) -> List[Dict]:
        """
        Find other systems with same compliance gap

        Note: This requires a database of registered systems.
        Currently returns empty list as placeholder.
        """
        # TODO: Implement when system database is available
        # This would query Fuseki for systems with:
        # - Same purpose/context as incident
        # - Missing the same requirement
        return []

    def get_stats(self) -> Dict:
        """Get statistics about loaded ontology"""
        return {
            "total_triples": len(self.graph),
            "namespaces": list(self.graph.namespaces()),
            "ontology_loaded": os.path.exists(self.ontology_path),
            "iso_mappings_loaded": os.path.exists(os.path.join(self.mappings_path, "iso-42001-mappings.ttl")),
            "nist_mappings_loaded": os.path.exists(os.path.join(self.mappings_path, "nist-ai-rmf-mappings.ttl"))
        }
